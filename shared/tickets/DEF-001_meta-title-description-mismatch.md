---
id: DEF-001
from: qa
to: developer
phase: P5
severity: major
status: open
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
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | TC-102·103·104 재수행 + `50_html_validate` 회귀 |
