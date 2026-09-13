---
doc_id: QA-PLAN
title: 테스트 계획서 — 1차(2026-11-06 오픈 범위)
phase: P5
owner: qa
version: 0.1
status: in-review
reviewers: [developer, planner]
inputs: [planning/02_requirements.md, planning/02_storyboard.md, planning/02_information-architecture.md, design/03_design-system.md, design/03_page-design.md, developer/04_tech-design.md, developer/04_dev-report.md, shared/reviews/P4a_tech-design_qa_r1.md, shared/reviews/P4a_tech-design_qa_r2.md]
updated: 2026-09-13
---

# 테스트 계획서 — 강남 요가패스 1차

> **판정 기준은 승인본 문서다.** 이 계획서는 판정 기준을 새로 만들지 않고, 승인본의 기준을 **실행 가능한 절차**로 옮긴다.
> 판정 기준 원본: 요구사항 v1.1 §5.0(측정 조건)·§5.3(화면 밖 검증)·§7.3(판정 모수)·§9(추적 기준선) / 기술 설계 v0.4 §9.6(폼 응답 7종)·§10.2(도구 규격)·§10.6(안전장치) / IA v1.1 §6(title·description 기준선) / 디자인 시스템 v1.1·페이지 디자인 v1.0.

---

## 1. 목적 · 범위

| 항목 | 내용 |
|---|---|
| 대상 | `developer/site/` — 개발 보고서 **v0.3**(2026-09-13, 13/14 작업 완료, 자동 테스트 53건 통과) 시점의 소스 |
| 목적 | **1차 게이트(G5a) 판정에 필요한 사실을 실행으로 확보**한다. 코드 독해만으로는 Pass를 주지 않는다 |
| 포함 | 1차 게이트 판정 모수 **96건**(`차수 = 1차` 35 + `공통` 61, 콘텐츠 포함 · 그중 Must 60) — 요구사항 §7.3 정본.<br>1차 구현 6화면(SCR-001·002·003·006·008·009), 문의 폼 응답 7종, SEO·접근성 마크업, JS 비활성 동작, 인프라·운영(compose·백업·복구·배포 스크립트·파기·메일), 검증 지원 도구와 운영 안전장치 |
| 제외 (사유) | ① **`차수 = 2차` REQ 145건** — 요구사항 §5.0 **M-7**에 따라 1차 게이트에서 **판정 대상 아님(N/A)**. 미충족으로 세지 않는다<br>② `공통` REQ의 **"2차" 수용 기준** — 같은 M-7 규칙<br>③ **운영 환경 대상 항목**(REQ-N-017 HTTPS 리다이렉트, REQ-N-022 SPF·DKIM·DMARC, REQ-N-023 ①의 운영 배포 시점 판정) — 운영 도메인·DNS 없이는 불가. §5.3이 이미 **P7 이월**로 지정한 항목이다<br>④ **P8 문서 대상 항목**(REQ-F-063 — 운영 가이드 미작성) |
| 계수 규칙 (요구사항 §7.3) | **추적률 분모 = 콘텐츠 포함 96건**, **Must 분자 = 기능+비기능만(60건)**. 콘텐츠 REQ 19건은 MoSCoW 집계 대상이 아니므로 Must로 세지 않는다 |
| qa 자체 재집계 결과 | 요구사항 §3·§5.1·§5.1.1·§6의 각 행 `차수` 열을 기계 집계한 결과 **1차 35 / 공통 61 / 2차 3(§5 안) = 판정 모수 96건 · Must 60건**으로 §7.3 정본과 **완전히 일치**했다 (증거 `qa/evidence/cycle1/37_req_1st_list.tsv`) |

---

## 2. 테스트 유형

| 유형 | 내용 | 도구 · 방법 | 합격 기준 |
|---|---|---|---|
| 기능 | 요구사항 수용 기준 기반. 문의 폼은 **기술 설계 §9.6 7행 표가 기대값 원본** | curl(= JS 0 상태) + `qa_show`/`qa_mail_log` 건수 + 앱 로그 `key=value` | 전 TC Pass, §9.6 표와 다른 값 0건 |
| 콘텐츠 | `[TBD` 잔존(§5.0 **M-5** 패턴), 화면 문구 대조 | `grep -oniE '\bTBD\b|\[TBD|고객 확인 필요|확인 필요|XXXX'` — 렌더 HTML·sitemap·robots 대상 | `/privacy` 외 0건. `/privacy`의 잔존은 REQ-F-050 1차 기준상 **정상**이며 `check_release`가 배포를 막는지로 판정 |
| 링크 | 내부 링크·정적 자산·앵커 ID | 렌더 HTML에서 href/src 추출 → 전수 상태 코드 확인 + 앵커 id 존재 확인 | 깨진 링크 0건 |
| 반응형 | 360 / 768 / 1280px | **Chrome headless 스크린샷**(실제 렌더) + CSS 구간 선언 확인 | 가로 스크롤 0건, 요소 겹침·잘림 0건 |
| 크로스브라우저 | Chrome(headless) 확인 / **Edge·Firefox·Safari 미검증** | §7 검증 한계 참조 | Chrome 기능 실패 0건. 나머지는 "미검증"으로 명시 |
| 접근성 | 랜드마크·h1·제목 계층·라벨 연결·`aria-*`·포커스·대체 텍스트·대비 | 마크업 정적 분석 + **Lighthouse 접근성** + CSS 토큰 기반 대비 계산 | Lighthouse 접근성 90+ · 마크업 결함 0건 |
| 성능 · SEO | Lighthouse 4지표, 메타·canonical·OG·sitemap·robots·JSON-LD | **Lighthouse CLI(npx 일회성)** — §5.0 **M-1** 조건 | 각 90점 이상(중앙값) |
| 폼 · 보안 | 서버 검증·honeypot·빈도 제한·중복 방지·CSP·비밀 정보 | curl + 동시 요청 스크립트 + `git grep` + 이미지 레이어 검색 | 실제 비밀 값 0건, §9.6 표와 일치 |
| 인프라 · 운영 | compose 동일 구성·백업·복구 리허설·회전·실패 주입·파기·배포 차단·롤백 가드 | 실제 명령 실행 | 각 수용 기준 충족 |
| 운영 안전장치 | 기술 설계 §10.6 ①~⑤ | 운영 이미지 직접 검사 | 5중 전부 동작 |
| 디자인 일치 | 디자인 명세·목업 대비 | 렌더 결과 비교(스크린샷) | Major 불일치 0건 |

### 2.1 M-4 검사 도구 — 사용한 도구와 대체 사유

> 요구사항 §5.0 M-4는 *"동등한 대체 도구를 쓰면 테스트 계획에 사유와 도구명을 기록한다"* 고 규정한다.

| M-4 지정 도구 | 1차에서 실제 사용 | 사유 |
|---|---|---|
| Schema Markup Validator (schema.org) | **JSON 파싱 + 필수 속성 대조**(로컬) | 외부 SaaS에 로컬 URL을 제출할 수 없다(사이트가 `localhost`). **P7 운영 URL에서 원 도구로 재확인**한다 — §5.3이 이미 "P5 로컬 · P7 운영"으로 지정 |
| W3C Markup Validation Service | **Nu Html Checker(vnu) 로컬 실행 시도 → 불가 시 마크업 정적 점검**(§7 한계에 결과 기재) | 같은 사유(로컬 URL). 파일 업로드 방식은 외부 전송이 되어 CLAUDE.md §8에 저촉될 소지가 있다 |
| 비밀 정보 검색 | `git grep -I -i -E 'api[_-]?key\|secret\|password\|token\|-----BEGIN'` + 운영 이미지 레이어 `grep -rI` | 지정 패턴 그대로 사용 |
| `[TBD]` 검색 (M-5) | `grep -oniE '\bTBD\b\|\[TBD\|고객 확인 필요\|확인 필요\|XXXX'` | 지정 패턴 그대로. **렌더된 HTML**을 대상으로 하고 번들 JS·해시 파일명은 참고로만 본다 |
| 대비 측정 | 디자인 시스템 색상 토큰 → **WCAG 상대휘도 계산**(스크립트) | 실측 도구 없이도 토큰 값으로 정확히 계산된다. 실제 렌더 조합은 스크린샷으로 교차 확인 |

---

## 3. 테스트 환경

| 항목 | 내용 |
|---|---|
| OS · 호스트 | Windows 11 Pro 22621 / Docker Desktop **24.0.2** · Docker Compose **v2.19.1** / Node **v24.14.1** / Chrome(headless) |
| 실행 방법 | `developer/site/README.md` §3. **명령은 전부 `developer/site/`에서 실행**하고 소스는 수정하지 않는다 |
| 스택 A (로컬 개발) | `docker compose -f compose.yaml -f compose.local.yaml up -d` → app·db·mail·scheduler·proxy 5서비스 + `backup` 1회성. `http://localhost:8000`(앱 직접) · `:8080`(nginx 경유) · `:8025`(Mailpit) |
| 스택 B (운영 미리보기) | 같은 compose에 `compose.prod.yaml` override, 프로젝트 `yogapass-prodcheck`, `http://localhost:8001`. **qa가 직접 빌드한 `yogapass-app:0.1.0-qa1`** 사용. `.env`는 **프로젝트 밖 임시 경로**에 만들고 `ENV_FILE`로 주입한다 (소스 트리 오염 금지) |
| 검증 전용 컨테이너 | `docker compose run --rm -d -p <port>:8000 -e <QA_*> app …` 으로 **일회용 컨테이너**를 띄운다. `.env`(`QA_TOOLS_ENABLED=0`)는 고치지 않는다. 관리 명령은 `docker exec -e QA_TOOLS_ENABLED=1 yogapass-app-1 …` 로 주입 |
| ⚠ 실행상 주의 | `docker compose exec app …` 은 `compose run` 으로 만든 일회용 컨테이너를 집을 수 있다. **운영 컨테이너를 판정할 때는 `docker exec yogapass-app-1 …` 로 컨테이너를 직접 지정**한다(이 계획서 1차 실행 중 실제로 겪은 함정) |
| 판정용 로그 | `docker compose -f compose.yaml -f compose.local.yaml logs app` / 일회용 컨테이너는 `docker logs <name>` — `inquiry.created` · `inquiry.invalid` · `inquiry.blocked reason=…` · `inquiry.duplicate token_state=used` · `inquiry.expired token_state=…` |
| 증거 저장 위치 | `qa/evidence/cycle1/` (명령 출력 원문·Lighthouse JSON/HTML·스크린샷) |

### 3.1 검증 지원 도구 사용 전제 (기술 설계 §10)

| 도구 | 사용 방법 | 비고 |
|---|---|---|
| `qa_show` / `qa_mail_log` / `qa_pii_columns` / `qa_purge_test_data` | `docker exec -e QA_TOOLS_ENABLED=1 yogapass-app-1 python manage.py …` | 마스킹 고정·읽기 전용 |
| `QA_RATE_LIMIT_MODE=off` · `QA_RETENTION_MINUTES__INQUIRY` · `QA_FAIL_INJECT` · `QA_CLOCK_OFFSET_SECONDS` | **일회용 컨테이너 기동 시 `-e`** 또는 배치 명령 실행 시 `-e` | 항목별 독립 토글 확인 포함 |
| `qa/concurrency.py` | `docker exec … python qa/concurrency.py --url http://127.0.0.1:8000/location --count N [--same-token]` | 컨테이너 내부에서 호출하므로 **출처 IP가 호스트 경유와 다르다** — 빈도 제한 TC와 섞지 않는다 |
| `seed_standard` | 1차분(번호 1,000건 생성·동시 제출 데이터) | 2차 시드는 대상 아님 |

### 3.2 표준 시드 데이터 정의 (요구사항 §5.0 M-2 ④)

1차 판정 대상 화면에는 목록·캘린더가 없고 **데이터 양에 따라 점수가 달라지는 화면이 존재하지 않는다**(강사 0명 · 수업 유형 5건 · 문의는 화면에 노출되지 않는다). 따라서 1차 Lighthouse 측정은 **`seed_content` 직후의 기본 상태**를 표준 상태로 정의한다. 2차 시드(슬롯 400·예약 200·상담 100)는 2차 게이트에서 정의한다.

### 3.3 테스트 데이터 규칙 (요구사항 §5.3 환경 요건 ⑤)

- 모든 제출 데이터의 이름·문의 내용에 **`TEST-` 접두어**를 붙인다.
- 종료 시 `qa_purge_test_data --since <실행 구간 시작 ISO> --confirm` 1회 실행 → 테이블별 삭제 건수를 증거로 남긴다.
- 운영 DB에는 접근하지 않는다(REQ-N-039). 1차 검증은 **로컬 스택과 로컬 운영 미리보기**에서만 수행한다.

---

## 4. 진입 · 종료 기준

**진입 기준 (1차 사이클 착수 시점 확인 결과)**

| 기준 | 결과 |
|---|---|
| G4(개발) 승인 | **미승인 — P4 진행 중**. PM 방침("최대한 빨리")에 따라 **G4 이전 선행 검증**으로 1차 사이클을 수행한다. 이 사실을 결과 보고서에 명시한다 |
| 로컬 빌드·실행 성공 | **충족** — `docker compose … up -d` 로 5서비스 healthy 재현 |
| 개발 보고서 제출 | **충족** — v0.3(`draft`) |
| 판정 기준 문서 승인 | **충족** — 요구사항 v1.1 / IA v1.1 / 화면정의서 v1.1 / 디자인 시스템 v1.1 · 페이지 디자인 v1.0 (전부 `approved`) |
| 기술 설계 §9.6·§10.2 확정 | **충족** — v0.4 |

**종료 기준 (G5a 권고 조건)**

1. 1차 판정 모수 96건이 **전부 TC 또는 §5.3 화면 밖 검증 행에 연결**(미추적 0건)
2. **Critical·Major 결함 0건**
3. Minor 이하 잔존 결함은 목록·이월 사유를 결과 보고서에 기재
4. `Block`·`미검증` 항목은 **사유와 해소 시점(P7/2차)** 을 명시
5. **복구 리허설 1회 성공**(REQ-N-032 ② — CR-001 조건 7이 게이트 통과 조건으로 요청한 항목)
6. 테스트 데이터 삭제 확인 기록

---

## 5. 결함 관리

- 심각도 기준: `CLAUDE.md` §5. 발행 위치: `shared/tickets/DEF-{nnn}_{slug}.md`
- 흐름: `open` → `in-progress` → `resolved`(developer) → `closed` / `reopened`(qa)
- **같은 원인은 하나의 티켓으로 묶는다.** 증상이 여러 화면에 퍼져도 원인이 하나면 1건이다.
- **입력 미확보(`[TBD]` 미수령)로 값이 비는 것은 결함이 아니다.** `Block`/`조건부`로 기록하고 §7에 모은다.
- **문서(승인본)와 구현이 다르면 그 자체가 결함**이다(기술 설계 §9.6 머리말과 같은 규칙을 IA §6 기준선에도 적용한다).

---

## 6. 사이클

| 사이클 | 내용 | 시점 | 비고 |
|---|---|---|---|
| **1차** | 전체 TC 수행 + 결함 발행 | 2026-09-13 (완료) | 이 문서와 같은 날 |
| 2차 | 결함 재검증 + 영향 범위 회귀 | developer 수정 후 | 수정 파일 기준 회귀 범위를 developer 조치 란에서 받아 정한다 |
| 3차 | 잔여 재검증 | 필요 시 | 3사이클 초과 시 PM 보고 |
| (P7) | 운영 스모크 — 이월 항목 판정 | 배포 후 | REQ-N-012(원 도구)·017·022·023 ① 등 |

---

## 7. 리스크 · 검증 한계 (이 계획으로 **판정할 수 없는 것**)

> 확인하지 못한 것을 "통과"로 적지 않기 위해 먼저 선언한다.

| # | 항목 | 영향 REQ | 한계 내용 | 처리 |
|---|---|---|---|---|
| L-1 | **실기기·소프트 키보드** | REQ-F-003 ⑤-2, REQ-N-002 | Android 실기기·에뮬레이터 없음. DevTools 에뮬레이션은 요건 ⑥을 충족하지 않는다 | **⑤-1(정적 확인)까지 수행**하고 ⑤-2는 "미검증"으로 명시(**Block 아님** — REQ-F-003 ⑤-4) |
| L-2 | **Safari · iOS(WebKit)** | REQ-N-003 | Windows에 WebKit 실행 수단 없음. 기술 설계 §10.5 ②의 WebKit 자동화도 엔진 미보유 | "미검증" 명시 + `developer/site/qa/webkit_checklist.md` 존재 확인까지. PM 조건부 승인·이월 판단 대상(§8.5 D-1) |
| L-3 | **Edge · Firefox** | REQ-N-003 | 이번 사이클에서 실행하지 않았다(Chrome headless만 수행) | 부분 검증으로 기록. 필요 시 2차 사이클에서 보완 |
| L-4 | **운영 도메인·DNS·HTTPS** | REQ-N-017, REQ-N-022 | 운영 도메인 미확보 | §5.3이 지정한 대로 **P7 이월**. P5는 혼합 콘텐츠·절대 URL 스킴만 확인 |
| L-5 | **실제 서버 배포·롤백** | REQ-N-033 | 서버·스테이징 미확보. 스크립트 0단계·가드·문법까지만 로컬 재현 가능 | **부분 Pass + P7 이월**. 기술 설계 §12.6.2의 ⓐ/ⓑ 경로 판정을 따른다 |
| L-6 | **스테이징 환경** | REQ-N-040 | 서브도메인·서버 미확보(§8.5 D-30) | 설정 파일(`yogapass-stg.conf.sample`·`FORCE_NOINDEX`) 대조까지. 실측은 P7 |
| L-7 | **운영 DB 권한자 목록·백업 보관 위치** | REQ-N-039 | `devops/07_deploy-plan.md` 미작성 → 대조 대상 문서가 없다 | **Block(입력 미확보)**. qa R2 Q-10 조건 ①이 미충족 |
| L-8 | **외부 검사 서비스**(Schema Validator·W3C) | REQ-N-012, REQ-N-016 | 로컬 URL 제출 불가 | 로컬 대체 검사(§2.1) + **P7 원 도구 재확인** |
| L-9 | **고객 제공 값 8묶음 미수령** | REQ-C-001·003~012·017~019, REQ-F-004·030·031·033, REQ-N-011·012·023 ② | 전화·주소·강사·처리방침 본문·도메인·로고가 전부 `[TBD]` → 화면에 요소 자체가 렌더되지 않는다 | **값 의존 부분은 `Block`(입력 미확보)**, 구조·분기 동작은 판정. 오픈 차단 항목이므로 pmo 추적 |
| L-10 | **`submit_token` 만료(24시간) 분기** | 기술 설계 §9.6 ⑦ | `QA_CLOCK_OFFSET_SECONDS`가 서명 만료 판정에 적용되지 않아 `token_state=expired`를 유발할 수단이 없다 | **부재·변조 2종만 판정**하고 만료는 Block → **DEF-005** 발행 |
| L-11 | **Lighthouse 측정 환경** | REQ-N-004·007·015 | 호스트 부하가 실행마다 달라 성능 점수에 편차가 있다 | M-1대로 **3회 실행 중앙값**으로 판정하고 원값 3개를 모두 기록 |
| L-12 | **G4 미승인 상태에서의 선행 검증** | 전체 | 구현이 14작업 중 13작업 완료 시점이며 작업 14(자체 점검 마감) 결과가 반영되지 않았다 | 결과 보고서 머리에 명시. 작업 14 완료분은 2차 사이클에서 회귀 |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.1 | 2026-09-13 | qa | 최초 작성 — 1차 판정 모수 96건(Must 60) 재집계 확인, 실행 환경·도구 대체 사유·검증 한계 12건 정의 | `shared/reviews/P4a_tech-design_qa_r1.md` · `_r2.md` |
