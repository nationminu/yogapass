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
#   ./deploy/rollback.sh --dry-run            # 대상 판정·가드까지만 수행하고 아무것도 바꾸지 않는다
#   ROLLBACK_ASSUME_YES=1 ./deploy/rollback.sh   # 확인 입력 생략(deploy.sh 자동 롤백이 쓴다)
#
# 대상 이미지 가드 (DEF-007):
#   · **릴리스 태그가 붙은 이미지만** 되돌린다. `yogapass-app` 처럼 태그 없는 이름,
#     `:latest`, 태그에 `/` 가 섞인 값은 거부한다.
#     (태그가 없으면 docker 가 `:latest` 로 해석해 가드를 그냥 통과하고,
#      APP_VERSION 에 이미지 이름이 그대로 들어가 엉뚱한 이미지로 기동된다.)
#   · 대상을 정할 수 없으면 **아무것도 실행하지 않고 종료**한다.
#   · 확인 입력 없이 스케줄러를 정지·재기동하지 않는다(대화형이 아니면 ROLLBACK_ASSUME_YES 필요).
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
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ROLLBACK_ASSUME_YES=1 ;;
  esac
done
[ "${1:-}" = "--restore" ] && { RESTORE_FILE=${2:?복구할 백업 파일 경로를 주십시오}; }

log()  { echo "[rollback] $*"; }
fail() { echo "[rollback] ✗ $*" >&2; exit 1; }

# ---------------------------------------------------------------- 대상 판정 + 가드
# 이미지 참조에서 태그만 떼어낸다. 태그가 없으면 빈 문자열을 돌려준다.
#   yogapass-app:0.1.0        → 0.1.0
#   yogapass-app              → (없음)
#   registry.example:5000/app → (없음, 포트 콜론은 태그가 아니다)
image_tag() {
  case "$1" in
    *:*) tag=${1##*:}; case "$tag" in */*) echo "" ;; *) echo "$tag" ;; esac ;;
    *)   echo "" ;;
  esac
}

TARGET_IMAGE=${ROLLBACK_IMAGE:-}
TARGET_SOURCE="ROLLBACK_IMAGE"
if [ -z "$TARGET_IMAGE" ] && [ -n "${ROLLBACK_VERSION:-}" ]; then
  TARGET_IMAGE="yogapass-app:${ROLLBACK_VERSION}"
  TARGET_SOURCE="ROLLBACK_VERSION"
fi
if [ -z "$TARGET_IMAGE" ] && [ -f .deploy-rollback-image ]; then
  TARGET_IMAGE=$(tr -d ' \t\r\n' < .deploy-rollback-image)
  TARGET_SOURCE=".deploy-rollback-image"
fi
[ -n "$TARGET_IMAGE" ] || fail "되돌릴 이미지를 정할 수 없습니다. ROLLBACK_VERSION 또는 ROLLBACK_IMAGE 를 주십시오."

# ★ 태그 가드 — 릴리스 태그가 붙은 이미지만 되돌린다 (DEF-007)
TARGET_TAG=$(image_tag "$TARGET_IMAGE")
[ -n "$TARGET_TAG" ] || fail "되돌릴 이미지 '$TARGET_IMAGE' ($TARGET_SOURCE) 에 태그가 없습니다. 릴리스 태그를 붙인 이미지(yogapass-app:<버전>)만 되돌릴 수 있습니다. ROLLBACK_VERSION 을 주십시오."
[ "$TARGET_TAG" != "latest" ] || fail "'latest' 태그로는 되돌리지 않습니다($TARGET_SOURCE). 되돌릴 릴리스 버전을 ROLLBACK_VERSION 으로 지정하십시오."

docker image inspect "$TARGET_IMAGE" >/dev/null 2>&1 \
  || fail "이미지 $TARGET_IMAGE 가 서버에 없습니다. (docker image prune -a 로 지워졌을 수 있습니다)"
ROLLBACK_VERSION=${ROLLBACK_VERSION:-$TARGET_TAG}

log "되돌릴 이미지: $TARGET_IMAGE (출처: $TARGET_SOURCE · APP_VERSION=$ROLLBACK_VERSION)"

if [ "$DRY_RUN" = "1" ]; then
  log "--dry-run: 대상 판정·가드까지만 수행했습니다. 변경한 것은 없습니다."
  exit 0
fi

# ★ 확인 — 인자 없이 실행해도 확인 없이 스케줄러를 정지·재기동하지 않는다 (DEF-007 부가 지적)
if [ "${ROLLBACK_ASSUME_YES:-0}" != "1" ]; then
  if [ -t 0 ]; then
    printf "[rollback] %s 로 롤백합니다. 계속하려면 yes 를 입력하십시오: " "$TARGET_IMAGE"
    read -r answer
    [ "$answer" = "yes" ] || fail "사용자가 취소했습니다."
  else
    fail "대화형 터미널이 아닙니다. 확인 없이 롤백하지 않습니다. ROLLBACK_ASSUME_YES=1 을 주거나 --yes 를 붙이십시오."
  fi
fi

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
