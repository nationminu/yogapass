---
id: DEF-010
from: qa
to: developer
phase: P5
severity: trivial
status: closed
related_req: [REQ-N-024]
related_tc: [TC-116]
related_scr: []
found_cycle: 1
created: 2026-09-13
---

# DEF-010 운영 이미지의 정적 자산에 작업 중간 파일 `og-image.TEMP-source.svg` 가 포함돼 자산 목록 대조에서 초과 1건이 난다

## 환경
- 실행 방법: `docker run --rm --entrypoint sh yogapass-app:0.1.0-qa1 -c 'ls -la /app/static/img/'`
- 대상 버전: 개발 보고서 v0.3, qa가 직접 빌드한 운영 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `APP_VERSION=0.1.0-qa1 docker compose -f compose.yaml -f compose.prod.yaml build app`
2. `docker run --rm --entrypoint sh yogapass-app:0.1.0-qa1 -c 'ls /app/static/img/'`
3. 출력 목록을 `design/assets/SOURCES.md` 기재 항목과 대조한다.

## 기대 결과
근거: **REQ-N-024**(Must) 수용 기준 — *"Given **사용된 모든 이미지** When 라이선스 목록(`design/assets/SOURCES.md`)을 대조한다 Then **누락 0건**이고 모두 상업적 사용 가능 라이선스이며 지도 서비스 화면 캡처 0건"*

## 실제 결과
운영 이미지의 `/app/static/img/` 12개 중 아래 1건이 **산출물이 아니라 변환 작업용 중간 파일**이다.

```
og-image.TEMP-source.svg   2,998 B   2026-09-13 01:25
```

- 개발 보고서 v0.3 §7이 *"임시본 표시 4곳: 작업 사본 파일명 `og-image.TEMP-source.svg` …"* 로 설명한 파일이며, 화면·메타 태그에서 참조되지 않는다.
- `design/assets/SOURCES.md` 의 자산 표에는 이 파일명이 없다 → 대조 시 **"이미지에 있는데 목록에 없는 항목" 1건**.
- 부수 영향: 배포 산출물에 내부 작업 파일이 노출된다(정적 경로로 직접 접근 가능).

**함께 확인한 정상 항목(참고)**: 지도 서비스 화면 캡처 **0건**(지도 대체 영역은 CSS `repeating-linear-gradient`), 인물 스톡 사진 **0장**(`<img>` 태그 자체가 0건), 나머지 11개 자산은 `design/assets/SOURCES.md` 에 기재돼 있다.

## 증거
- `qa/evidence/cycle1/51_assets_sources.txt` (이미지 내 `/app/static/img/` 목록 + `SOURCES.md` 기재 항목)
- `qa/evidence/cycle1/33_prod_image_safety.txt` (운영 이미지 파일 구성)

## 비고
같은 성격으로 운영 이미지 루트에 `compose.yaml`·`compose.local.yaml`·`compose.prod.yaml`·`Dockerfile`·`requirements-dev.txt` 가 함께 들어 있다. 비밀 값은 없고(REQ-N-018 검색 0건) 보안 문제로 보지는 않으나, `.dockerignore` 정리 시 함께 검토하면 좋겠다.

---

## 조치 (developer 작성)

- **원인**: OG 임시본을 구울 때 쓴 **작업 사본을 `static/img/` 안에 두었다.** `static/` 은 이미지에 복사되고 `collectstatic` 이 배포 산출물로 굽는 경로라 작업 파일이 그대로 따라갔다. 작업 파일 위치 규칙과 `.dockerignore` 규칙이 없었다.
- **조치 내용**
  1. 작업 사본을 **`developer/site/assets-work/og-image.TEMP-source.svg` 로 옮겼다**(삭제하지 않았다 — 정식본 수령 전까지 임시본 재생성에 필요하고, 파일명·머리 주석이 "임시본" 표시 역할을 한다).
  2. `.dockerignore` 에 **`assets-work/` · `*.TEMP-*`** 추가(이중 차단). 함께 **`Dockerfile` · `.dockerignore` · `compose*.yaml` · `.deploy-rollback-image`** 도 제외했다(qa 비고 — 컨테이너 안에서 쓰지 않는 파일들). ⚠ `requirements-dev.txt` 는 **제외하지 않았다** — dev 스테이지가 `COPY` 하므로 빌드가 깨진다.
  3. `static/img/SOURCES.md` 갱신 — 표에서 작업 사본 행을 빼고, **작업 사본을 `static/` 아래에 두지 않는다는 이유**와 새 생성 명령(`assets-work` → `/work`, `static/img` → `/out`), 정식본 교체 절차의 경로를 고쳤다.
  4. **회귀 테스트 추가** — `tests/test_seo_markup.py::StaticAssetHygieneTests`: `static/` 아래 `*TEMP*` 파일 **0건**, `.dockerignore` 에 두 규칙이 있는지.
- **확인 결과**(운영 이미지 재빌드 `yogapass-app:0.1.0-fix1`)
  - `/app/static/img/` **11개** — `SOURCES.md` · `apple-touch-icon.png/.svg` · `favicon.ico/.svg` · `icon-192/512.png` · `logo-horizontal.svg` · `logo-mark.svg` · `og-image.png` · `og-image.svg` (**TEMP 파일 없음**)
  - `find /app -name "*TEMP*"` → **0건**
  - `/app` 루트에 `Dockerfile`·`compose*.yaml` **없음**(종전 5개 → `requirements-dev.txt` 만 남음), `qa/`·`tests/`·`.env` 없음(종전 유지)
  - `og:image` 경로 응답 **200**(해시 파일명 `og-image.a3f7089eddd0.png`), 메타 5줄 정상
- **수정 파일**: `developer/site/.dockerignore`, `developer/site/static/img/SOURCES.md`, 이동 `static/img/og-image.TEMP-source.svg → assets-work/og-image.TEMP-source.svg`, 신규 `tests/test_seo_markup.py`
- **영향 범위 (회귀 테스트 필요 영역)**: 운영 이미지 구성·정적 자산 목록·OG 이미지 서빙. 배포 스크립트는 호스트에서 compose 파일을 읽으므로 이미지에서 빠져도 영향 없음(로컬 `--dry-run` 으로 확인).
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| **2** | **closed** | 2026-09-13 | 운영 이미지 `yogapass-app:0.1.0-qa2` 의 `/app/static/img/` **11개**(작업 중간 파일 없음), `find /app -iname "*TEMP*"` 실파일 **0건**(매치 2건은 `templates`·`templatetags` 디렉토리). `assets-work`·`qa`·`tests`·`.env`·`Dockerfile`·`compose*` **전건 0건**. 자산 10종 전건 `SOURCES.md` 기재. 증거 `cycle2/16_prod_image_assets.txt` |
