---
id: DEF-002
from: qa
to: developer
phase: P5
severity: minor
status: resolved
related_req: [REQ-N-016, REQ-N-006]
related_tc: [TC-108]
related_scr: [SCR-001, SCR-002, SCR-003, SCR-006, SCR-008]
found_cycle: 1
created: 2026-09-13
---

# DEF-002 전 화면에서 로고 SVG 접근 이름 id(`ypht`)가 중복되어 HTML 검증 오류 5건이 난다

## 환경
- 실행 방법 / URL: 운영 미리보기 `http://localhost:8001/` · `/instructors` · `/location` · `/privacy` · 404
- 검사 도구: **Nu Html Checker (vnu.jar 24.x)** — W3C Markup Validation Service(`validator.w3.org/nu`)와 같은 엔진. 로컬 URL을 외부 서비스에 제출할 수 없어 동일 엔진을 로컬 실행했다(테스트 계획 §2.1 대체 도구 기록)
- 대상 버전: 개발 보고서 v0.3, 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `curl -s http://localhost:8001/{,instructors,location,privacy,nope} -o html/<name>.html` 로 5화면을 저장한다.
2. `java -jar qa/tools/node_modules/vnu-jar/build/dist/vnu.jar --format gnu --skip-non-html html/`

## 기대 결과
근거: **REQ-N-016**(Must) 수용 기준 — *"Given W3C Markup Validation Service When 차수별 전 화면을 검사한다 Then **오류 0건**, 랜드마크 요소가 모두 존재한다"* (검사 도구는 §5.0 M-4).

## 실제 결과
**error 5건 (5화면 전건 · 화면당 1건)**

```
html/e404.html:141.3-141.19: error: Duplicate ID “ypht”.
html/e404.html:47.3-47.19:  info warning: The first occurrence of ID “ypht” was here.
html/home.html:242.3-242.19: error: Duplicate ID “ypht”.
html/instructors.html:197.3-197.19: error: Duplicate ID “ypht”.
html/location.html:306.3-306.19: error: Duplicate ID “ypht”.
html/privacy.html:342.3-342.19: error: Duplicate ID “ypht”.
```

- 원인 위치: **헤더 로고 SVG와 푸터 로고 SVG가 같은 `<title id="ypht">`를 쓴다**. 두 SVG 모두 `role="img" aria-labelledby="ypht"`다.
- 접근성 영향: 중복 id에서 `aria-labelledby`는 **문서상 첫 번째 요소만** 참조하므로, 푸터 로고의 접근 이름이 헤더 로고의 title로 해석된다. 보조기기 동작이 명세와 달라질 수 있다(REQ-N-006 ④).
- 랜드마크는 전 화면 존재(header 1 · main 1 · footer 1 · nav 2~3) → 수용 기준의 뒷부분은 충족.

**참고(오류 아님)**: `instructors.html:117` `info warning: Section lacks heading.` — `<section>`에 제목이 없다. error가 아니므로 REQ-N-016 판정에는 영향이 없으나 문서 구조상 `div` 전환 또는 제목 추가를 권장한다.

## 증거
- `qa/evidence/cycle1/50_html_validate.txt` (vnu 전체 출력 11줄)
- `qa/evidence/cycle1/html/*.html` (검사 대상 원본)
- `qa/evidence/cycle1/18_a11y_markup.txt` (랜드마크·SVG 대체 텍스트 집계)

---

## 조치 (developer 작성)

- **원인**: `{% inline_svg %}` 태그가 SVG 파일 내용을 **그대로** 삽입한다. `logo-horizontal.svg` 안에 `<title id="ypht">` 와 `aria-labelledby="ypht"` 가 들어 있고, 이 파일을 헤더·푸터 두 곳에서 넣으므로 같은 id 가 문서에 2번 나온다. "같은 자산을 한 문서에 두 번 넣을 때 id 를 분리한다"는 장치가 없었다.
- **조치 내용**
  1. `inline_svg` 에 **`uid` 인자 추가** — 파일 안의 모든 `id` 와 그 참조(`aria-labelledby`·`aria-describedby` 토큰, `href="#…"`, `url(#…)`)에 `-{uid}` 접미사를 붙인다. 헤더 `uid="hdr"` · 푸터 `uid="ftr"` · 메인 히어로 심볼 `uid="hero"` → `ypht-hdr` / `ypht-ftr` / `ypmt-hero`.
     **접근 이름도 함께 고쳐진다** — 푸터 로고가 자기 `<title>` 을 참조한다(REQ-N-006 ④).
  2. **회귀 테스트 추가** — `tests/test_seo_markup.py::MarkupRulesTests`: 5화면 전건 **중복 id 0건**, 그리고 `aria-labelledby` 가 **자기 SVG 안의 title id** 를 가리키는지.
  3. 재검사(운영 미리보기 `:8001` 5화면, `vnu.jar 26.x --format gnu --skip-non-html`): **error 0건**.
- **수정 파일**: `developer/site/apps/core/templatetags/icons.py`(`inline_svg`·`_namespace_ids`), `templates/partials/header.html`, `templates/partials/footer.html`, `templates/pages/home.html`, 신규 `tests/test_seo_markup.py`
- **영향 범위 (회귀 테스트 필요 영역)**: 인라인 SVG 를 넣는 모든 위치(헤더·푸터 로고, 히어로 심볼). 아이콘(`{% icon %}`)은 id 를 쓰지 않아 영향 없음. → vnu 재실행 + `18_a11y_markup`(SVG 대체 텍스트·랜드마크) 회귀.
- **미처리(의도)**: `instructors.html` 의 `info warning: Section lacks heading` 은 **오류가 아니라** REQ-N-016 판정 대상이 아니고, `<section>`→`<div>` 전환은 랜드마크·문서 구조 변경이라 designer 확인이 필요해 이번 수정에 넣지 않았다(개발 보고서 §4.3 확인 요청 ④).
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | vnu 재실행(오류 0건) + `18_a11y_markup` 회귀 |
