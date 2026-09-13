---
id: DEF-007
from: qa
to: developer
phase: P5
severity: minor
status: resolved
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

- **원인**: qa 의 코드 분석과 같다. 가드가 **"값이 있는가 + 이미지가 존재하는가"** 만 보고 **"그 값이 릴리스 태그인가"** 를 보지 않았다. 태그 없는 이름은 docker 가 `:latest` 로 해석해 존재 확인을 통과하고, `sed 's/.*://'` 가 콜론 없는 문자열을 그대로 돌려주어 `APP_VERSION=yogapass-app` 이라는 의미 없는 값이 만들어졌다. 개발 보고서 §4.1 #44 의 기재("인자 없이 → 거부")는 **`.deploy-rollback-image` 가 없던 상태에서 본 결과**를 일반화한 것이라 실제 동작과 달랐다 — 잘못된 기재였다.
- **조치 내용** (`deploy/rollback.sh`)
  1. **태그 가드 신설** — 대상 이미지에서 태그를 떼어(`image_tag()`; 레지스트리 포트 콜론과 구분) ⓐ 태그 없음 ⓑ `latest` 면 **거부하고 아무것도 실행하지 않는다.** 대상의 **출처**(`ROLLBACK_IMAGE` / `ROLLBACK_VERSION` / `.deploy-rollback-image`)를 로그와 오류 메시지에 찍는다. `.deploy-rollback-image` 는 공백·개행을 제거하고 읽는다(빈 파일 = 대상 없음).
  2. **확인 입력 추가** — `ROLLBACK_ASSUME_YES=1`(또는 `--yes`)이 없으면 대화형에서 `yes` 를 받고, **비대화형이면 거부**한다. `deploy.sh` 의 자동 롤백 3곳은 `ROLLBACK_ASSUME_YES=1` 로 호출한다(응급 경로는 그대로 동작).
  3. **`--dry-run` 추가** — 대상 판정·가드까지만 수행하고 종료(변경 0).
  4. **`deploy.sh` 0단계 수정** — 현재 이미지에 릴리스 태그가 없으면 **`.deploy-rollback-image` 에 기록하지 않고**(있던 파일은 지운다) 경고만 남긴다. **`--dry-run` 은 이 파일을 만들지도 지우지도 않는다**(부수 효과 제거 — qa 부가 지적).
  5. 기술 설계 §12.4 에 대상 가드·확인 규칙을 표로 추가(v0.5).
- **실행 확인** (`developer/site`, 실제 실행 · 컨테이너 상태 변화 없음)

| 상황 | 결과 |
|---|---|
| `.deploy-rollback-image` = `yogapass-app`(태그 없음) → `sh deploy/rollback.sh` | `✗ … 에 태그가 없습니다. 릴리스 태그를 붙인 이미지(yogapass-app:<버전>)만 …` **종료 1** |
| 빈 파일 → 무인자 | `✗ 되돌릴 이미지를 정할 수 없습니다.` **종료 1** |
| `yogapass-app:latest` → 무인자 | `✗ 'latest' 태그로는 되돌리지 않습니다` **종료 1** |
| 파일·인자 모두 없음 | `✗ 되돌릴 이미지를 정할 수 없습니다.` **종료 1** |
| `ROLLBACK_VERSION=9.9.9` | `✗ 이미지 yogapass-app:9.9.9 가 서버에 없습니다` **종료 1** |
| 정상 태그(`yogapass-app:0.1.0-fix1`) + `--dry-run` | `되돌릴 이미지: … (출처: .deploy-rollback-image · APP_VERSION=0.1.0-fix1)` → `변경한 것은 없습니다` **종료 0** |
| 정상 태그 · 비대화형 · 확인 없음 | `✗ 대화형 터미널이 아닙니다. 확인 없이 롤백하지 않습니다.` **종료 1** |
| `deploy.sh --dry-run`(로컬 조합, 현재 이미지 `yogapass-app` 무태그) | `⚠ … 릴리스 태그가 없어 롤백 대상으로 기록하지 않습니다` → 종료 후 **`.deploy-rollback-image` 없음** |
| `sh -n deploy/{deploy,rollback,restore}.sh` | 3건 통과 |

  실행 전후 `docker ps` 동일(스택 재생성·이미지 교체 **0건**).

- **수정 파일**: `developer/site/deploy/rollback.sh`, `developer/site/deploy/deploy.sh`, `developer/04_tech-design.md` §12.4
- **영향 범위 (회귀 테스트 필요 영역)**: 배포·롤백 스크립트 전 경로(P7 실제 배포 전 필수 재확인). 자동 롤백이 확인 입력 때문에 막히지 않는지(`ROLLBACK_ASSUME_YES=1` 경유)를 devops 배포 리허설에서 함께 본다.
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | 태그 없는 `.deploy-rollback-image`·빈 파일·정상 태그 3경우 재수행 + `deploy.sh --dry-run` 부수 효과 확인 |
