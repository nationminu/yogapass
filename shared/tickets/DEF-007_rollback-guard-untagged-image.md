---
id: DEF-007
from: qa
to: developer
phase: P5
severity: minor
status: open
related_req: [REQ-N-033]
related_tc: [TC-125]
related_scr: []
found_cycle: 1
created: 2026-09-13
---

# DEF-007 `rollback.sh`를 인자 없이 실행하면 태그 없는 이미지 이름을 APP_VERSION으로 오판정해 롤백을 실행한다

## 환경
- 실행 방법: `developer/site/` 에서 `sh deploy/rollback.sh` (인자·환경 변수 없음)
- 선행 상태: 직전에 `APP_VERSION=0.1.0-qa COMPOSE_FILES="-f compose.yaml -f compose.local.yaml" sh deploy/deploy.sh --dry-run` 을 실행해 `.deploy-rollback-image` 파일이 생성된 상태(내용 = `yogapass-app`, **태그 없음**)
- 대상 버전: 개발 보고서 v0.3

## 재현 절차
1. `APP_VERSION=0.1.0-qa COMPOSE_FILES="-f compose.yaml -f compose.local.yaml" sh deploy/deploy.sh --dry-run`
   → 0단계 점검 후 `check_release` 실패로 중단(의도된 동작). 이때 `.deploy-rollback-image` 가 남는다.
2. `cat .deploy-rollback-image` → `yogapass-app` (태그 없음)
3. `sh deploy/rollback.sh` (인자 없이)

## 기대 결과
- 개발 보고서 v0.3 §4.1 #44는 *"`ROLLBACK_VERSION=9.9.9 sh deploy/rollback.sh` / 인자 없이 → `✗ 이미지 … 가 서버에 없습니다` / `✗ 되돌릴 이미지를 정할 수 없습니다`"* 로 **양쪽 모두 거부**된다고 기록한다.
- **REQ-N-033**(Must) 수용 기준 — *"When 이전 태그로 롤백한다 Then 이전 버전이 정상 동작한다"*. 되돌릴 **릴리스 태그**를 특정할 수 없으면 실행하지 않아야 한다.

## 실제 결과
롤백이 **거부되지 않고 그대로 실행**됐다.

```
$ sh deploy/rollback.sh
 Container yogapass-app-1  Started
[rollback] ④ /healthz 확인 (앱에 직접 호출)
[rollback] ✓ 롤백 완료 (APP_VERSION=yogapass-app)
```

실행 후 스택 상태:
```
NAME                   IMAGE                       SERVICE
yogapass-app-1         yogapass-app:yogapass-app   app
yogapass-scheduler-1   yogapass-app:yogapass-app   scheduler
```
→ 로컬 개발 스택이 **`compose.prod.yaml` 기본 조합 + `APP_VERSION=yogapass-app`** 로 재생성됐다(소스 바인드 마운트 소실). qa가 `docker compose … up -d --force-recreate app scheduler` 로 원복했다.

### 원인 (코드 기준 · `deploy/rollback.sh` 39~52행)
```sh
if [ -z "$TARGET_IMAGE" ] && [ -f .deploy-rollback-image ]; then
  TARGET_IMAGE=$(cat .deploy-rollback-image)
fi
[ -n "$TARGET_IMAGE" ] || fail "되돌릴 이미지를 정할 수 없습니다. …"
docker image inspect "$TARGET_IMAGE" >/dev/null 2>&1 || fail "이미지 $TARGET_IMAGE 가 …"
ROLLBACK_VERSION=${ROLLBACK_VERSION:-$(echo "$TARGET_IMAGE" | sed 's/.*://')}
```
- `.deploy-rollback-image` 에 **태그 없는 이름**(`yogapass-app`)이 들어가면 `docker image inspect` 가 `:latest` 로 해석돼 **통과**한다.
- `sed 's/.*://'` 는 콜론이 없으면 문자열 전체를 그대로 돌려주므로 `ROLLBACK_VERSION=yogapass-app` 이라는 **의미 없는 버전**이 만들어지고, 그대로 `APP_VERSION` 으로 기동된다.
- 운영에서는 `compose.prod.yaml` 이 `image: yogapass-app:${APP_VERSION}` 를 쓰므로 `yogapass-app:yogapass-app` 를 찾다 **기동 실패**로 끝난다 — 즉 가드가 "막았어야 할 것"을 통과시키고 **더 늦은 단계에서 실패**한다.

### 부가 지적
- `rollback.sh` 에는 `--dry-run` 이나 확인 입력이 없다(`deploy.sh` 는 `--dry-run`, `restore.sh` 는 `yes` 확인이 있다). 인자 없이 실행하면 **확인 없이 스케줄러 정지 → 재기동**까지 진행된다.
- `deploy.sh --dry-run` 이 `.deploy-rollback-image` 를 남기는 것도 확인했다(dry-run이 부수 효과로 파일을 만든다). qa는 검증 후 이 파일을 삭제해 소스 트리를 원상 복구했다.

## 증거
- `qa/evidence/cycle1/29_deploy.txt` (`deploy.sh --dry-run` 0단계 점검 → `check_release` 실패로 배포 차단 = 정상 / 그 아래 `rollback.sh` 무인자 실행 로그)
- `qa/evidence/cycle1/30_rollback_defect.txt` (실행 후 이미지 태그·서비스 목록 + 로컬 스택 원복)

## 비고
- `ROLLBACK_VERSION=9.9.9` 인 경우의 거부(`✗ 이미지 yogapass-app:9.9.9 가 서버에 없습니다`)와 `sh -n` 문법 검사 3건은 **정상 동작**을 확인했다. 실제 서버 배포·롤백은 P7 이월(테스트 계획 §7 L-5).

---

## 조치 (developer 작성)
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | 태그 없는 `.deploy-rollback-image`·빈 파일·정상 태그 3경우 재수행 + `deploy.sh --dry-run` 부수 효과 확인 |
