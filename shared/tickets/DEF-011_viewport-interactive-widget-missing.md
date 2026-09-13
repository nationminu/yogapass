---
id: DEF-011
from: qa
to: developer
phase: P5
severity: major
status: open
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
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2 | 신규 발행(open) | 2026-09-13 | 1차 사이클 미검출 잔존 결함. 회귀 아님 |
