---
doc_id: DEV-REPORT
title: 개발 보고서 — 1차 구현(3단계) + P5 결함 수정(DEF-001~010 · DEF-011)
phase: P4
owner: developer
version: 0.5
status: draft
reviewers: [designer, planner]
inputs: [developer/04_tech-design.md, planning/02_requirements.md, planning/02_storyboard.md, design/03_design-system.md, design/03_page-design.md, design/mockups/, shared/tickets/TKT-DSN-002_to-developer_favicon-og-raster.md, shared/reviews/P4a_tech-design_devops_r2.md, shared/reviews/P4a_tech-design_qa_r2.md, qa/05_test-report.md, shared/tickets/DEF-001_meta-title-description-mismatch.md, shared/tickets/DEF-002_duplicate-id-html-validation.md, shared/tickets/DEF-003_csp-blocks-inline-style-home.md, shared/tickets/DEF-004_reflow-320px-horizontal-scroll.md, shared/tickets/DEF-005_touch-target-and-font-minimum.md, shared/tickets/DEF-006_bottom-padding-without-fixed-bar.md, shared/tickets/DEF-007_rollback-guard-untagged-image.md, shared/tickets/DEF-008_clock-offset-not-applied-to-token-expiry.md, shared/tickets/DEF-009_privacy-collected-items-vs-schema.md, shared/tickets/DEF-010_temp-source-file-in-prod-image.md, shared/tickets/DEF-011_viewport-interactive-widget-missing.md]
updated: 2026-09-13
---

# 개발 보고서 (초안) — 1차 구현 3단계 + **P5 1차 결함 수정**

> **이 문서의 상태**: `draft`. 1차 구현 **14개 작업 중 작업 1~13 + 작업 14 일부**를 마치고, **P5 1차 검증 결함(DEF-001~010)** 과 **2차 검증 결함(DEF-011)** 을 전건 수정한 시점의 보고다.
> **규칙**: 이 문서에는 **직접 실행해 확인한 것만** 적는다. 실행하지 않은 항목은 "미확인"으로 적고 "완료"로 쓰지 않는다.
> 설계 근거는 `developer/04_tech-design.md` **v0.6**, 실행 절차는 `developer/site/README.md`.
> v0.1(1단계) 대비 달라진 곳은 **▲**, v0.3(3단계)에서 새로 한 것은 **★**, **v0.4(P5 1차 결함 수정)에서 한 것은 ★★** 로 표시했다.
>
> **★★★ 이번 판(v0.5)의 핵심 3줄 — P5 2차 결함 DEF-011(Major) 1건 수정**
> 1. **G-9 ①(viewport 메타 `interactive-widget=resizes-content`)을 `templates/base.html` 에 넣었다.** 전 화면이 base 를 상속하므로 **5화면 전건 반영**(누락 0건 — 운영 미리보기 응답 HTML·런타임 DOM 양쪽에서 확인). base 를 상속하지 않는 `templates/errors/maintenance.html` 도 같은 문자열로 맞췄다.
> 2. **결함의 원인은 설계 공백이었다** — 기술 설계서가 G-9 ②(§10.5)·③(디자인 문서)만 다루고 **①을 어디에도 적지 않았다**. 설계서 **§9.1에 3단 구현 표를 신설**해 메타 문자열을 정본으로 고정했다(설계서 v0.6).
> 3. **회귀 테스트 5건 + 런타임 점검 1항목을 추가**했다(자동 테스트 80 → **85건**). qa 인계 건으로 `layout-check.js` 가 **`/nope` 의 자기 404 를 위반으로 세던 문제**도 함께 고쳤다(하위 리소스 404 는 그대로 위반 — 음성 확인 완료).
>
> **★★ 이번 판(v0.4)의 핵심 3줄**
> 1. **DEF-001~010 을 전건 수정**했다(미수정·`rejected` 제안 **0건**). 판정 기준이 있는 것은 **승인 산출물의 문자열·수치를 그대로** 따랐다(IA §6.2·§6.3, REQ-N-006, REQ-F-003 ②).
> 2. **회귀 테스트 27건과 브라우저 레이아웃 점검 도구를 추가**했다 — 같은 결함이 다시 들어오면 `manage.py test`(80건) 또는 `tests/browser/layout-check.js` 가 먼저 실패한다.
> 3. **결함 수정 중 발견해 함께 고친 것 2건**: 헤더 주 CTA 가 전 구간에 노출되던 CSS 순서 문제(G-8 위반 · DEF-004 의 실제 원인), `viewport.js` ↔ `--header-h` 되먹임으로 **헤더가 1px 씩 계속 자라던 현상**. §4.3 에 확인 요청 6건을 남겼다.
>
> **★ 이번 판(v0.3)의 핵심 3줄**
> 1. **PM 결정 2건을 반영했다** — ① 폼 토큰 **만료 = 다시 작성 안내**(설계 §9.6 ⑤를 ⑤/⑦로 분리, 테스트 5건 추가) ② **OG 이미지 임시본** 생성·교체 절차 확정.
> 2. **운영·배포·백업·복구·검증 지원 도구를 구현하고, 로컬에서 재현 가능한 범위를 전부 실행해 확인했다** — 백업 회전·실패 주입·락 충돌 중단·**복구 리허설 1회 성공**·안전장치 5중.
> 3. **구현 중 결함 1건을 발견해 고쳤다** — 같은 토큰 **동시 이중 제출이 500** 이 되던 경로(UNIQUE 충돌 미처리). 동시 5건 실행으로 재현·수정 확인.

---

## 1. 요약

| 항목 | 내용 |
|---|---|
| 이번 범위 | ★ **PM 결정 2건**(토큰 만료 처리 · OG 임시본) + 기술 설계 §11.1 **작업 11(성능·폰트 폴백 메트릭 실측) · 12(운영 compose·배포/롤백/복구·백업·nginx 샘플·일일 요약) · 13(검증 지원 도구 ①~⑪)** |
| 진척(작업 단위) | ★ **13 / 14 작업** (남은 것: 14 자체 점검 마감. 작업 11 중 **Lighthouse 측정만 미실행** — 브라우저 실행 환경 없음) |
| 1차 화면 | ▲ **6화면 전부 구현** — SCR-001·002·003·006·008·009 |
| Must REQ 구현률 | ▲ 1차 Must 60건 기준 **추정** — **완료 약 34 · 부분 약 14 · 미착수 약 12** (§2 표가 근거. **확정 집계는 qa 추적 매트릭스가 한다** — 이 숫자를 게이트 판정에 그대로 쓰지 않는다) |
| 로컬 빌드 · 실행 | **성공** — `docker compose … up` 으로 app·db·mail·scheduler·proxy **5개 서비스 healthy**, 4개 공개 화면 200 / 없는 경로 404 (§4) |
| 운영 빌드 | **성공** — prod 이미지 빌드 + gunicorn 기동 + 해시·brotli·`immutable` 확인, 새 화면 4종 200 (§4) |
| 문의 폼 | ★ **설계 §9.6 응답 형태 7종**(v0.4에서 ⑤/⑦ 분리)을 전부 구현하고 전건 실행 확인(자동 테스트 + curl) |
| 백업·복구 | ★ `run_backup` **정상·`--dry-run`·라벨·락 충돌 중단·실패 주입·회전(일7/주4/월3)** 전건 실행. **`restore.sh` 로컬 복구 리허설 1회 성공**(문의 36건 → 백업 시점 11건으로 복원) |
| 배포·롤백 | ★ `deploy.sh` **0단계 사전 점검 실행 확인**(디스크·롤백 이미지·IRREVERSIBLE·최근 백업·`check_release` 로 **배포 차단까지 확인**) · `rollback.sh` 가드 2종 확인. **실제 배포·롤백은 서버 필요 → 미확인** |
| 검증 지원 도구 | ★ **①~⑪ 전부 구현**, 운영 안전장치 **5중 전건 실행 확인**(운영 이미지에 `qa/`·`qa_*` 명령 **0건**, `QA_TOOLS_ENABLED` 없이 실행 시 **종료 코드 2**, 운영+QA 조합 **기동 거부**) |
| 자동 테스트 | ★★ **80건 전부 통과** (v0.3 53건 → 80건 · **P5 결함 회귀 27건 추가**), `ruff check` · `ruff format --check` 통과 |
| ★★ P5 1차 결함 | **DEF-001~010 전건 수정 완료**(미수정 0건). 확인 명령·결과는 **§4.2**, designer·planner·qa 확인 요청 6건은 **§4.3** |
| 검증팀 전달 가능 여부 | ★ **가능.** 화면·폼·SEO·접근성·**백업/복구·검증 지원 도구 전부** 지금 검증할 수 있다. 남은 제약은 **브라우저·실기기·서버가 필요한 항목**뿐이다(§4 말미·§8) |

---

## 2. 요구사항별 구현 현황 (REQ ID ↔ 구현 파일)

> 경로는 모두 `developer/site/` 기준이다. **부분**은 "이번 범위의 몫은 끝났고 남은 조건(데이터 수령·측정·배포)이 있다"는 뜻이다.

### 2.1 기능 요구사항

| REQ ID | 요구사항 | 상태 | 구현 위치 |
|---|---|---|---|
| REQ-F-001·002·003 | 공통 헤더·푸터·전역 주 CTA | 완료 | `templates/partials/{header,footer,fixed_bar}.html` · `apps/core/cta.py` |
| REQ-F-004 | 전화 걸기 링크 | 부분 | `apps/core/templatetags/icons.tel_href` — 대표 전화 `[TBD]` 라 **현재 렌더되는 `tel:` 0건**(의도된 동작, 테스트로 고정) |
| REQ-F-005 | 처리방침 전역 링크 | ▲ 완료 | 푸터·모바일 패널·폼 동의 → `/privacy` 실제 화면 존재 |
| REQ-F-006 | 화면 간 이동 일관성 | ▲ 완료 | `apps/content/services.nav_items` (GNB 단일 원본) + 4화면 상호 링크 |
| REQ-F-010~015 | 메인 7섹션 | 부분 | `templates/pages/home.html` — 문구·데이터 미수령 섹션은 렌더하지 않는다 |
| REQ-F-020 | 강사 목록 | ▲ 완료(1차 정의) | `templates/pages/instructors.html` · `apps/content/services.all_instructors` — 비활성 강사 제외 |
| REQ-F-021 | 강사 데이터 분리 · **경계값 0·1·3·12명** | ▲ 완료 | `content/instructors.yml` → `seed_content`. 인원별 열 수 전환(0=빈 상태 / 1=`g-1c` / 2=`g-2c` / 3·12=`g-3`) — `tests/test_pages.py` 로 고정 |
| REQ-F-022 | 강사 사진 대체 처리 | ▲ 완료 | CMP-027 이니셜 아바타(`aria-hidden`), **인물 스톡 0장**(`<img>` 0건을 테스트로 고정) |
| REQ-F-023 | 강사 → 전환 연결 | ▲ 완료 | 하단 CTA 밴드(CMP-025) 1차 문구 |
| REQ-F-030 | 지도 표시 | ▲ 부분 | `templates/pages/location.html` + `static/css/pages/location.css` — CMP-022 대체 영역(CSS 격자, **지도 캡처 0건**). **임베드 URL 미확정(T-E)이라 지도 자체는 미표시** |
| REQ-F-031 | 길찾기 외부 링크 | ▲ 부분 | `map_directions_url` 확정 시 새 창 링크 렌더. 값 미확정이라 현재 미노출 |
| REQ-F-032 | 지도 지연 로딩(클릭 투 로드) | ▲ 완료(구현) | `static/js/map.js` — 버튼 클릭 시에만 iframe 생성. **초기 요청 0건**은 구조상 보장(외부 URL이 `data-map-src` 속성에만 있다) |
| REQ-F-033 | 오시는 길 정보 | ▲ 완료(구조) | `apps/core/views.LOCATION_ROWS` 7행(주소·지하철·버스·주차·운영시간·휴무일·대표 전화). **값 미확정 행은 렌더하지 않고**, 전부 없으면 CMP-026 빈 상태 |
| REQ-F-034 | 주소 복사 (Could) | ▲ 완료 | `static/js/map.js` — 클립보드 + CMP-021 토스트 3초(`role="status"`), 비보안 컨텍스트 폴백 포함 |
| REQ-F-035 | 지도 접근성 대체 | ▲ 완료 | 주소·교통 `<dl>` 이 지도와 **별개 텍스트**로 존재 + iframe `title` + `<noscript>` 대체 |
| REQ-F-040 | 문의 폼 제공 | ▲ 완료 | `apps/inquiry/forms.py` · `templates/components/form_field.html` — 4항목 + honeypot, 경계값 20/21·500/501 테스트 |
| REQ-F-041 | 클라이언트 검증(blur 이후) | ▲ 완료 | `static/js/form.js` — blur 이후에만 오류 표시, 입력 중 실시간 오류 없음 |
| REQ-F-042 | 서버 측 입력 검증 | ▲ 완료 | `apps/inquiry/forms.py` + `services.handle_submission` — **응답 형태는 설계 §9.6 표 그대로**(§3.1) |
| REQ-F-043 | 개인정보 수집·이용 동의 | ▲ 완료 | 수집 항목·목적·**보관 기간(D-19 잠정 "1년")** 표기 + 처리방침 새 창 링크. 미동의 시 제출 거부 |
| REQ-F-044 | 스팸 방지 | ▲ 완료 | honeypot(화면 밖 배치) + 빈도 제한 + 서버 검증. **차단 사실 미노출**(③이 ①과 픽셀 단위로 같음을 테스트로 고정) |
| REQ-F-045 | 스튜디오 알림 | ▲ 완료 | `apps/inquiry/services._notify_body` → `mailer_outbox` → `send_outbox` → **Mailpit 수신 확인**(§4 #14). 수신 주소는 `INQUIRY_NOTIFY_TO` |
| REQ-F-046 | 전송 결과 안내 · 중복 제출 방지 | ▲ 완료 | 1회용 `submit_token`(서명 값, 24시간) + `inquiry_inquiry.submit_token` UNIQUE. **재제출·새로고침 시 저장 1건·알림 1건** |
| REQ-F-050 | 처리방침 화면 | ▲ 완료(1차 정의) | `templates/pages/privacy.html` + `content/privacy.yml` — **목차 11항목 전부 소제목으로 존재**, 미확정 항목은 `[TBD]` 표시(1차 수용 기준) |
| REQ-F-051 | 처리방침 입력 항목 정의 | ▲ 완료(제작 몫) | `content/privacy.yml` 이 곧 **고객이 채울 입력 항목 목록**이다(항목·표 칸 단위) |
| REQ-F-052 | 위탁·외부 처리 목록 | ▲ 완료(제작 몫) | 기술 설계 §7.1 → `content/privacy.yml` 6항 위탁 표 3행으로 반영 |
| REQ-F-053 | 시행일·개정 이력 | ▲ 완료(구조) | 헤더 시행일(확정 시 렌더) + 11항 개정 이력 표 |
| REQ-F-060 | 404 화면 | ▲ 완료 | `templates/errors/404.html` — 실제 404 + `noindex` + 헤더/푸터 유지 + 텍스트 링크 2종 |
| REQ-F-061 | SNS 링크 | 부분 | 푸터 — 계정 미확정(T-H)이라 섹션 미노출 |
| REQ-F-062·063 | 분석 도구 · 대체 수단 | 미착수 | `ANALYTICS_ID` 자리만 있음. 오픈 이후 설치 가능(Should) |
| REQ-F-064 | 콘텐츠 데이터 분리 | 완료(1차 정의) | `content/*.yml` + `seed_content`. ▲ 오시는 길 7행·지도 3키·보관 기간 라벨까지 같은 경로로 확장 |
| REQ-F-065 | 공용 오류 화면 (Could) | ▲ 완료 | `templates/errors/500.html` — 404 템플릿 재사용, **동적 데이터 비의존**(렌더 테스트로 고정) |

### 2.2 비기능 요구사항

| REQ ID | 요구사항 | 상태 | 구현 위치 |
|---|---|---|---|
| REQ-N-001·002 | 반응형 4구간 | 부분 | 각 페이지 CSS 에 `min-width` 4구간 작성. **실측(360/768/1280px)은 미수행** — 브라우저 실행 환경 없음(§6 #1) |
| REQ-N-004·005·007·015 | 성능·Lighthouse | 부분 | 폰트 self-host·해시·brotli·`immutable` 확인. **측정은 작업 11** |
| REQ-N-006·008·009 | 접근성 | ▲ 부분 | skip link · `main[tabindex=-1]` · h1 1개 · 랜드마크 · 44px 하한 · `label[for]` · `aria-describedby` · `aria-invalid` · **오류 요약 `role="alert"` + 항목 링크** · 결과 블록 `role="status"` + 포커스 이동 · **색 외 아이콘·텍스트 병기**. 자동 점검 도구 실행은 작업 13 |
| REQ-N-010~016 | SEO | ★★ 완료(값 제외) | **`apps/core/seo.py`(title·description 원본 — IA §6.2·§6.3 표)** · `templates/partials/meta.html`(출력·canonical·OG) · `apps/core/sitemaps.py`(색인 4화면) · `views.robots_txt`(Disallow 0건)  · `jsonld_localbusiness.html` + ★★ `jsonld_website.html`(메인). 회귀 테스트 `tests/test_seo_markup.py`. **도메인은 `SITE_BASE_URL` 교체만으로 전환된다**(§4 #12) |
| REQ-N-017·022 | HTTPS · 메일 발신 인증 | 미착수 | 운영 nginx·도메인 확정 후(§13) |
| REQ-N-018 | 비밀 정보 분리 | 완료 | `.env` 커밋 제외 확인, 운영 이미지 레이어 비밀 문자열 0건(1단계 확인 유지) |
| REQ-N-019 | 폼 악용 방지 **단일 구현** | ▲ 완료 | `apps/core/ratelimit.py`(10분 5회 / 1일 20회, 차단 지속·`Retry-After` 계산, **사용량 알림 3임계 + 1시간 합산**) · honeypot · 서버 검증 |
| REQ-N-020 | 개인정보 최소 수집 | ★★ 완료 | 저장 항목 3개 + `consent_at`·`phone_norm`(파생) + `source_ip_hash`(**원본 IP 미저장**). 로그에 이름·전화·본문 미기록(테스트로 고정). ★★ `Inquiry.PII_FIELDS`·`PII_POLICY_TERMS` ↔ `content/privacy.yml` **양방향 대조를 `tests/test_privacy_policy.py` 가 자동 검사** |
| REQ-N-023 | `[TBD]` 노출 금지 · 오픈 판정 | ▲ 완료(장치) | `/`·`/instructors`·`/location` 렌더 HTML 에 `TBD` **0건**(테스트). `/privacy` 는 1차 수용 기준상 `[TBD]` 를 보이며, **그 상태의 운영 배포는 `manage.py check_release` 가 종료 코드 1 로 막는다**(§3.2) |
| REQ-N-027 | 한국어 | 완료 | `LANGUAGE_CODE=ko-kr` · `<html lang="ko">` |
| REQ-N-028 | JS 비활성 시 정보 화면 동작 | ▲ 완료 | 전 화면이 **서버 렌더 HTML 단독으로 완성**된다. 모바일 메뉴·처리방침 목차·강사 경력 접기 모두 `<details>` 기반이라 JS 없이 동작. **curl(=JS 0) 로 전 화면 본문·링크 확인**(§4 #5) |
| REQ-N-029 | `<noscript>` 대체 안내 | ▲ 완료 | 전역 `partials/noscript.html` + **지도 영역·폼 전용 `<noscript>` 2곳** |
| REQ-N-030 | JS 없는 폼 제출 (Could) | ▲ **완료** | 서버 렌더 POST 가 표준 경로다. **curl 로 6종 응답을 전부 재현**했다(§4 #6~#11) — JS 경로와 서버 경로를 이중 구현하지 않았다 |
| REQ-N-031 | 헬스 엔드포인트·헬스체크 | 완료 | `/healthz` · compose 헬스체크 · `unless-stopped` |
| REQ-N-034 | 세 환경 동일 compose | 완료 | `compose.yaml` + override 1개 + 환경 변수 |
| REQ-N-036 | 기본값 거부 권한 레이어 | 완료 | `apps/core/access.py` — ▲ 1차 공개 4경로 등록, 미등록 경로는 거부 |
| REQ-N-037 | 알림 메일 체계 | ▲ 완료(1차 1종) | `apps/mailer/*` + `kind=inquiry_notify`·`rate_limit_alert`. 발송 로그·재시도·실패 기록 포함 |
| REQ-N-024 | 지도 화면 캡처 금지 | ▲ 완료 | 대체 영역은 CSS `repeating-linear-gradient` 격자다. **이미지 파일 0건** |
| REQ-N-032 | ★ DB 백업·무결성·회전·실패 알림 | ★ **완료(로컬 확인)** | `apps/core/management/commands/run_backup.py` — `pg_dump -Fc` → **`pg_restore --list` 무결성 확인** → 회전(일7/주4/월3, 라벨 제외 최근 3) → `core_jobrunlog` → 실패 시 `mailer_outbox(kind=backup_failed)`. 여유 공간 하한 `BACKUP_MIN_FREE_GB`. **복구는 `deploy/restore.sh`(가드 3중)**. 실행 증거 §4 #29~#36 |
| REQ-N-033 | ★ 배포·롤백 절차 | ★ **부분(스크립트 완료 · 서버 실행 미확인)** | `deploy/deploy.sh`(0 → 0.5 스케줄러 정지 → 1 라벨 백업 → 2 빌드 → 3 마이그레이션 → 4 기동 → 5 `/healthz` **앱 직접** 확인·다운타임 실측 → 6 실패 시 자동 롤백) · `deploy/rollback.sh`(이미지 보존 3중 전제 확인). **로컬에서는 0단계와 가드만 확인 가능** |
| REQ-N-037 | ★ 발송 실패·재시도 기록 | ★ 완료 | `send_outbox` 백오프 5단계 + `attempts`·`last_error`. **`QA_FAIL_INJECT=smtp` 로 실패 주입 확인**(§4 #37) |
| REQ-N-038 | ★ 보관 기간 경과 자동 파기 | ★ 완료(로컬 확인) | `purge_expired`(항목별 `RETENTION_DAYS` · 검증 시 `QA_RETENTION_MINUTES__<KEY>` 분 단위 단축 · `--dry-run` · `QA_FAIL_INJECT=purge`) · 스케줄 03:10 |
| REQ-N-039 | 운영 DB 접근 최소화·백업 위치 문서화 | 부분 | 제작 측 몫: **qa 조회 수단을 마스킹 읽기 전용 명령으로 한정**(`qa_show`, 해제 옵션 없음) · 백업 파일 경로·권한 규칙은 설계 §12.5.2. **권한자 목록은 devops 배포 계획서 소관** |
| REQ-N-040 | 스테이징 접근 제어 | 부분 | `deploy/nginx/yogapass-stg.conf.sample`(server 전체 `auth_basic` + IP 제한 · **예외 경로 0건**) + 앱 `FORCE_NOINDEX`. **로컬 더미 자격으로 선검증 가능**(설계 §13 #12). 실제 적용은 devops |
| REQ-N-031 (보강) | ★ 살아 있지만 응답 실패 인지 | ★ 완료 | `ping_health`(5분, **앱 직접 호출**) + `report_failures` 일일 요약 6항목 ⓐ~ⓕ. **요약 메일 Mailpit 수신 확인**(§4 #35) |

---

## 3. 화면별 구현 현황 (SCR ID ↔ 페이지 파일)

| SCR ID | 화면 | URL | 상태 | 구현 파일 | 디자인 명세와 차이 (사유) |
|---|---|---|---|---|---|
| — (공통) | 헤더·푸터·고정 바·스킵 링크·메타 | — | 완료 | `templates/base.html` · `partials/*` | ▲ `<link rel="icon">`(ico)·`apple-touch-icon`. ★ **`og:image` 계열 5줄이 붙는다** — 임시본 `og-image.png` 반영(§7) |
| SCR-001 | 메인 | `/` | 부분(뼈대) | `pages/home.html` | 문구·데이터 미수령으로 현재 4섹션만 렌더(v0.1과 동일) |
| SCR-002 | 요가 강사 소개 | `/instructors` | ▲ **완료(데이터 대기)** | `pages/instructors.html` · `css/pages/instructors.css` | 강사 0명이라 **현재는 CMP-026 빈 상태**만 보인다. 1·2·3·12명 레이아웃은 테스트로 검증했다. 경력 접기는 **항목 4개 이상**을 기준으로 접는다(디자인의 "3줄 초과"를 렌더 줄 수 대신 항목 수로 근사 — §6 #3) |
| SCR-003 | 오시는 길 + 문의 폼 | `/location`(`#contact`) | ▲ **완료(값 대기)** | `pages/location.html` · `css/pages/location.css` · `css/components/form.css` · `js/map.js` · `js/form.js` | 지도 임베드 URL·주소·전화가 `[TBD]` 라 **지도 버튼·정보 행·길찾기·주소 복사·전화 링크가 전부 미노출**이다(설계대로). 고정 바는 **S3 미노출**, 헤더 주 CTA 는 **H3 미노출** — 목업의 기본 상태와 같다 |
| SCR-006 | 개인정보 처리방침 | `/privacy` | ▲ **완료(본문 대기)** | `pages/privacy.html` · `css/pages/privacy.css` · `content/privacy.yml` | 이 화면에만 있는 패턴 2가지 구현 — ⓐ `≥1024px` 좌 240px sticky 목차 + 우 720px 본문 ⓑ `<768px` 표 → 카드 전환(`data-label`). **JS 없이 동작**(`<details>`) |
| SCR-008 | 404 | 없는 경로 | ▲ 완료 | `errors/404.html` · `css/pages/error.css` | 대형 "404" 장식(`aria-hidden`) + 버튼 2 + 텍스트 링크 2 + 전화 콜아웃(전화 확정 시) |
| SCR-009 | 공용 오류 | 5xx | ▲ 완료 | `errors/500.html` | 404 템플릿 재사용, `alert-triangle` 80px 로 심볼만 교체. 동적 데이터 비의존 |

### 3.1 문의 폼 응답 형태 — 설계 §9.6 표와 구현 대조 (P5 기대값)

| # | 상황 | 상태 코드 | 본문 | DB 저장 | 아웃박스 | 서버 기록 | 확인 방법 |
|---|---|---|---|---|---|---|---|
| ① | 정상 접수 | **200** | 성공 결과 블록(폼 교체) · `role="status"` · 포커스 이동 | **1건** | **1건**(`inquiry_notify`) | `INFO inquiry.created ref=<uuid>` | 자동 테스트 + curl(§4 #6) |
| ② | 서버 검증 실패 | **200** | 오류 요약(`role="alert"`) + 항목별 `aria-invalid`, **입력값 보존·토큰 유지** | 0건 | 0건 | `INFO inquiry.invalid fields=[name,phone,consent]` | 자동 테스트 + curl(§4 #8) |
| ③ | honeypot | **200** | **①과 동일 화면** | 0건 | 0건 | `WARNING inquiry.blocked reason=honeypot ip_hash=…` | 자동 테스트(동일성 비교) + curl(§4 #9) |
| ④ | 빈도 제한 초과 | **429** | 실패(일반) + `Retry-After` | 0건 | 0건(임계 초과 시 `rate_limit_alert` 1건) | `WARNING inquiry.blocked reason=rate_limit ip_hash=… scope=form` | 자동 테스트 + curl(§4 #10, `Retry-After: 95` 관측) |
| ⑤ | ★ 토큰 **재사용**(중복 제출) | **200** | **①과 동일 화면** | 0건(추가 없음) | 0건 | `INFO inquiry.duplicate token_state=used ref=…` | 자동 테스트 + curl(§4 #7) + **동시 5건 실행**(§4 #28) |
| ⑥ | 서버 오류 | **500** | `errors/500.html`, 스택 트레이스 미노출 | 0건(롤백) | 0건(롤백) | `ERROR` + 트레이스(개인정보 없음) | 자동 테스트(예외 주입) |
| ★ ⑦ | **토큰 만료·부재·변조** | **200** | **"시간이 지나 문의가 접수되지 않았습니다." + 폼 재렌더**(입력값 4항목 보존 · 새 토큰 발급) · `role="alert"` · 포커스 이동 | 0건 | 0건 | `INFO inquiry.expired token_state=expired\|missing\|invalid ref=none` | 자동 테스트 5건 + curl(§4 #27) |

- **설계와 다른 점 0건.** 구현이 표를 벗어난 곳은 없다(설계 §9.6 도 v0.4 에서 7행으로 함께 고쳤다).
- ★ **⑦은 PM 결정(2026-09-13)으로 ⑤에서 분리됐다.** v0.2까지는 만료도 "저장 없이 성공 화면"이어서 **24시간 이상 폼을 열어 둔 이용자의 문의가 조용히 버려질 수 있었다**(v0.2 §6 #7로 올렸던 항목). 이제 저장하지 않되 **다시 작성하도록 안내하고 입력값을 보존**한다. 재제출하면 정상 접수(①)된다 — 자동 테스트로 고정했다.
- ★ **동시 이중 제출**(같은 토큰 동시 5건)은 UNIQUE 충돌로 **500이 되고 있었다**. 충돌을 잡아 ⑤로 처리하도록 고쳤고, 재실행 결과 **200 × 5 · 저장 1건**이다(§4 #28).
- ③·⑤가 ①과 구분되는 유일한 증거는 **저장·발송 건수와 `key=value` 로그**다(설계 §9.6 · qa R2 #4). 로그 조회는 `docker compose … logs app`.
- ④의 차단 지속: 10분 창 초과 → 창 잔여 시간 / 1일 초과 → 익일 00:00(Asia/Seoul), 둘 다면 늦은 쪽. `core_ratelimitcounter` 에는 **한도를 넘긴 창의 행에만** `blocked_until` 이 기록된다.

### 3.2 REQ-N-023 ①(운영 배포 시 `[TBD]` 0건)과 REQ-F-050(1차에 `[TBD]` 표시)의 충돌 처리 — **판단 근거**

| 항목 | 내용 |
|---|---|
| 충돌 | REQ-F-050 1차 수용 기준은 `/privacy` 에서 **"미확정 항목은 `[TBD]`로 보인다"** 를 요구하고, 페이지 디자인 §5.3 도 같다. 반면 REQ-N-023 ①은 **운영 배포 시점** `[TBD]` 0건을 요구한다 |
| 해석 | 두 기준의 **시점이 다르다**. REQ-N-023 ①의 판정 시점은 "운영 배포 시점"(P7)이고, REQ-F-050 은 1차 구현 시점의 화면 요건이다. 따라서 **지금 `/privacy` 에 `[TBD]` 가 보이는 것은 요구사항 충족**이다 |
| 장치 | 그대로 두면 오픈 시점에 새어 나갈 수 있으므로 **`manage.py check_release`** 를 만들었다. `content/privacy.yml` 에 `status: pending` 이 하나라도 남으면 **종료 코드 1** 로 끝난다. `manage.py check`(운영·스테이징)에서는 같은 사실을 `content.W001` 경고로 낸다 |
| 왜 시스템 점검 Error 가 아닌가 | `migrate`·`collectstatic` 등 일반 명령이 함께 막혀 **배포 중간 단계에서 불투명하게 실패**한다. 배포 0단계에서 명시적으로 부르는 편이 devops 에게 낫다 |
| devops 에게 요청 | `deploy.sh` 0단계(사전 점검)에 **`python manage.py check_release`** 를 넣는다. 스테이징은 `--warn-only`. 작업 12에서 우리가 작성할 스크립트에 반영 예정 |

---

## 4. 로컬 빌드 · 실행 확인 (2026-09-13)

> **환경**: Windows 11 + Docker Desktop. `docker --version` = **24.0.2**, `docker compose version` = **v2.19.1**.
> 모든 명령은 `developer/site/` 에서 실행했다. 아래는 **이번 범위에서 실제로 실행한 명령과 출력 요지**다(1단계 28건은 v0.1 §4 참조).

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 1 | 마이그레이션 생성 | `… exec app python manage.py makemigrations inquiry` | `apps/inquiry/migrations/0001_initial.py` · `+ Create model Inquiry` |
| 2 | 마이그레이션 적용 | `… exec app python manage.py migrate --noinput` | `Applying inquiry.0001_initial... OK` |
| 3 | 시드 재적재 | `… exec app python manage.py seed_content` | `created=9 updated=11` (오시는 길·지도·보관 기간 키 9개 추가) |
| 4 | 화면 상태 코드(앱) | `curl -o /dev/null -w %{http_code}` × 5 | `/` 200 · `/instructors` 200 · `/location` 200 · `/privacy` 200 · `/nope` **404** |
| 5 | 화면 상태 코드(nginx 경유) | 같은 5경로 `:8080` | **동일**(200·200·200·200·404) — `proxy_intercept_errors off` 유지 |
| 6 | **폼 ① 정상 접수** | `curl -X POST /location` (CSRF+토큰 동봉) | `status=200` + "문의가 접수되었습니다." |
| 7 | **폼 ⑤ 토큰 재사용** | 같은 토큰으로 재전송 | `status=200` + 성공 화면, **DB 증가 없음** |
| 8 | **폼 ② 검증 실패** | 이름 공백·전화 `010-12`·동의 없음 | `status=200` + "입력 내용을 확인해 주세요" |
| 9 | **폼 ③ honeypot** | `company_ref=http://spam.example` | `status=200` + 성공 화면, **DB·아웃박스 증가 없음** |
| 10 | **폼 ④ 빈도 제한** | 같은 출처로 연속 제출(창 5회 초과) | `try1 200 / try2·3·4 **429**` + `Retry-After: 95` + "문의를 접수하지 못했습니다." |
| 11 | DB 건수 대조 | `psql -c "select count(*) from inquiry_inquiry" …` | 저장 2건(① + 제한 전 1건) / `mailer_outbox` `inquiry_notify` 2건 / `core_ratelimitcounter` `form`·`form_day` 각 1행 |
| 12 | **UTF-8 왕복** | 퍼센트 인코딩 UTF-8 본문 POST → `psql` | `name=테스트 · message=수강료 문의` — 정상 저장 |
| 13 | **nginx 경유 제출** | `:8080` 으로 ① 반복 | `status=200` + 성공 화면 (`TRUSTED_PROXY_COUNT` 경로 동작) |
| 14 | **알림 메일 도달** | `… exec app python manage.py send_outbox` → Mailpit API | `send_outbox sent=1 failed=0`, 수신함에 **`[문의 접수] 강남 요가패스`** 도착(본문에 접수 일시·이름·연락처·문의 내용) |
| 15 | 텍스트 압축 | `curl -I -H 'Accept-Encoding: gzip' :8080/{instructors,location,privacy}` | 3화면 모두 `Content-Encoding: gzip` (앱 직접 `:8000` 은 비압축 — 설계 §12.3 그대로) |
| 16 | 새 정적 자산 | `curl` 10개 경로(css 5·js 2·img 2·icon 1) | **전부 200** |
| 17 | 템플릿 주석 누출 점검 | `curl … | grep "{#"` | **0건**(아래 §6 #2 에 원인·조치) |
| 18 | 린트·포맷 | `ruff check .` / `ruff format --check .` | `All checks passed!` / `64 files already formatted` |
| 19 | 자동 테스트 | `manage.py test`(`config.settings.test`) | **Ran 48 tests … OK** |
| 20 | 운영 이미지 빌드 | `docker compose -f compose.yaml -f compose.prod.yaml build app` | **성공** (`collectstatic` 포함, 태그 `yogapass-app:0.1.0-dev`) |
| 21 | 운영 미리보기 기동 | prod 이미지 + gunicorn, `:8001` | 4화면 **200** · `/nope` **404** · `/healthz` **200** |
| 22 | 운영 정적 파이프라인 | `curl -I -H 'Accept-Encoding: br' /static/css/components/form.<hash>.css` | `200` + `Cache-Control: max-age=315360000, public, immutable` + `Content-Encoding: br` |
| 23 | 운영 설정 점검 | `manage.py check --deploy` (미리보기 컨테이너) | **오류 0건**. 경고는 `content.W001`(처리방침 미확정 — 의도) + HTTPS 관련 4건(`W004`·`W008`·`W012`·`W016` — **http 미리보기라 SSL 옵션을 끈 탓**이며 운영 `.env` 에서는 해제된다) |
| 24 | **배포 사전 점검** | `manage.py check_release` | `check_release FAILED pending=11 …` + **종료 코드 1** (의도된 동작) · `--warn-only` 는 0 |
| 25 | 파비콘·OG 래스터 | 아래 §7 (TKT-DSN-002) | `favicon.ico`(32+48) · `icon-192.png` · `icon-512.png` · `apple-touch-icon.png` 생성. **`og-image.png` 는 보류** |
| 26 | 이미지 내용 | `docker run --rm --entrypoint sh yogapass-app:0.1.0-dev -c "ls /app"` | `qa/`·`tests/`·`.env` 없음(구조적 제외 유지) |
| 27 | 정리 | 미리보기 컨테이너 중지 · 임시 env 파일 삭제 · 검증용 DB 행 삭제 | 로컬 DB 에 검증 데이터 0건 |

### ★ 4.1 3단계 실행 확인 (2026-09-13 · 20건)

> 아래는 **이번 판에서 직접 실행한 것**만 적었다. 명령은 전부 `developer/site/` 에서 실행했다.
> `C` = `docker compose -f compose.yaml -f compose.local.yaml`

**PM 결정 ① — 토큰 만료 처리**

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 27 | **⑦ 만료·부재 응답** | `curl -X POST /location` (CSRF 동봉 · `submit_token=` 빈 값) | **HTTP 200** + "시간이 지나 문의가 접수되지 않았습니다." + `id="contact-form"` 재렌더 + **입력값 4항목 보존**(`value="홍길동"`·전화·본문·`checked`) + 새 토큰. 로그 `inquiry.expired token_state=missing ref=none`. **저장 0건** |
| 28 | **⑤ 동시 이중 제출** | `$C exec app python qa/concurrency.py --url …/location --count 5 --same-token` | **수정 전: 200×2 + `500`×3** → 원인 = `submit_token` UNIQUE 충돌 미처리 → 수정 후 **200×5 · 저장 정확히 1건**(`qa_show inquiry --count-only` 로 전후 비교) |

**PM 결정 ② — OG 이미지 임시본**

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 29 | 임시본 생성 | 일회용 `alpine:3.20` 컨테이너 (`rsvg-convert` + `font-noto-cjk` + `optipng`) | `og-image.png` **1200×630 · 30,916 B**(상한 300KB) |
| 30 | **여백 실측**(눈이 아니라 측정) | 텍스트+로고만 렌더 → `magick text.png -trim` | 경계 **516×323 at (97,136)** → 좌 97 ≥ 96 · 우 613 ≤ 1104 → **좌우 96px 여백 안** |
| 31 | 태그·서빙 | `curl /` · `curl -I /static/img/og-image.png` | `og:image`·`:width`·`:height`·**`og:image:alt`**·`twitter:card` **5줄 자동 부착**, 파일 **200** |

**작업 11 — 폰트 폴백 메트릭 실측**

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 32 | 폰트 테이블 실측 | 일회용 `python:3.13-slim` + `fonttools`·`brotli` 로 `head`·`hhea`·`OS/2` 직접 읽기 | Pretendard(upm 2048 · asc 1950 · desc −494 · gap 0 · sxHeight 1086) / Malgun Gothic(upm 2048 · sxHeight 1050) → **size-adjust 103.43% · ascent 92.06% · descent 23.32% · line-gap 0%**. `static/css/fonts.css` 에 적용 |
| 33 | 정적 압축·캐시 | 운영 이미지 `staticfiles` 검사 + 헤더 | `.br` **82개** · `.gz` 82개. `fonts.css` **113,298 B → brotli 11,258 B**. `Cache-Control: max-age=315360000, public, immutable`(2단계 #22 유지) · nginx 경유 HTML `Content-Encoding: gzip` |

**작업 12 — 백업·복구·배포**

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 34 | 백업 정상·dry-run·라벨 | `$C exec scheduler python manage.py run_backup` / `--dry-run` / `--label pre-deploy` | `file=yogapass-local-20260913-1043.dump bytes=68389 elapsed=0.2s` · dry-run 은 여유 공간·회전 예정만 출력 · 라벨 파일 `…​.label-pre-deploy.dump` 생성 |
| 35 | **회전(일7/주4/월3)** | 합성 덤프 23개 배치 후 `run_backup` | **`rotated=12`** → 남은 12개 = 일 7 + 주(0906·0826·0819) + 월(0729) + 라벨 1. 계산과 실제 파일 목록 일치 |
| 36 | **락 충돌 시 라벨 백업 중단** | 다른 세션이 `pg_try_advisory_lock` 보유 상태에서 `run_backup --label pre-deploy` | **종료 코드 1** + `job.skipped … required=True` + `backup_failed` 알림 1건. **라벨 없는 실행은 `skipped` 로 종료 코드 0** — devops R2 #1 ②가 실제로 성립한다 |
| 37 | **백업 실패 주입** | `QA_TOOLS_ENABLED=1 QA_FAIL_INJECT=backup … run_backup` | 종료 코드 1 · `core_jobrunlog status=failed` · `mailer_outbox(kind=backup_failed)` 1건 · 로그 `QA_FAIL_INJECT: backup 주입됨` |
| 38 | **SMTP 실패 주입** | `QA_FAIL_INJECT=smtp … send_outbox` | `sent=0 failed=1` · `attempts=1` · `last_error` 기록 · **1분 뒤 재시도로 재스케줄**(`scheduled_at` +1분) |
| 39 | 일일 운영 요약 | `report_failures --dry-run` → 실제 발송 → Mailpit | 6항목 ⓐ~ⓕ 출력, 실패 항목 있을 때 제목 **`[점검필요]`**. Mailpit 수신 확인 |
| 40 | `/healthz` 5분 폴링 | `ping_health` | `url=http://app:8000/healthz status=200 ok=True` — **앱 직접 호출**(nginx 비경유) |
| 41 | **복구 리허설(로컬)** | `echo yes \| COMPOSE_FILES="… compose.local.yaml" sh deploy/restore.sh /backups/…dump` | 백업(11건) → 시드로 36건 → 복구 → **11건**. **`pre-restore` 자동 덤프 생성 확인** · `migrate --check` 통과 · `/healthz` 200 |
| 42 | 복구 **운영 가드** | `DJANGO_ENV=production` .env 로 `restore.sh` | `✗ 운영 환경입니다. … --i-know-this-is-production` 로 중단. **인라인 주석이 붙은 값에서도 가드가 걸리도록** 파서를 고쳤다(§6 #11) |
| 43 | **배포 0단계** | `APP_VERSION=… sh deploy/deploy.sh --dry-run` | 디스크 여유·현재 이미지·IRREVERSIBLE 0개·최근 백업 확인 후 **`check_release` 실패로 배포 중단** — REQ-N-023 ①이 실제로 배포를 막는다 |
| 44 | 롤백 가드 | `ROLLBACK_VERSION=9.9.9 sh deploy/rollback.sh` / 인자 없이 | `✗ 이미지 … 가 서버에 없습니다` / `✗ 되돌릴 이미지를 정할 수 없습니다`<br>⚠ **v0.4 정정(DEF-007)**: 뒤쪽 기재는 **`.deploy-rollback-image` 가 없을 때만** 맞다. 그 파일에 **태그 없는 이름**이 들어 있으면 v0.3 시점 스크립트는 거부하지 않고 **롤백을 실행했다.** 태그 가드를 추가해 지금은 거부한다 — 실행 확인은 §4.2 표 |
| 45 | 점검 화면 | `$C stop app` → `curl :8080/` | **HTTP 502 + 정적 점검 화면**(앱 없이 렌더) → `start app` 후 200 복귀 |
| 46 | 스크립트 문법 | `sh -n deploy/{deploy,rollback,restore}.sh` | 3건 모두 통과 |

**작업 13 — 검증 지원 도구·안전장치**

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 47 | `qa_show` | `qa_show inquiry` / `--count-only` / `--since` / `--format json` | 마스킹(`T******증` · `010-****-0000`) · ISO8601+KST 병기 · 건수 1줄 · **0건도 종료 코드 0** |
| 48 | `qa_mail_log` | `--kind backup_failed` · `--status queued` | `scheduled_at`(요청)·`sent_at`(발송) **두 시각 모두 출력** · 수신자 마스킹 |
| 49 | `qa_purge_test_data` | `--dry-run` → `--since … --confirm` | 테이블별 건수 출력(`inquiry 11 · outbox 6 · counter 4 · joblog 0`) · 총계 · `--since` 없으면 카운터·작업 로그 **제외** |
| 50 | `qa_pii_columns` | 실행 | `inquiry_inquiry` 6컬럼 · 목적 · **보관 기간 365일** · 마스킹 여부 — REQ-N-020 대조표로 바로 쓸 수 있다 |
| 51 | `seed_standard` | `--count 5 --refs 1000` | 고정 시드(재실행 시 신규 0) · **표시 번호 1,000건 중복 0건 · 인접 증가 50.8%**(난수 기대치 ≈50%) → REQ-N-R-010 ④ 근거 |
| 52 | `qa_session` | 토큰 미설정 / 불일치 / `--role member1` / 정상 | 앞의 셋 **종료 코드 2**, 정상 시 쿠키 이름·값·만료 출력(1차는 staff 만) |
| 53 | `qa/concurrency.py` | `--count 8` / `--count 5 --same-token` | 8건 동시 → **200×4 · 429×4**(빈도 제한 5회) / 같은 토큰 5건 → 저장 1건 |
| 54 | **항목별 독립 토글** | `QA_RATE_LIMIT_MODE=off` 로 앱 기동 | 빈도 제한만 꺼지고 다른 항목은 그대로. **이 상태에서 빈도 제한 테스트 3건이 의도대로 실패**하는 것을 보고 토글이 실제로 듣는 것을 확인했다(원복 후 53건 전건 통과) |
| 55 | **안전장치 ①** 마스터 스위치 | `QA_TOOLS_ENABLED` 없이 `qa_show` | `이 환경에서는 사용할 수 없습니다` + **종료 코드 2** |
| 56 | **안전장치 ②** 구조적 제외 | 운영 이미지 `ls /app/qa /app/tests /app/.env` · `find -name "qa_*.py"` | **전부 없음 · 0건** |
| 57 | **안전장치 ③** 기동 거부 | 운영 이미지 + `QA_TOOLS_ENABLED=1` (production / staging 각각) | `QA_TOOLS_ENABLED=1 과 DJANGO_ENV=production 은 함께 쓸 수 없습니다` / **`검증 도구(qa/)가 이 이미지에 없습니다`** — 둘 다 종료 코드 1 |
| 58 | **안전장치 ④** 명령 미등록 | 운영 이미지 `manage.py help \| grep -c "qa_\|seed_standard"` | **0** |
| 59 | **안전장치 ⑤** HTTP 노출 0 | `grep -c qa config/urls.py` | **0** |
| 60 | 린트·포맷·테스트 | `ruff check .` / `ruff format --check .` / `manage.py test` | `All checks passed!` / `85 files already formatted` / **Ran 53 tests … OK** |
| 61 | 운영 설정 점검 | `check --deploy` (운영 수준 보안 env 주입) | **3건** — HSTS `W005`·`W021`(설계 §9.5 가 도메인 확인 전 금지한 옵션) + `content.W001`(처리방침 미확정, 의도) |

**확인하지 않은 것(중요)**

| 항목 | 사유 |
|---|---|
| Lighthouse 4지표 측정 | 측정 조건(M-1)을 만족할 브라우저 실행 환경이 없다. **작업 11 잔여분 — P5 구간으로 넘긴다** |
| ★ **실제 배포·롤백**(스테이징·운영) | 스크립트는 완성했고 **0단계 점검·가드·문법까지 로컬에서 확인**했지만, 2~5단계(빌드·마이그레이션·기동·다운타임 실측)와 롤백은 **서버가 있어야 한다**. 설계 §12.6.1 일정(10-17)의 devops 협업 항목 |
| ★ **운영 nginx 샘플의 실제 적용** | `yogapass-prod.conf.sample`·`yogapass-stg.conf.sample` 은 **요청안**이다. 로컬 `local.conf` 로 같은 지시어 집합(`proxy_intercept_errors off`·gzip·`error_page`·`auth_basic` 더미)을 확인했을 뿐, 호스트 nginx 반영은 devops 소관 |
| ★ **폰트 폴백 메트릭 중 macOS 분** | `Apple SD Gothic Neo` 폰트 파일이 이 작업 환경에 없어 **x-height 를 실측하지 못했다.** 지어내지 않고 size-adjust 를 보정 없음(100%)으로 두고 행 높이만 맞췄다 → **designer 1회 확인 필요**(§6 #12) |
| ★ **오프사이트 백업·`.env` 보관 절차** | 설계 §12.5.4·§14.4 PM-3 의 PM 결정 대기 항목. 구현 범위 밖 |
| 실제 뷰포트 렌더(360/768/1024/1280px)·가로 스크롤·요소 겹침 | 위와 동일. CSS 구간은 작성했으나 **눈으로 확인하지 않았다** |
| 브라우저에서의 JS 동작(카운터·blur 검증·전송 중·지도 로드·주소 복사 토스트) | **코드 경로만 작성**했고 브라우저 실행 확인은 못 했다. 서버 경로(JS 없음)는 curl 로 전부 확인했다 |
| W3C HTML 검사 · 축 기반 접근성 자동 점검 | 도구 미설치. 작업 13·P5 |
| Safari·iOS 실기기 | 설계 §10.5 대로 P5 구간 |
| 지도 실제 임베드·길찾기 동작 | 지도 서비스·URL 미확정(T-E). 값이 오면 코드 변경 없이 동작한다 |

---

## ★★ 4.2 P5 1차 결함 수정 실행 확인 (2026-09-13 · DEF-001~010)

> **전제**: qa 1차 검증에서 발행된 **DEF-001~010 을 전건 수정**했다(미수정 0건). 아래는 **직접 실행한 명령과 결과**다.
> 실행 환경: 로컬 개발 스택 `:8000`(바인드 마운트) + **운영 미리보기 `:8001`**(prod 이미지 `yogapass-app:0.1.0-fix1`, `DJANGO_SETTINGS_MODULE=config.settings.production`, gunicorn + WhiteNoise).
> 운영 미리보기 기동: `sed` 로 만든 `.env.prodcheck`(`DJANGO_ENV=production` · `DJANGO_DEBUG=0` · `APP_PORT=8001` · `COMPOSE_PROFILES=` · `APP_VERSION=0.1.0-fix1`) + `ENV_FILE=.env.prodcheck docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck --env-file .env.prodcheck up -d --build` → `migrate` → `seed_content`.
> ⚠ **`.env` 를 그대로 복사하면 `DJANGO_SETTINGS_MODULE=config.settings.local` 이 함께 따라와 운영 미리보기가 local 설정으로 뜬다**(404 가 디버그 화면으로 나온다). `.env.prodcheck` 에서 이 줄도 `config.settings.production` 으로 바꿔야 한다 — qa 가 미리보기를 다시 만들 때 주의.

### 4.2.1 결함별 확인

| DEF | 확인 명령 | 결과 |
|---|---|---|
| **001** | `curl -s :8001/{,instructors,location,privacy,nope} \| grep -oE '<title>…\|<meta name="description"…'` | **5화면 title 전건 IA §6.2 표와 일치**(`강남 요가패스 \| 강남 요가 스튜디오·수업 안내` 외 4건), **4화면 description 전건 IA §6.3 표와 문자열 일치 · 길이 62·69·57·56자**(50~90 충족). `noindex` 화면 description 없음 |
| **001 ④** | `curl -s :8001/ \| grep -o '"@type": "[^"]*"'` | `HealthAndBeautyBusiness` + **`WebSite`** 2건 (오시는 길은 `HealthAndBeautyBusiness` 1건) |
| **002** | `java -jar vnu.jar --format gnu --skip-non-html html/`(5화면 저장본) | **error 0건**(종전 5건 → 0). 남은 출력은 `instructors.html` 의 `info warning: Section lacks heading` 1줄뿐 — 오류 아님(§4.3 ④) |
| **002** | `curl … \| grep -oE ' id="[^"]+"' \| sort \| uniq -d` | 5화면 전건 **중복 id 0건** |
| **003** | `curl … \| grep -c 'style="'` (5화면) | **전건 0** (종전 메인 2건) |
| **003** | Chrome 헤드리스 콘솔 수집 | 4화면 × 4뷰포트 **콘솔 오류 0건**. `/nope` 만 1건 — **자기 응답 코드 404 를 브라우저가 기록한 것**(REQ-F-060 이 요구하는 동작. 스크립트·CSP 오류 아님) |
| **004** | `BASE=http://localhost:8001 NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js` | 5화면 × **320/360/768/1280px 가로 스크롤 0건**(320px `scrollWidth == clientWidth == 320`). 헤더 구성도 명세대로 — `<768` CTA 없음 / `768~1279` **CTA 없음(G-8)** / `≥1280` CTA 표시 + 전화 아이콘 숨김 |
| **004(추가)** | 같은 도구의 헤더 높이 재측정 | 65 → 65 · 69 → 69 · 73 → 73px (**되먹임 증가 없음**. 수정 전에는 로드마다 106·110·118px 로 자랐다) |
| **005** | Chrome 헤드리스 실측(360px) | 헤더 로고 **그래픽 140×32 / 링크 140×44** · 푸터 링크 6종 **328×44** · 저작권 **14px**(`© 2026 강남 요가패스`) · GNB 항목 최소 **44×44**(37→44) |
| **006** | 같은 도구의 `body` 하단 여백 | `/location`(전화 `[TBD]`) 320·360·768px **고정 바 없음 + `padding-bottom: 0px`** / 다른 4화면 77px(바 있음) / 1280px 0px |
| **006** | 전화 확정 시드 후 재측정 | `/location` 에 고정 바 노출 + 여백 **77px**, 320px 가로 스크롤 없음 → **확인 후 값 원복**(`phone` = null · `is_published: false`) |
| **007** | `sh deploy/rollback.sh` 8가지 상황(태그 없음·빈 파일·`latest`·대상 없음·없는 버전·정상 태그 `--dry-run`·비대화형 확인 없음·`deploy.sh --dry-run`) | **8건 전부 의도대로**(DEF-007 티켓 표에 전문 기재). 실행 전후 `docker ps` 동일 — **스택 변경 0건**, `.deploy-rollback-image` 잔존 0 |
| **008** | 오프셋 컨테이너(+25시간) 로 만료 토큰 POST | `HTTP 200` + "시간이 지나 문의가 접수되지 않았습니다." + 폼 재렌더 + **새 토큰** · 저장 **0건**(`qa_show inquiry --count-only` = 0) · 로그 **`inquiry.expired token_state=expired ref=none`** → **§9.6 ⑦ `expired` 판정 가능** |
| **009** | `manage.py test` + `qa_pii_columns` ↔ `privacy.yml` 대조 | 개인정보 컬럼 **6개 전부 방침 표에 존재**(누락 0). 자동 테스트가 매번 대조 |
| **010** | `docker run --rm --entrypoint sh yogapass-app:0.1.0-fix1 -c 'ls -la /app/static/img/'` · `find /app -name "*TEMP*"` | `/app/static/img/` **11개(TEMP 파일 없음)** · `find` **0건** · `/app` 루트에서 `Dockerfile`·`compose*.yaml` 도 사라짐(`qa/`·`tests/`·`.env` 없음은 종전 유지) |

### 4.2.2 전체 회귀 (수정 후)

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 62 | 자동 테스트 | `manage.py test`(`config.settings.test`) | **Ran 80 tests … OK** (53 → 80, **+27**) |
| 63 | 린트·포맷 | `ruff check .` / `ruff format --check .` | `All checks passed!` / `88 files already formatted` |
| 64 | 화면 상태 코드(운영 미리보기) | `curl -o /dev/null -w %{http_code}` × 6 | `/` 200 · `/instructors` 200 · `/location` 200 · `/privacy` 200 · `/nope` **404**(SCR-008 화면) · `/healthz` 200 |
| 65 | 운영 이미지 빌드 | `… -f compose.prod.yaml build app`(`--build` 동반 기동) | **성공** — `yogapass-app:0.1.0-fix1` |
| 66 | 운영 설정 점검 | `manage.py check --deploy`(미리보기) | **오류 0건** · 경고 5건 = `content.W001`(처리방침 미확정, 의도) + HTTPS 관련 4건(http 미리보기라 SSL 옵션 해제 — 종전과 동일) |
| 67 | 배포 차단 점검 | `manage.py check_release` | **종료 코드 1 · `pending=11`**(의도된 동작 유지 — 처리방침 확정 전 배포 차단) |
| 68 | CSP 헤더 | `curl -I :8001/` | `default-src 'self'; script-src 'self'; style-src 'self'; …` 종전과 동일 |
| 69 | OG 이미지 | `curl -o /dev/null -w %{http_code} <og:image 경로>` | **200**(해시 파일명). 절대 URL 의 호스트는 `SITE_BASE_URL` 값이라 미리보기 포트와 다름 — 설정 문제 아님 |

### 4.2.3 새로 추가한 회귀 테스트 (27건)

| 파일 | 건수 | 막는 결함 |
|---|---|---|
| `tests/test_seo_markup.py` | 21 | **DEF-001**(IA 표 문자열 일치·길이·유일성·키워드·**DB 값 무관**·JSON-LD) · **DEF-002**(중복 id·접근 이름) · **DEF-003**(인라인 style 0) · **DEF-006**(고정 바 유무 ↔ 하단 여백) · **DEF-010**(static 작업 파일·`.dockerignore`) *(v0.5에서 `ViewportMetaTests` 5건이 더 붙어 26건이 된다 — §4.4)* |
| `tests/test_privacy_policy.py` | 3 | **DEF-009**(PII 컬럼 ↔ 처리방침 표 양방향 대조) |
| `tests/test_inquiry.py`(추가분) | 3 | **DEF-008**(오프셋으로 만료 유발 / TTL 안이면 정상 / **마스터 스위치 꺼지면 무영향**) |
| `tests/browser/layout-check.js`(신규 도구) | — | **DEF-003·004·005·006** — 5화면 × 4뷰포트에서 가로 스크롤·터치 타깃·글꼴 하한·인라인 style·콘솔 오류·헤더 높이 증가·고정 바 대비 여백을 한 번에 측정(위반 시 종료 코드 1) |

> `layout-check.js` 는 **puppeteer-core·Chrome 이 필요**하다(저장소에 두지 않는다 — 검증 도구는 qa 소관).
> 실행: `BASE=http://localhost:8001 NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js`

---

## ★★ 4.3 확인 요청 (designer · planner · qa)

| # | 항목 | 내용 | 요청 대상 |
|---|---|---|---|
| ① | **로고 클릭 영역 44px** | DEF-005 의 qa 권고 ⓐ 를 적용했다 — **로고 그래픽은 32px 그대로**, 링크에 `min-height: 44px` 만 걸어 클릭 영역을 140×44 로 만들었다. 디자인 시스템 §헤더의 "로고 높이 32px" 와 충돌하지 않는다고 판단했지만 **명세 해석이므로 확인이 필요**하다 | designer · planner |
| ② | **푸터 링크 행 높이 32 → 44px** | 터치 타깃 하한을 맞추느라 푸터 링크 6종의 행 높이가 커졌다(1열 구간 푸터 세로 +약 72px). 글자 크기·색·정렬은 그대로다. **인접 간격은 0px**(맞닿음) — 44px 이상 타깃이 맞닿는 구성을 허용할지 판단이 필요하다 | designer · qa |
| ③ | **GNB 항목 최소 폭 44px** | `768px` 이상에서 "홈"이 37×44px 이라 가로 하한 미달이었다(qa 1차는 360px 만 실측). 패딩 토큰 `--gnb-item-pad-x`(12px — IA §2.1 GNB 폭 계산 전제)는 **건드리지 않고** `min-width: 44px` 만 걸었다 → GNB 전체 폭 284 → **291px**. IA §2.1 의 폭 전제와 어긋나지 않는지 확인 필요 | designer · planner |
| ④ | **`instructors` 의 `Section lacks heading`** | vnu **오류가 아니라 info warning** 이라 REQ-N-016 판정에 영향이 없고, `<section>` → `<div>` 전환은 랜드마크 구성 변경이라 이번 수정에 넣지 않았다. 전환할지 제목을 넣을지 정해 주면 반영하겠다 | designer |
| ⑤ | **표시 상호를 "강남 요가패스" 로 통일** | DEF-001 수정에서 `content/site.yml` 의 `name` 을 `요가패스` → **`강남 요가패스`** 로 맞췄다(IA §6.2 브랜드·`SITE_NAME` 기본값과 동일). 화면 노출 지점: 헤더 로고 `aria-label`, 푸터 저작권, 메인 h1 폴백, 알림 메일 제목. **정식 상호(T-G)가 확정되면 함께 교체**한다 | planner · PM |
| ⑥ | **헤더 높이 토큰 분리** | `viewport.js` 가 실측값을 쓰는 `--header-h` 와 헤더 행의 `min-height` 가 같은 변수를 써서 헤더가 1px 씩 계속 자라고 있었다(측정 중 64 → 118px). `min-height` 전용 **정적 토큰 `--header-min-h`(64/68/72px — 값은 디자인 시스템 그대로)** 를 분리했다. 토큰 **이름이 추가**된 변경이라 알린다 | designer |

---

## ★★★ 4.4 P5 2차 결함 수정 실행 확인 (2026-09-13 · DEF-011)

> **범위**: qa 2차 검증에서 발행된 **DEF-011(Major) 1건**과, 같은 티켓에 딸려온 **qa 인계 메모 1건**(`layout-check.js` 의 `/nope` 자기 404 계수).
> 실행 환경: 로컬 개발 스택 `:8000`(바인드 마운트) + **운영 미리보기 `:8001`** — prod 이미지 **`yogapass-app:0.1.0-fix2`**, `DJANGO_SETTINGS_MODULE=config.settings.production`, `DJANGO_DEBUG=0`, gunicorn + WhiteNoise.
> 미리보기 기동: `.env.prodcheck`(`.env` 를 `sed` 로 변형 — `DJANGO_ENV=production` · `DJANGO_DEBUG=0` · **`DJANGO_SETTINGS_MODULE=config.settings.production`** · `APP_PORT=8001` · `COMPOSE_PROFILES=` · `APP_VERSION=0.1.0-fix2` · `SITE_BASE_URL=http://localhost:8001`)
> → `ENV_FILE=.env.prodcheck docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck --env-file .env.prodcheck up -d --build` → `migrate` → `seed_content`.
> ⚠ **§4.2 의 주의 그대로 재현됐다** — `DJANGO_SETTINGS_MODULE` 을 바꾸지 않으면 미리보기가 local 설정으로 떠서 `/nope` 가 **Django 디버그 404 화면**(SCR-008 아님)으로 나온다. 처음 기동에서 실제로 그렇게 떴고, 그 줄을 고쳐 다시 올린 뒤 판정했다.

### 4.4.1 원인

| 층 | 사실 |
|---|---|
| 직접 원인 | `templates/base.html` 8행의 viewport `content` 에 **`interactive-widget=resizes-content` 가 없었다.** 전 화면이 이 파일을 상속하므로 **5화면 전건 누락**이었다 |
| 근본 원인 | **기술 설계서에 ①이 적혀 있지 않았다.** G-9 는 3단 구현인데 v0.5까지 설계서는 ②를 §10.5(WebKit 검증 수단)에, ③을 §9.1 토큰 계산식 근처에만 두고 **①(메타 문자열)은 어느 절에도 없었다**. 디자인 문서(`design/03_page-design.md` §2.5)에만 있는 명세를 구현이 놓쳤고, **1차 TC-009 도 폴백 스크립트와 `--fixed-bar-h` 만 봐서 함께 놓쳤다** |
| 왜 관측되지 않았나 | 유일한 폼 화면 `/location` 이 **S3(자기 참조 + 대표 전화 `[TBD]`)라 고정 바를 렌더하지 않는다.** 가릴 바가 없어 현재 빌드에서는 겹침이 발생하지 않는다 — **대표 전화(T-E) 확정 즉시 S2 로 바뀌며 실제 결함이 된다**(티켓 완화 정황과 동일 판단) |

### 4.4.2 조치

| # | 파일 | 내용 |
|---|---|---|
| 1 | `developer/site/templates/base.html` | viewport 메타를 **`width=device-width, initial-scale=1, interactive-widget=resizes-content`** 로 교체 + 근거 주석(`{% comment %}` — `{# … #}` 는 렌더에 노출된다, §6 #2) |
| 2 | `developer/site/templates/errors/maintenance.html` | base 를 **상속하지 않는 유일한 화면**이라 같은 문자열로 맞췄다. 점검 안내는 1차 공개 화면이 아니지만 "전 화면 누락 0건"을 파일 단위로 성립시킨다 |
| 3 | `developer/site/static/js/viewport.js` | 코드 변경 없음. **머리 주석만** 고쳤다 — 이 파일은 G-9 3단 중 **②만** 담당하고, `isWebKit` 가드는 **①이 있는 전제에서만 옳다**는 것을 남겼다(①을 지우면 Chromium 무방비) |
| 4 | `developer/04_tech-design.md` **v0.6** | **§9.1에 G-9 3단 구현 표 신설** — 단별 구현 위치·정본 문자열·담당 브라우저·판정 수단. 설계 공백(근본 원인)을 메운 것이 이번 수정의 본체다 |
| 5 | `developer/site/tests/test_seo_markup.py` | 회귀 테스트 **5건**(`ViewportMetaTests`) |
| 6 | `developer/site/tests/browser/layout-check.js` | 런타임 DOM 점검 ⑥ 추가 + **qa 인계 건**(자기 404 계수) 수정 |

### 4.4.3 실행 확인

| # | 항목 | 명령 | 결과 |
|---|---|---|---|
| 70 | **응답 HTML 5화면**(운영 미리보기) | `for p in / /instructors /location /privacy /nope; do curl -s -w '%{http_code}' :8001$p \| grep -oE '<meta name="viewport" content="[^"]*">'; done` | **5/5 모두** `width=device-width, initial-scale=1, interactive-widget=resizes-content` · 상태 코드 `200 200 200 200 **404**`(`/nope` 는 SCR-008 화면) — **누락 0건** |
| 71 | **런타임 DOM 5화면 × 4뷰포트** | `BASE=http://localhost:8001 NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js` | **20행 전부 `G-9메타: 있음`** · **✓ 위반 0건**(종료 코드 0). 가로 스크롤·터치 타깃·글꼴·인라인 style·헤더 높이·고정 바 여백도 종전과 동일하게 0건 |
| 72 | **G-9 ②③ 번들 잔존** | `curl -s :8001/static/js/viewport.<hash>.js \| grep -c 'visualViewport\|data-vk-fallback'` · `curl -s :8001/static/css/tokens.<hash>.css \| grep -oE 'scroll-padding-bottom:[^;]*;'` | `visualViewport` **2건** · `data-vk-fallback` **2건** · `scroll-padding-bottom: var(--scroll-pad-bottom);` — **③까지 3단 전부 번들에 존재**(REQ-F-003 ⑤-1 후단) |
| 73 | 회귀 테스트 **음성 확인** | 메타에서 토큰만 뺀 상태로 `manage.py test tests.test_seo_markup.ViewportMetaTests` | **FAIL 3건** — `viewport 메타에 G-9 ① 토큰이 없는 화면: ['/', '/instructors', '/location', '/privacy', '/nope']` 로 **5화면을 모아서 보고**. 되돌린 뒤 재실행 **5건 OK** → 테스트가 실제로 이 결함을 잡는다 |
| 74 | 자동 테스트 전체 | `manage.py test`(`config.settings.test`) | **Ran 85 tests … OK** (80 → 85, **+5**) |
| 75 | 린트·포맷 | `ruff check .` / `ruff format --check .` | `All checks passed!` / `88 files already formatted` |
| 76 | 운영 이미지 빌드 | `… -f compose.prod.yaml up -d --build` | **성공** — `yogapass-app:0.1.0-fix2`, app·db·scheduler 기동 |

### 4.4.4 함께 처리한 qa 인계 건 — `layout-check.js` 의 `/nope` 자기 404

| 항목 | 내용 |
|---|---|
| 문제 | `/nope` 는 **사양상 404 로 응답**하는 화면(SCR-008)인데, 브라우저가 그 응답 자체를 `Failed to load resource: … status of 404` 로 콘솔에 찍는다. 도구가 이를 "콘솔 오류"로 세어 **위반 2건**(320·360px)으로 판정했다 — 구현 결함이 아니다 |
| 조치 | 콘솔 오류를 `{text, url}` 로 모으고, **문서 응답이 404 이고 메시지의 출처 URL 이 문서 URL 과 같은 것만** 제외한다. 제외 건수는 출력에 `(자기404 n건 제외)` 로 남긴다 |
| 왜 "1건"이 아니라 전건 제외인가 | 도구는 ⑤(헤더 높이 재측정)에서 뷰포트를 다시 설정하는데, **`isMobile` 이 바뀌면 puppeteer 가 페이지를 다시 읽는다.** 그래서 320·360px 에서는 같은 자기 404 가 **2번** 찍힌다(실측: 320·360px `자기404 2건`, 768·1280px `1건`). "첫 1건만 제외" 로는 남은 1건이 위반으로 남았다 |
| 안전장치 | 판정은 **자르지 않은 원문**으로 한다(표시만 100자로 자른다 — 잘린 문자열에서 "404" 가 사라지면 판정이 바뀐다). **하위 리소스의 404 는 그대로 위반**이다 — 음성 확인: `/nope` 에 없는 이미지(`/static/img/missing-on-purpose.png`)를 주입하니 **자기404 1건 제외 · 남은 위반 1건**(주입한 이미지)으로 판정됐다 |
| 결과 | 수정 후 전체 실행 **✓ 위반 0건 · 종료 코드 0** |

> **이번 수정에서 드러난 그 밖의 불일치 — 처리 1건 · 미처리 0건**
> - 처리: `templates/errors/maintenance.html` 이 **base 를 상속하지 않아 메타를 따로 들고 있었다**(위 표 #2). 같은 누락이 다시 생길 수 있어 `ViewportMetaTests.test_standalone_error_templates_also_carry_the_token` 이 **viewport 메타를 직접 선언하는 템플릿 전부**를 훑도록 했다 — 독립 화면이 늘어나도 자동으로 대상이 된다.
> - **처리하지 않은 것**: `viewport.js` 의 `if (!isWebKit) return;` **가드는 그대로 두었다.** ①이 들어온 지금 Chromium 경로는 메타가 담당하고, 폴백을 Chromium 에도 켜면 **메타에 의한 리사이즈와 `translateY` 보정이 겹쳐 고정 바가 두 번 밀린다.** 설계 §9.1 표의 "담당 브라우저" 란에 이 판단을 적었다.

---

## 5. 자체 테스트

| 파일 | 건수 | 내용 |
|---|---|---|
| `tests/test_smoke.py` | 9 | URL·상태 코드·공통 레이아웃·CTA 상태(H1~H3/S1~S3)·식별자 규칙·보안 헤더 |
| ▲ `tests/test_pages.py` | 19 | 화면 공통 규칙(h1 1개·랜드마크·canonical·OG·sitemap·robots·**템플릿 주석 누출 0**) · SCR-002 인원 경계값 · 경력 접기 · SCR-006 목차 11항목·표 라벨·`<details>` · 404·500 · 전화 확정 전후 렌더 · **배포 사전 점검** |
| ★ `tests/test_inquiry.py` | 25 | **응답 형태 7종 전건** + 경계값 + 아웃박스 본문 + 사용량 알림 + honeypot 화면 동일성 + 필수 표시 3중 + 동의 문구 + `<noscript>` + 지도 버튼 조건부 렌더 + ★ **만료 5건**(부재·만료·변조·재제출 성공·검증 우선) + ★ **동시 이중 제출 1건** |
| ★★ `tests/test_seo_markup.py` | 21 | **P5 결함 회귀** — title·description 이 IA 표와 문자열 일치·50~90자·유일·키워드·**DB 값 무관** / 구조화 데이터 2종 / **중복 id 0·접근 이름** / **인라인 style 0** / 고정 바 유무 ↔ 하단 여백 / static 작업 파일 0 |
| ★★ `tests/test_privacy_policy.py` | 3 | **P5 결함 회귀** — 개인정보 컬럼(`PII_FIELDS`) ↔ 처리방침 수집 항목 표 양방향 대조 |
| ★★★ `tests/test_seo_markup.py` `ViewportMetaTests`(추가분) | 5 | **DEF-011 회귀** — 전 화면 viewport 메타에 G-9 ① 토큰 존재(누락 0건) · 문자열 정본 일치 · 화면당 메타 1개 · 독립 오류 템플릿도 동일 · 번들에 ②(`visualViewport`·`data-vk-fallback`)·③(`scroll-padding-bottom`) 존재 |
| **합계** | ★★★ **85** | `manage.py test` **전건 통과** (v0.3 53건 → v0.4 80건 → **85건**, DEF-011 회귀 5건 추가) |

- 린트: `ruff check .` 통과(규칙 `E,F,W,I,UP,B,DJ,S`).
- 정적 자산 크기(참고): 페이지 CSS brotli 합계 **약 12KB**, 폰트 선언 `fonts.css` brotli **10.3KB**, JS 합계 **13KB(비압축, 4파일)**. 최종 측정은 작업 11.

---

## 6. 알려진 이슈 · 제약

| # | 내용 | 영향 | 계획 |
|---|---|---|---|
| 1 | 브라우저 실행 확인(반응형·JS 동작·Lighthouse)이 **전부 미수행** | 반응형·성능·클라이언트 상호작용 **판정 불가** | 작업 11 + P5. 이번 보고서에서 "완료"로 적지 않았다 |
| 2 | ▲ **(수정 완료)** Django 템플릿의 여러 줄 `{# … #}` 주석이 **HTML 로 그대로 출력되고 있었다**(1단계부터 전 화면) | 렌더 HTML 에 내부 주석·설계 근거가 노출. 유효성·용량·정보 노출 문제 | 전 템플릿을 `{% comment %}` 로 교체하고 **재발 방지 테스트**(`test_no_page_leaks_template_comments`)를 넣었다. README §9 에도 적었다 |
| 3 | ▲ 강사 경력 접기 기준을 디자인의 **"3줄 초과"** 대신 **"항목 4개 이상"** 으로 구현 | 실제 줄 수는 카드 폭·글자 길이에 따라 달라진다 | 줄 수 판정은 JS 실측이 필요해 **JS 비활성에서 동작하지 않는다**. 디자인 검토에서 designer 확인을 받는다 |
| 4 | ▲ 앵커 칩·처리방침 목차의 **현재 위치(`aria-current`) 표시 미구현** | 디자인 명세의 선택 항목(§4.1·§5.4 "JS, 선택") | 스크롤 스파이 JS 가 필요하다. 작업 11 이후 여유가 있으면 추가 |
| 5 | ▲ CMP-029 "맨 위로"(Could) 미구현 | 긴 문서(`/privacy`) 편의 저하 | Could 항목. 작업 11 이후 판단 |
| 6 | ★ **(해소)** `og-image.png` 미생성 | — | **PM 결정에 따라 임시본 생성·태그 부착 완료**(§7). 정식본은 같은 경로에 덮어쓰면 코드 변경 0 |
| 7 | ★ **(해소)** `submit_token` 만료 시 조용한 성공 | — | **PM 결정으로 ⑦(재작성 안내)로 분리**. 설계 §9.6 v0.4 · 구현 · 테스트 5건 모두 반영 |
| 8 | ★ **(부분 해소)** 폰트 폴백 메트릭 · nginx 운영 샘플 | — | 폴백 메트릭 **Windows 실측 적용**(macOS 분은 #12) · nginx **운영·스테이징 샘플 2종 작성**. `requirements.lock` 은 **미도입**(아래 #10) |
| ★ 10 | `requirements.lock`(해시 고정) **미도입** | 같은 태그를 다시 빌드할 때 하위 의존성 패치가 달라질 수 있다 | `requirements.txt` 는 직접 의존성 5개를 **패치까지 고정**하고 있어 1차 재현성은 확보돼 있다. 전이 의존성까지 고정하려면 `pip-compile` 도구가 필요하다 — devops 와 도입 여부를 합의한 뒤 넣는다 |
| ★ 11 | `.env` **인라인 주석**이 파서를 깨뜨리는 문제 | `docker run --env-file` 은 `TRUSTED_PROXY_COUNT=0  # …` 을 값으로 읽어 **기동이 깨졌다**. 더 위험한 것은 **셸 파서**였다 — `restore.sh` 가 `DJANGO_ENV=production  # …` 을 `production` 과 다르게 읽어 **운영 복구 가드가 통과할 수 있었다** | `.env.example` 의 인라인 주석을 **전부 값 줄 위로 옮기고** 머리에 금지 문구를 넣었다. `restore.sh` 파서도 주석·따옴표·공백을 떼어내도록 고치고 **주석이 붙은 상태로 가드가 걸리는 것을 실행 확인**(§4 #42) |
| ★ 12 | 폰트 폴백 메트릭 중 **macOS(Apple SD Gothic Neo) 미실측** | macOS Safari 에서 폴백 표시 시 글자 크기 보정이 없다(행 높이는 맞다) | 폰트 파일이 없어 **지어내지 않았다.** `@font-face` 를 플랫폼별 2벌로 선언해 두었으므로 designer 가 실측값을 주면 **숫자 1개(size-adjust)만 교체**하면 된다 |
| ★ 13 | 복구 직후 `core_jobrunlog` 에 **`running` 상태로 남는 백업 기록 1건** | 복구 대상 덤프는 **자기 자신의 실행 중 상태를 담고 있다**(백업 도중 덤프를 뜬 것이므로). 복구 직후 일일 요약이 "최근 성공 기록 없음"으로 보일 수 있다 | 데이터 손상이 아니라 표시 문제이며, 다음 03:00 백업 1회로 정상화된다. **P8 운영 가이드의 "복구 직후 확인 사항"에 적는다** |
| 9 | 지도·주소·전화·강사·처리방침 본문이 전부 `[TBD]` | **현재 화면 대부분이 "값 없음" 상태로 보인다** — 디자인 검토 시 목업과 달라 보인다 | 코드 변경 없이 `content/*.yml` 수정(+`seed_content`)으로 반영된다. 수령 일정은 pmo 추적(T-C·T-E·T-F·T-G) |

---

## 7. TKT-DSN-002 (파비콘·OG 래스터) 처리 결과

| 산출물 | 결과 | 크기 |
|---|---|---|
| `favicon.ico` (32+48 멀티사이즈) | ✅ 생성 | 13.9KB |
| `icon-192.png` | ✅ 생성 | 3.1KB |
| `icon-512.png` | ✅ 생성 | 8.8KB |
| `apple-touch-icon.png` (180) | ✅ 생성 | 3.0KB |
| `og-image.png` (1200×630) | ★ ⚠ **임시본 생성**(2026-09-13 · PM 결정) | 30.9KB |

- 변환은 **일회용 컨테이너**에서 했다(틀·프로젝트에 도구를 설치하지 않았다):
  `docker run --rm -v …:/in -v …:/out alpine:3.20 sh -c "apk add --no-cache rsvg-convert imagemagick && rsvg-convert -w 192 -h 192 /in/icon-master-512.svg -o /out/icon-192.png … && magick /tmp/f32.png /tmp/f48.png /out/favicon.ico"`
- 산출물 위치: `developer/site/static/img/`. `base.html` 에 `<link rel="icon" …ico>` · `<link rel="apple-touch-icon" …>` 를 추가했다.
- ★ **`og-image.png` 임시본 (PM 결정 2026-09-13)**: 아래 보류 사유는 그대로지만, PM 결정에 따라 **변환 환경에서 쓸 수 있는 폰트(Noto Sans CJK KR)로 렌더한 임시본**을 넣었다. **임시인 것은 폰트(자간·글자 폭)뿐이고 레이아웃·색·문구·좌표는 원본 그대로**다.
  - 티켓이 경고한 **여백 초과는 실측으로 배제**했다 — 텍스트+로고만 렌더해 `magick -trim` 으로 잰 경계가 **516×323 at (97,136)** 이라 좌우 96px 여백 안에 들어간다(§4 #30).
  - **임시본 표시 4곳**: 작업 사본 파일명 `og-image.TEMP-source.svg` · 그 파일 머리 주석 · `og-image.png` 의 PNG `tEXt Comment` · 인계 메모 `static/img/SOURCES.md`.
    ★★ **v0.4(DEF-010) 변경**: 작업 사본을 **`assets-work/og-image.TEMP-source.svg` 로 옮겼다**(운영 이미지·`collectstatic` 대상에서 제외). 표시 4곳은 그대로이며 경로만 바뀌었다.
  - **교체 시 코드 변경 0** — 같은 경로에 덮어쓰면 된다. 절차는 `static/img/SOURCES.md` 와 티켓 처리 결과 ⑤에 적었다.
- **원래의 보류 사유(유지)**: 원본 `og-image.svg` 는 `font-family: Pretendard` 로 조판돼 있고, 우리가 가진 Pretendard 는 **`unicode-range` 분할 woff2 서브셋**뿐이라 fontconfig 가 로드하지 못한다. 폴백 폰트로 구우면 글자 폭이 달라져 **좌우 96px 여백을 넘을 수 있다**(티켓이 경고한 바로 그 상황)고 판단했고, 육안 확인 수단도 없다. 티켓의 방침 ②대로 **placeholder 를 만들지 않고 `og:image` 계열 태그를 빼고 빌드**했다. 파일이 `static/img/og-image.png` 에 놓이면 **코드 변경 없이** 태그 5줄(`og:image`·width·height·alt·`twitter:card`)이 붙는다(`apps/core/context_processors._og_image`).
- **designer 에게 알릴 사항 1건(결함)**: `design/assets/favicon.svg` 는 **XML 로 파싱되지 않는다.** 6행 주석 안의 `--color-primary` 가 XML 주석 규칙(연속 하이픈 금지)을 어긴다. 브라우저는 `image/svg+xml` 을 XML 로 파싱하므로 **파비콘이 표시되지 않는다.** 우리 사본(`static/img/favicon.svg`)은 문구를 고쳐 해소했고 변환도 그 사본으로 했다. **원본 수정은 designer 소관**이라 티켓 처리 결과에 적었다.

---

## 8. 검증팀 전달 사항

- **실행 방법**: `developer/site/README.md` (설치 → 기동 → 자주 쓰는 명령 → 화면·콘텐츠 표 → 운영 빌드 미리보기)
- **지금 검증할 수 있는 것**: 1차 6화면 전부 · ★ **문의 폼 응답 형태 7종**(§3.1 이 기대값) · SEO(메타·canonical·sitemap·robots·JSON-LD·**OG 이미지**) · 접근성 마크업 · **JS 비활성 동작** · 콘텐츠 시드 반영 절차 · 빈도 제한과 복귀 · ★ **백업·복구·회전·실패 주입** · ★ **검증 지원 도구 ①~⑪ 전부** · ★ **운영 안전장치 5중**
- **아직 검증할 수 없는 것**: 성능·Lighthouse(브라우저 필요) · **실제 배포·롤백**(서버 필요 — 설계 §12.6.1 의 10-17 항목) · Safari·iOS 실기기(체크리스트는 제공: `developer/site/qa/webkit_checklist.md`) · 지도 실제 동작(T-E)
- ★ **검증 도구 켜는 법**: `.env` 에 `QA_TOOLS_ENABLED=1` → `docker compose … up -d app scheduler`. **끄면 모든 `qa_*` 명령이 종료 코드 2** 로 끝난다. 항목별 토글은 서로 영향을 주지 않는다(`QA_RATE_LIMIT_MODE` · `QA_RETENTION_MINUTES__INQUIRY` · `QA_FAIL_INJECT` · `QA_CLOCK_OFFSET_SECONDS`(음수 허용) · `QA_SESSION_TOKEN`).
- ★ **증거 만들기**: `qa_show inquiry --since <ISO> --format json` · `qa_mail_log --kind … --format json` 은 **그대로 첨부 가능한 단일 JSON 배열**이다. 구간 정리는 `qa_purge_test_data --since <ISO> --confirm`(테이블별 건수 출력).
- **판정용 로그 조회**: `docker compose -f compose.yaml -f compose.local.yaml logs app` — `inquiry.created` / `inquiry.invalid` / `inquiry.blocked reason=…` / `inquiry.duplicate token_state=used` / ★ `inquiry.expired token_state=expired|missing|invalid`
- **빈도 제한 조정**: `.env` 의 `RATE_LIMIT_FORM_WINDOW_MAX`·`RATE_LIMIT_FORM_DAY_MAX` 로 낮춘다. 사용량 알림 임계는 `QA_TOOLS_ENABLED=1` 일 때만 `QA_RATE_LIMIT_ALERT_*` 로 낮아진다
- ★ **`.env` 작성 주의**: **값 줄에 인라인 주석을 쓰지 않는다.** `docker run --env-file` 과 셸 파서가 주석을 값으로 읽는다(§6 #11).
- **의견을 받고 싶은 것 1건**: §6 #3(강사 경력 접기 기준을 "3줄 초과" 대신 **항목 4개 이상**으로 근사 — designer 확인). §6 #7(토큰 만료)은 **PM 결정으로 종결**됐다.
- ★★ **2차 검증(재검증) 요청 범위** — 자세한 확인 명령·결과는 §4.2
  1. **DEF-001~010 재검증**: TC-102·103·104(메타) · `50_html_validate`(vnu) · TC-107(콘솔·Lighthouse 권장사항) · TC-098(320px reflow) · TC-096(터치 타깃·글꼴) · TC-004(고정 바·하단 여백, **전화 확정/미확정 양쪽**) · TC-125(롤백 가드) · TC-059(§9.6 ⑦ **`expired` 포함 3상태 전건**) · TC-112(PII ↔ 처리방침) · TC-116(운영 이미지 자산 목록)
  2. **회귀로 함께 봐야 하는 것**: 전 화면 헤더·푸터(로고·GNB·푸터 링크 크기 변경) · 앵커 이동 위치(`#contact`·`#map`, `--header-h` 사용처) · `/privacy` 표 카드 전환(p2 행 2개 증가) · 알림 메일 제목의 상호 표기 · 문의 폼 ①⑤(오프셋 없는 정상 환경)
  3. **운영 미리보기를 다시 만들 때**: `.env.prodcheck` 의 `DJANGO_SETTINGS_MODULE` 도 `config.settings.production` 으로 바꿔야 한다(§4.2 머리말 주의)
  4. **판정 보류를 부탁하는 것**: §4.3 확인 요청 ①②③(로고·푸터·GNB 의 클릭 영역 처리와 인접 간격 해석) — designer·planner 확인 결과에 따라 값이 달라질 수 있다
- ★★★ **3차 검증(DEF-011 재검증) 요청 범위** — 자세한 확인 명령·결과는 §4.4
  1. **DEF-011**: TC-009 · TC-091 — **정적 확인(REQ-F-003 ⑤-1)만으로 닫을 수 있다**(티켓 요청 3). 5화면 응답 HTML·런타임 DOM 의 `meta[name="viewport"]` 에 `interactive-widget=resizes-content` 존재(누락 0건) + 번들의 ②③ 잔존. **⑤-2(실기기 동작)는 기기 미확보로 이번에도 "미검증"** 이다(REQ-F-003 ⑤-4 · `developer/site/qa/webkit_checklist.md`)
  2. **회귀로 함께 봐야 하는 것**: 메타 변경은 **레이아웃에 영향을 줄 수 있다**(뷰포트 해석 변경). 5화면 × 320/360/768/1280px 에서 가로 스크롤·고정 바 위치·앵커 이동(`#contact`·`#map`)을 한 번 더 본다 — 제작 측 `layout-check.js` 실행은 **위반 0건**이었다(§4.4 #71)
  3. **도구 변경 인지**: `tests/browser/layout-check.js` 가 **`/nope` 의 자기 404 를 더 이상 위반으로 세지 않는다**(출력에 `(자기404 n건 제외)` 표시). 하위 리소스 404 는 그대로 위반이다 — qa 1차 판정과 기준이 달라지는 지점이니 확인 바란다(§4.4.4)

---

## 9. 발행·처리한 티켓

| ID | 내용 | 상태 |
|---|---|---|
| TKT-DSN-002 | 파비콘·OG 래스터 변환 요청 | ★ **처리 완료(임시본 포함)** — 래스터 **5종 산출**(`og-image.png` 은 임시본 + 교체 절차 명시) · `favicon.svg` XML 오류 1건 회신 (§7) |
| DEF-011 | viewport 메타의 `interactive-widget=resizes-content` 누락(Major) | ★★★ **수정 완료 → `status: resolved`** — 티켓 "조치" 절에 원인·조치·수정 파일·영향 범위 기입 (§4.4). `closed` 전환은 qa 재검증 후 |
| — | 이번 작업에서 신규 발행한 티켓 없음 | designer 확인 요청 2건(경력 접기 기준 · macOS 폰트 메트릭)은 **P4-④ 디자인 검토에서 함께 다루는 편이 빠르다고 보고** 티켓을 따로 발행하지 않았다 |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| **0.5** | **2026-09-13** | developer | **P5 2차 결함 수정 — DEF-011(Major) 1건 + qa 인계 건 1건.** ① **G-9 ①(viewport 메타 `interactive-widget=resizes-content`)을 `templates/base.html` 에 추가** → 5화면 전건 반영(응답 HTML·런타임 DOM 양쪽 확인, 누락 0건). base 를 상속하지 않는 `errors/maintenance.html` 도 동일하게 맞췄다 ② **근본 원인인 설계 공백을 메웠다** — 기술 설계서 **§9.1에 G-9 3단 구현 표 신설**(설계서 v0.6): 단별 구현 위치·정본 문자열·담당 브라우저·판정 수단. `viewport.js` 의 `isWebKit` 가드가 ①을 전제로 한다는 것도 코드 주석에 남겼다 ③ **회귀 테스트 5건 추가**(`ViewportMetaTests` — 누락 0건·문자열 정본·화면당 1개·독립 템플릿·②③ 번들 잔존). 토큰을 뺀 상태에서 실패하는 것까지 확인(§4.4 #73). 자동 테스트 80 → **85건** ④ **qa 인계 건**: `layout-check.js` 가 `/nope` 의 **자기 404 를 위반으로 세던 문제** 수정(문서 URL 과 같은 출처의 404 만 제외, 하위 리소스 404 는 그대로 위반 — 음성 확인 완료) + **런타임 viewport 메타 점검 ⑥ 추가** → 전체 실행 **위반 0건**. §4.4 신설 | `shared/tickets/DEF-011_viewport-interactive-widget-missing.md`, `qa/05_test-report.md` |
| **0.4** | **2026-09-13** | developer | **P5 1차 결함 수정 — DEF-001~010 전건(미수정 0건).** ① **DEF-001(Major)**: title·description 원본을 `apps/core/seo.py`(IA §6.2·§6.3 표 그대로)로 단일화하고 브랜드 문자열을 DB 에서 분리, 메인 `WebSite` JSON-LD 추가, 표시 상호를 "강남 요가패스" 로 통일 ② **002** 인라인 SVG id 네임스페이스(`inline_svg uid=`) → vnu **error 0건** ③ **003** 메인 인라인 style 4곳 제거(유틸리티 클래스) ④ **004** 헤더 주 CTA 가 전 구간 노출되던 CSS 순서 문제 수정(G-8 위반 동반) + **헤더 높이 되먹임 제거** → 320px 가로 스크롤 0 ⑤ **005** 로고·푸터·GNB **클릭 영역만** 44px 확보 + 저작권 14px(토큰 값 불변, qa 권고 ⓐ) ⑥ **006** 고정 바 미렌더 화면의 하단 여백 해제(`html[data-fixed-bar]`) ⑦ **007** 롤백 대상 **태그 가드**·확인 입력·`--dry-run` + `deploy.sh --dry-run` 부수 효과 제거, **§4.1 #44 의 잘못된 기재 정정** ⑧ **008** `submit_token` 만료 판정에 clock 오프셋 적용 → §9.6 ⑦ `expired` 판정 가능 ⑨ **009** 처리방침 수집 항목 표에 `consent_at`·`phone_norm` 추가 + 자동 대조 ⑩ **010** 작업 사본을 `assets-work/` 로 옮기고 `.dockerignore` 정리 → 운영 이미지 자산 11개. **회귀 테스트 27건 + 브라우저 레이아웃 점검 도구 추가**(자동 테스트 53 → **80건**), §4.2 실행 확인 표·§4.3 확인 요청 6건 신설 | `shared/tickets/DEF-001…010`, `qa/05_test-report.md` |
| **0.3** | **2026-09-13** | developer | **PM 결정 2건 + 구현 3단계(작업 11·12·13).** ① 폼 **토큰 만료 → 재작성 안내**(⑤/⑦ 분리 · 입력값 보존 · 새 토큰 · 테스트 5건) ② **OG 이미지 임시본**(여백 실측 · 임시 표시 4곳 · 교체 시 코드 변경 0) ③ **폰트 폴백 메트릭 실측 적용**(Windows 실측 / macOS 미실측 표시) ④ **배포·롤백·복구 스크립트 + nginx 운영·스테이징 샘플 2종** ⑤ **백업 일원화(`run_backup`)·회전·실패 주입·락 충돌 중단 + 복구 리허설 1회 성공** ⑥ **일일 운영 요약·`/healthz` 폴링·파기·카운터 정리 스케줄 가동** ⑦ **검증 지원 도구 ①~⑪ + 안전장치 5중 전건 실행 확인** ⑧ **결함 1건 수정** — 동시 이중 제출 500. 실행 확인 **20건 추가**(§4.1), 자동 테스트 48 → **53건** | PM 결정 2026-09-13, TKT-DSN-002 |
| 0.2 | 2026-09-13 | developer | **구현 2단계** — 1차 6화면 완성(SCR-002·003·006 신규, 008·009 디자인 반영) · **문의 폼과 응답 형태 6종**(§3.1) · 빈도 제한·사용량 알림 · SEO/접근성/`<noscript>` 마감 · 파비콘 래스터 4종(TKT-DSN-002) · **템플릿 주석 누출 결함 수정** · 자동 테스트 9 → 48건 | TKT-DSN-002 |
| 0.1 | 2026-09-13 | developer | 최초 작성(초안) — 구현 1단계(작업 1~3 + SCR-001 뼈대)와 실행 명령 28건의 확인 결과 | `shared/reviews/P4a_tech-design_devops_r2.md`, `shared/reviews/P4a_tech-design_qa_r2.md` |
