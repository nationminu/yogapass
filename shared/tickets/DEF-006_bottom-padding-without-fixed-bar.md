---
id: DEF-006
from: qa
to: developer
phase: P5
severity: minor
status: closed
related_req: [REQ-F-003, REQ-N-002]
related_tc: [TC-004]
related_scr: [SCR-003]
found_cycle: 1
created: 2026-09-13
---

# DEF-006 대표 전화 미확정 + 자기 참조 화면에서 고정 바가 없는데 본문 하단 여백 76px이 남는다

## 환경
- 실행 방법 / URL: 운영 미리보기 `http://localhost:8001/location` (대표 전화 `[TBD]` 상태 = 현재 기본 시드)
- 브라우저 · 뷰포트: Chrome headless(puppeteer-core) 360×780 · 768×1024 (1280px은 정상)
- 대상 버전: 개발 보고서 v0.3, 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `content/site.yml`의 `settings.phone`이 `value: null / is_published: false`(현재 기본값)인 상태에서 `seed_content`를 실행한다.
2. `cd qa/tools && BASE=http://localhost:8001 node probe2.js`
3. `/location` 행의 `고정바` 와 `body.padding-bottom` 값을 본다.

## 기대 결과
근거: **REQ-F-003 ②**(Must) 수용 기준 — *"Given 대표 전화 미확정 Then 고정 바가 노출되지 않고 **본문 하단 여백도 적용되지 않으며** 폼 하단 대체 연락 안내는 그대로 보인다"*
(§3.0 G-6 ② 단서 · G-3 "고정 바가 **노출되는 뷰포트에서** 본문 하단 여백을 둔다")

## 실제 결과

| 화면 | 뷰포트 | 고정 바 | `body` padding-bottom | 판정 |
|---|---|---|---|---|
| `/location` | 360px | **없음**(기대대로) | **76px** | **여백이 남는다 — 위반** |
| `/location` | 768px | **없음**(기대대로) | **76px** | **위반** |
| `/location` | 1280px | 없음 | 0px | 정상 |
| `/` (비자기참조) | 360px | 있음 h=61 | 77px | 정상 |

- 고정 바가 사라지는 조건(자기 참조 + 전화 `[TBD]`)에서 **여백 제거 조건만 함께 적용되지 않았다.**
- 영향: 1차 유일 폼 화면인 `/location` 하단에 빈 여백 76px이 남아 페이지 디자인의 하단 간격과 달라진다. 기능 영향은 없다.
- 참고: 전화번호를 확정 값으로 시드하면 `/location`에 "전화 문의" 전폭 1버튼 고정 바가 정상 노출되고 여백 77px이 맞는 상태가 된다(증거 `48_…`). 즉 **`[TBD]` 경로에서만 나타난다**.

## 증거
- `qa/evidence/cycle1/44_fixedbar_focus_nojs.txt` (전화 `[TBD]` 상태 측정표 — `/location` 360·768px `body.padding-bottom=76px`, 고정바 없음)
- `qa/evidence/cycle1/48_fixedbar_phone_confirmed.txt` (전화 확정 상태 — 고정 바 1버튼 + 여백 77px, 정상)

---

## 조치 (developer 작성)

- **원인**: 고정 바의 **렌더 여부는 서버가**(`cta.show_bar` — 자기 참조 + 전화 미확정이면 S3 로 요소 자체를 렌더하지 않음), **하단 여백은 CSS 가**(`body { padding-bottom: var(--body-pad-bottom) }`, 뷰포트 조건만 봄) 각각 판단했다. 두 판단이 연결돼 있지 않아 "바는 없는데 여백은 있는" 상태가 생겼다. `≥1280px` 은 미디어 쿼리가 여백을 0 으로 만들어 정상으로 보였을 뿐이다.
- **조치 내용**
  1. **서버 판단을 CSS 로 전달** — `templates/base.html` 의 `<html>` 에 `data-fixed-bar="{% if cta.show_bar %}on{% else %}off{% endif %}"` 를 붙였다.
  2. `tokens.css` 에 `html[data-fixed-bar="off"] { --fixed-bar-h: 0px; --body-pad-bottom: 0px; --scroll-pad-bottom: var(--anchor-offset); }` 추가. 선택자 특이성 (0,1,1) 이라 미디어 쿼리의 `:root` (0,1,0) 선언을 **순서와 무관하게** 덮는다. `scroll-padding-bottom`(G-9)도 함께 풀린다.
  3. **회귀 테스트 추가**
     - `tests/test_seo_markup.py::FixedBarPaddingTests` — `/location`(전화 `[TBD]`)은 `barwrap` 없음 + `data-fixed-bar="off"`, 다른 화면은 `on`, **전화 확정 시 `/location` 도 `on`**, 그리고 스타일시트에 여백 해제 규칙이 있는지.
     - `tests/browser/layout-check.js` — 매 화면·뷰포트에서 "고정 바가 없는데 `body` 하단 여백이 0 이 아니면" 위반으로 잡는다.
- **확인 결과**(운영 미리보기 `:8001`, Chrome 헤드리스): `/location` 320·360·768px **고정 바 없음 + `padding-bottom: 0px`** / 1280px 0px / 다른 4화면 77px(바 있음). **전화 확정 시드 상태에서는 `/location` 도 바 노출 + 77px** 로 정상 복귀(확인 후 값 원복).
- **수정 파일**: `developer/site/templates/base.html`, `static/css/tokens.css`, 신규 `tests/test_seo_markup.py` · `tests/browser/layout-check.js`
- **영향 범위 (회귀 테스트 필요 영역)**: 전 화면 `body` 하단 여백과 앵커 스크롤 여백. 특히 `/location`(TC-004) + 전화 확정/미확정 양쪽(TC-003·005·007).
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| **2** | **closed** | 2026-09-13 | `/location`(자기 참조 + 전화 `[TBD]`): `data-fixed-bar="off"` · `.barwrap` **DOM 없음** · `body padding-bottom` **0px**(320·360·768·1280 전건). 다른 4화면은 바 표시 + 77px, 1280px 는 미표시 + 0px. 전화 확정 주입 시 `/location` 도 바 표시 + 77px 로 전환(검증 후 원복). 증거 `cycle2/10_fixedbar_gnb.txt`, `36_fixedbar_phone.txt` |
