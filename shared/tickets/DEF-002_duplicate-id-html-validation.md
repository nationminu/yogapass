---
id: DEF-002
from: qa
to: developer
phase: P5
severity: minor
status: open
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
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | vnu 재실행(오류 0건) + `18_a11y_markup` 회귀 |
