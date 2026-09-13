---
id: DEF-003
from: qa
to: developer
phase: P5
severity: minor
status: closed
related_req: [REQ-N-015, REQ-N-004]
related_tc: [TC-107]
related_scr: [SCR-001]
found_cycle: 1
created: 2026-09-13
---

# DEF-003 메인의 인라인 `style` 2곳이 CSP에 차단되어 여백이 적용되지 않고 콘솔 오류 2건이 발생한다

## 환경
- 실행 방법 / URL: 운영 미리보기 `http://localhost:8001/` (로컬 스택 `:8000`에서도 동일 — 두 환경 모두 같은 CSP 헤더)
- 브라우저 · 뷰포트: Chrome headless 360 / 768 / 1280px (뷰포트 무관, 매 로드마다 발생)
- 대상 버전: 개발 보고서 v0.3, 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. Chrome DevTools 콘솔을 열고 `http://localhost:8001/` 을 연다. (또는 `npx lighthouse http://localhost:8001/ --quiet` 후 `errors-in-console` 감사 확인)
2. `curl -s http://localhost:8001/ | grep -o 'style="[^"]*"'`

## 기대 결과
- 응답 헤더의 CSP는 `style-src 'self'` 이므로 **인라인 `style` 속성이 적용되지 않는다.** 템플릿은 CSP 안에서 동작하는 방식(클래스·유틸리티)만 써야 한다.
- 근거: **REQ-N-015**(Must) Lighthouse 권장사항 90점 이상 + 테스트 계획 §2 "콘솔 에러 0건" + 페이지 디자인의 섹션 간격 명세가 실제로 적용되어야 한다.

## 실제 결과
- 메인(`/`)에만 인라인 style 2건이 있고 **둘 다 차단된다**(다른 4화면은 0건).

```
/ : 2
style="margin-top: var(--space-3)"    ← 오시는 길 섹션의 "지도·길찾기 보기" 링크 문단
style="margin-top:10px"               ← 문의 유도 섹션의 설명 문단
```

- 콘솔 오류(매 로드 2건, 3회 측정 3/3 재현):
```
security: Applying inline style violates the following Content Security Policy directive
'style-src 'self''. … The action has been blocked.   (…/ line 170, line 157)
```
- Lighthouse 모바일 **권장사항 점수: 메인 92 / 나머지 3화면 100** — 감점 감사 항목이 `errors-in-console`, `inspector-issues (Content security policy)` 2건이다.
- 결과적으로 **해당 두 문단의 상단 여백(`--space-3`, `10px`)이 적용되지 않는다** → 디자인 명세와 간격 불일치.

## 증거
- `qa/evidence/cycle1/40_console_errors.txt` (Lighthouse `errors-in-console` 원문)
- `qa/evidence/cycle1/41_inline_style.txt` (인라인 style 추출 · 전 화면 개수)
- `qa/evidence/cycle1/39_lighthouse_mobile_summary.txt` (권장사항 92 · 감점 항목)
- `qa/evidence/cycle1/42_viewport.txt` (Chrome 실제 렌더에서 콘솔 오류 2건, 360/768/1280 전건)

---

## 조치 (developer 작성)

- **원인**: 메인 템플릿에서 한 번만 쓰이는 간격을 CSS 클래스로 만들지 않고 인라인 `style` 로 적었다. 응답 헤더의 CSP 가 `style-src 'self'` 라 인라인 style 속성은 **적용되지 않고 콘솔 오류만 남는다.** 템플릿에 인라인 style 이 들어가는 것을 막는 검사도 없었다.
- **조치 내용**
  1. 메인의 인라인 style **4곳 전부**(qa 가 관측한 2곳 + 조건부 렌더라 그때 보이지 않던 2곳)를 클래스로 교체했다.
     - `margin-top: var(--space-6)` → 기존 클래스 `callout-sec`(같은 값)
     - `margin-top: var(--space-4)` → `mt-4`, `margin-top: var(--space-3)` → `mt-3` (`static/css/base.css` 에 간격 토큰을 쓰는 **유틸리티 `.mt-3/4/5/6` 신설**)
     - `margin-top:10px` → `.inquiry-note-lead`(`pages/home.css`, `.sec-h p`·`.band p` 와 같은 10px)
  2. **회귀 테스트 추가** — `tests/test_seo_markup.py::MarkupRulesTests.test_no_inline_style_attribute`: 5화면 렌더 결과에 `style="` 0건. 브라우저 점검(`tests/browser/layout-check.js`)도 서버가 내려준 인라인 style 수를 매 화면·뷰포트마다 센다.
  3. 확인: 운영 미리보기 `:8001` 5화면 `grep -c 'style="'` → **전건 0**, Chrome 헤드리스 4뷰포트 × 4화면 **콘솔 오류 0건**(404 화면은 자기 응답 코드 404 가 콘솔에 1줄 남는 것이 전부 — 스크립트·CSP 오류 아님).
- **수정 파일**: `developer/site/templates/pages/home.html`, `static/css/base.css`, `static/css/pages/home.css`, 신규 `tests/test_seo_markup.py` · `tests/browser/layout-check.js`
- **영향 범위 (회귀 테스트 필요 영역)**: 메인 섹션 3(수업 안내 콜아웃)·4(강사 전체 보기)·5(지도·길찾기 보기)·6(문의 유도) 상단 여백, Lighthouse 권장사항 점수. → 메인 콘솔 0건 + Lighthouse 재측정.
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| **2** | **closed** | 2026-09-13 | 5화면 인라인 `style="` **0건**. Chrome 헤드리스 4화면×4뷰포트 **콘솔 오류 0건**(`/nope` 1건은 자기 404 응답 — REQ-F-060 동작). Lighthouse 권장사항 메인 **92 → 100**(3회 중앙값), 감점 항목 `errors-in-console`·`inspector-issues` 소멸. 증거 `cycle2/07_viewport.txt`, `12_lighthouse_mobile_summary.txt` |
