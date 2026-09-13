#!/bin/sh
# ============================================================================
# 복구 스크립트 — 기술 설계 §12.5.3
#
#   ⓐ 대상(프로젝트·DB·파일)을 출력하고 **명시적 확인 입력(yes)** 을 받는다
#   ⓑ 대상이 운영이면 **추가 플래그** --i-know-this-is-production 를 요구한다
#   ⓒ 복구 전에 현재 DB 를 **자동 덤프**한다 (run_backup --label pre-restore).
#      이 덤프는 라벨 실행이라 락 충돌 시 실패로 끝나며, **실패하면 복구를 진행하지 않는다**
#      (devops R2 #1 ②)
#
# 실제 사용 시점은 사고 직후, 운영자가 가장 긴장한 상태다. 그래서 3중으로 막는다.
#
# 사용법:
#   ./deploy/restore.sh /backups/yogapass-staging-20261028-0300.dump
#   ./deploy/restore.sh <파일> --i-know-this-is-production
#   ./deploy/restore.sh <파일> --dry-run      # 무엇을 할지만 출력
# ============================================================================
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR/.."

BACKUP_FILE=${1:?복구할 백업 파일 경로를 주십시오}
shift || true
PROD_FLAG=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --i-know-this-is-production) PROD_FLAG=1 ;;
    --dry-run) DRY_RUN=1 ;;
  esac
done

ENV_FILE=${ENV_FILE:-.env}
COMPOSE_PROJECT=${COMPOSE_PROJECT:-yogapass}
# 기본은 운영·스테이징 구성이다. 로컬에서 절차를 그대로 재현할 때만 파일 조합을 바꾼다:
#   COMPOSE_FILES="-f compose.yaml -f compose.local.yaml" ./deploy/restore.sh …
COMPOSE_FILES=${COMPOSE_FILES:--f compose.yaml -f compose.prod.yaml}
COMPOSE="docker compose $COMPOSE_FILES -p $COMPOSE_PROJECT"

log()  { echo "[restore] $*"; }
fail() { echo "[restore] ✗ $*" >&2; exit 1; }

# .env 에서 DB 정보를 읽는다(값은 화면에만 보이고 어디에도 기록하지 않는다)
# ⚠ 인라인 주석(`KEY=value   # 설명`)과 따옴표·공백을 반드시 떼어낸다.
#    떼어내지 않으면 DJANGO_ENV 값이 "production   # …" 가 되어 **운영 가드가 통과해 버린다.**
[ -f "$ENV_FILE" ] || fail "$ENV_FILE 이 없습니다."
env_value() {
  grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//' | tr -d '"'"'"' '
}
DJANGO_ENV=$(env_value DJANGO_ENV)
DJANGO_ENV=${DJANGO_ENV:-local}
POSTGRES_DB=$(env_value POSTGRES_DB)
POSTGRES_USER=$(env_value POSTGRES_USER)

# ---------------------------------------------------------------- ⓐ 대상 출력
cat <<INFO
------------------------------------------------------------
 복구 대상 확인
   프로젝트(compose -p) : $COMPOSE_PROJECT
   환경(DJANGO_ENV)     : $DJANGO_ENV
   데이터베이스          : $POSTGRES_DB (user=$POSTGRES_USER)
   백업 파일            : $BACKUP_FILE
 ⚠ 이 작업은 **현재 데이터베이스의 내용을 백업 시점으로 되돌린다.**
------------------------------------------------------------
INFO

if [ "$DRY_RUN" = "1" ]; then
  log "--dry-run: 여기까지만 수행합니다."
  exit 0
fi

# ---------------------------------------------------------------- ⓑ 운영 가드
if [ "$DJANGO_ENV" = "production" ] && [ "$PROD_FLAG" != "1" ]; then
  fail "운영 환경입니다. 정말 복구하려면 --i-know-this-is-production 를 함께 주십시오."
fi

# ---------------------------------------------------------------- ⓐ 확인 입력
printf "계속하려면 정확히 'yes' 를 입력하십시오: "
read -r answer
[ "$answer" = "yes" ] || fail "취소했습니다."

# ---------------------------------------------------- ⓒ 복구 전 현재 DB 자동 덤프
log "ⓒ 복구 전 현재 DB 를 덤프합니다 (--label pre-restore · required)"
if ! $COMPOSE run --rm -T scheduler python manage.py run_backup --label pre-restore; then
  fail "복구 전 덤프가 실패했거나 건너뛰어졌습니다. **복구를 진행하지 않습니다.**"
fi

# ---------------------------------------------------------------- 복구
log "스케줄러·앱 정지"
$COMPOSE stop scheduler app || true

log "pg_restore 실행 (--clean --if-exists)"
$COMPOSE run --rm -T scheduler sh -c "
  set -e
  export PGPASSWORD=\"\$POSTGRES_PASSWORD\"
  pg_restore --clean --if-exists --no-owner --no-privileges \
    -h \"\$POSTGRES_HOST\" -p \"\$POSTGRES_PORT\" -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\" \
    '$BACKUP_FILE'
" || fail "pg_restore 실패 — pre-restore 덤프로 되돌릴 수 있습니다."

log "스키마 확인 (migrate --check)"
$COMPOSE run --rm -T app python manage.py migrate --check \
  || log "⚠ 마이그레이션 상태가 코드와 다릅니다. 필요한 경우 migrate 를 실행하십시오."

log "앱·스케줄러 기동"
$COMPOSE up -d app scheduler

APP_PORT=${APP_PORT:-8000}
HEALTH_URL=${HEALTH_URL:-http://127.0.0.1:${APP_PORT}/healthz}
i=0
while [ "$i" -lt 120 ]; do
  if curl -fsS "$HEALTH_URL" 2>/dev/null | grep -q "^ok$"; then
    log "✓ 복구 완료 · /healthz 200"
    log "   기록할 값: 복구 파일 · 소요 시간 · pre-restore 덤프 파일명 (P8 운영 가이드에 싣는다)"
    exit 0
  fi
  i=$((i+3)); sleep 3
done
fail "복구 후 /healthz 가 응답하지 않습니다."
