#!/bin/sh
# ============================================================================
# 롤백 스크립트 — 기술 설계 §12.4
#
# 실행 순서는 배포와 같다:
#   ① scheduler 정지 → ② 마이그레이션 되돌리기(필요 시) 또는 DB 복구 → ③ 이전 이미지로 기동 → ④ /healthz 확인
#
# 사용법:
#   ./deploy/rollback.sh                      # deploy.sh 가 남긴 .deploy-rollback-image 사용
#   ROLLBACK_VERSION=0.1.0 ./deploy/rollback.sh
#   ./deploy/rollback.sh --restore <백업파일>  # 되돌릴 수 없는 마이그레이션이 있을 때
#
# 전제 (§12.1): **이전 이미지가 서버에 남아 있어야 한다.**
#   · 모든 앱 이미지에 LABEL org.yogapass.keep=release 가 붙어 있다.
#   · 정리는 반드시 `docker image prune --filter "label!=org.yogapass.keep=release"` 로만 한다.
#     `docker image prune -a` 는 **금지**다 — 롤백 경로가 사라진다.
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
HEALTH_TIMEOUT=${HEALTH_TIMEOUT:-120}
RESTORE_FILE=""

[ "${1:-}" = "--restore" ] && { RESTORE_FILE=${2:?복구할 백업 파일 경로를 주십시오}; }

log()  { echo "[rollback] $*"; }
fail() { echo "[rollback] ✗ $*" >&2; exit 1; }

# 되돌릴 대상 판정
TARGET_IMAGE=${ROLLBACK_IMAGE:-}
if [ -z "$TARGET_IMAGE" ] && [ -n "${ROLLBACK_VERSION:-}" ]; then
  TARGET_IMAGE="yogapass-app:${ROLLBACK_VERSION}"
fi
if [ -z "$TARGET_IMAGE" ] && [ -f .deploy-rollback-image ]; then
  TARGET_IMAGE=$(cat .deploy-rollback-image)
fi
[ -n "$TARGET_IMAGE" ] || fail "되돌릴 이미지를 정할 수 없습니다. ROLLBACK_VERSION 또는 ROLLBACK_IMAGE 를 주십시오."
docker image inspect "$TARGET_IMAGE" >/dev/null 2>&1 \
  || fail "이미지 $TARGET_IMAGE 가 서버에 없습니다. (docker image prune -a 로 지워졌을 수 있습니다)"
ROLLBACK_VERSION=${ROLLBACK_VERSION:-$(echo "$TARGET_IMAGE" | sed 's/.*://')}

log "되돌릴 이미지: $TARGET_IMAGE"

# ① scheduler 정지
log "① scheduler 정지"
$COMPOSE stop scheduler || true

# ② DB 복구 또는 마이그레이션 되돌리기
if [ -n "$RESTORE_FILE" ]; then
  log "② DB 복구: $RESTORE_FILE"
  ./deploy/restore.sh "$RESTORE_FILE" || fail "복구 실패 — 수동 조치가 필요합니다."
else
  log "② 마이그레이션 되돌리기는 수행하지 않습니다(필요하면 migrate <app> <번호> 를 먼저 실행하십시오)."
fi

# ③ 이전 이미지로 기동
log "③ 이전 이미지로 기동 (APP_VERSION=$ROLLBACK_VERSION)"
APP_VERSION="$ROLLBACK_VERSION" $COMPOSE up -d --no-deps app scheduler || fail "기동 실패"

# ④ 확인
log "④ /healthz 확인 (앱에 직접 호출)"
i=0
while [ "$i" -lt "$HEALTH_TIMEOUT" ]; do
  if curl -fsS "$HEALTH_URL" 2>/dev/null | grep -q "^ok$"; then
    log "✓ 롤백 완료 (APP_VERSION=$ROLLBACK_VERSION)"
    exit 0
  fi
  i=$((i+3)); sleep 3
done
fail "롤백 후에도 /healthz 가 응답하지 않습니다. 즉시 수동 조치가 필요합니다."
