---
id: DEF-004
from: qa
to: developer
phase: P5
severity: minor
status: resolved
related_req: [REQ-N-006, REQ-N-001]
related_tc: [TC-098]
related_scr: [SCR-001, SCR-002, SCR-006, SCR-008]
found_cycle: 1
created: 2026-09-13
---

# DEF-004 320px(1280px 400% 확대 상당)에서 헤더 우측 블록이 6px 넘쳐 가로 스크롤이 생긴다

## 환경
- 실행 방법 / URL: 운영 미리보기 `http://localhost:8001/` · `/instructors` · `/privacy` · 404
- 브라우저 · 뷰포트: Chrome headless(puppeteer-core) **320×780**, `deviceScaleFactor 1`
- 대상 버전: 개발 보고서 v0.3, 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `cd qa/tools && BASE=http://localhost:8001 node viewport-check.js`
   (스크립트가 각 화면을 360·768·1280·**320**px로 열고 `documentElement.scrollWidth` vs `clientWidth`를 비교하고, `getBoundingClientRect().right > clientWidth`인 요소를 수집한다)
2. 또는 Chrome에서 1280px 창을 400% 확대한 뒤 가로 스크롤바를 확인한다.

## 기대 결과
근거: **REQ-N-006 ⑤**(Must) — *"Given 1280px를 400% 확대한다(320px 상당) When 공개·회원 영역 전 화면을 본다 Then **가로 스크롤이 없고** 콘텐츠 손실이 없으며(WCAG 1.4.10), 고정 바·헤더는 §3.0 G-11 규칙대로 동작한다"*

## 실제 결과
**4화면에서 가로 스크롤 발생 (`scrollWidth 326 > clientWidth 320`, 초과 6px)**

| 화면 | 320px 결과 | 넘치는 요소 (left,right) |
|---|---|---|
| `/` | **가로 스크롤 있음** 326/320 | `div.hdr-right [180,326]` · `details.mnav [282,326]` · `summary.mnav-btn [282,326]` · `nav.mpanel [282,326]` |
| `/instructors` | **있음** 326/320 | 동일 |
| `/privacy` | **있음** 326/320 | 동일 |
| 404 | **있음** 326/320 | 동일 |
| `/location` | 없음 320/320 | — (자기 참조 화면이라 헤더 주 CTA가 렌더되지 않아 헤더 우측 폭이 줄어든다) |

- 원인 구간: 헤더 우측 클러스터(`div.hdr-right` = 주 CTA + 햄버거 `summary.mnav-btn` 44×44 + 모바일 패널)가 320px 컨테이너를 6px 초과한다.
- **`/location`만 통과하는 사실이 원인을 특정한다** — 전화번호가 확정되어 헤더 CTA가 렌더되면 `/location`도 같은 증상이 날 가능성이 있다(전화 확정 시드 상태에서 헤더 CTA "전화 문의"가 렌더되는 것을 별도 확인했다).
- 360 / 768 / 1280px **측정 지점에서는 전 화면 가로 스크롤 0건**이다(REQ-N-001은 Pass).

## 증거
- `qa/evidence/cycle1/42_viewport.txt` (5화면 × 4뷰포트 측정 표)
- `qa/evidence/cycle1/screenshots/*_320.png` (320px 전체 페이지 스크린샷)
- `qa/evidence/cycle1/48_fixedbar_phone_confirmed.txt` (전화 확정 시 헤더 CTA 렌더 확인)

## 비고
- 심각도는 초과 폭이 6px이고 콘텐츠 손실이 없어 **Minor**로 두었으나, **REQ-N-006(Must)의 수용 기준 ⑤가 미충족 상태로 남으면 해당 REQ는 Fail**이다. G5 판정 시 잔존 여부를 PM이 판단할 수 있도록 결과 보고서에 함께 적었다.

---

## 조치 (developer 작성)

- **원인 (qa 가 지목한 `div.hdr-right` 가 맞다. 왜 커졌는지가 원인이다)**
  **헤더 주 CTA("문의하기", `a.btn.btn-p.hdr-cta`)가 `<1280px` 에서도 렌더되고 있었다.** CSS 선택자 특이성·순서 문제다.
  - `components/nav.css` 의 `.hdr-cta { display: none }` 은 특이성 (0,1,0)
  - 뒤에 로드되는 `components/base.css` 의 `.btn { display: inline-flex }` 도 (0,1,0) → **나중 규칙이 이긴다**
  → 320px 에서 `hdr-right` = CTA 94px + 8px + 햄버거 44px = **146px**, 로고 140 + gap 24 + 146 = 310px 로 콘텐츠 폭(288px)을 넘겨 `scrollWidth 326 > 320`.
  같은 이유로 **`≥1280px` 에서 숨겼어야 할 전화 아이콘 버튼(`.hdr-tel-icon`)도 숨겨지지 않고 있었다**(전화 미확정이라 qa 눈에 띄지 않았다). 즉 **G-8("768~1279px 헤더 주 CTA 없음")도 함께 위반**이었다.
- **조치 내용**
  1. 선택자에 `.hdr` 을 붙여 (0,2,0) 으로 올렸다 — `.hdr .hdr-cta { display: none }`, `≥1280px` 에서 `.hdr .hdr-cta { display: inline-flex }` · `.hdr .hdr-tel-icon { display: none }`.
     이제 구간별 헤더 구성이 CMP-003 H1~H3 명세와 일치한다(실측: `<768` 로고+전화아이콘+햄버거 / `768~1279` 로고+GNB+전화아이콘, **CTA 없음** / `≥1280` 로고+GNB+전화번호+CTA, 아이콘 없음).
  2. **함께 발견해 고친 것 — 헤더 높이 되먹임**: `viewport.js` 가 실측 높이를 `--header-h` 에 쓰고 `.hdr-row { min-height: var(--header-h) }` 가 그 값을 다시 쓰고 있어 **ResizeObserver 가 돌 때마다 헤더가 1px 씩 커졌다**(측정 중 64px → 106 → 118px 로 증가하는 것을 확인). min-height 용 정적 토큰 `--header-min-h`(64/68/72px — **값은 디자인 시스템 그대로**)를 분리하고, `--header-h` 는 앵커 오프셋용 실측값으로만 남겼다.
  3. **회귀 점검 도구 추가** — `tests/browser/layout-check.js`(Chrome 헤드리스, 5화면 × 320/360/768/1280px): 가로 스크롤·넘치는 요소·터치 타깃·글꼴 하한·인라인 style·콘솔 오류·**헤더 높이 증가**·고정 바 유무 대비 하단 여백을 한 번에 잰다. 위반이 있으면 종료 코드 1.
- **확인 결과**: 운영 미리보기 `:8001` 5화면 × 4뷰포트 **가로 스크롤 0건**(320px 에서도 `scrollWidth == clientWidth`), 헤더 높이 65/69/73px 로 재측정에도 불변. **전화 확정 시드 상태에서도 `/location` 320px 가로 스크롤 없음**(qa 가 우려한 경로 — 확인 후 값 원복).
- **수정 파일**: `developer/site/static/css/components/nav.css`, `static/css/tokens.css`, `static/js/viewport.js`, 신규 `tests/browser/layout-check.js`
- **영향 범위 (회귀 테스트 필요 영역)**: 전 화면 헤더(3구간 전부) · 앵커 이동 오프셋(G-10, `--header-h` 사용처: `/privacy` 목차 sticky, `:target`) · 400% 확대 조건. → 320/360/768/1280px 재측정 + 앵커(`#contact`·`#map`) 진입 위치 확인 + 전화 확정/미확정 양쪽.
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | 320px 재측정 + 360/768/1280 회귀 + 전화 확정 시드 상태에서도 재측정 |
