---
id: DEF-001
from: qa
to: developer
phase: P5
severity: major
status: closed
related_req: [REQ-N-010, REQ-N-011, REQ-N-012, REQ-C-016]
related_tc: [TC-102, TC-103, TC-104]
related_scr: [SCR-001, SCR-002, SCR-003, SCR-006, SCR-008]
found_cycle: 1
created: 2026-09-13
---

# DEF-001 색인 대상 전 화면의 title·description이 IA 기준선과 다르고 description이 길이 하한(50자)에 미달한다

## 환경
- 실행 방법 / URL: 운영 미리보기 `docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck up -d` → `http://localhost:8001/` · `/instructors` · `/location` · `/privacy` (로컬 스택 `:8000`도 동일)
- 브라우저 · 뷰포트: curl + Chrome headless 360/768/1280px (뷰포트 무관)
- 대상 버전: 개발 보고서 v0.3 (2026-09-13), 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `curl -s http://localhost:8001/ | grep -oE '<title>[^<]*</title>|<meta name="description" content="[^"]*"'`
2. 같은 명령을 `/instructors` · `/location` · `/privacy` · 없는 경로(404)에 대해 반복한다.
3. 출력 문자열을 `planning/02_information-architecture.md` v1.1 **§6.2 title 패턴 표**·**§6.3 description 초안 표**와 대조한다.
4. description의 글자 수(공백 포함)를 센다.

## 기대 결과
근거: **REQ-N-010**(Must) 수용 기준 — *"Given 색인 대상 공개 화면 Then description이 **IA §6.2·§6.3 표의 값과 문자열까지 일치**하고 서로 다르며 각 **50~90자**다(판정 기준은 IA 표 하나로 고정)"* / IA §6.3 *"아래 표가 REQ-N-010의 판정 기준이다. P5는 구현된 `<meta name="description">`을 이 표와 문자열 단위로 대조한다."*
추가 근거: **REQ-N-011**(Must) — *"Given 메인·오시는 길 When 메타·h1을 확인한다 Then '강남'과 '요가' 키워드가 자연스러운 문장으로 포함된다"* / IA §6.2 title 패턴 `{화면명} | 강남 요가패스` / IA §6.4 *"메인: `WebSite`"*.

## 실제 결과

**① description — 색인 4화면 전건 불일치 + 전건 50자 미만**

| SCR | 구현값(자수) | IA §6.3 기준값(자수) |
|---|---|---|
| SCR-001 `/` | "강남 요가 스튜디오 요가패스의 위치와 수업 안내, 문의 방법을 안내합니다." (**41자**) | "강남에 있는 요가 스튜디오 요가패스입니다. 수업과 강사를 확인하고 궁금한 점은 온라인 문의나 전화로 남겨주세요." (62자) |
| SCR-002 `/instructors` | "요가패스에서 수업을 진행하는 강사와 담당 수업을 소개합니다." (**33자**) | "강남 요가패스에서 수업을 진행하는 강사들을 소개합니다. 강사별 담당 수업과 자격·경력을 확인하고 체험 수업을 신청해 보세요." (69자) |
| SCR-003 `/location` | "강남 요가패스의 위치와 찾아오시는 방법, 문의하기를 안내합니다." (**35자**) | "강남 요가패스 오시는 길입니다. 주소와 가까운 지하철역, 운영시간을 확인하고 길찾기로 바로 이동하세요." (57자) |
| SCR-006 `/privacy` | "요가패스가 수집하는 개인정보의 항목과 이용 목적, 보관 기간, 파기 절차를 안내합니다." (**48자**) | "강남 요가패스 개인정보 처리방침입니다. 수집하는 개인정보 항목과 이용 목적, 보관 기간을 안내합니다." (56자) |

→ **4/4 문자열 불일치, 4/4 길이 하한(50자) 미달**. SCR-001은 "위치와 수업 안내, 문의 방법"이라 오시는 길 설명에 가깝고, IA가 정한 "수업과 강사를 확인하고…" 와 소구점 자체가 다르다.

**② title — 패턴 불일치 (구분자 `·` / 브랜드 `요가패스`)**

| SCR | 구현값 | IA §6.2 기준값 |
|---|---|---|
| SCR-001 | `요가패스` | `강남 요가패스 \| 강남 요가 스튜디오·수업 안내` |
| SCR-002 | `요가 강사 소개 · 요가패스` | `요가 강사 소개 \| 강남 요가패스` |
| SCR-003 | `오시는 길 · 요가패스` | `오시는 길 \| 강남 요가패스` |
| SCR-006 | `개인정보 처리방침 · 요가패스` | `개인정보 처리방침 \| 강남 요가패스` |
| SCR-008 | `페이지를 찾을 수 없습니다 · 요가패스` | `페이지를 찾을 수 없습니다 \| 강남 요가패스` |

**③ REQ-N-011 — 메인·오시는 길의 title·h1에 '강남' 없음**

| 화면 | title 강남 | title 요가 | h1 | h1 강남 |
|---|---|---|---|---|
| SCR-001 | ✗ | ○ | "요가패스" | ✗ |
| SCR-003 | ✗ | ○(브랜드명) | "오시는 길" | ✗ |

**④ IA §6.4 — 메인의 `WebSite` 구조화 데이터 미적용** (현재 `/`·`/location` 모두 `HealthAndBeautyBusiness` 1건만)

## 원인 분석 참고 (qa 관찰 — 조치 판단은 developer)
- `content/site.yml`의 `settings.name.value = "요가패스"`(주석: `[TBD: T-G] 정식 상호 확정 후 교체`)가 title 브랜드 부분의 원본이다. **DB가 없는 상태에서 렌더하면 `SITE_NAME` 환경 변수 폴백으로 "강남 요가패스"가 나온다**(DB 정지 중 확인, 증거 `12_error500.txt`) — 즉 브랜드 문자열 원본이 두 곳이고 서로 다르다.
- description은 `[TBD]`에 막힌 값이 아니라 **IA에 이미 확정 문자열이 있는 항목**이므로, 고객 값 수령과 무관하게 지금 맞출 수 있다.
- 구분자는 IA가 `|`, 구현이 `·`다.

## 증거
- `qa/evidence/cycle1/49_meta_vs_ia.txt` (대조 스크립트 출력 — 문자열·자수)
- `qa/evidence/cycle1/03_meta_landmarks.txt` (원 렌더 메타 태그)
- `qa/evidence/cycle1/20_jsonld.txt` (구조화 데이터)
- `qa/evidence/cycle1/pages/*.html`

## 심각도 근거 (Major)
- Must REQ 2건(REQ-N-010·011)의 **명시적 수치·문자열 기준을 색인 대상 전 화면(4/4)이 미충족**한다. 범위가 전면적이다.
- 사이트 목적이 "강남 지역 검색 유입 → 예약 문의 증가"(CR-000·요구사항 §1)이고 description·title은 그 1차 수단이다. 40자 내외 description은 검색 스니펫 품질에 직접 영향한다.
- 반면 수정 비용은 문자열 교체 수준으로 낮다.

---

## 조치 (developer 작성)

- **원인**
  1. **원본이 코드 안에 흩어져 있었다.** title 의 화면명·description 을 각 뷰 함수에 문자열 리터럴로 직접 적었고, 구현 시 IA 표를 옮겨 적는 대신 요약해서 썼다. 표와 대조하는 절차도 자동화도 없어 어긋난 것을 아무도 못 봤다.
  2. **브랜드 문자열의 원본이 둘이었다.** 템플릿이 `{{ meta_title }} · {{ site_name }}` 로 title 을 **조립**했고 `site_name` 은 DB(`content/site.yml` → `content_sitesetting`)에서 왔다. 그래서 ⓐ 구분자가 IA 의 `|` 가 아니라 `·` 였고 ⓑ 브랜드가 콘텐츠 적재 상태에 따라 "요가패스"/"강남 요가패스" 로 달라졌다(qa 관찰과 같다).
  3. 메인의 `WebSite` 구조화 데이터는 구현 누락이다(IA §6.4).

- **조치 내용**
  1. **IA 표를 그대로 옮긴 단일 원본 모듈 `apps/core/seo.py` 신설** — `TITLES`(§6.2) · `DESCRIPTIONS`(§6.3) · `BRAND`("강남 요가패스") · `SEPARATOR`(" | "). 문구를 다듬지 않고 **문자열 단위로 복사**했다. 뷰는 `seo.meta("SCR-00n")` 으로만 메타를 넣는다.
  2. **템플릿은 title 을 조립하지 않는다.** `partials/meta.html` 이 `meta_title` 전문을 그대로 출력한다(og:title 도 동일). 브랜드는 DB 가 아니라 `seo.BRAND`(컨텍스트 `seo_brand`)에서 온다 → **DB 가 비어 있거나 값이 달라도 title 은 IA 표 값이다.**
  3. **표시용 상호를 IA 브랜드와 같은 문자열로 맞췄다** — `content/site.yml` `settings.name.value: "요가패스" → "강남 요가패스"`(환경 변수 기본값 `SITE_NAME` 과도 일치). 정식 상호 확정(T-G) 시 두 곳을 함께 바꾼다는 주석을 남겼다. 이로써 메인 h1 폴백(`{{ site_name }}`)·헤더 로고 `aria-label`·푸터 저작권에도 '강남'·'요가' 가 들어간다(REQ-N-011 ③).
  4. **메인에 `WebSite` 구조화 데이터 추가** — `templates/partials/jsonld_website.html`(`name` = 브랜드, `url`, `inLanguage`). 1차에 사이트 내 검색이 없어 `SearchAction` 은 넣지 않았다. 오시는 길은 종전대로 `LocalBusiness` 1건이다.
  5. **회귀 테스트 추가** — `tests/test_seo_markup.py`: IA 표와 문자열 일치(title·description) / 길이 50~90자 실측 / 서로 다름 / 구분자·브랜드 패턴 / `noindex` 화면 description 없음 / 메인·오시는 길의 '강남'·'요가' / **DB 값을 바꿔도 title 이 안 바뀌는지** / `WebSite`·`LocalBusiness` JSON-LD 파싱.

  실측(운영 미리보기 `:8001`): description 길이 **62 · 69 · 57 · 56자**(IA 표 기재값과 동일), title 5화면 전건 IA 표와 일치.

- **수정 파일**
  - 신규 `developer/site/apps/core/seo.py` · `developer/site/templates/partials/jsonld_website.html` · `developer/site/tests/test_seo_markup.py`
  - 수정 `developer/site/apps/core/views.py` · `apps/core/context_processors.py` · `templates/partials/meta.html` · `templates/pages/home.html` · `content/site.yml`
  - 문서 `developer/04_tech-design.md` §9.3(원본 위치·브랜드 분리·WebSite 추가)

- **영향 범위 (회귀 테스트 필요 영역)**: 전 화면 `<head>`(title·description·canonical·OG), 메인·오시는 길 구조화 데이터, **브랜드 문자열이 보이는 모든 곳**(헤더 로고 `aria-label`="강남 요가패스 홈", 푸터 "© 2026 강남 요가패스", 메인 h1 폴백, 알림 메일 제목 `[문의 접수] 강남 요가패스`), sitemap·robots(변경 없음). → TC-102·103·104 + `50_html_validate` 회귀 + 메일 본문 확인 권장.
- **일자**: 2026-09-13

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| **2** | **closed** | 2026-09-13 | 색인 4화면 title·description 이 IA §6.2·§6.3 표와 **문자열 단위 일치**, 길이 62·69·57·56자(50~90 충족), title 5건 전건 유일. 메인 JSON-LD 에 `WebSite` 추가 확인. **DB 미적재 상태에서도 같은 title** 출력(브랜드 원본 분리 확인). 알림 메일 제목 `[문의 접수] 강남 요가패스`. 증거 `cycle2/04_meta_vs_ia.txt`, `02_meta_db_empty.txt`, `37_jsonld.txt`, `25_mail.txt` |
