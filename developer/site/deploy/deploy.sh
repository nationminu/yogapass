#!/bin/sh
# ============================================================================
# 배포 스크립트 — 기술 설계 §12.2 의 0 ~ 6 단계를 그대로 구현한다.
#
#   0)   사전 점검 (릴리스 태그 · .env · 디스크 여유 · 롤백 대상 이미지 · IRREVERSIBLE · 최근 백업)
#   0.5) 스케줄러 정지      ← 라벨 백업과 03:00 정기 백업의 락 경합을 **원천 차단**한다
#   1)   라벨 백업          ← skipped 를 성공으로 보지 않는다. 실패하면 배포 중단
#   2)   빌드
#   3)   마이그레이션
#   4)   기동 (app · scheduler)
#   5)   확인 (/healthz 는 **앱에 직접** 호출 — nginx 비경유)
#   6)   실패 시 rollback.sh 자동 호출
#
# 사용법:
#   APP_VERSION=0.1.0 ./deploy/deploy.sh            # 운영
#   ENV_FILE=.env.staging COMPOSE_PROJECT=yogapass-stg ./deploy/deploy.sh
#   ./deploy/deploy.sh --dry-run                    # 0단계 점검만 수행
#
# ⚠ 이 스크립트는 **서버에서** 실행한다. 로컬에서는 --dry-run 까지만 확인된다.
# ============================================================================
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR/.."

ENV_FILE=${ENV_FILE:-.env}
COMPOSE_PROJECT=${COMPOSE_PROJECT:-yogapass}
# 기본은 운영·스테이징 구성이다. 로컬에서 절차를 그대로 재현할 때만 파일 조합을 바꾼다:
#   COMPOSE_FILES="-f compose.yaml -f compose.local.yaml" ./deploy/restore.sh …
COMPOSE_FILES=${COMPOSE_FILES:--f compose.yaml -f compose.prod.yaml}
COMPOSE="docker compose $COMPOSE_FILES -p $COMPOSE_PROJECT"
APP_PORT=${APP_PORT:-8000}
HEALTH_URL=${HEALTH_URL:-http://127.0.0.1:${APP_PORT}/healthz}
MIN_FREE_GB=${BACKUP_MIN_FREE_GB:-5}
HEALTH_TIMEOUT=${HEALTH_TIMEOUT:-120}   # 초. 초과하면 실패로 보고 롤백한다
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

log()  { echo "[deploy] $*"; }
fail() { echo "[deploy] ✗ $*" >&2; exit 1; }

# ---------------------------------------------------------------- 0) 사전 점검
log "0) 사전 점검"
[ -f "$ENV_FILE" ] || fail "$ENV_FILE 이 없습니다."
[ -n "${APP_VERSION:-}" ] || fail "APP_VERSION 이 비어 있습니다 (릴리스 태그와 1:1)."
command -v docker >/dev/null 2>&1 || fail "docker 를 찾을 수 없습니다."

# 릴리스 태그 확인 (저장소에서 빌드하는 경우)
if [ -d .git ] && [ "${SKIP_TAG_CHECK:-0}" != "1" ]; then
  git rev-parse "release-v${APP_VERSION}" >/dev/null 2>&1 \
    || log "⚠ release-v${APP_VERSION} 태그를 찾지 못했습니다(아카이브 반입이면 정상)."
fi

# 디스크 여유
FREE_GB=$(df -Pk . | awk 'NR==2 {printf "%.1f", $4/1048576}')
log "   디스크 여유 ${FREE_GB}GB (하한 ${MIN_FREE_GB}GB)"
awk -v a="$FREE_GB" -v b="$MIN_FREE_GB" 'BEGIN{exit !(a<b)}' && fail "디스크 여유 부족"

# ★ 롤백 대상 이미지 존재 확인 — 없으면 **배포하지 않는다** (§12.1)
CURRENT_IMAGE=$($COMPOSE ps -q app 2>/dev/null | head -1 | xargs -r docker inspect -f '{{.Config.Image}}' 2>/dev/null || true)
if [ -n "$CURRENT_IMAGE" ]; then
  log "   현재 가동 이미지: $CURRENT_IMAGE"
  docker image inspect "$CURRENT_IMAGE" >/dev/null 2>&1 \
    || fail "롤백 대상 이미지($CURRENT_IMAGE)가 서버에 없습니다. 배포를 중단합니다."
  echo "$CURRENT_IMAGE" > .deploy-rollback-image
else
  log "   현재 가동 중인 app 컨테이너가 없습니다(최초 배포로 간주)."
fi

# # IRREVERSIBLE 마이그레이션 유무
IRREVERSIBLE=$(grep -rl "# IRREVERSIBLE" apps/*/migrations/ 2>/dev/null | wc -l | tr -d ' ')
log "   되돌릴 수 없는 마이그레이션: ${IRREVERSIBLE}개"

# ★ 최근 24시간 내 run_backup 성공 기록 (없으면 경고 — devops R2 #2 ①)
if [ -n "$CURRENT_IMAGE" ]; then
  $COMPOSE run --rm -T scheduler python -c "
import django, os
django.setup()
from apps.core.jobs import has_recent_success
print('recent_backup_success=%s' % has_recent_success('run_backup'))
" 2>/dev/null | grep -q "recent_backup_success=True" \
    || log "⚠ 최근 24시간 내 백업 성공 기록이 없습니다. 1단계 라벨 백업 결과를 특히 확인하십시오."
fi

# 배포 차단 점검 (REQ-N-023 ① — [TBD] 가 남아 있으면 여기서 멈춘다)
if [ -n "$CURRENT_IMAGE" ]; then
  $COMPOSE run --rm -T app python manage.py check_release || fail "check_release 실패 — 미확정 콘텐츠가 남아 있습니다."
fi

if [ "$DRY_RUN" = "1" ]; then
  log "--dry-run: 0단계까지만 수행했습니다."
  exit 0
fi

DEPLOY_START=$(date +%s)

# ------------------------------------------------------------ 0.5) 스케줄러 정지
log "0.5) 스케줄러 정지 (락 경합 차단 — devops R2 #1)"
$COMPOSE stop scheduler || true

# ---------------------------------------------------------------- 1) 라벨 백업
log "1) 배포 직전 백업 (--label pre-deploy · required)"
if ! $COMPOSE run --rm -T scheduler python manage.py run_backup --label pre-deploy; then
  fail "배포 직전 백업이 실패했거나 건너뛰어졌습니다. 배포를 중단합니다."
fi

# ---------------------------------------------------------------- 2) 빌드
log "2) 이미지 빌드 (APP_VERSION=$APP_VERSION)"
APP_VERSION="$APP_VERSION" $COMPOSE build app || fail "빌드 실패"

# ---------------------------------------------------------- 3) 마이그레이션
log "3) 마이그레이션"
if ! APP_VERSION="$APP_VERSION" $COMPOSE run --rm -T app python manage.py migrate --noinput; then
  log "✗ 마이그레이션 실패 → 롤백"
  ./deploy/rollback.sh || true
  exit 1
fi

# ---------------------------------------------------------------- 4) 기동
log "4) 기동 (app · scheduler)"
APP_VERSION="$APP_VERSION" $COMPOSE up -d --no-deps app scheduler || {
  log "✗ 기동 실패 → 롤백"; ./deploy/rollback.sh || true; exit 1;
}

# ---------------------------------------------------------------- 5) 확인
log "5) 확인 — /healthz 는 **앱에 직접** 호출한다 (nginx 비경유, devops R2 #3)"
OK=0
i=0
while [ "$i" -lt "$HEALTH_TIMEOUT" ]; do
  if curl -fsS "$HEALTH_URL" 2>/dev/null | grep -q "^ok$"; then OK=1; break; fi
  i=$((i+3)); sleep 3
done
DOWNTIME=$(( $(date +%s) - DEPLOY_START ))
if [ "$OK" != "1" ]; then
  log "✗ /healthz 가 ${HEALTH_TIMEOUT}초 안에 200 을 주지 않았습니다 → 롤백"
  ./deploy/rollback.sh || true
  exit 1
fi
log "   /healthz 200 · 실측 다운타임(0.5단계~최초 200): ${DOWNTIME}초 (목표 60초 이내)"

# 주요 4경로 (프록시 경유. 스테이징은 BASIC_AUTH 를 준다)
BASE=${PUBLIC_BASE_URL:-}
if [ -n "$BASE" ]; then
  for path in / /instructors /location /privacy; do
    code=$(curl -s -o /dev/null -w '%{http_code}' ${BASIC_AUTH:+-u "$BASIC_AUTH"} "${BASE}${path}")
    log "   ${path} → ${code}"
    [ "$code" = "200" ] || log "⚠ ${path} 가 200 이 아닙니다."
  done
fi

# 스케줄러 헬스 (devops R2 #2 ③)
SCHED=$($COMPOSE ps -q scheduler | head -1)
[ -n "$SCHED" ] && log "   scheduler 상태: $(docker inspect -f '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' "$SCHED")"

# 로그 오류
ERRORS=$($COMPOSE logs --since "${DOWNTIME}s" app 2>/dev/null | grep -c " ERROR " || true)
log "   기동 후 ERROR 로그: ${ERRORS}건"

log "✓ 배포 완료 (APP_VERSION=$APP_VERSION · 다운타임 ${DOWNTIME}s · ERROR ${ERRORS}건)"
log "   기록할 값: 배포 시각 · APP_VERSION · 다운타임 · 롤백 대상 이미지($(cat .deploy-rollback-image 2>/dev/null || echo '-'))"
