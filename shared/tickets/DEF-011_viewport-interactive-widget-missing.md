---
id: DEF-011
from: qa
to: developer
phase: P5
severity: major
status: closed
related_req: [REQ-F-003, REQ-N-002]
related_tc: [TC-009, TC-091]
related_scr: [SCR-001, SCR-002, SCR-003, SCR-006, SCR-008]
found_cycle: 2
created: 2026-09-13
---

# DEF-011 viewport 메타에 `interactive-widget=resizes-content` 가 전 화면에서 빠져 있다 (G-9 3단 구현 중 1단 미구현)

## 환경
- 실행 방법 / URL: 운영 미리보기 `yogapass-app:0.1.0-qa2` · `http://localhost:8001/` · `/instructors` · `/location` · `/privacy` · `/nope`
- 브라우저 · 뷰포트: Chrome(headless, puppeteer-core) 360×780 · isMobile/hasTouch
- 대상 버전: 개발 보고서 **v0.4** (커밋 `bcda9e0`, DEF-001~010 수정 반영본)

## 재현 절차
1. 운영 미리보기 기동 후 5화면을 요청한다.
2. 응답 HTML 과 **런타임 DOM** 양쪽에서 `meta[name="viewport"]` 의 `content` 를 읽는다.
   - `curl -s http://localhost:8001/ | grep -oE '<meta name="viewport" content="[^"]*"'`
   - `node qa/tools/probe10.js` (렌더 후 `document.querySelector('meta[name=viewport]').content`)

## 기대 결과
(근거: `planning/02_requirements.md` **REQ-F-003 ⑤-1**(Must · "정적 확인(P5 로컬, **필수**)"), §3.0 **G-9**, `planning/02_information-architecture.md` §G-9, `planning/02_storyboard.md` §공통 규칙, `design/03_page-design.md` §2.5)

- **⑤-1**: *"빌드 결과물의 **공개·회원 영역 전 화면 `<head>` 에 `interactive-widget=resizes-content` 가 포함**(누락 0건) + WebKit 폴백 스크립트와 `scroll-padding-bottom` 선언이 번들에 존재"*
- 요구사항 §3.0 G-9 는 구현 수단을 **3단**으로 못박고 있다:
  ① **기본**: viewport 메타 `interactive-widget=resizes-content` — *"**지정하지 않으면 Android 기본값에서도 고정 바가 가려진다**"*
  ② **WebKit 폴백(필수)**: `visualViewport` 보정 (iOS 전 브라우저)
  ③ **포커스 필드 가림 방지**: `scroll-padding-bottom`

## 실제 결과
**① 만 구현되지 않았다. 5화면 전건 누락(누락 0건 기준 미충족).**

```
  /              viewport="width=device-width, initial-scale=1"  interactive-widget=**없음**
  /instructors   viewport="width=device-width, initial-scale=1"  interactive-widget=**없음**
  /location      viewport="width=device-width, initial-scale=1"  interactive-widget=**없음**
  /privacy       viewport="width=device-width, initial-scale=1"  interactive-widget=**없음**
  /nope          viewport="width=device-width, initial-scale=1"  interactive-widget=**없음**
```

- 원본: `developer/site/templates/base.html` 8행 `<meta name="viewport" content="width=device-width, initial-scale=1">` — **1차 구현 시점(`c6fa91f`)부터 같다.** 이번 결함 수정으로 생긴 회귀가 아니라 **1차 사이클이 놓친 잔존 결함**이다(1차 TC-009 는 폴백 스크립트·`--fixed-bar-h` 만 확인하고 메타 토큰을 대조하지 않았다).
- ②③ 은 충족한다 — `static/js/viewport.js` 에 `visualViewport` 폴백 존재(런타임 `data-vk-fallback` 는 WebKit 에서만 부착, Chrome 측정이라 `null` 이 정상), `tokens.css` 194행 `html { scroll-padding-bottom: var(--scroll-pad-bottom); }` 존재, 런타임 계산값 77px(바 있는 화면) / 81px(바 없는 화면).
- **Chromium 경로에는 대체 수단이 없다.** `viewport.js` 의 폴백은 `if (!isWebKit) return;` 으로 Chrome·Edge 를 명시적으로 제외한다. 즉 Android Chrome 에서 키보드가 뜨면 ①도 ②도 동작하지 않는다.

## 증거
- `qa/evidence/cycle2/39_interactive_widget.txt` (런타임 DOM 5화면)
- `qa/evidence/cycle2/38_viewport_js.txt` (응답 HTML 5화면 · `viewport.js` 번들 발췌 · `scroll-padding-bottom` 선언)
- `qa/evidence/cycle2/pages/*.html` (검사 대상 원문)

## 심각도 근거 (Major)
- **Must REQ(REQ-F-003)의 명시적 "필수" 수용 기준을 색인·공개 전 화면(5/5)이 미충족**한다. 범위가 전면적이다.
- 요구사항 본문이 *"지정하지 않으면 Android 기본값에서도 고정 바가 가려진다"* 로 **결과까지 단정**하고 있고, REQ-N-002 는 *"미지원 브라우저에서 키보드 활성 중 고정 바가 가려지면 '허용'이 아니라 **결함**"* 이라고 못박는다.
- 영향 경로가 사이트의 **유일한 전환 동선**(`/location#contact` 문의 폼)이다.

### 완화 정황 (PM 판단에 필요한 사실)
- **지금 이 순간의 사용자 영향은 관측되지 않는다.** 1차의 유일한 폼 화면 `/location` 은 자기 참조 + 대표 전화 `[TBD]` 이라 고정 바를 **렌더하지 않는다**(S3 · `data-fixed-bar="off"`). 가릴 바가 없으므로 현재 빌드에서 겹침이 발생하지 않는다.
- **대표 전화(T-E)가 확정되는 순간 S2 로 바뀌어 `/location` 에 고정 바가 렌더되고, 그때부터 실제 결함이 된다.** 전화 확정은 오픈 전제(REQ-N-023 ②)이므로 **오픈 전에 반드시 해소해야 한다.**
- 수정 비용은 **속성 1개**다 (`base.html` 의 viewport `content` 에 `, interactive-widget=resizes-content` 추가).

## 요청 사항
1. `templates/base.html` 의 viewport 메타에 `interactive-widget=resizes-content` 를 추가한다.
2. **재발 방지 테스트**를 `tests/test_pages.py` 또는 `tests/test_seo_markup.py` 에 1건 추가한다(전 화면 `<head>` 에 토큰 존재, 누락 0건).
3. 재검증은 **정적 확인(⑤-1)** 만으로 닫을 수 있다. ⑤-2(실기기 동작)는 기기 미확보로 이번에도 **"미검증"** 으로 남는다(REQ-F-003 ⑤-4).

---

## 조치 (developer 작성)
- **원인**
  - **직접 원인**: `developer/site/templates/base.html` 8행의 viewport `content` 에 `interactive-widget=resizes-content` 가 없었다. 전 화면이 이 파일을 상속하므로 **5화면 전건 누락**이다. 티켓 판정대로 **회귀가 아니라 1차 구현(`c6fa91f`)부터의 잔존 결함**이다.
  - **근본 원인 — 설계 공백**: 기술 설계서가 G-9 3단 중 **①만 어느 절에도 적지 않았다.** ②는 §10.5(WebKit 검증 수단), ③은 §9.1 토큰 계산식 근처에 있었지만 ①(메타 문자열)은 승인 **디자인 문서(`design/03_page-design.md` §2.5)에만** 있었다. 구현이 설계서를 보고 작성되므로 ①만 빠졌고, 1차 TC-009 도 폴백 스크립트와 `--fixed-bar-h` 만 봐서 함께 놓쳤다.
  - **왜 지금 사용자 영향이 없었나**: 티켓의 완화 정황과 같다 — 유일한 폼 화면 `/location` 이 S3(자기 참조 + 대표 전화 `[TBD]`)라 고정 바를 렌더하지 않는다. **대표 전화(T-E) 확정 즉시 S2 가 되어 실제 결함이 된다.**
- **조치 내용**
  1. viewport 메타를 정본 문자열 **`width=device-width, initial-scale=1, interactive-widget=resizes-content`** 로 교체했다(요청 사항 1). base 를 상속하지 않는 유일한 화면인 점검 안내 템플릿도 같은 문자열로 맞췄다.
  2. **재발 방지 테스트 5건**을 `tests/test_seo_markup.py` 에 추가했다(요청 사항 2) — `ViewportMetaTests`: ⓐ 전 화면 토큰 존재(**누락 0건 · 빠진 화면을 모아서 보고**) ⓑ 문자열 정본 일치 ⓒ 화면당 메타 1개(뒤엣것이 이기는 사고 차단) ⓓ viewport 메타를 직접 선언하는 템플릿 전부 동일(독립 화면이 늘어나도 자동 대상) ⓔ ②`visualViewport`·`data-vk-fallback` 과 ③`scroll-padding-bottom` 의 번들 잔존.
     **음성 확인**: 토큰만 뺀 상태에서 3건이 FAIL 하고 `['/', '/instructors', '/location', '/privacy', '/nope']` 를 보고한다 → 테스트가 이 결함을 실제로 잡는다.
  3. **근본 원인(설계 공백) 해소** — 기술 설계서 **§9.1에 "가상 키보드 대응(G-9) 3단 구현" 표를 신설**했다(설계서 v0.6): 단별 구현 위치·정본 문자열·**담당 브라우저**·판정 수단. `static/js/viewport.js` 머리 주석에도 *이 파일은 ②만 담당하고 `isWebKit` 가드는 ①이 있는 전제에서만 옳다*를 남겼다.
  4. **함께 처리한 qa 인계 건**: `tests/browser/layout-check.js` 가 `/nope` 의 **자기 404**(사양상 404 응답)를 콘솔 오류로 세어 위반 2건으로 판정하던 문제를 고쳤다. **문서 응답이 404 이고 메시지 출처 URL 이 문서 URL 과 같은 것만** 제외하고(제외 건수는 `(자기404 n건 제외)` 로 출력), **하위 리소스의 404 는 그대로 위반**이다(음성 확인: 없는 이미지를 주입하니 위반 1건으로 잡힘). 같은 도구에 **런타임 DOM 의 viewport 메타 점검 ⑥**도 추가했다.
  - **하지 않은 것**: `viewport.js` 의 `if (!isWebKit) return;` 가드는 **그대로 두었다.** ①이 들어온 지금 Chromium 은 메타가 담당하며, 폴백을 Chromium 에도 켜면 메타에 의한 리사이즈와 `translateY` 보정이 **겹쳐 고정 바가 두 번 밀린다.** 이 판단을 설계서 §9.1 표에 적었다.
- **수정 파일**
  | 파일 | 내용 |
  |---|---|
  | `developer/site/templates/base.html` | viewport 메타 + 근거 주석 |
  | `developer/site/templates/errors/maintenance.html` | 동일 문자열(base 미상속 화면) |
  | `developer/site/static/js/viewport.js` | 머리 주석만(코드 변경 없음) |
  | `developer/site/tests/test_seo_markup.py` | `ViewportMetaTests` 5건 신설 |
  | `developer/site/tests/browser/layout-check.js` | 자기 404 제외 + 런타임 메타 점검 ⑥ |
  | `developer/site/README.md` | §9 주의에 "viewport 메타 문자열을 바꾸지 않는다" 추가 |
  | `developer/04_tech-design.md` **v0.6** | §9.1 G-9 3단 구현 표 신설 |
  | `developer/04_dev-report.md` **v0.5** | §4.4 실행 확인 신설, 자동 테스트 80 → 85건 |
- **실행 확인** (운영 미리보기 `yogapass-app:0.1.0-fix2` · `config.settings.production` · `:8001`)
  | 확인 | 명령 | 결과 |
  |---|---|---|
  | 응답 HTML 5화면 | `curl -s :8001{/,/instructors,/location,/privacy,/nope} \| grep -oE '<meta name="viewport" content="[^"]*">'` | **5/5 토큰 존재 — 누락 0건** (상태 코드 200·200·200·200·**404**) |
  | 런타임 DOM 5화면 × 4뷰포트 | `BASE=http://localhost:8001 NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js` | **20행 전부 `G-9메타: 있음` · ✓ 위반 0건**(종료 코드 0) |
  | ②③ 번들 잔존 | 해시 자산 `viewport.<hash>.js` · `tokens.<hash>.css` 를 `curl` | `visualViewport` 2 · `data-vk-fallback` 2 · `scroll-padding-bottom: var(--scroll-pad-bottom);` |
  | 자동 테스트 | `manage.py test`(`config.settings.test`) | **Ran 85 tests … OK**(80 → 85) |
  | 린트·포맷 | `ruff check .` / `ruff format --check .` | `All checks passed!` / `88 files already formatted` |
- **영향 범위 (회귀 테스트 필요 영역)**
  - **전 화면 `<head>`**(5/5). 메타 1개 변경이고 DOM·CSS·JS 는 건드리지 않았다.
  - 다만 viewport 메타는 **뷰포트 해석 자체를 바꾸므로** 레이아웃을 한 번 더 보기를 권한다 — 5화면 × 320/360/768/1280px 의 가로 스크롤·고정 바 위치·앵커 이동(`#contact`·`#map`). 제작 측 `layout-check.js` 실행 결과는 **위반 0건**이다.
  - **판정 기준이 달라지는 지점 1가지**: `layout-check.js` 가 `/nope` 의 자기 404 를 더 이상 위반으로 세지 않는다(1차 qa 판정과 다름 — 출력에 제외 건수를 표시한다).
  - **닫는 조건**: 티켓 요청 3 그대로 **정적 확인(⑤-1)** 으로 닫을 수 있다. **⑤-2(실기기 동작)는 기기 미확보로 이번에도 "미검증"** 이다(REQ-F-003 ⑤-4 · `developer/site/qa/webkit_checklist.md`).
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2 | 신규 발행(open) | 2026-09-13 | 1차 사이클 미검출 잔존 결함. 회귀 아님 |
| **3** | **closed** | **2026-09-13** | **qa 직접 재검증. 아래 확인 결과 참조.** |

### 사이클 3 재검증 상세 (qa 실행 · 증거 `qa/evidence/cycle3/`)

| # | 확인 | 실행 | 결과 |
|---|---|---|---|
| ① | 응답 HTML 5화면 토큰 | `curl` × 5 (운영 미리보기 `:8001` · `config.settings.production` · `DEBUG=False`) | **5/5 존재 · 누락 0건** · 화면당 메타 **1개** · 상태 200·200·200·200·**404** (`01_interactive_widget.txt`) |
| ② | 런타임 DOM 5화면 × 4뷰포트 | qa 자체 계측 `cycle3-probe.js` + developer `layout-check.js` | **20조합 전건 토큰 있음** · `layout-check.js` **✓ 위반 0건 · 종료 코드 0** (`05`, `06`) |
| ③ | 정본 문자열 | 템플릿 전수 `grep` | 선언 2곳(`base.html`·`errors/maintenance.html`) **정본 일치** · 다른 선언 **0건** (`02`) |
| ④⑤ | G-9 ②③ 번들 잔존 | 해시 자산 직접 `curl` | `visualViewport`·`data-vk-fallback` 각 2회 · `scroll-padding-bottom: var(--scroll-pad-bottom);` 존재. 런타임 계산 77/81/85/89px (`01`, `06`) |
| ⑥ | 재발 방지 테스트 | `manage.py test … ViewportMetaTests -v 2` | **Ran 5 tests … OK** (전체 **85건 OK**) (`16`) |
| ⑦ | **테스트 음성 확인** | 저장소 **사본**을 임시 경로에 만들어 토큰만 제거 → 일회용 컨테이너 실행 | **FAILED (failures=7)** — 테스트가 이 결함을 실제로 잡는다. 저장소 원본 무변경(`git status --porcelain developer/` = 0행) (`17`) |
| ⑧ | 회귀 | 5화면 × 320/360/768/1280 · 앵커 2종 × 4뷰포트 · S2(전화 주입) 상태 | **위반 0건** — 가로 스크롤 0 · 고정 바 하단 밀착(`bottom == innerHeight`) · 여백 77px · 앵커 여유 97~105px · 헤더 되먹임 0 · 콘솔 기타 오류 0 · HTML 오류 0 · Lighthouse 변동 없음 (`05`~`08`, `14`, `18`) |
| ⑨ | ⑤-2 실기기 동작 | — | **"미검증"** (기기 미확보). REQ-F-003 **⑤-4**에 따라 **Block 아님** · `developer/site/qa/webkit_checklist.md` 존재 확인 |

**부수 확인 — `layout-check.js` 판정 기준 변경(자기 404 제외)**: qa가 404 + 하위 리소스 404를 심은 최소 서버로 **음성 확인**한 결과 **위반 4건 · 종료 코드 1**로 잡혔다. 제외되는 것은 문서 자신의 404뿐이고 하위 리소스 404는 그대로 계수된다 → **기준 변경 수용**(`09`).

**종결 판정: `closed`** — 티켓 요청 1·2·3 전건 충족. reopen 사유 없음.
