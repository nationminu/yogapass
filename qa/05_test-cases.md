---
doc_id: QA-TC
title: 테스트 케이스 · 요구사항 추적 매트릭스 — 1차
phase: P5
owner: qa
version: 0.1
status: in-review
reviewers: [developer, planner]
inputs: [planning/02_requirements.md, planning/02_storyboard.md, planning/02_information-architecture.md, design/03_page-design.md, design/03_design-system.md, developer/04_tech-design.md, developer/04_dev-report.md, qa/05_test-plan.md]
updated: 2026-09-13
---

# 테스트 케이스 — 강남 요가패스 1차

판정 표기: `Pass` · `Fail` · `Block`(실행 불가·입력 미확보) · `N/A`(판정 대상 아님) · `부분`(일부 조건만 판정, 나머지는 사유 명시)
1차 사이클 실행일: **2026-09-13** / 증거: `qa/evidence/cycle1/`

---

## 1. 요구사항 추적 매트릭스 (RTM) — 1차 게이트 판정 모수 96건

> 모수 산출 근거: 요구사항 v1.1 §7.3 정본(1차 35 + 공통 61 = **96건**, 그중 Must **60건**).
> qa가 §3·§5.1·§5.1.1·§6의 각 행 `차수` 열을 기계 집계한 결과와 **완전히 일치**했다 (`evidence/cycle1/37_req_1st_list.tsv`).
> 화면 밖 항목은 요구사항 §5.3의 검증 행을 TC 대신 연결한다(연결처를 `§5.3` 로 표기).

### 1.1 기능 요구사항 (39건)

| REQ ID | 요구사항 | 우선순위 | 차수 | SCR | 구현 위치(`developer/site/`) | TC | 1차 결과 |
|---|---|---|---|---|---|---|---|
| REQ-F-001 | 공통 헤더 | Must | 공통 | 전 화면 | `templates/partials/header.html` | TC-001 | Pass |
| REQ-F-002 | 공통 푸터 | Must | 공통 | 전 화면 | `templates/partials/footer.html` | TC-002 | Pass |
| REQ-F-003 | 전역 주 CTA | Must | 공통 | 전 화면 | `partials/fixed_bar.html` · `apps/core/cta.py` | TC-003~007 | **Fail** (DEF-006) |
| REQ-F-004 | 전화 걸기 링크 | Must | 1차 | 전 화면 | `apps/core/templatetags/icons.tel_href` | TC-010 | 부분 (값 주입 시 Pass · 실값 `[TBD]`) |
| REQ-F-005 | 처리방침 전역 링크 | Must | 공통 | 전 화면 | 푸터·모바일 패널·폼 동의 | TC-011 | Pass |
| REQ-F-006 | 화면 간 이동 일관성 | Must | 공통 | 전 화면 | `apps/content/services.nav_items` | TC-012 | Pass |
| REQ-F-010 | 메인 Hero | Must | 1차 | SCR-001 | `templates/pages/home.html` | TC-020 | **Block** (T-G 문구 미수령) |
| REQ-F-011 | 스튜디오 소개 요약 | Must | 1차 | SCR-001 | `pages/home.html` | TC-021 | **Block** (T-G 강점 미수령) |
| REQ-F-012 | 강사 미리보기 | Should | 공통 | SCR-001 | `pages/home.html` | TC-022 | Pass (0명 미노출 · 2명 노출) |
| REQ-F-013 | 위치 요약 | Should | 1차 | SCR-001 | `pages/home.html` | TC-023 | Pass |
| REQ-F-014 | 수업 유형 소개 | Should | 공통 | SCR-001 | `content/lesson_types.yml` | TC-024 | Pass (시간표·요금 수치 0건) |
| REQ-F-015 | 메인 하단 전환 섹션 | Should | 공통 | SCR-001 | `pages/home.html` | TC-025 | Pass |
| REQ-F-020 | 강사 목록 | Must | 공통 | SCR-002 | `pages/instructors.html` | TC-030 | Pass |
| REQ-F-021 | 강사 데이터 분리 | Must | 공통 | SCR-002 | `content/instructors.yml` + `seed_content` | TC-031 | 부분 (0·2·3명 실행 / 1·12명 자동 테스트) |
| REQ-F-022 | 강사 사진 대체 처리 | Must | 공통 | SCR-002 | CMP-027 이니셜 아바타 | TC-032 | Pass (`<img>` 0건) |
| REQ-F-023 | 강사 → 전환 연결 | Should | 공통 | SCR-002 | CMP-025 CTA 밴드 | TC-033 | Pass |
| REQ-F-030 | 지도 표시 | Must | 1차 | SCR-003 | `pages/location.html` · `css/pages/location.css` | TC-040 | **Block** (T-E 지도 URL 미확정) |
| REQ-F-031 | 길찾기 외부 링크 | Must | 1차 | SCR-003 | `map_directions_url` | TC-041 | **Block** (T-E 좌표·장소 ID 미확정) |
| REQ-F-032 | 지도 지연 로딩 | Must | 1차 | SCR-003 | `static/js/map.js` | TC-042 | Pass (초기 외부 요청 0건) |
| REQ-F-033 | 오시는 길 정보 | Must | 1차 | SCR-003 | `apps/core/views.LOCATION_ROWS` | TC-043 | 부분 (구조 Pass · 값 Block) |
| REQ-F-034 | 주소 복사 | Could | 1차 | SCR-003 | `static/js/map.js` | TC-044 | 부분 (주소 확정 시 버튼 렌더 확인 · 클립보드 동작 미검증) |
| REQ-F-035 | 지도 접근성 대체 | Must | 1차 | SCR-003 | `<dl>` + iframe title + `<noscript>` | TC-045 | Pass |
| REQ-F-040 | 문의 폼 제공 | Must | 공통 | SCR-003 | `apps/inquiry/forms.py` | TC-050 | Pass |
| REQ-F-041 | 클라이언트 검증 | Must | 1차 | SCR-003 | `static/js/form.js` | TC-051 | Pass |
| REQ-F-042 | 서버 측 입력 검증 | Must | 공통 | SCR-003 | `apps/inquiry/services.handle_submission` | TC-052 | Pass |
| REQ-F-043 | 개인정보 동의 | Must | 공통 | SCR-003 | `components/form_field.html` | TC-053 | Pass |
| REQ-F-044 | 스팸 방지 | Must | 공통 | SCR-003 | honeypot + `apps/core/ratelimit.py` | TC-054·055 | Pass |
| REQ-F-045 | 스튜디오 알림 | Must | 공통 | SCR-003 | `apps/inquiry/services._notify_body` → `mailer_outbox` | TC-057 | Pass |
| REQ-F-046 | 결과 안내 · 중복 방지 | Must | 공통 | SCR-003 | `submit_token` UNIQUE | TC-058·059·061 | 부분 (①②③ Pass · 만료 분기 Block — DEF-008) |
| REQ-F-050 | 처리방침 화면 | Must | 공통 | SCR-006 | `pages/privacy.html` · `content/privacy.yml` | TC-070 | Pass (1차 기준: 목차 11항목 + `[TBD]` 표시) |
| REQ-F-051 | 처리방침 입력 항목 정의 | Must | 공통 | — | `content/privacy.yml` | §5.3 · TC-071 | Pass (문서 확인) |
| REQ-F-052 | 위탁·외부 처리 목록 | Must | 공통 | — | 기술 설계 §7.1 → `privacy.yml` 6항 | §5.3 · TC-072 | Pass (문서 확인) |
| REQ-F-053 | 시행일·개정 이력 | Should | 공통 | SCR-006 | `pages/privacy.html` 11항 | TC-073 | 부분 (구조 Pass · 시행일 값 Block) |
| REQ-F-060 | 404 화면 | Must | 공통 | SCR-008 | `templates/errors/404.html` | TC-080 | Pass |
| REQ-F-061 | SNS 링크 | Should | 1차 | 푸터 | `footer.html` | TC-081 | **Block** (T-H 계정 미수령) |
| REQ-F-062 | 분석 도구 설치 | Should | 공통 | 전 화면 | `ANALYTICS_ID` 자리만 | TC-082 | **N/A** (미착수 · 고객 계정 필요 · 오픈 후 설치 가능) |
| REQ-F-063 | 전환 측정 대체 수단 | Should | 공통 | — | 운영 가이드 | §5.3 · TC-083 | **Block** (P8 산출물 미작성) |
| REQ-F-064 | 콘텐츠 데이터 분리 | Must | 공통 | — | `content/*.yml` + `seed_content` | §5.3 · TC-084 | Pass |
| REQ-F-065 | 공용 오류 화면 | Could | 1차 | SCR-009 | `templates/errors/500.html` | TC-085 | Pass |

### 1.2 비기능 요구사항 (38건)

| REQ ID | 요구사항 | 우선순위 | 차수 | 적용 범위 | 검증 위치 | TC | 1차 결과 |
|---|---|---|---|---|---|---|---|
| REQ-N-001 | 반응형 360/768/1280 | Must | 공통 | 전 화면 | CSS 4구간 | TC-090 | Pass |
| REQ-N-002 | 모바일 우선 · 고정 바 | Must | 공통 | 공개 영역 | `fixed_bar.html` | TC-091 | Pass |
| REQ-N-003 | 브라우저 호환 | Must | 공통 | 전 화면 | — | TC-092 | 부분 (Chrome만 · Edge·FF·Safari **미검증**) |
| REQ-N-004 | Lighthouse 성능 90+ | Must | 공통 | M-2 대상 | 운영 미리보기 | TC-093 | Pass (중앙값 99·100·99·99) |
| REQ-N-005 | 지도 초기 로딩 저하 방지 | Must | 1차 | SCR-003 | `map.js` | TC-094 | Pass |
| REQ-N-006 | WCAG 2.1 AA | Must | 공통 | 전 화면 | 토큰·마크업·CSS | TC-095~098 | **Fail** (② 터치 타깃 · ⑤ reflow·글꼴 — DEF-004·005) |
| REQ-N-007 | Lighthouse 접근성 90+ | Must | 공통 | M-2 대상 | — | TC-099 | Pass (전 화면 100) |
| REQ-N-008 | 폼 접근성 | Must | 공통 | SCR-003 | `form_field.html` | TC-100 | Pass |
| REQ-N-009 | skip link · 문서 구조 | Should | 공통 | 전 화면 | `base.html` | TC-101 | Pass |
| REQ-N-010 | title · description | Must | 공통 | 전 화면 | `partials/meta.html` | TC-102 | **Fail** (DEF-001) |
| REQ-N-011 | 지역 검색 대응 문구 | Must | 1차 | SCR-001·003 | `meta.html` · `home.html` | TC-103 | **Fail** (DEF-001) |
| REQ-N-012 | 지역 업체 구조화 데이터 | Must | 1차 | 공개 영역 | `jsonld_localbusiness.html` | §5.3 · TC-104 | 부분 (JSON 유효 · 값 `[TBD]` · `WebSite` 누락 — DEF-001) |
| REQ-N-013 | sitemap · robots · canonical | Must | 공통 | 전 화면 | `apps/core/sitemaps.py` · `views.robots_txt` | §5.3 · TC-105 | Pass |
| REQ-N-014 | OG · 소셜 공유 태그 | Should | 1차 | 색인 화면 | `meta.html` · `context_processors._og_image` | TC-106 | Pass |
| REQ-N-015 | Lighthouse SEO·권장사항 90+ | Must | 공통 | M-2 대상 | — | TC-107 | Pass (SEO 100 / 권장 92~100 — 메인 감점 DEF-003) |
| REQ-N-016 | 시맨틱 마크업 · 검증 오류 0건 | Must | 공통 | 전 화면 | 템플릿 | TC-108 | **Fail** (오류 5건 — DEF-002) |
| REQ-N-017 | 전 구간 HTTPS | Must | 1차 | 운영 | 리버스 프록시 | §5.3 · TC-109 | **P7 이월** (P5 부분: 혼합 콘텐츠 0건) |
| REQ-N-018 | 비밀 정보 분리 | Must | 공통 | 저장소·이미지 | `.env` · `.gitignore` | §5.3 · TC-110 | Pass |
| REQ-N-019 | 폼 악용 방지 단일 정의 | Must | 공통 | SCR-003 | `apps/core/ratelimit.py` | TC-055·056 · TC-111 | Pass (1차 해당 1종) |
| REQ-N-020 | 수집 최소화 · 고지 · 파기 | Must | 공통 | SCR-003·006 | `qa_pii_columns` ↔ `privacy.yml` | TC-112 | **Fail(부분)** (DEF-009) |
| REQ-N-021 | 외부 처리 사업자 기록 | Must | 공통 | — | 기술 설계 §7.1 | §5.3 · TC-113 | Pass (문서 확인) |
| REQ-N-022 | 알림 메일 도달 · 발신 인증 | Must | 공통 | 운영 | SMTP | §5.3 · TC-114 | **P7 이월** (P5 부분: 로컬 수신·본문 확인) |
| REQ-N-023 | 오픈 판정 기준 | Must | 공통 | 전체 | `manage.py check_release` | §5.3 · TC-115 | Pass (P5 범위: 차단 장치 동작) · ②는 **P7** |
| REQ-N-024 | 이미지 출처·라이선스 100% | Must | 공통 | 자산 | `design/assets/SOURCES.md` | §5.3 · TC-116 | 부분 (지도 캡처 0건 Pass · 초과 1건 DEF-010) |
| REQ-N-025 | 화이트·블루 · 로고 | Must | 공통 | 전 화면 | `static/css/tokens.css` | TC-117 | Pass |
| REQ-N-026 | 콘텐츠 수정 절차 문서화 | Should | 공통 | — | 운영 가이드 | TC-118 | **Block** (P8 산출물 미작성 · `site/README.md` §4에 부분 기재) |
| REQ-N-027 | 한국어 단일 언어 | Must | 공통 | 전 화면 | `<html lang="ko">` | TC-119 | Pass |
| REQ-N-028 | JS 비활성 정보 화면 동작 | Must | 공통 | 정보 화면 | 서버 렌더 | TC-120 | Pass |
| REQ-N-029 | JS 비활성 대체 안내 | Must | 공통 | 지도·폼 | `partials/noscript.html` | TC-121 | 부분 (안내 Pass · `tel:` 링크는 값 확정 후) |
| REQ-N-030 | JS 없는 폼 제출 | Could | 1차 | SCR-003 | 서버 렌더 POST | TC-122 | Pass |
| REQ-N-031 | 헬스체크 · 자동 재시작 | Should | 1차 | 인프라 | `/healthz` · compose | §5.3 · TC-123 | Pass |
| REQ-N-032 | 백업 · 복구 (리허설 포함) | Must | 1차 | 인프라 | `run_backup` · `deploy/restore.sh` | §5.3 · TC-124 | Pass (**복구 리허설 1회 성공**) |
| REQ-N-033 | 배포 · 롤백 절차 | Must | 1차 | 인프라 | `deploy/deploy.sh` · `rollback.sh` | §5.3 · TC-125 | **Fail(부분)** (DEF-007) + 서버 구간 P7 이월 |
| REQ-N-034 | 세 환경 동일 compose | Must | 1차 | 인프라 | `compose*.yaml` | §5.3 · TC-126 | Pass |
| REQ-N-037 | 알림 메일 체계 | Must | 공통 | 인프라 | `apps/mailer/*` | §5.3 · TC-127 | Pass (1차 1종 + 운영 알림) |
| REQ-N-038 | 항목별 보관 · 파기 | Must | 공통 | 인프라 | `purge_expired` | §5.3 · TC-128 | Pass (1차 해당 1분류) |
| REQ-N-039 | 개인정보 접근 통제 | Must | 공통 | 인프라 | `qa_show` 마스킹 · 설계 §12.5.2 | §5.3 · TC-129 | **Block** (대조 대상 `devops/07_deploy-plan.md` 미작성) |
| REQ-N-040 | 스테이징 환경 | Should | 1차 | 인프라 | `yogapass-stg.conf.sample` · `FORCE_NOINDEX` | §5.3 · TC-130 | 부분 (설정 대조 Pass · 실측 P7) |

### 1.3 콘텐츠 요구사항 (19건)

> 콘텐츠 REQ는 MoSCoW 집계 대상이 아니다(요구사항 §7 머리말). **추적률 분모에는 포함**한다.

| REQ ID | 콘텐츠 | 차수 | 제공 주체 | TC | 1차 결과 |
|---|---|---|---|---|---|
| REQ-C-001 | 로고 원본 + 브랜드 색상 | 1차 | 고객 | TC-140 | 부분 (제작 제작본 SVG 사용 중 · 고객 원본 미수령 T-B) |
| REQ-C-002 | 스튜디오 소개 문구 | 1차 | 제작 초안 → 고객 확정 | TC-141 | **Block** (T-G · `hero_headline` 미렌더) |
| REQ-C-003 | 강점 3~4가지 | 1차 | 고객 | TC-141 | **Block** (T-G) |
| REQ-C-004 | 강사 정보 | 공통 | 고객 | TC-142 | **Block** (T-C · 데이터 파일 구조·경계값은 TC-031로 확인) |
| REQ-C-005 | 강사 사진 | 공통 | 고객 | TC-142 | **Block** (T-C · 대체 표시 동작은 TC-032 Pass) |
| REQ-C-006 | 수업 유형·시간표·요금 | 공통 | 고객 | TC-024 | 부분 (유형 5건 제작 초안 노출 · 시간표·요금 1차 미노출이 정상) |
| REQ-C-007 | 주소·역·출구·주차 | 1차 | 고객 | TC-143 | **Block** (T-E) |
| REQ-C-008 | 운영시간·휴무일 | 공통 | 고객 | TC-143 | **Block** (T-E) |
| REQ-C-009 | 대표 전화번호 | 1차 | 고객 | TC-010 | **Block** (T-E · 주입 시 3곳 반영 확인) |
| REQ-C-010 | 사업자 정보 | 1차 | 고객 | TC-143 | **Block** (T-G) |
| REQ-C-011 | SNS 계정 | 1차 | 고객 | TC-081 | **Block** (T-H) |
| REQ-C-012 | 처리방침 입력값 | 공통 | 고객 | TC-070 | **Block** (T-F · 11항목 전부 `pending`) |
| REQ-C-013 | 분위기 이미지 | 1차 | 제작 | TC-144 | Pass (인물 스톡 0장 · 지도 캡처 0건 · CSS 그래픽 대체) |
| REQ-C-014 | 이미지 플레이스홀더 규격 | 1차 | 제작 | TC-144 | Pass (P3 에셋 총량표 존재) |
| REQ-C-015 | 화면 안내 문구 | 공통 | 제작 | TC-145 | Pass ("준비 중" 0건 · 빈 상태 문구 확인) |
| REQ-C-016 | 메타 title·description·OG 문구 | 공통 | 제작 | TC-102 | **Fail** (DEF-001) |
| REQ-C-017 | 파비콘·OG 이미지 | 1차 | 제작 | TC-146 | 부분 (5종 산출 · `og-image.png`는 **임시본**) |
| REQ-C-018 | 도메인 주소 | 1차 | 고객 | TC-105 | **Block** (T-A · `SITE_BASE_URL` 교체로 전환됨을 확인) |
| REQ-C-019 | 알림 수신 이메일 | 공통 | 고객 | TC-057 | **Block** (T-E · 테스트 주소로 도달 확인) |

### 1.4 커버리지

| 항목 | 값 |
|---|---|
| 1차 판정 모수 | **96건** (기능 39 · 비기능 38 · 콘텐츠 19) |
| TC 또는 §5.3 검증 행에 **연결된 REQ** | **96건** |
| **미추적 REQ** | **0건** |
| 추적률 | **100%** |
| 그중 Must (기능+비기능) | **60건** — 전건 연결 |
| 2차 REQ 145건 | **N/A** (요구사항 §5.0 M-7 — 미충족으로 세지 않는다) |

---

## 2. 테스트 케이스

### 2.1 공통 UI · 전역 동선

| TC ID | 관련 REQ / SCR | 유형 | 사전 조건 | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|---|---|
| TC-001 | REQ-F-001 / 전 화면 | 기능 | 스택 A 기동 | 360·768·1280px에서 5화면 헤더 확인 | 로고 + GNB 4종(홈·강사 소개·오시는 길·문의하기) + 현재 항목 `aria-current="page"` | **Pass** | 03, 44 |
| TC-002 | REQ-F-002 | 기능 | — | 각 화면 푸터의 링크 확인 | 처리방침 `/privacy`, 문의하기 `/location#contact`, 페이지 링크 4종 | **Pass** | 03, 19 |
| TC-003 | REQ-F-003 ① · REQ-N-002 / §3.0 G-1 | 기능 | 전화 확정 시드 | 360·768·1280px × 5화면에서 하단 고정 바 확인 | `<1280px` 고정 바 노출(높이 61px ≥56), `≥1280px` 미노출 | **Pass** | 48 |
| TC-004 | REQ-F-003 ② · §3.0 G-6 ② | 기능 | 전화 `[TBD]` | `/location`(자기 참조) 360px | 고정 바 미노출 **+ 본문 하단 여백도 미적용** | **Fail** — 여백 76px 잔존 | 44 → **DEF-006** |
| TC-005 | REQ-F-003 ② ③-2 | 기능 | 전화 확정 시드 | `/location` 360·1280px | 고정 바 = "전화 문의" 전폭 1버튼 / 헤더 주 CTA도 "전화 문의"로 대체 | **Pass** | 48 |
| TC-006 | REQ-F-003 ③-1·③-3·③-4·③-5 | 기능 | 전화 `[TBD]` | 1280px에서 문서 끝까지 스크롤 | 헤더 sticky 유지, 비자기참조 화면 주 CTA "문의하기", `/location`은 **버튼 미렌더**(빈·비활성·`[TBD]` 0건), 768~1279px 헤더 CTA 없음 | **Pass** | 44 |
| TC-007 | §3.0 G-3 | 기능 | 고정 바 노출 화면 | `body` padding-bottom 측정 | `고정 바(60) + 16 + safe-area` = 76~77px | **Pass** (77px) | 44 |
| TC-008 | §3.0 G-4 (REQ-F-003 ④) | 기능 | 폼 화면 + 고정 바 | 문서 끝까지 스크롤 후 제출 버튼 ↔ 고정 바 간격 | 16px 이상 | **N/A** — 1차 유일 폼 화면(`/location`)이 자기 참조라 고정 바 미노출(G-6 ②). 측정 대상 없음 | 45 |
| TC-009 | REQ-F-003 ⑤-1 | 정적 | 빌드 결과물 | `<head>` `interactive-widget` · WebKit 폴백 · `scroll-padding-bottom` 존재 확인 | 공개 영역 전 화면 누락 0건 | **부분** — `viewport.js` 폴백·`--fixed-bar-h` 반영 확인. ⑤-2(실기기)는 **미검증** | 44, L-1 |
| TC-010 | REQ-F-004 · REQ-C-009 | 기능 | 전화 확정 시드 | 헤더·푸터·오시는 길 `tel:` 링크 | 3곳 모두 `tel:` 렌더, 값 정규화 | **부분 Pass** — 주입 시 헤더 4·푸터 1·본문 5건. 실값 `[TBD]` | 46 |
| TC-011 | REQ-F-005 | 기능 | — | 폼 동의 영역의 처리방침 링크 | `/privacy` 새 창 + 접근 이름에 "(새 창 열림)" | **Pass** | 41 |
| TC-012 | REQ-F-006 | 링크 | — | 5화면의 href/src 전수 상태 코드 + 앵커 id | 깨진 링크 0건 | **Pass** (25/25 = 200, 앵커 누락 0) | 19, 20 |

### 2.2 메인 (SCR-001)

| TC ID | 관련 REQ | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|
| TC-020 | REQ-F-010 · REQ-C-002 | 360px 메인 첫 화면 | 헤드라인·서브카피·주 CTA 노출, 헤드라인에 '강남'·'요가' | **Block** — `hero_headline`·`hero_lead` 미수령으로 섹션 미렌더(설계대로). 현재 h1 = "요가패스" | 04, 49 |
| TC-021 | REQ-F-011 · REQ-C-003 | 소개 카드 개수 | 3~4개 | **Block** — `features` 미수령으로 섹션 미렌더 | 04 |
| TC-022 | REQ-F-012 | 강사 0명 / 2명 상태 비교 | 0명이면 섹션 미노출, 있으면 "강사 전체 보기" 링크 | **Pass** | 47 |
| TC-023 | REQ-F-013 | 메인 위치 섹션 | "오시는 길" 링크가 `/location`으로 | **Pass** | 03, 19 |
| TC-024 | REQ-F-014 · REQ-C-006 | 메인 수업 섹션 | 유형 5개 이하, **시간표·요금 수치 0건** | **Pass** | 04 |
| TC-025 | REQ-F-015 | 메인 하단 | 문의 링크 노출(전화는 값 확정 시) | **Pass** | 03 |

### 2.3 강사 (SCR-002)

| TC ID | 관련 REQ | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|
| TC-030 | REQ-F-020 | 강사 3명(1명 비활성) 시드 후 공개 화면 | 활성 2명만 카드 노출 | **Pass** | 47 |
| TC-031 | REQ-F-021 | `instructors.yml` 변경 → `seed_content` → 재조회 | 0명(빈 상태) · 2명 · 3명(1 비활성) 레이아웃 정상 | **부분 Pass** — 0·2·3명 실행 확인. **1명·12명은 개발팀 자동 테스트(`test_pages.py`) 근거** | 46, 47, 52 |
| TC-032 | REQ-F-022 · REQ-C-005 | 사진 없는 강사 카드 | 인물 스톡 아님 + 대체 텍스트 | **Pass** (`<img>` 0건, 이니셜 아바타 3건) | 47 |
| TC-033 | REQ-F-023 | 강사 목록 하단 CTA | `/location#contact` 이동 | **Pass** | 47 |

### 2.4 오시는 길 · 문의 폼 (SCR-003)

| TC ID | 관련 REQ | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|
| TC-040 | REQ-F-030 | 지도 영역 확인 | 지도 표시 + 마커 + 가로 스크롤 0 | **Block** (지도 서비스·URL `[TBD]`) — 대체 영역은 CSS 그래픽, **지도 화면 캡처 0건** 확인 | 51 |
| TC-041 | REQ-F-031 | 길찾기 링크 | 목적지=스튜디오 | **Block** (좌표·장소 ID `[TBD]`) | 03 |
| TC-042 | REQ-F-032 · REQ-N-005 | 초기 로드 네트워크 | 지도 도메인 요청 **0건** | **Pass** (외부 URL이 `data-map-src` 속성에만 존재, 초기 요청 목록에 지도 도메인 0건) | 19, 42 |
| TC-043 | REQ-F-033 · REQ-C-007·008 | 정보 7행 | 라벨과 값 표시 / 미확정 행 미렌더 | **부분** — 주소·전화 주입 시 렌더 확인. 실값 Block | 46 |
| TC-044 | REQ-F-034 (Could) | 주소 복사 버튼 | 클립보드 복사 + 토스트 | **부분** — 주소 확정 시 버튼 렌더 확인. 클립보드 API 동작은 미검증 | 46 |
| TC-045 | REQ-F-035 | 스크린리더 관점 | 주소·교통이 지도와 별개 텍스트 | **Pass** (`<dl>` + `<noscript>` 대체) | 18, 44 |
| TC-050 | REQ-F-040 | 폼 항목 확인 | 이름·전화·내용·동의 + honeypot(비노출) + 글자 수 표시 | **Pass** (글자 수 "14 / 500" 동작, honeypot `company_ref` 화면 밖 `-9999px`) | 41, 42, 56 |
| TC-051 | REQ-F-041 | 이름 1자 입력 중 / blur 후 / 제출 | 입력 중 오류 0, blur 후 `aria-invalid`, 제출 시 첫 오류 항목으로 포커스 | **Pass** (입력 중 0 → blur 후 1 → 제출 후 `#f-name` 포커스·`aria-invalid` 4) | 56 |
| TC-052 | REQ-F-042 / §9.6 ② | 이름 공백·전화 `010-12`·동의 없음 POST | **200** 재렌더 + 오류 요약 `role="alert"` + `aria-invalid` + 입력값 보존 + 토큰 유지 · 저장 0 · 발송 0 · `inquiry.invalid fields=[name,phone,consent]` | **Pass** | 06, 08, 09 |
| TC-053 | REQ-F-043 | 동의 영역 문구 | 수집 항목·목적·보관 기간 + 처리방침 링크 | **Pass** ("수집 항목: 이름, 휴대폰 번호, 문의 내용 / 목적: 문의 답변 / 보관 기간: 1년") | 41 |
| TC-054 | REQ-F-044 / §9.6 ③ | honeypot 채워 POST | **200** + ①과 동일 화면 · 저장 0 · 발송 0 · `inquiry.blocked reason=honeypot` | **Pass** | 06, 08, 09 |
| TC-055 | REQ-F-044 · REQ-N-019 / §9.6 ④ | 10분 창에 7회 POST → 창 경과 후 1회 | 1~5회 200, 6·7회 **429 + `Retry-After`**(관측 102초 = 창 잔여) + 일반 문구 · 저장 0 · 발송 0 · `reason=rate_limit scope=form`. 창 경과 후 200 복귀 | **Pass** | 10, 11, 14 |
| TC-056 | REQ-N-019 사용량 알림 | `QA_RATE_LIMIT_ALERT_PER_SOURCE_DAY=1`로 차단 1회 유발 | `mailer_outbox(kind=rate_limit_alert)` 1건 | **Pass** | 16, 16b |
| TC-057 | REQ-F-045 · REQ-N-037 / §9.6 ① | 정상 접수 | **200** + 성공 블록 `role="status"` · 저장 1 · 아웃박스 `inquiry_notify` 1 · `inquiry.created ref=…` · 5분 내 Mailpit 수신 | **Pass** (저장 8 ↔ 알림 8 1:1) | 06, 08, 11 |
| TC-058 | REQ-F-046 ② / §9.6 ⑤ | 같은 토큰 2회 순차 + 동시 5건 | 순차: 200 + ①과 동일 화면 · 추가 저장 0 · `inquiry.duplicate token_state=used`. 동시 5건: 200×5 · 저장 정확히 1건 | **Pass** | 07, 09, 15 |
| TC-059 | REQ-F-046 ① / §9.6 ⑦ | 토큰 부재 / 변조 / 24h 만료 | **200** + "시간이 지나 문의가 접수되지 않았습니다." + 폼 재렌더 + 입력값 4항목 보존 + 새 토큰 · 저장 0 · `inquiry.expired token_state=…` | **부분 Pass** — `missing`·`invalid` Pass, **`expired`는 유발 수단 없음 → Block** | 06, 09, 13 → **DEF-008** |
| TC-060 | §9.6 ⑥ | DB 정지 상태에서 폼 POST | **500** + `errors/500.html` + `noindex` + 스택 트레이스 미노출 · 저장 0 | **Pass** | 12b |
| TC-061 | REQ-F-046 ③ | 정상 제출 직후 Tab 1회 | 포커스가 결과 블록 안 또는 직후(body로 튀지 않음) | **Pass** (Tab 1회 → 결과 블록 내 "다시 문의하기") | 57 |

### 2.5 처리방침 · 보조 화면

| TC ID | 관련 REQ | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|
| TC-070 | REQ-F-050 · REQ-C-012 | `/privacy` | 목차 11항목 소제목 존재 + 미확정 항목 `[TBD]` 표시(1차 기준) | **Pass** (h2 11개 + `[TBD]` 34개소 — 1차 수용 기준상 정상) | 03, 04 |
| TC-071 | REQ-F-051 | `content/privacy.yml` | 고객이 채울 입력 항목 목록이 문서로 존재 | **Pass** | 17 |
| TC-072 | REQ-F-052 · REQ-N-021 | 기술 설계 §7.1 | 외부 서비스별 사업자·업무·리전 기재 | **Pass** (SMTP·지도·분석 3행, 미확인은 `[TBD]`) | 문서 |
| TC-073 | REQ-F-053 | `/privacy` 하단 | 시행일 + 개정 이력 표 | **부분** (표 구조 존재 · 시행일 값 `[TBD]`) | 04 |
| TC-080 | REQ-F-060 | `DJANGO_DEBUG=0` 환경에서 없는 URL | **404** + 안내 + 홈·문의·강사·오시는 길 링크 + `noindex` + 헤더·푸터 유지 | **Pass** ⚠ 판정 조건: `config/settings/local.py`가 `DEBUG=True` 고정이라 **기본 로컬 스택(:8000)에서는 Django 기본 404가 보인다**. `DEBUG=0` 컨테이너와 운영 미리보기(:8001)에서 판정 | 02, 36 |
| TC-081 | REQ-F-061 · REQ-C-011 | 푸터 SNS 섹션 | 계정 있으면 새 탭 링크 / 없으면 섹션 미노출 | **Block** (T-H) — 미노출 동작은 확인 | 03 |
| TC-082 | REQ-F-062 | 분석 스크립트 | 전환 이벤트 기록 | **N/A** (미착수 · 고객 계정 필요) | 개발 보고서 §2.1 |
| TC-083 | REQ-F-063 | 운영 가이드 | 월별 접수 건수 확인 절차 기재 | **Block** (P8 미작성) | — |
| TC-084 | REQ-F-064 | `content/site.yml` 전화·주소 변경 → `seed_content` → 재조회 | 헤더·푸터·오시는 길 **3곳 동시 반영** | **Pass** (헤더 4 · 푸터 1 · 본문 5건 `tel:` 렌더, 주소 본문 노출) | 46 |
| TC-085 | REQ-F-065 | 500 상황 / nginx 502 | 브랜드 유지 오류 화면 + 전화 링크 자리 | **Pass** (500: `errors/500.html` · 502: 정적 점검 화면 "잠시 점검 중입니다") | 12b, 53 |

### 2.6 비기능

| TC ID | 관련 REQ | 절차 | 기대 결과 | 1차 | 증거 |
|---|---|---|---|---|---|
| TC-090 | REQ-N-001 | Chrome 실제 뷰포트 360·768·1280px × 5화면 | 가로 스크롤 0 · 넘치는 요소 0 | **Pass** (scrollWidth = clientWidth 전건) | 42, screenshots/ |
| TC-091 | REQ-N-002 | 360px 로드 직후 | 고정 바가 스크롤 0에서 보인다 | **Pass** | 48 |
| TC-092 | REQ-N-003 | Chrome / Edge / Firefox / Safari | 기능 실패 0 · Major 레이아웃 결함 0 | **부분** — Chrome(headless) Pass. **Edge·Firefox·Safari 미검증**(L-2·L-3) | 42 |
| TC-093 | REQ-N-004 | Lighthouse 모바일 3회 중앙값, 운영 미리보기 | 성능 90+ | **Pass** — 99 / 100 / 99 / 99 | 39, lighthouse-mobile/ |
| TC-094 | REQ-N-005 | 초기 렌더 차단 경로 | 지도 리소스 없음 | **Pass** | 42 |
| TC-095 | REQ-N-006 ① | 디자인 토큰 18개 색 조합 WCAG 대비 계산 | 본문 4.5:1 · UI 경계 3:1 | **Pass** (미달 0건, 최소 3.31:1/경계·4.83:1/본문) | 38 |
| TC-096 | REQ-N-006 ② | 360px 조작 요소 실측 | 44×44px 이상 · 인접 8px | **Fail** — 헤더 로고 140×32, 푸터 링크 328×32 (5종) | 42, 43, 45 → **DEF-005** |
| TC-097 | REQ-N-006 ③④ | 키보드 Tab 순회 + 이미지 대체 텍스트 | 전 요소 도달·포커스 표시 · 대체 텍스트 100% | **Pass** (Tab 16스텝 전건 3px outline, SVG 전건 `aria-hidden` 또는 `role="img"`+`aria-labelledby`, `<img>` 0건) | 18, 45 |
| TC-098 | REQ-N-006 ⑤ | 320px(400% 확대 상당) · 최소 글꼴 | 가로 스크롤 없음 · 본문 14px 이상 | **Fail** — 320px에서 `scrollWidth 326 > 320`(4화면), 푸터 저작권 13px | 42, 43 → **DEF-004·005** |
| TC-099 | REQ-N-007 | Lighthouse 접근성 | 90+ | **Pass** (전 화면 100) | 39 |
| TC-100 | REQ-N-008 | 폼 오류 상태 마크업 | `label[for]` · `aria-describedby` · `aria-invalid` · 오류 요약 `role="alert"` · 색 외 전달 | **Pass** | 18, 06, 56 |
| TC-101 | REQ-N-009 | 문서 구조 | h1 1개 · 제목 단계 건너뜀 0 · 랜드마크 · skip link | **Pass** (5화면 전건) | 18 |
| TC-102 | REQ-N-010 · REQ-C-016 | title·description ↔ IA §6.2·§6.3 문자열 대조 + 길이 | 문자열 일치 · 50~90자 | **Fail** — 색인 4화면 전건 불일치, 길이 41/33/35/48자 (전건 50자 미만) | 49 → **DEF-001** |
| TC-103 | REQ-N-011 | 메인·오시는 길의 title·description·h1 | '강남'·'요가' 포함 | **Fail** — title·h1에 '강남' 없음 | 49 → **DEF-001** |
| TC-104 | REQ-N-012 | JSON-LD 파싱 + 필수 속성 | 오류 0 · 상호·주소·전화·영업시간·URL | **부분** — JSON 유효·`HealthAndBeautyBusiness`. 주소·전화·영업시간 `[TBD]`로 미포함. IA §6.4의 메인 `WebSite` 미적용. **원 도구(Schema Validator) 검사는 P7** | 20 → DEF-001 |
| TC-105 | REQ-N-013 · REQ-C-018 | `/sitemap.xml`·`/robots.txt`·canonical | 색인 4화면만 포함 · Disallow 0건 · canonical 존재 | **Pass** | 03, pages/ |
| TC-106 | REQ-N-014 | OG 태그 + 이미지 응답 | og:title·description·image·url + twitter:card | **Pass** (5줄 + `og:image:alt`, 이미지 200·30,916B) | 03, 20 |
| TC-107 | REQ-N-015 | Lighthouse SEO·권장사항 | 각 90+ | **Pass** (SEO 100 전건 / 권장사항 메인 92 · 나머지 100) | 39 |
| TC-108 | REQ-N-016 | Nu Html Checker(vnu) 5화면 | 오류 0건 + 랜드마크 존재 | **Fail** — error **5건**(전 화면 `Duplicate ID "ypht"`) | 50 → **DEF-002** |
| TC-109 | REQ-N-017 | 혼합 콘텐츠·절대 URL 스킴 | 경고 0건 | **부분(P7 이월)** — 로컬 http 환경이라 리다이렉트 판정 불가. 외부 http 리소스 0건 확인 | 19 |
| TC-110 | REQ-N-018 | M-4 패턴 저장소 검색 + 이미지 레이어 검색 + `.gitignore` | 실제 비밀 값 0건 · `.env` 미추적 | **Pass** (저장소·이미지 모두 변수명/참조만, `.env*` 이미지 내 0건) | 21, 34 |
| TC-111 | REQ-N-019 | 1차 해당 1종(폼 제출) | 차단 + 안내 + 서버 기록 | **Pass** (조회·로그인·재설정 4종은 2차 → N/A) | 10, 11 |
| TC-112 | REQ-N-020 | `qa_pii_columns` ↔ `privacy.yml` 수집 항목 양방향 대조 | 누락 0건 | **Fail(부분)** — 스키마 6컬럼 중 `consent_at`·`phone_norm`이 방침 표에 없음 | 17b → **DEF-009** |
| TC-113 | REQ-N-021 | 기술 설계 외부 서비스 표 | 사업자·리전·처리 항목 | **Pass** | 문서 |
| TC-114 | REQ-N-022 | 테스트 수신 주소 발송 | 수신 + 본문 항목 | **부분(P7 이월)** — Mailpit 수신·본문 확인. SPF/DKIM/DMARC는 운영 도메인 필요 | 08, 11 |
| TC-115 | REQ-N-023 ① | `check_release` + `deploy.sh --dry-run` | `[TBD]` 잔존 시 **종료 코드 1**, 배포 중단 | **Pass** (`pending=11 sections=[p1..p11]` → exit 1, 배포 0단계에서 중단, `--warn-only` exit 0) | 17b, 29 |
| TC-116 | REQ-N-024 · REQ-C-013 | 빌드 자산 ↔ `design/assets/SOURCES.md` | 누락 0 · 지도 캡처 0 | **부분 Pass** — 지도 캡처 0건·인물 스톡 0장. 목록에 없는 작업 중간 파일 1건 | 51 → **DEF-010** |
| TC-117 | REQ-N-025 | `tokens.css` 팔레트 | 화이트·블루 + 로고 색 조화 + 대비 충족 | **Pass** | 38 |
| TC-118 | REQ-N-026 | 운영 가이드 | 콘텐츠 수정 절차 | **Block** (P8 미작성 · `site/README.md` §4에 `seed_content` 절차만 존재) | — |
| TC-119 | REQ-N-027 | `<html lang>` + 미번역 문자열 | `ko` · 미번역 0 | **Pass** (렌더 5화면 · 오류 문구·메일 본문 한국어) | 03, 12b |
| TC-120 | REQ-N-028 | JS 비활성으로 5화면 로드 | 본문·링크 표시, 헤더·푸터로 전 화면 이동 | **Pass** (본문 307~1,989자, 링크 19~29개, `<details>` 메뉴 동작) | 44 |
| TC-121 | REQ-N-029 | JS 비활성 4분류 | `<noscript>` 안내 + `tel:` | **부분** — 전역 1 + 지도·폼 2 = 3곳 확인. `tel:` 링크는 전화 확정 후(값 주입 시 렌더 확인) | 44, 46 |
| TC-122 | REQ-N-030 (Could) | curl(JS 0)로 7종 응답 재현 | 서버 렌더 응답으로 결과 표시 | **Pass** (①~⑦ 전부 서버 렌더, 제출도 전체 페이지 이동 1회) | 06, 07, 57 |
| TC-123 | REQ-N-031 | `/healthz` · compose 헬스체크 · `ping_health` | 200 `ok` · 부가 정보 미노출 · 자동 재시작 | **Pass** (5서비스 healthy, `/healthz` = `ok` 만, `CLOCK OFFSET` 미노출) | 01, 28 |
| TC-124 | REQ-N-032 ①②③④ | `run_backup` / 실패 주입 / **복구 리허설** | 백업 성공·기록, 실패 시 `backup_failed` 알림, 복구 후 데이터·앱 정상 | **Pass** — 백업 85,533B, 실패 주입 `status=failed` + 알림 1건, **복구 리허설: 17건 → 백업 시점 16건 복원 + `/healthz` 200 + `pre-restore` 자동 덤프** | 22, 23, 24, 25 |
| TC-125 | REQ-N-033 | `deploy.sh --dry-run` / `rollback.sh` 가드 / `sh -n` | 0단계 점검 후 `check_release` 실패로 중단 · 롤백 대상 불명 시 거부 · 문법 통과 | **Fail(부분)** — 배포 차단·문법·없는 태그 거부는 Pass. **무인자 `rollback.sh`가 태그 없는 이미지로 롤백을 실행** | 29, 30 → **DEF-007** |
| TC-126 | REQ-N-034 | `docker compose … up -d`(플래그 없이) + 세 환경 정의 비교 | 앱·DB·프록시 기동 + 구조적 차이 0건 | **Pass** — `down` → `up -d`로 app·db·mail·scheduler·proxy 5서비스 healthy + `backup` 1회성 exit 0. 운영 미리보기는 `mail` **0건**(설계 §3.2 판정 지점 충족) | 01, 35 |
| TC-127 | REQ-N-037 | 1차 메일 1종 + 운영 알림 | 발송 로그(요청·발송 시각) + 실패 기록·재시도 | **Pass** (`inquiry_notify`·`rate_limit_alert`·`backup_failed`·`ops_daily` 로그, SMTP 실패 주입 시 `attempts`·`last_error` 기록) | 08, 11, 16b, 22 |
| TC-128 | REQ-N-038 | `QA_RETENTION_MINUTES__INQUIRY` 단축 → `purge_expired` | 기간 경과분 삭제 + 분류별 건수 기록 + 실패 알림 경로 | **Pass** (365일=0건 → 10분=8건 → 실행 후 16 → 8건, `QA_FAIL_INJECT=purge` 실패 기록) | 26, 27, 28 |
| TC-129 | REQ-N-039 | 운영 DB 권한자 목록 ↔ 배포 계획 대조 | qa 계정 0건 · 백업 파일 위치·권한 문서화 | **Block** — 대조 대상 `devops/07_deploy-plan.md` 미작성(qa R2 Q-10 조건 ① 미충족). 제작 측 몫(`qa_show` 마스킹 고정·해제 옵션 없음)은 확인 | 05, 17b |
| TC-130 | REQ-N-040 | 스테이징 설정 파일 | `auth_basic` + IP 제한 + `noindex` | **부분** — `deploy/nginx/yogapass-stg.conf.sample`·`FORCE_NOINDEX=True`(staging 설정) 확인. 실제 URL 실측은 P7 | 파일 확인 |
| TC-131 | 기술 설계 §10.6 ①~⑤ | 운영 이미지 직접 검사 | 5중 안전장치 동작 | **Pass** — ① `QA_TOOLS_ENABLED` 없으면 종료 코드 2 ② 이미지에 `qa/`·`tests/`·`.env`·`qa_*.py` **0건** ③ prod 이미지 + `QA_TOOLS_ENABLED=1` → production·staging 모두 **기동 거부** ④ `manage.py help`에 `qa_` **0건** ⑤ `config/urls.py`에 `qa` 경로 **0건** | 05, 17b, 33, 34 |

### 2.7 콘텐츠

| TC ID | 관련 REQ | 절차 | 1차 | 증거 |
|---|---|---|---|---|
| TC-140 | REQ-C-001 | 로고 자산 사용 여부 | **부분** — 제작 SVG(`logo-yogapass-*.svg`) 사용 중, 고객 원본 미수령(T-B) | 51 |
| TC-141 | REQ-C-002·003 | 메인 문구·강점 | **Block** (T-G) | 04 |
| TC-142 | REQ-C-004·005 | 강사 정보·사진 | **Block** (T-C) | 47 |
| TC-143 | REQ-C-007·008·010 | 주소·운영시간·사업자 정보 | **Block** (T-E·T-G) — 미확정 행 미렌더 동작은 확인 | 03, 46 |
| TC-144 | REQ-C-013·014 | 이미지 자산·플레이스홀더 규격 | **Pass** (인물 스톡 0장, 지도 캡처 0건, 규격 문서 존재) | 51 |
| TC-145 | REQ-C-015 | 화면 안내 문구 | **Pass** — 빈 상태 문구에 "준비 중" **0건** 확인 | 04, pages/ |
| TC-146 | REQ-C-017 | 파비콘·OG 이미지 | **부분** — `favicon.ico`·`icon-192/512`·`apple-touch-icon` 정상, `og-image.png`는 **임시본**(폰트만 임시) | 51 |

---

## 3. 비기능 점검 체크리스트

| 항목 | 대상 | 1차 | 2차 | 3차 | 증거 |
|---|---|---|---|---|---|
| 반응형 360px | 5화면 | **Pass** (가로 스크롤 0) | | | `42_viewport.txt` |
| 반응형 768px | 5화면 | **Pass** | | | 동 |
| 반응형 1280px | 5화면 | **Pass** | | | 동 |
| 반응형 320px(400% 확대 상당) | 5화면 | **Fail** (4화면 326/320) | | | 동 · DEF-004 |
| Lighthouse 성능(모바일 중앙값) | 4화면 | **Pass** 99·100·99·99 | | | `39_…` |
| Lighthouse 접근성 | 4화면 | **Pass** 100 전건 | | | 동 |
| Lighthouse 권장사항 | 4화면 | **Pass** 92·100·100·100 | | | 동 · DEF-003 |
| Lighthouse SEO | 4화면 | **Pass** 100 전건 | | | 동 |
| Lighthouse 404 화면 | SCR-008 | **Block** — LH CLI가 비200 응답을 `ERRORED_DOCUMENT_REQUEST`로 거부 | | | 동 |
| 깨진 링크 | 전체 | **Pass** 25/25 = 200 | | | `19_…` |
| 콘솔 에러 | 5화면 | **Fail** — 메인 2건(CSP 인라인 스타일 차단) | | | `40_…` · DEF-003 |
| `[TBD` 잔존 (M-5) | 렌더 HTML | **Pass** — `/privacy` 외 0건(`/privacy`는 REQ-F-050 1차 기준상 정상, 배포는 `check_release`가 차단) | | | `04_…` |
| HTML 검증 오류 | 5화면 | **Fail** 5건 | | | `50_…` · DEF-002 |
| 명도 대비 | 18조합 | **Pass** 미달 0건 | | | `38_…` |
| 키보드 탐색·포커스 | `/location` | **Pass** 16스텝 | | | `45_…` |
| 터치 타깃 44px | 360px | **Fail** 5종 | | | `43_…` · DEF-005 |
| 본문 최소 14px | 360px | **Fail** 1종(13px) | | | 동 · DEF-005 |
| JS 비활성 | 5화면 | **Pass** | | | `44_…` |
| 비밀 정보 노출 | 저장소·이미지 | **Pass** 0건 | | | `21_…`·`34_…` |
| 운영 안전장치 5중 | 운영 이미지 | **Pass** | | | `33_…`·`34_…` |
| 복구 리허설 | 로컬 | **Pass** 1회 성공 | | | `24_…`·`25_…` |
| 테스트 데이터 삭제 | 로컬 DB | **Pass** — 최종 `inquiry` **0건** (삭제 30건) | | | `54_…` |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.1 | 2026-09-13 | qa | 최초 작성 — RTM 96건(추적률 100%) + TC 99건 정의 및 1차 사이클 실행 결과 기입 | — |
