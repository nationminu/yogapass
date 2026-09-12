---
doc_id: DEV-REPORT
title: 개발 보고서 — 1차 구현 (1단계 · 스캐폴딩/compose/공통 레이아웃)
phase: P4
owner: developer
version: 0.1
status: draft
reviewers: [designer, planner]
inputs: [developer/04_tech-design.md, planning/02_requirements.md, planning/02_storyboard.md, design/03_design-system.md, design/03_page-design.md, design/mockups/, shared/reviews/P4a_tech-design_devops_r2.md, shared/reviews/P4a_tech-design_qa_r2.md]
updated: 2026-09-13
---

# 개발 보고서 (초안) — 1차 구현 1단계

> **이 문서의 상태**: `draft`. 1차 구현 **14개 작업 중 작업 1~3 + 작업 4(SCR-001) 일부**를 마친 시점의 중간 보고다.
> **규칙**: 이 문서에는 **직접 실행해 확인한 것만** 적는다. 실행하지 않은 항목은 "미확인"으로 적고 "완료"로 쓰지 않는다.
> 설계 근거는 `developer/04_tech-design.md` v0.3, 실행 절차는 `developer/site/README.md`.

---

## 1. 요약

| 항목 | 내용 |
|---|---|
| 구현 범위 | 기술 설계 §11.1 **작업 1(스캐폴딩·설정 분리·compose·`/healthz`) · 작업 2(커스텀 사용자 모델·콘텐츠 모델·`seed_content`) · 작업 3(디자인 토큰 이식·공통 레이아웃·폰트·아이콘)** + **작업 4(SCR-001 메인) 뼈대**. 그 밖에 메일 아웃박스·스케줄러(작업 8의 기반)를 함께 세웠다 |
| 진척(작업 단위) | **3.5 / 14 작업** (설계 산정 약 16작업일 중 약 4.2작업일분) |
| Must REQ 구현률 | **전체 1차 Must 60건 기준 — 완료 9 · 부분 11 · 미착수 40** (§2 표) |
| 로컬 빌드 · 실행 | **성공** — `docker compose … up` 으로 **app·db·mail·scheduler·proxy 5개 서비스 healthy**, `http://localhost:8000` · `http://localhost:8080` 200 (2026-09-13 확인, §4) |
| 운영 빌드 | **성공** — prod 타깃 이미지 빌드 + 운영 미리보기 기동 + 해시 정적 파일·brotli·immutable 캐시 확인 (§4) |
| 자동 테스트 | **9건 전부 통과** (`manage.py test`), `ruff check` 통과 (§5) |
| 검증팀 전달 가능 여부 | **아직 아니다.** 문의 폼(작업 7)·검증 지원 도구(작업 13)가 없어 P5 판정 대상 대부분을 실행할 수 없다. 다만 **환경 구성(REQ-N-034)·기동·404·로그 형식** 은 지금도 확인 가능하다 |

---

## 2. 요구사항별 구현 현황 (REQ ID ↔ 구현 파일)

> 경로는 모두 `developer/site/` 기준이다. **부분**은 "이번 범위의 몫은 끝났고 나머지 화면·기능에서 이어진다"는 뜻이다.

| REQ ID | 요구사항 | 상태 | 구현 위치 | 비고 |
|---|---|---|---|---|
| REQ-F-001 | 공통 헤더 | **완료(1차 화면 기준)** | `templates/partials/header.html` · `static/css/components/nav.css` | 3구간 변형(64/68/72px)·GNB·`aria-current`·모바일 `<details>` 패널·H1~H3 CTA 상태 |
| REQ-F-002 | 공통 푸터 | **완료** | `templates/partials/footer.html` · `static/css/components/layout.css` | 1/2/4열, 미확정 행 미렌더 |
| REQ-F-003 | 전역 주 CTA | **완료** | `apps/core/cta.py` · `templates/partials/fixed_bar.html` | 고정 바 S1~S3 · 헤더 H1~H3 을 **한 판정 함수**로 공유(G-6·G-7) |
| REQ-F-004 | 전화 걸기 링크 | **부분** | `apps/core/templatetags/icons.py`(`tel_href`) · 헤더/푸터/고정 바 | 대표 전화가 `[TBD]` 라 **현재 렌더되는 `tel:` 링크 0건**(의도된 동작). 값이 들어오면 자동 노출 |
| REQ-F-005 | 처리방침 전역 링크 | **부분** | 푸터·모바일 패널 | 링크는 있고 대상 화면(SCR-006)은 작업 9 |
| REQ-F-006 | 화면 간 이동 일관성 | **부분** | `apps/content/services.py`(`nav_items`) | GNB 4항목 단일 원본. 나머지 화면 추가 시 그대로 적용 |
| REQ-F-010 | 메인 Hero | **부분** | `templates/pages/home.html` · `static/css/pages/home.css` | 레이아웃·최소 높이(320/420/520px)·CTA 완료. **헤드라인/서브카피 문구는 `[TBD: T-G]` 라 미노출**(§6 #1) |
| REQ-F-011 | 스튜디오 소개 요약(강점 3~4) | **부분** | `templates/pages/home.html` 섹션 2 | 그리드·카드·아이콘 프레임 구현. 문구 미수령이라 **섹션 미렌더** 상태 |
| REQ-F-012 | 강사 미리보기 | **부분** | 섹션 4 + `apps/content/services.featured_instructors` | 이니셜 아바타 포함. 데이터 0건이라 섹션 미렌더 |
| REQ-F-013 | 위치 요약 | **부분** | 섹션 5 | `<dl>` 3행·브랜드 그래픽(지도 아님)·`/location` 링크. 값 미확정 행은 렌더하지 않는다 |
| REQ-F-014 | 수업 유형 소개 | **부분** | 섹션 3 + `LessonType` | 설명 없는 유형은 렌더하지 않고 전부 없으면 섹션 미렌더 |
| REQ-F-015 | 메인 하단 전환 섹션 | **완료** | 섹션 7 (CMP-025) | |
| REQ-F-021 · REQ-F-064 | 강사·콘텐츠 데이터 분리 | **완료(1차 정의대로)** | `content/*.yml` · `apps/content/models.py` · `apps/content/management/commands/seed_content.py` | **파일 수정 → `manage.py seed_content` 1회 실행**으로 반영(설계 §5.1.1). 실행 확인: `created=11` |
| REQ-F-022 | 강사 사진 대체 처리 | **완료** | `card--instructor` + `.avatar`(CMP-027) | 인물 스톡 미사용 |
| REQ-F-060 | 404 화면 | **완료** | `apps/core/views.page_not_found` · `templates/errors/404.html` | **실제 404 상태 코드** 확인(앱·nginx 경유 모두 404) |
| REQ-F-065 | 공용 오류 화면(5xx·점검) | **부분** | `templates/errors/500.html` · `deploy/nginx/maintenance.html` | 점검 화면은 **외부 자산 0건 자립형**. 앱 다운 상태 검증은 작업 12 |
| REQ-N-001 · 002 | 반응형 4구간 | **부분** | `static/css/tokens.css`(토큰) · 각 컴포넌트 CSS | 모바일 우선 `min-width` 4구간. **실측 확인은 브라우저 도구가 필요해 미수행**(§6 #4) |
| REQ-N-006 · 008 · 009 | 접근성(터치 44px·포커스·랜드마크) | **부분** | `tokens.css` 포커스 블록 · `base.css` · 각 템플릿 | h1 1개·`main[tabindex=-1]`·skip link·`aria-current`·44px 하한 적용. 자동 점검 도구 실행은 작업 10 |
| REQ-N-010~016 | SEO(title·description·canonical·OG·sitemap·robots·구조화 데이터) | **부분** | `templates/partials/meta.html` · `jsonld_localbusiness.html` · `apps/core/sitemaps.py` · `views.robots_txt` | robots(Disallow 0건 + Sitemap 1줄)·sitemap(`SITE_BASE_URL` 기준)·JSON-LD(미확정 속성 제외) 동작 확인 |
| REQ-N-018 | 비밀 정보 분리 | **완료** | `.env.example` · `.gitignore` · `Dockerfile` | `.env` 는 커밋 대상에서 제외됨을 `git status` 로 확인. 운영 이미지 레이어에서 비밀 문자열 검색 0건 |
| REQ-N-019 | 폼·인증 악용 방지 | **부분** | `apps/core/models.RateLimitCounter` · `apps/core/net.py` | 저장소·식별자 해시(IP 원본 미저장)까지. 판정 로직은 작업 7 |
| REQ-N-020 | 개인정보 최소 수집 | **부분** | `apps/core/net.ip_hash` | 솔트 해시만 저장하는 구조 |
| REQ-N-023 | `[TBD]` 노출 금지 | **완료** | 전 템플릿 + `icons.inline_svg` 주석 제거 | 렌더 HTML 에 `TBD` 문자열 **0건** 확인(자동 테스트에 포함) |
| REQ-N-027 | 한국어 | **완료** | `LANGUAGE_CODE=ko-kr` · `<html lang="ko">` | |
| REQ-N-028 · 029 | JS 비활성 동작 · `<noscript>` | **부분** | `<details>` 기반 메뉴 · `templates/partials/noscript.html` | 서버 렌더 HTML 이 기본 산출물. 폼(REQ-N-030)은 작업 7 |
| REQ-N-031 | 헬스 엔드포인트·헬스체크·재시작 | **완료** | `apps/core/views.healthz` · `compose.yaml` · `apps/core/management/commands/scheduler_health.py` | 5개 서비스 healthy 확인. `unless-stopped` 적용 |
| REQ-N-034 | 로컬·스테이징·운영 **동일 compose** | **완료(구조)** | `compose.yaml` · `compose.local.yaml` · `compose.prod.yaml` | 공통 파일 1개 + override 1개 + 환경 변수. **플래그 없는 `up` 으로 프록시까지 기동** 확인 |
| REQ-N-036 | 기본값 거부 권한 레이어 | **완료(1차 골격)** | `apps/core/access.py` · `apps/core/middleware.AccessControlMiddleware` | 공개 경로표 미등록 = 접근 거부 |
| REQ-N-037 | 알림 메일 체계·발송 로그·재시도 | **부분** | `apps/mailer/models.Outbox` · `services.enqueue` · `management/commands/send_outbox.py` | **아웃박스 → 스케줄러 → SMTP → Mailpit 수신까지 실 경로 확인**(§4). 문의 알림 본문은 작업 8 |
| REQ-N-041 · N-004 | 성능(폰트·캐시) | **부분** | `static/css/fonts.css` · WhiteNoise 설정 | 폰트 self-host(unicode-range 92청크 × 400/700) + preload 2개, 해시·brotli·`immutable` 확인. **Lighthouse 측정은 작업 11** |
| REQ-N-017 · 022 · 032 · 033 · 035 · 038 · 039 · 040 | HTTPS·메일 인증·백업·배포/롤백·DB 제약·파기·권한·스테이징 | **미착수** | — | 작업 12(+2차 스키마) 범위 |
| REQ-F-030~035 · F-040~046 · F-050~053 | 오시는 길·문의 폼·처리방침 | **미착수** | — | 작업 6·7·9 |

---

## 3. 화면별 구현 현황 (SCR ID ↔ 페이지 파일)

| SCR ID | 화면 | 상태 | 구현 파일 | 디자인 명세와 차이 (사유) |
|---|---|---|---|---|
| — (공통) | 헤더·푸터·고정 바·스킵 링크 | **완료** | `templates/base.html` · `partials/{header,footer,fixed_bar,skip_link,noscript,meta,jsonld_localbusiness}.html` | 없음. CMP-005 는 디자인 시스템 정본대로 **`<details>` 기반**이고 `aria-expanded` 를 수동 부착하지 않았다 |
| SCR-001 | 메인 | **부분(뼈대)** | `templates/pages/home.html` · `static/css/pages/home.css` · `apps/core/views.home` | ① 7섹션 구조·조건부 렌더 구현. ② **Hero 문구·강점·수업 유형·강사 데이터가 미수령이라 실제 렌더는 "최소 구성"보다 적은 4섹션**(Hero·위치 요약·문의 안내·전환)이다 — 페이지 디자인 §2.3 의 "미수령 시 섹션 미렌더" 규칙을 그대로 따른 결과다(§6 #1) |
| SCR-008 | 404 | **완료** | `templates/errors/404.html` | 실제 404 + `noindex` |
| SCR-009 | 공용 오류·점검 | **부분** | `templates/errors/500.html` · `deploy/nginx/maintenance.html` | 앱 다운 상태에서의 nginx `error_page` 동작 확인은 작업 12 |
| SCR-002 · 003 · 006 | 강사 소개 · 오시는 길 · 처리방침 | **미착수** | — | 작업 5·6·7·9. 현재 `/instructors`·`/location`·`/privacy` 는 **404**이며 공개 경로표(`apps/core/access.py`)에 주석으로 자리를 남겨 두었다 |

---

## 4. 로컬 빌드 · 실행 확인 (2026-09-13)

> **환경**: Windows 11 + Docker Desktop. `docker --version` = **24.0.2**, `docker compose version` = **v2.19.1**.
> 모든 명령은 `developer/site/` 에서 실행했다. 아래는 **실제로 실행한 명령과 그 출력 요지**다.

| # | 항목 | 명령 | 결과 요약 |
|---|---|---|---|
| 1 | 이미지 빌드(dev) | `docker compose -f compose.yaml -f compose.local.yaml build app` | **성공.** `python:3.13-slim` + `postgresql-client` + supercronic(sha1 검증) + pip 5개 |
| 2 | pg_dump 동봉 확인 | `docker compose … run --rm --no-deps app pg_dump --version` | **`pg_dump (PostgreSQL) 17.11`** — 설계 §2.7 의 "클라이언트 17" 충족 |
| 3 | 마이그레이션 생성 | `docker compose … run --rm app python manage.py makemigrations accounts content core mailer` | accounts(User)·content(3)·core(2)·mailer(1) **초기 마이그레이션 4개 생성** |
| 4 | 마이그레이션 적용 | `docker compose … run --rm app python manage.py migrate --noinput` | **19개 마이그레이션 적용 OK** (커스텀 사용자 모델이 첫 마이그레이션에 포함) |
| 5 | 시드 적재 | `docker compose … run --rm app python manage.py seed_content` | `seed_content 완료 created=11 updated=0 dry_run=False` |
| 6 | 전체 기동 | `docker compose -f compose.yaml -f compose.local.yaml up -d` | **app·db·mail·scheduler·proxy 5개 컨테이너 기동.** `.env` 의 `COMPOSE_PROFILES=proxy` 로 **플래그 없이 프록시까지** 떴다(qa R2 #1) |
| 7 | 상태 확인 | `docker compose … ps` | **5개 전부 `healthy`** (app / db / mail / proxy / scheduler) |
| 8 | 앱 직접 응답 | `curl http://127.0.0.1:8000/` · `/healthz` | `200` · `200` |
| 9 | 프록시 경유 응답 | `curl http://127.0.0.1:8080/` | `200` (본문 크기 앱 직접과 동일) |
| 10 | 404 | `curl -o /dev/null -w %{http_code} …/no-such-page` (앱·nginx 양쪽) | **404 / 404** — `proxy_intercept_errors off` 동작 확인 |
| 11 | 후행 슬래시 | `curl …/location/` | `301 → /location` (설계 §6.1) |
| 12 | robots·sitemap | `curl …/robots.txt` · `/sitemap.xml` | `Disallow:` 0건 + `Sitemap:` 1줄 / `<loc>http://localhost:8000/</loc>`(= `SITE_BASE_URL` 기준) |
| 13 | 보안 헤더 | `curl -I …/` | `Content-Security-Policy: default-src 'self' …` · `Permissions-Policy` · `X-Content-Type-Options: nosniff` · `Referrer-Policy` |
| 14 | HTML 압축(주체 = nginx) | `curl -I -H 'Accept-Encoding: gzip' …:8080/` | `Content-Encoding: gzip` (앱 직접 `:8000` 은 비압축 — 설계 §12.3 #4 그대로) |
| 15 | 정적 자산 | `curl` 9개 경로(css·js·woff2·svg) | **전부 200** |
| 16 | 스케줄러 동작 | `docker compose … logs scheduler` | `job.finished job=send_outbox status=success detail=sent=0 failed=0 scanned=0` 이 **1분 주기로** 기록 |
| 17 | 작업 실행 기록 | `psql -c "select job,status,detail from core_jobrunlog …"` | `send_outbox / success` 행 누적 확인 (시각은 Asia/Seoul) |
| 18 | 메일 경로 전체 | `manage.py shell -c "enqueue(...)"` → `manage.py send_outbox` → Mailpit API | `send_outbox sent=1 failed=0`, **Mailpit 수신함에 1통 도착** 확인 |
| 19 | 자동 테스트 | `manage.py test` (`config.settings.test`) | **Ran 9 tests … OK** |
| 20 | 린트·포맷 | `ruff check .` / `ruff format .` | `All checks passed!` / 30파일 포맷 적용 |
| 21 | 운영 이미지 빌드 | `docker compose -f compose.yaml -f compose.prod.yaml build app` | **성공.** `collectstatic` = **207개 복사 / 299개 후처리**, 이미지 태그 `yogapass-app:0.1.0-dev` + 라벨 `org.yogapass.keep=release` |
| 22 | 운영 이미지 내용 | `docker run --rm … ls -a /app` | **`qa/`·`tests/`·`.env` 없음** (설계 §10.6 ② 구조적 제외) |
| 23 | 이미지 비밀 정보 검색 | `docker run --rm … grep -rl '<로컬 DB 비밀번호>' /app` | **0건** (M-4 패턴) |
| 24 | 운영 미리보기 기동 | `ENV_FILE=.env.prodcheck docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck up -d` | app·db·scheduler 기동, **app healthy**, DB 포트 **비게시**, `mail` **0건**(qa R2 #2 판정 지점) |
| 25 | 운영 미리보기 응답 | `curl http://127.0.0.1:8001/` · `/healthz` · `/nope` | `200` · `200` · `404` (gunicorn) |
| 26 | 정적 파이프라인 | `curl -I -H 'Accept-Encoding: br' …/static/css/tokens.<hash>.css` | **해시 파일명** + `Cache-Control: max-age=315360000, public, immutable` + `Content-Encoding: br` |
| 27 | 운영 설정 자체 점검 | `manage.py check --deploy` (production 설정) | **경고 2건만** — `security.W005`(`includeSubDomains` 미설정) · `security.W021`(`preload` 미설정). **설계 §9.5 가 의도적으로 끈 항목**이며 다른 경고·오류는 0건 |
| 28 | 미리보기 정리 | `docker compose … -p yogapass-prodcheck down -v` · `rm .env.prodcheck` | 볼륨·네트워크 제거, 임시 env 파일 삭제 |

**확인하지 않은 것(중요)**

| 항목 | 사유 |
|---|---|
| Lighthouse 4지표 측정 | 측정 조건(M-1: 모바일 프리셋·3회 중앙값)을 만족할 브라우저 실행 환경이 이 작업 환경에 없다. **작업 11에서 수행**하고 결과를 이 문서에 추가한다 |
| 실제 뷰포트(360/768/1280px) 렌더 확인 | 위와 동일. CSS 구간은 작성했으나 **눈으로 확인하지 않았다** |
| Safari·iOS 실기기 | 설계 §10.5 대로 P5 구간. 관측 신호(`html[data-vk-fallback]`)만 구현했다 |
| 백업·배포·롤백 스크립트 | 작업 12 범위. `deploy/crontab` 에도 **구현이 끝난 작업만** 등록했고 나머지는 주석으로 예약했다 |

---

## 5. 자체 테스트

| 항목 | 방법 | 결과 |
|---|---|---|
| 주요 페이지 렌더링 | `curl` + 자동 테스트 | `/` 200 · `/healthz` 200 · 없는 경로 404 · `/location/` 301 — **통과** |
| 공통 레이아웃 규칙 | 자동 테스트 `tests/test_smoke.py` | **h1 1개 · `<main id="main" tabindex="-1">` · skip link 존재 · 렌더 HTML 에 `TBD` 0건** — 통과 |
| CTA 상태 판정(G-6·G-7) | 자동 테스트 (H1/H2/H3 × S1/S2/S3 4조합) | 통과. 전화 미확정 시 **좌측 버튼 미렌더 + 우측 전폭**, 자기 참조 화면은 **바 미노출** |
| 식별자 규칙(§5.5) | 자동 테스트 | `YP-XXXX-XXXX` 형식 + **1,000건 생성 중복 0건** (I·L·O·U 제외 문자 집합) |
| 보안 헤더 | 자동 테스트 + `curl -I` | CSP·nosniff 통과 |
| 메일 경로 | 실제 발송 → Mailpit | 통과(§4 #18) |
| 반응형 (360/768/1280) | — | **미확인** (§4 "확인하지 않은 것") |
| 콘솔 에러 | — | **미확인** (브라우저 미실행) |
| 린트 | `ruff check .` | 통과 |

---

## 6. 알려진 이슈 · 제약

| # | 내용 | 영향 | 계획 |
|---|---|---|---|
| 1 | **메인 화면에 넣을 문구·데이터가 대부분 `[TBD]`** (Hero 헤드라인/서브카피 T-G, 강점 3~4 T-G, 강사 T-C, 수업 유형 T-D, 주소·전화·운영시간 T-E) | 현재 SCR-001 은 **4섹션만 렌더**된다. 화면 골격·조건부 렌더는 검증 가능하지만 **디자인 검토(P4-④)에서 "실제로 보이는 화면"이 목업과 달라 보인다** | 값이 오면 `content/*.yml` 수정 + `seed_content` 1회로 반영된다(코드 변경 없음). **문구를 지어내지 않았다**(CLAUDE.md §8). 수령 일정은 pmo 추적 항목 |
| 2 | **폰트 폴백 메트릭(`size-adjust`·`ascent-override`·`descent-override`)이 잠정값** | 웹폰트 로드 전후 레이아웃 이동(CLS)이 남을 수 있다 | 작업 11에서 360/768/1280px 실측 → 1% 단위 조정 → **designer 1회 확인**. 측정표를 이 문서에 첨부한다(페이지 디자인 D-7) |
| 3 | `requirements.txt` 가 **버전 고정까지만**이고 해시 고정(`--require-hashes`)은 아직 아니다 | 공급망 무결성 검증이 한 단계 약하다 | 작업 12에서 `requirements.lock` 추가 |
| 4 | 실제 브라우저 렌더·Lighthouse·실기기 확인 미수행 | 반응형·성능·접근성 **판정 불가** 상태 | 작업 10·11 + P5 |
| 5 | `backup` compose 프로필은 정의만 되어 있고 **동작하지 않는다**(`manage.py run_backup` 미구현) | `.env.example` 기본값을 `COMPOSE_PROFILES=proxy` 로 두었다(설계 v0.3 §3.2.1 에 사유 기재) | 작업 12 완료 시 `proxy,backup` 으로 바꾼다 |
| 6 | **운영 의존성이 5개 → 6개**로 늘었다(PyYAML) | 설계 §2.1 ⑤(의존성 최소)의 근거가 약간 약해진다 | 시드 파일 형식(YAML)을 설계가 이미 확정했으므로 채택했고 **§2.7 표에 반영**했다. JSON 전환 시 제거 가능 |
| 7 | `deploy/nginx/yogapass-prod.conf.sample` · `yogapass-stg.conf.sample` 미작성 | devops 가 배포 계획서를 쓸 때 필요한 입력 | 작업 12. **`local.conf` 가 같은 지시어 집합의 선행본**이라 옮겨 쓰면 된다 |

---

## 7. 검증팀 전달 사항

- **실행 방법**: `developer/site/README.md` (설치 → 기동 → 자주 쓰는 명령 → 운영 빌드 미리보기 순)
- **지금 검증할 수 있는 것**: 환경 구성(REQ-N-034) · 기동/헬스체크(REQ-N-031) · 404 실제 상태 코드(REQ-F-060) · robots/sitemap · 보안 헤더 · 비밀 정보 분리(REQ-N-018) · 콘텐츠 시드 반영 절차(REQ-F-021·064) · **판정용 로그 형식**(설계 §9.6 — `key=value`)
- **아직 검증할 수 없는 것**: 문의 폼 6종 응답(작업 7) · 메일 알림 본문(작업 8) · 처리방침·오시는 길(작업 6·9) · 백업/배포/롤백(작업 12) · **검증 지원 도구 ①~⑪ 전부(작업 13)**
- **테스트 데이터·계정**: 시드 데이터는 `content/*.yml` 이며 **강사·수업 유형은 0건**(실데이터 미수령). 관리자 계정은 `manage.py createsuperuser` 로 각자 만든다 — **저장소에 계정 값을 두지 않는다**
- **주의**: `QA_TOOLS_ENABLED` 는 기본 `0`이고, `1` + `DJANGO_ENV=production` 조합은 **기동을 거부**한다(확인 완료: 설정 모듈에서 `ImproperlyConfigured`)

---

## 8. 발행·처리한 티켓

| ID | 내용 | 상태 |
|---|---|---|
| — | 이번 작업에서 발행한 티켓 없음 | — |

> 설계 v0.3 §16 Q-10(REQ-N-039 증거 초안 10-14 제공) 티켓은 **qa·devops 양측 동의를 R2 에서 받았으므로 오케스트레이터 경유로 발행 예정**이다(이번 작업 범위 밖).

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.1 | 2026-09-13 | developer | 최초 작성(초안) — 구현 1단계(작업 1~3 + SCR-001 뼈대) 결과와 **실행 명령 28건의 확인 결과** 기록. 미확인 항목(Lighthouse·실뷰포트·실기기·백업/배포)을 명시적으로 분리 | `shared/reviews/P4a_tech-design_devops_r2.md`, `shared/reviews/P4a_tech-design_qa_r2.md` |
