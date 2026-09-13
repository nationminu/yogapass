---
id: DEF-004
from: qa
to: developer
phase: P5
severity: minor
status: open
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
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | 320px 재측정 + 360/768/1280 회귀 + 전화 확정 시드 상태에서도 재측정 |
