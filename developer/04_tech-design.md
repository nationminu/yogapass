---
doc_id: DEV-TECH
title: 기술 설계서 — 1차(2026-11-06 오픈 범위) + 2차 스키마 선설계
phase: P4
owner: developer
version: 0.3
status: in-review
reviewers: [devops, qa]
inputs: [planning/02_requirements.md, planning/02_information-architecture.md, planning/02_storyboard.md, design/03_design-system.md, design/03_page-design.md, design/mockups/, interviews/2026-09-12_infra-constraints.md, interviews/2026-09-12_booking-rules.md, pm/01_project-plan.md, pm/gates/G3a_design.md, shared/reviews/CR-001_impact_developer_r2.md, shared/reviews/P3_design-docs_developer_r1.md, shared/reviews/P4a_tech-design_devops_r1.md, shared/reviews/P4a_tech-design_qa_r1.md, shared/reviews/P4a_tech-design_devops_r2.md, shared/reviews/P4a_tech-design_qa_r2.md]
updated: 2026-09-13
---

# 기술 설계서 — 강남 요가패스

> **읽는 법**
> 1. 이 문서는 **1차(2026-11-06 오픈: 소개 6화면 + 문의 폼 + full compose)를 구현하기 위한 확정 설계**이고, 동시에 **2차(회원·레슨 예약·상담·관리자 39화면)에서 1차 결정을 되돌리지 않기 위한 선설계**다. 두 목적이 섞이지 않도록 각 절에 **`[1차 구현]` / `[2차 설계만]`** 을 표시했다.
> 2. **§2(스택)·§3(compose)·§5(데이터 모델)·§12(배포·백업)가 이 문서의 본체**다. 나머지는 그 결정의 전개다.
> 3. **R2에서 devops·qa 모두 조건부 승인(신규 Must 0건)** 했고 두 팀 다 R3를 요구하지 않았으므로, v0.3 반영과 함께 **구현 1단계(§11.1 작업 1~3)에 착수했다.** 구현 결과와 실행 증거는 `developer/04_dev-report.md`(P4-③ 초안)에 있다. 이 문서의 설계와 구현이 어긋나면 **구현이 아니라 이 문서를 먼저 고친다.**
> 4. 확정 권한이 없는 값은 `[TBD]`로 두고 **무엇이 막히는지**를 함께 적었다(§14).

> **v0.2 반영 요약 (R1 리뷰 2건 — devops Must 2·Should 9·Could 4 / qa Must 3·Should 10·Could 3)**
>
> | 반영 | 바뀐 것 | 위치 |
> |---|---|---|
> | devops Must #1 | **`backup` 상시 컨테이너를 없애고** 스케줄러가 부르는 `manage.py run_backup`으로 일원화 → 실행 기록·실패 알림·실패 주입이 한 경로 | §3.2 · §3.3 · §12.5 |
> | devops Must #2 | 스테이징에 **nginx basic auth + 출처 IP 제한**, `QA_*`는 `QA_TOOLS_ENABLED=1` 명시 시에만 해석, **검증 도구 HTTP 노출 금지** | §3.5 · §10.6 · §12.3 |
> | qa Must #1 | 문의 폼 **실패·차단 응답 형태 표(6행 × 5열)** 신설 — P5는 이 값으로 판정 | **§9.6(신설)** |
> | qa Must #2 | 로컬 compose에 **`proxy`·`backup` 선택 프로필 추가**(qa 권고 ⓐ 채택) + "동일 구성" 판정 정의 명문화 | §3.2 · §3.5 |
> | qa Must #3 | 스테이징 **배포·롤백·백업 실패 주입·회전 확인을 10-20까지 선행**(P5 창 안), 불가 시 G7 이월을 pmo·PM 합의 사항으로 표시 | §12.6 |
> | Should 19건 | 전건 반영(미반영 0건) — 상세는 §17 처리 대장 | §17 |
>
> **구현 착수 조건**: 이 v0.2가 R2에서 승인되면 §11.1 순서대로 착수한다. 반영 과정에서 늘어난 공수는 **+0.8~1.05작업일**(§11.1 #12 +0.5~0.75 · #13 +0.3)이며, 산정은 **약 15작업일 → 약 16작업일**이 된다. **§11.2의 결론(ⓐ 기준 오픈일 11-06 사용)은 바뀌지 않고, 차이가 5일에서 약 6일로 커진다 — PM 결정 사항이다**(§14.4 PM-1).

> **v0.3 반영 요약 (R2 리뷰 2건 — devops Should 3·Could 2 / qa Should 5·Could 2 · **신규 Must 0건**)**
>
> | 반영 | 바뀐 것 | 위치 |
> |---|---|---|
> | devops #1 | **배포 직전 백업이 조용히 건너뛰어지는 경로를 닫았다** — 스케줄러 정지를 **0.5단계**로 앞당기고, **라벨 백업(`pre-deploy`·`pre-restore`)은 락 충돌 시 `skipped`를 성공으로 보지 않고 배포를 중단**한다 | §12.2 · §12.5.1 · §12.5.3 |
> | devops #2 | **백업 "미실행"도 통지에 걸리게** 판정을 뒤집었다 — 일일 요약 ⓒ를 **"최근 24시간 내 성공 기록이 없으면 `[점검필요]`"** 로, `skipped`는 ⓓ에 별도 집계. `deploy.sh` 0단계 사전 점검에도 같은 규칙 | §3.3 · §12.2 |
> | devops #3 | **`/healthz` 호출은 항상 앱에 직접**(`http://app:8000/healthz`), **nginx 비경유·`SITE_BASE_URL` 미사용** — 스테이징 `auth_basic` 예외 0건과 충돌하지 않는다(자동 롤백 오발동 차단) | §3.3 ⓐ · §3.4 · §3.5.1 ① · §12.2 5단계 |
> | devops #4 (Could) | 로컬 `local.conf`에 **`auth_basic` 블록(주석)과 검증 전용 더미 `htpasswd.dummy`** 를 넣어 REQ-N-040(무인증 401)을 **로컬에서 선검증** 가능하게 했다 | §3.2.1 · §12.3 #8 · §13 #12 |
> | devops #5 (Could) | `${BACKUP_DIR}` 바인드를 **`scheduler`에만** 두고 배포 직전 백업도 `run --rm scheduler` 로 실행 — `app`(외부 노출) 노출면 축소, 비용 0 | §3.5 · §12.2 1단계 |
> | qa #1 | **`.env.example`에 `COMPOSE_PROFILES`** 를 두어 **플래그 없는 `docker compose up`** 으로 프록시까지 뜬다 → REQ-N-034 수용 기준의 문면-실행 간극 0 | §3.2.1 · §3.5 · §8 |
> | qa #2 | **`mail`을 `compose.prod.yaml`에 프로필 `mail`로 정의**하고 스테이징 `.env.staging`에서만 켠다 → 판정 지점 확정(**운영 `ps` 에 `mail` 0건 / 스테이징 1건**) | §3.2 · §3.5 |
> | qa #3 | **폼 빈도 제한의 차단 지속 시간**과 **`Retry-After` 계산식**을 확정 → "429 → 대기 → 200 복귀" TC 작성 가능 | §5.3 · §9.6 ④ |
> | qa #4 | **판정용 로그 라인을 `key=value` 형식으로 고정**하고 **조회 수단**(로컬 `docker compose logs app` / 스테이징 devops 대행)을 명시 → ③honeypot ↔ ⑤토큰 재사용 구분 가능 | §9.6 · §10.2 |
> | qa #5 | **선행 조건 #3·#4를 10-16 종료 시점에 재확인**하고 결과를 즉시 pmo·qa에 통지하는 체크포인트 신설 | §12.6.2 |
> | qa #6·#7 (Could) | `qa/qa_settings.py` 경로 표기 정정 · `developer/site/qa/webkit_checklist.md` 로 경로 명시 | §10.1 ④ · §10.5 ③ |
> | 구현 반영 | 구현 1단계에서 확정된 사실을 표에 반영: **PyYAML 6.0.3 의존성 추가**(시드 파일 파서), 패치 버전 고정값, `deploy/nginx/htpasswd.dummy`·`config/env.py` 파일 추가 | §2.7 · §4 |
>
> **미반영 0건.** Should 8건·Could 4건 전건 반영. 처리 대장은 §17.4.

---

## 0. 이 문서가 확정하는 것 / 확정하지 않는 것

| 구분 | 항목 |
|---|---|
| **확정한다** | 애플리케이션 프레임워크·렌더링 방식·DB·마이그레이션 도구·메일 발송 구조·템플릿/정적 파일 파이프라인(§2) · 로컬/운영 compose 구성(§3) · 디렉토리 구조(§4) · 1차 생성 테이블과 2차 전체 스키마·DB 제약(§5) · URL 규칙과 화면 매핑(§6) · 환경 변수 이름(§7) · 품질 구현 방법(§9) · **문의 폼 응답 형태 6종(§9.6 — REQ-F-042 수용 기준이 P4에 위임)** · 검증 지원 도구 ①~⑪의 구현 방식·출력 규격·공수(§10) · 1차 구현 순서와 일수(§11) · 배포·백업·복구·롤백 절차의 설계와 **백업 실행 주체·실패 알림 경로(§12.5)** |
| **확정하지 않는다** (타 팀·PM 소관) | 운영 nginx 서버 블록의 최종 형태와 반영 절차(devops) · 인증서 발급·갱신 방식(devops, I-2-d) · 도메인(PM·고객, I-9) · SMTP 계정(I-5-b) · 백업 보관 기간·RTO/RPO 확정(devops, I-7-a) · 지도 서비스·분석 도구 선택(고객, T-E) · 2차 관리자 화면 디자인 수준(D-27) |
| **P4 권한으로 확정한 결정 대기 항목** | D-5(빈도 제한 값) · D-6(번호 길이) · D-7(조회 실패 최소 응답) · D-8(파기 배치 실행 수단) · D-9(빈도 제한 저장소) · D-13(WebKit 폴백 구현 방식) · D-28(DB) · D-29(스택 구성안) · D-33(세션·비밀번호 정책 수치) · D-34(시도 제한 값) → **§14.1에 한 표로 모았다** |

---

## 1. 기술 관점 요구사항 요약

> 1차 게이트 판정 모수는 **96건(1차 35 + 공통 61), 그중 Must 60건**이다(요구사항 §7.3). 아래는 그중 **기술 선택이 직접 좌우하는 항목**만 추린 것이다. 전건 대조는 §6·§9와 개발 보고서(P4-③)의 매핑 표에서 한다.

| REQ ID | 요구사항 | 기술적 고려 사항 | 결정 위치 |
|---|---|---|---|
| REQ-N-028 · 029 · 030 | JS 비활성 시 정보 화면 동작 / `<noscript>` 안내 / JS 없는 폼 제출(Could) | **서버 렌더 HTML이 기본 산출물이어야 한다.** 클라이언트 하이드레이션에 의존하면 충족 불가 | §2.2 |
| REQ-N-004 · 007 · 015 | Lighthouse 성능·접근성·SEO·권장사항 각 90+ (모바일, M-1/M-2) | JS 번들 크기·웹폰트·캐시 헤더·압축이 결정 요인. 1차는 사진 0장이라 **한글 웹폰트가 유일한 큰 변수** | §9.4 |
| REQ-N-010~016 | title/description·구조화 데이터·sitemap·robots·canonical·OG·시맨틱 | 라우팅과 메타를 서버에서 생성. `[TBD]` 값은 출력하지 않고 **항목 자체를 렌더하지 않는다** | §9.3 |
| REQ-N-034 | 로컬·스테이징·운영 **동일 compose 구성**, 차이는 환경 변수·override 파일로만 | compose 파일 설계가 요구사항 자체 | §3 |
| REQ-N-031 | 헬스 엔드포인트 + compose 헬스체크 + 재시작 정책 | 앱에 `/healthz` 필요 | §3.4 |
| REQ-N-032 · 033 | 백업·**복구 리허설**(게이트 조건) · 배포·롤백·마이그레이션 적용 절차 | 되돌릴 수 없는 마이그레이션 식별 방침 포함 | §12 |
| REQ-N-035 | **DB 무결성 제약** ① 슬롯 겹침 ② 강사 중복 배정 ③ 상담 중복 신청 | DB 선택을 좌우한 항목 | §2.3 · §5.4 |
| REQ-N-036 | 권한·소유자 검사 **공통 레이어**, 기본값 "거부" | 프레임워크의 인증·미들웨어 체계가 직접 영향 | §2.1 · §5.6 |
| REQ-N-037 | 알림 메일 체계(1차 1종 → 2차 12종) + 발송 로그 + 실패 기록·재시도 | 동기 발송이면 폼 응답이 SMTP 타임아웃에 묶인다 | §2.5 |
| REQ-N-018 | 비밀 정보 `.env` 분리, 저장소·이미지 레이어에 없을 것 | 이미지 빌드 시 시크릿 미포함, 런타임 주입 | §7 · §12.1 |
| REQ-N-019 (+ M-3) | 폼·인증 공통 악용 방지(서버 검증·honeypot·빈도 제한·사용량 알림) **단일 구현** | 상태 저장소 선택(D-9) | §5.3 · §9.5 |
| REQ-N-038 · R-003 | 항목별 보관·자동 파기 배치 + 실패 알림 | 정기 실행 수단(D-8) | §3.3 · §12.5 |
| REQ-N-017 · 022 | 전 구간 HTTPS·리다이렉트 / 메일 발신 인증 | **운영 nginx 소관 + 도메인 확정 후**. 로컬에서 재현 불가 | §13 |
| REQ-N-040 | 스테이징 = 별도 compose 프로젝트 + 별도 DB + 별도 서브도메인 | 같은 파일로 프로젝트명·볼륨만 분리 | §3.5 |
| REQ-F-040~046 | 문의 폼(검증·동의·honeypot·중복 제출 방지·결과 상태 6종·DB 저장·알림) | 1차의 유일한 쓰기 경로 | §5.1 · §9.5 |
| REQ-F-021 · 064 | 콘텐츠 데이터 분리(1차 파일 → 2차 DB·관리자) | 요구사항 §10이 **1차 저장 위치를 P4에 위임**했다 | §5.1.1 |
| REQ-F-030~032 | 지도 클릭 투 로드, 대체 영역 높이 고정(CLS 0) | 외부 도메인 초기 요청 0건 유지 | §9.4 |
| REQ-F-060 · 065 | 404는 **실제 404 상태 코드**, 5xx·점검 화면 | 앱과 프록시 양쪽 설정 | §6.2 · §12.3 |
| REQ-N-R-002 · 010 (2차) | 번호 2종 추측 불가 / 식별 정보 URL·로그 노출 차단 | URL 식별자 전략을 **1차에 고정**해야 2차에 안 뒤집힌다 | §5.5 · §6.1 |
| REQ-N-M-001 (2차) | 비밀번호 해시 | 프레임워크 기본 해시 사용 | §2.1 |

---

## 2. 기술 스택

### 2.0 결론 요약

| 영역 | **확정** | 검토한 대안 | 선택 근거(요약) |
|---|---|---|---|
| 사이트 생성 방식 | **서버 렌더링(SSR) 단일 애플리케이션** — 정적 생성(SSG) 미사용 | 정적 HTML 수작업 / Astro·Eleventy SSG + 별도 API / SPA+API 분리 | 요구사항 §10 말미가 **"1차를 정적 산출물로 만들지 않는다"** 를 이미 확정(2차 "재빌드 없이 반영" 기준). SSR 하나로 JS 비활성 동작·SEO·로그인 분기를 동시에 만족 |
| 프레임워크·언어 | **Python 3.13 + Django 5.2 LTS** | Node.js SSR(Next.js·Remix·SvelteKit) / Laravel / Spring Boot / Rails | §2.1 |
| 데이터베이스 | **PostgreSQL 17** (`postgres:17-alpine`) | MariaDB/MySQL / SQLite | §2.3 (D-28 확정) |
| 마이그레이션 | **Django 기본 마이그레이션** — 배제 제약·부분 유니크·확장 설치까지 **선언형으로 표현 가능** | Prisma·Drizzle + raw SQL 병용 / Alembic / Flyway | §2.4 |
| 스타일링 | **순수 CSS** (디자인 시스템 §1.6 CSS 변수 블록 그대로) + `staticfiles` 해시·압축 | Sass·PostCSS·Tailwind | §2.6 |
| 스크립트 | **바닐라 JS(점진적 향상 전용)**, 번들러·npm 없음 | React·Alpine·htmx | §2.2 |
| 폼 처리 | **Django Forms** — 서버 렌더 POST가 표준 경로, JS는 향상만 | 클라이언트 폼 + JSON API | §9.5 |
| 메일 | **SMTP(Django 이메일 백엔드) + 아웃박스 테이블 + 스케줄러 플러시** | 동기 발송 / Celery+Redis 큐 / 외부 메일 API | §2.5 |
| 정적 파일 서빙 | **WhiteNoise**(앱 컨테이너 내부, 사전 압축 + 불변 캐시 헤더) | 운영 nginx가 직접 서빙 | §2.6 |
| WSGI 서버 | **Gunicorn** (sync worker) | uvicorn/ASGI | 1차·2차 모두 동기 I/O 위주, 운영 단순성 우선 |
| 정기 실행 | **스케줄러 컨테이너**(앱 이미지 재사용 + supercronic) — **백업도 이 경로로 실행**(`manage.py run_backup`) | 호스트 crontab / 앱 내부 스레드 스케줄러 / 별도 backup 상시 컨테이너 | §3.3 · §12.5 (D-8 확정, devops R1 #1) |
| 응답 압축 | 정적 자산 = **WhiteNoise 사전 압축**(brotli·gzip) / **HTML = nginx `gzip`(우리 server 블록 한정)** | Django `GZipMiddleware` | §12.3 (devops R1 #4) |
| 빈도 제한·세션 저장소 | **PostgreSQL 테이블** | Redis 컨테이너 추가 | §5.3 (D-9 확정) |
| 호스팅 전제 | 보유 리눅스 서버(8코어 16GB) · docker compose · **운영 nginx만 재사용**(TLS 종료·리버스 프록시) | — | infra §9 |

### 2.1 프레임워크 — Django 5.2 LTS를 고른 이유

**판단 기준**은 CR-001 영향도 R2 §4.3에서 정한 3가지였다: ① 기존 compose의 런타임(I-2) ② 후속 유지보수자의 언어 ③ 관리자 화면 디자인 수준 합의. **I-2 회신이 "재사용 없음, 운영 nginx만 재사용"으로 나와 ①의 제약이 사라졌다.** 따라서 ②·③과 요구사항 자체의 성격으로 판단했다.

| # | 근거 | 설명 |
|---|---|---|
| **①** | **DB 무결성 제약(REQ-N-035)을 ORM이 선언형으로 표현한다** | CR-001 R2 §2.3 ③에서 "Node ORM은 배제 제약·부분 인덱스를 표현하지 못해 raw SQL 수작업이 필요하다"고 적었다. Django는 `BtreeGistExtension`(확장 설치)·`ExclusionConstraint`(배제 제약)·`UniqueConstraint(condition=…)`(부분 유니크)·`CheckConstraint`를 **모델 정의에 그대로 쓰고 마이그레이션이 자동 생성**된다. **이 프로젝트에서 가장 위험한 3가지 제약이 전부 표준 경로로 들어온다** — 스키마 드리프트 위험과 raw SQL 관리 절차(+0.25작업일)가 사라진다 |
| **②** | **JS 없이 동작하는 HTML이 기본 산출물이다** | REQ-N-028(정보 화면 JS 비활성)·REQ-N-030(JS 없는 폼 제출, Could)이 **추가 공수 없이** 충족된다. Node SSR 프레임워크는 하이드레이션 번들이 기본으로 딸려 오고, 그것을 없애는 설정이 프레임워크마다 달라 Lighthouse 성능 점수의 주 변수가 된다 |
| **③** | **인증·권한·세션·비밀번호 해싱·CSRF·마이그레이션·관리 명령이 프레임워크에 내장** | 2차 REQ-N-036(기본값 거부 공통 권한 레이어)·REQ-N-M-001(해시)·REQ-F-M-010/011(재설정 토큰)의 기반이 표준 제공된다. 관리형 인증 서비스를 쓰지 않기로 한 뒤 늘어난 공수(+0.5~1.0작업일)의 상당 부분을 되돌린다 |
| **④** | **2차 관리자 39화면의 하한선을 프레임워크가 깔아 준다** | Django 관리자를 **저부가 CRUD(강사·유형·공지·회원 조회)** 에 쓰면 CR-001 R2 §4.2 추정대로 **-2.0~-3.25작업일**. 고부가 화면(월 편성 그리드·캘린더·해피콜)은 어차피 직접 만든다. 채택 범위는 2차 D-27 결정과 함께 확정한다(§14.2 T-1) |
| **⑤** | **의존성이 적다** | 운영 의존성 5개(Django·psycopg·gunicorn·whitenoise·Pillow(2차)). npm·번들러·lock 파일·노드 모듈 트리가 없어 이미지가 작고 공급망 위험이 낮다. 인도 후 유지보수자가 읽을 것도 적다 |

**단점과 대응**

| 단점 | 대응 |
|---|---|
| 프런트엔드 상호작용이 많아지면(2차 월 편성 그리드) 서버 렌더만으로는 번거롭다 | 1차는 바닐라 JS로 충분하다. **2차 착수 시 캘린더·편성 그리드에 한해** 경량 수단(htmx·Alpine, 각 ~15KB) 도입 여부를 재평가한다(T-3). 1차 결정에 영향 없음 |
| 프런트(HTML/CSS/JS)와 백엔드 언어가 다르다 | 1차 JS 총량은 4~5파일·수십 줄 수준이라 사실상 단일 언어 프로젝트다 |
| Django 관리자 UI는 디자인 시스템과 모양이 다르다 | 고객 내부 전용이라 대외 영향 없음. 2차 D-27과 함께 PM 결정 |
| Django 6.1 LTS가 2026-08에 나왔다 | **1차는 5.2 LTS로 간다**(2025-04 출시, 패치 성숙, 지원 2028-04까지). 6.1 LTS(지원 ~2029-08) 전환은 **2차 착수 전(2026-12) 평가 항목**으로 등록한다(T-2, 전환 0.25~0.5작업일 예상). 1차 오픈 직전 창(10월)에 출시 3개월 된 메이저를 얹는 위험을 피한다 |

> **탈락 대안 요약** — **Node SSR(Next/Remix/SvelteKit)**: 프런트 표현력은 가장 좋으나 ①(제약 표현)·②(JS 비활성)에서 추가 작업이 생기고, 2차 관리자 39화면을 전량 직접 만든다. **SSG(Astro·Eleventy)**: 1차만 보면 가장 단순하지만 요구사항 §10이 명시적으로 배제했다(2차 전면 재작성). **Laravel·Rails·Spring**: ①~④를 비슷하게 만족하지만 PostgreSQL 배제 제약을 마이그레이션 DSL로 직접 표현하는 범위가 좁거나(raw SQL 필요) 운영 메모리·빌드 복잡도가 크다. **SPA+API 분리**: 화면 수 대비 계층이 두 배가 되고 SEO·JS 비활성 요구와 정면으로 충돌한다.

### 2.2 렌더링 방식 — 서버 렌더 + 점진적 향상

| 항목 | 결정 |
|---|---|
| 기본 | **모든 화면을 서버에서 완성된 HTML로 응답한다.** 클라이언트 프레임워크·하이드레이션 없음 |
| JS 역할 | ⓐ 모바일 메뉴 패널 개폐 ⓑ 폼 blur 검증·글자 수 카운터·전송 중 상태 ⓒ 지도 클릭 투 로드 ⓓ 가상 키보드 대응(G-9 WebKit 폴백)·고정 바/헤더 높이 `ResizeObserver` 보정 ⓔ 주소 복사(Could). **모두 없어도 화면과 폼이 동작한다** |
| 캐싱 | 1차 공개 화면은 로그인 분기가 없으므로 `Cache-Control: public, max-age=0, must-revalidate` + ETag. 정적 자산은 해시 파일명 + `immutable, max-age=31536000` |
| 2차 | 회원·관리자 화면은 `Cache-Control: no-store`(REQ-F-M-008 검증 대상) |

### 2.3 데이터베이스 — PostgreSQL 17 확정 (D-28)

infra §4와 CR-001 R2 §2의 권고를 **그대로 채택**한다. 결정 근거는 §5.4의 제약이며, 애플리케이션 코드가 아니라 **DB가 직접 막는다**는 점이 핵심이다.

| 항목 | 값 | 비고 |
|---|---|---|
| 버전 | **PostgreSQL 17** (`postgres:17-alpine`, 마이너 버전은 빌드 시점에 고정) | 2024-09 출시로 2년 성숙, 지원 2029-11. Django 5.2의 검증 범위 안. (PostgreSQL 18은 Django 6.1 전환 시 함께 검토 — T-2) |
| 확장 | `btree_gist` (배제 제약에 필요) | 마이그레이션 `BtreeGistExtension`으로 설치 |
| 타임존 | 저장은 `timestamptz`(UTC), 앱 `TIME_ZONE=Asia/Seoul`, `USE_TZ=True` | 한국은 서머타임이 없어 30분 그리드 검사를 절대 시각으로 표현할 수 있다(§5.4 ④) |
| 문자셋 | `UTF8` | 전화번호는 숫자만 남긴 생성 컬럼으로 비교(§5.4 ③) |
| 대안 | MariaDB/MySQL을 고르면 §5.4 ①②③을 애플리케이션에서 구현해야 하고 **+1.0~2.0작업일**(CR-001 R2 §2.4) | 마지막 판단 기준은 "운영자가 어느 DB의 백업·복구에 익숙한가"였다 → **§14.3 O-1 확인 요청** |
| SQLite 미채택 | 동시 쓰기·배제 제약·부분 인덱스·타입 안정성이 모두 부족 | — |

### 2.4 마이그레이션 — Django 마이그레이션 단일 체계

- `apps/*/migrations/`에 파이썬 마이그레이션으로 전부 관리한다. **raw SQL(`RunSQL`)은 ⓐ 감사 로그 변경 차단 트리거 ⓑ 데이터 백필에만** 쓰고, 그 외는 선언형 제약으로 표현한다.
- 배포 시 `python manage.py migrate --noinput`을 **앱 컨테이너 기동 전 별도 단계**로 실행한다(중복 적용 방지, §12.2).
- **되돌릴 수 없는 마이그레이션 식별 방침**(REQ-N-033): 컬럼·테이블 삭제, 타입 축소, 기본값 없는 `NOT NULL` 추가, 파괴적 백필은 마이그레이션 파일 상단에 `# IRREVERSIBLE` 주석을 달고 **배포 체크리스트의 사전 백업 필수 항목**으로 표시한다. 롤백은 이미지 태그 되돌리기 + (필요 시) 배포 직전 백업으로 DB 복구다(§12.4).

### 2.5 메일 — SMTP + 아웃박스 테이블 + 스케줄러 플러시

> PM 지시: **"SMTP 구현만 해 두고 계정 연결은 나중"**(infra §8). 계정 값은 환경 변수로 분리하고, 로컬·검증은 메일 수집 컨테이너로 대체한다.

```
[요청 처리 트랜잭션] 문의 저장 + mail_outbox INSERT (같은 트랜잭션 — 로그는 즉시, M-8)
        ↓ 커밋
[스케줄러 컨테이너] 1분마다 manage.py send_outbox → SMTP 발송 → sent/failed 기록, 재시도(지수 백오프, 최대 5회)
        ↓ 실패 지속
[운영 알림] 운영자 수신 주소로 실패 요약 (실패 주입 ⑨ⓐ로 검증)
```

| 왜 이렇게 하는가 | 설명 |
|---|---|
| 동기 발송을 피한다 | SMTP 서버가 느리거나 죽으면 **폼 제출 응답이 그대로 묶인다**(REQ-N-R-006 3초 기준 위반). 저장은 성공했는데 사용자에게 실패로 보이는 상황도 생긴다 |
| Celery·Redis를 넣지 않는다 | 운영 요소가 2개(브로커·워커) 늘고 compose·백업·모니터링 범위가 커진다. **분당 수 건 규모**에 맞지 않는다 |
| REQ-N-037을 그대로 만족 | 발송 로그(종류·수신자·상태·시각·오류)·실패 기록·재시도가 **아웃박스 테이블 한 곳**에 모인다. 2차 12종은 `kind` 값만 늘어난다 |
| 로컬·검증 | `EMAIL_HOST=mail`(Mailpit 컨테이너, SMTP 1025 / UI 8025)로 실제 발송 없이 본문·수신자·도달을 확인한다 |

### 2.6 템플릿·정적 파일 파이프라인 — 빌드 도구 없음

| 단계 | 처리 |
|---|---|
| HTML | Django 템플릿. `base.html` + `partials/`(header·footer·fixed-bar·skip-link·noscript·meta) + `pages/`. 컴포넌트(CMP-001~030)는 **템플릿 partial + CSS 클래스** 1:1 대응(§6.3) |
| CSS | **순수 CSS 파일**. `tokens.css`(디자인 시스템 §1.6 블록을 그대로 복사) → `base.css` → `components/*.css` → `pages/*.css`. 전처리기 없음 — 디자인 시스템이 이미 CSS 변수로 되어 있어 필요가 없다 |
| JS | 바닐라 4~5파일, `defer`. 번들러·npm 없음 |
| 폰트 | Pretendard **static 400/700 × `unicode-range` 분할 subset woff2**를 `static/fonts/`에 포함(§9.4). `OFL.txt` 동봉(SOURCES §2 요건) |
| 아이콘 | Lucide SVG 파일을 `static/icons/`에 두고 **템플릿 태그 `{% icon "phone" %}`로 인라인 삽입**(HTTP 요청 0건, `aria-hidden` 기본, `currentColor` 상속) |
| 수집·해시·압축 | `collectstatic` + **ManifestStaticFilesStorage**(내용 해시 파일명) + **WhiteNoise**(빌드 시 gzip·brotli 사전 압축, `immutable` 캐시 헤더) |
| 왜 WhiteNoise인가 | 운영 nginx는 **남의 자산**이다(I-2-b 권한·절차 미확인, I-2-c 다른 서비스 공유 가능성). 정적 서빙까지 nginx에 맡기면 **호스트 경로 공유 + 설정 추가**가 필요해 결합이 커진다. WhiteNoise를 쓰면 nginx 쪽 요구가 `proxy_pass` + 헤더 전달로 끝난다. 이 규모(공개 6화면·자산 20개 미만)에서 성능 차이는 무의미하다 |

**⚠ 디자인 시스템 §1.6 블록을 복사할 때 적용할 수정 1건** — `:focus-visible` 규칙의 `border-radius: var(--radius-sm)` 선언을 **제거하고 복사**한다. outline이 아니라 요소 자체의 모서리를 바꿔 포커스 순간 버튼·칩 모양이 변한다(P3 리뷰 developer R1 #1, designer 처리 결과 = "구현 시 제거"). 그 외 값은 한 글자도 바꾸지 않는다.

### 2.7 버전 고정 표

| 구성 요소 | 버전 | 이미지·패키지 |
|---|---|---|
| Python | 3.13 | `python:3.13-slim` (앱 이미지 베이스) |
| Django | **5.2 LTS** — 구현 고정값 **5.2.9** | pip |
| psycopg | 3.x (binary) — 구현 고정값 **3.3.5** | pip |
| Gunicorn | 23.x 이상 — 구현 고정값 **26.2.0** | pip |
| WhiteNoise | 6.x (`[brotli]`) — 구현 고정값 **6.12.0** | pip |
| Pillow | 11.x **(2차 강사 사진 리사이즈용, 1차 미설치)** | pip |
| PostgreSQL | **17** | `postgres:17-alpine` |
| Mailpit (로컬·스테이징만) | 최신 안정 | `axllent/mailpit` |
| supercronic (스케줄러) | 최신 안정 | 앱 이미지에 바이너리 포함 |
| **`postgresql-client` (17)** | 17.x | **앱 이미지에 포함** — `manage.py run_backup`이 `pg_dump`·`pg_restore --list`를 호출한다(§12.5). 클라이언트 도구만 설치하며 서버는 설치하지 않는다(이미지 증가 ~15MB) |
| nginx (**로컬 프로필 전용**) | 최신 안정 | `nginx:alpine` — `compose.local.yaml`의 `--profile proxy`에서만 기동. **운영·스테이징은 기존 nginx 재사용이므로 우리 compose에 없다**(§3.2) |
| **PyYAML** (v0.3 추가) | **6.0.3** | pip — `content/*.yml` 시드 파서(§5.1.1). 운영 의존성이 5개 → **6개**가 된다. JSON 으로 바꾸면 뺄 수 있으나 설계 §4가 확정한 파일 형식(사람이 고치는 단일 원본)이 YAML 이라 채택했다 |
| supercronic (구현 고정값) | **v0.2.49** (sha1 검증 후 앱 이미지에 포함) | GitHub release |
| ruff (개발만) | 최신 — 구현 고정값 **0.16.7** | pip (dev) |

> 의존성은 `requirements.txt`에 **정확한 버전 + 해시**로 고정하고, 업그레이드는 별도 작업 단위로 한다. 정확한 패치 버전은 구현 착수 시점에 확정해 `site/README.md`와 개발 보고서에 기록한다.

### 2.8 고객 운영 관점 (콘텐츠 수정 난이도·비용)

| 항목 | 1차 | 2차 |
|---|---|---|
| 강사·수업 유형·주소·전화·운영시간 수정 | `content/*.yml` 수정 → **`manage.py seed_content` 1회 실행이 필요하다**(파일 수정만으로는 반영되지 않는다 — P8 운영 가이드에 명시, qa R1 Q-2 ④) | **관리자 화면에서 직접, 재빌드 없이**(TR-02·TR-03·TR-04) |
| 문구·레이아웃 수정 | 소스 수정 → 배포 | 동일 |
| 월 비용 | 보유 서버 외 **추가 비용 0원**(폰트 OFL·아이콘 ISC, 외부 관리형 서비스 없음). 도메인·SMTP는 고객 기존 자산 | 동일 |
| 운영자가 해야 하는 일 | 백업 확인, 보안 패치, 인증서 갱신 확인 — 절차는 P8 운영 가이드에 기재(REQ-N-026) | 동일 + 월 스케줄 게시 |

---

## 3. 시스템 구성 — docker compose

### 3.1 전제와 확인 항목 (I-2-a ~ I-2-d)

> infra §9가 남긴 파생 확인 4건은 **설계 착수를 막지 않지만 운영 compose의 최종 형태를 가른다.** 아래처럼 **기본안을 정하고 분기만 남긴다.**

| # | 확인 항목 | 이 설계의 **전제(기본안)** | 회신이 다를 때의 영향 |
|---|---|---|---|
| **I-2-a** | 운영 nginx가 **호스트 설치**인가 **컨테이너**인가 | **호스트 설치로 가정.** 앱을 `127.0.0.1:${APP_PORT}`에만 게시하고 nginx가 `proxy_pass http://127.0.0.1:${APP_PORT}`. **v0.2: devops 권고에 따라 `compose.prod.yaml`에 주석 처리된 external network 블록을 미리 넣어** 전환 비용을 더 낮춘다 | 컨테이너면 포트 게시를 없애고 **외부 네트워크(`external: true`)에 앱을 참여**시켜 `proxy_pass http://yogapass-app:8000`. compose 한 블록 차이, **0.25작업일 이내**(devops 동의). **운영팀 미회신 상태이며 devops가 10-09까지 추적한다 — 구현 착수는 막지 않는다** |
| **I-2-a 부수** | 운영·스테이징이 같은 서버 → **`APP_PORT`가 2개 필요** | **설계에는 환경 변수로만 두고 숫자를 박지 않는다**(현 설계 유지 — devops 요청) | 기존 서비스가 쓰는 포트 대역을 피해야 하므로 **값은 devops가 배포 계획서에서 지정** |
| **I-2-b** | nginx 설정 **수정 권한·반영 절차** | devops가 반영한다고 가정. 우리는 `deploy/nginx/yogapass.conf.sample`(서버 블록 예시)만 제공하고 **직접 고치지 않는다** | 우리가 반영해야 하면 P7 devops 작업에 권한 확보가 선행. 설계 변경은 없음 |
| **I-2-c** | 같은 nginx를 **다른 서비스도 쓰는가** | 쓴다고 가정하고 **설정 충돌을 만들지 않는 형태**로만 요청한다(server 블록 1개 추가, `http` 전역 지시어 변경 요청 없음, 별도 로그 파일) | 전역 설정 변경이 필요해지면 devops·운영자 합의 필요. 요청 목록은 §12.3 |
| **I-2-d** | 인증서 **발급·갱신 방식** | devops·운영자 소관. 앱은 `X-Forwarded-Proto`만 신뢰한다 | 앱 설계 영향 없음. 도메인(I-9) 확정 후 P7 |

### 3.2 서비스 구성

> **v0.2 변경 2건** — ① **`backup` 상시 컨테이너를 없앴다.** 백업은 `scheduler`가 부르는 관리 명령(`manage.py run_backup`)이다(devops R1 #1, §12.5). ② **로컬에 `proxy`(nginx)를 선택 프로필로 추가**했다(qa R1 #2, 아래 §3.2.1).

```
[로컬]  기본: docker compose … up                      [운영 · 스테이징]
        선택: … --profile proxy --profile backup
 브라우저 → http://localhost:8000                 인터넷 → (기존) nginx :443  TLS 종료
     │        (--profile proxy 시 :8080 = nginx)        │  proxy_pass  (+스테이징: auth_basic)
  ┌──▼───────┐  ┌──────────┐                     ┌─────▼────┐  ┌──────────┐
  │   app    │──│    db    │                     │   app    │──│    db    │
  │ runserver│  │ postgres │                     │ gunicorn │  │ postgres │
  └──┬───────┘  └──────────┘                     └─────┬────┘  └──────────┘
     │                                                 │
  ┌──▼────────┐  ┌──────────┐                    ┌─────▼─────┐
  │ scheduler │  │   mail   │                    │ scheduler │  ← send_outbox / purge_expired /
  │supercronic│  │ Mailpit  │                    │supercronic│     run_backup / report_failures
  └───────────┘  └──────────┘                    └───────────┘
   (백업도 여기)   (스테이징 필수)                  (백업도 여기 — 별도 컨테이너 없음)
```

| 서비스 | 로컬 | 운영·스테이징 | 이미지 | 비고 |
|---|---|---|---|---|
| `app` | ○ (`runserver`, 소스 바인드 마운트, 자동 리로드) | ○ (`gunicorn`, 이미지 내 소스) | 같은 Dockerfile의 `dev`/`prod` 타깃 | 운영은 비루트 사용자로 실행 |
| `db` | ○ (포트 `127.0.0.1:5432` 게시 — 로컬 조회용) | ○ (**포트 게시 없음**, 내부 네트워크만) | `postgres:17-alpine` | 명명 볼륨 |
| `mail` | ○ (Mailpit, SMTP 1025 / UI `localhost:8025`) | **스테이징 필수** / 운영 미배치 | `axllent/mailpit` | qa R1 #6 — "선택적"을 **필수**로 확정. **갈라내는 수단(v0.3, qa R2 #2): `compose.prod.yaml`에 프로필 `mail`로 정의하고 스테이징 `.env.staging`의 `COMPOSE_PROFILES=mail`로만 켠다. 운영 `.env`에는 넣지 않는다 → 판정 지점 = 운영 `docker compose ps`에 `mail` 0건 / 스테이징 1건.** 스테이징에 실제 SMTP 계정이 연결되면 그때 `EMAIL_HOST`를 교체하고 Mailpit을 내린다 |
| `scheduler` | ○ | ○ | app 이미지 재사용 | supercronic + `deploy/crontab`. **백업·파기·아웃박스·요약 알림을 전부 여기서 실행**(§3.3) |
| `proxy` (nginx) | **△ 선택 프로필 `proxy`** — `http://localhost:8080` | ✕ (**기존 nginx 재사용 — 우리 compose에 포함하지 않는다**) | `nginx:alpine` + `deploy/nginx/*.conf.sample` 마운트 | §3.2.1 |
| `backup` | **△ 선택 프로필 `backup`** — `scheduler`와 같은 명령을 짧은 주기로 도는 1회성 실행자 | **서비스로 존재하지 않는다** (`scheduler`가 수행) | app 이미지 재사용 | §3.2.1 · §12.5 |

#### 3.2.1 로컬 선택 프로필 `proxy`·`backup` (qa R1 #2 — REQ-N-034 · devops R1 #3)

| 프로필 | 기동 | 무엇을 로컬에서 선검증하게 되는가 | 왜 기본 기동이 아닌가 |
|---|---|---|---|
| `proxy` | **`docker compose -f compose.yaml -f compose.local.yaml up`** (플래그 불필요 — `.env`의 `COMPOSE_PROFILES=proxy` 가 켠다, v0.3/qa R2 #1) → `http://localhost:8080` | §12.3에서 **기존 nginx에 요청할 설정 9행을 그대로 로컬에서 적용·확인**한다: `proxy_intercept_errors off`(→ REQ-F-060 실제 404), `X-Forwarded-*` 전달과 `TRUSTED_PROXY_COUNT` 동작(§13 #6 — TR-3 Critical급), HTML `gzip`(§13 #11), `error_page 502 503` 정적 점검 화면(§13 #9), 별도 로그 파일. **스테이징 지연(TR-2·TR-5) 시의 방어선**이 된다 | 일상 개발에서는 `:8000` 직접 접근이 빠르고 `runserver`의 자동 리로드·디버그 경로가 단순하다. **프로필은 검증·재현용**이며 `compose.local.yaml` 안에 정의되어 있으므로 누구나 같은 명령으로 켤 수 있다 |
| `backup` | 같은 방식(`COMPOSE_PROFILES=proxy,backup`) 또는 `… run --rm scheduler python manage.py run_backup` (devops R2 #5 — 백업 디렉토리는 `scheduler`에만 붙인다) | `run_backup`의 정상 경로·회전·`pg_restore --list` 검증·**실패 주입 ⑨ⓑ**(`QA_FAIL_INJECT=backup`)·`core_jobrunlog` 기록·`mailer_outbox`의 `kind=backup_failed` INSERT를 **로컬에서 전부 재현**한다(qa R1 #2 부수 영향 해소 — 백업 판정이 스테이징에만 의존하지 않는다) | 로컬 디스크에 덤프 파일이 쌓이는 것을 기본 동작으로 두지 않기 위함. `${BACKUP_DIR}`는 로컬에서 `./backups`(`.gitignore` 대상) |

**"세 환경 동일 구성"의 판정 정의 (REQ-N-034 수용 기준 대조용 — devops R1 #3)**

> `compose.yaml`(공통 정의)이 **세 환경에서 바이트 단위로 동일**하고, 차이는 **override 파일 1개와 환경 변수에만** 있다.
> **애플리케이션 스택 `app`·`db`·`scheduler`는 3환경 모두 동일하게 존재**한다.
> `proxy`·`backup`·`mail`은 **환경 전용 보조 서비스**이며 override에서만 정의된다 — 로컬은 프로필로 **켤 수 있고**(구조가 없는 것이 아니다), 운영·스테이징의 프록시는 **기존 nginx**가, 백업은 **`scheduler`의 작업**이 담당한다.
> 따라서 **"로컬에서 앱·DB·프록시가 모두 뜨고 사이트가 동작한다"는 수용 기준은 `--profile proxy`로 충족**되고, **"구조적 차이 0건"은 위 정의로 판정**한다.

**v0.3 보강 (qa R2 #1 — 문면-실행 간극 0)**: `.env.example`에 **`COMPOSE_PROFILES`** 키를 두고 기본값을 `proxy`(작업 12에서 `run_backup` 구현이 끝나면 `proxy,backup`)로 둔다. compose 가 이 환경 변수로 프로필을 켜므로 **문서가 안내하는 명령과 수용 기준이 적은 명령이 같아진다** — `docker compose -f compose.yaml -f compose.local.yaml up` 한 줄로 `app`·`db`·`proxy` 가 함께 뜬다(2026-09-13 실행 확인: 5개 서비스 healthy). 일상 개발에서 끄고 싶으면 `.env`에서 값을 비우면 되므로 "기본 기동이 아닌 이유"의 취지도 유지된다. planner 문구 정렬 요청은 하지 않는다(qa R2 Q-9 회신 = 정렬 불필요).

- **planner 티켓 경로와 비용(채택하지 않았을 경우의 대안 — 기록용)**: 프로필을 만들지 않았다면 planner에게 **REQ-N-034 수용 기준 문구 정렬**(프록시·백업의 로컬 제외 명시)을 티켓으로 요청해야 했다. 비용은 문서 작업 자체(0.1작업일)보다 **일정 리스크**가 크다 — 요구사항 개정 → planner 반영 → qa 판정 기준 갱신 → G5a 전 종결까지 팀 3곳을 거치고, 그 사이 §13의 스테이징 판정 5건이 스테이징 가용에만 묶인다. **프로필 추가(+0.5작업일, §11.1 #12)가 더 싸고 검증 이득이 크다고 판단해 ⓐ를 채택**했다.
- 다만 **요구사항 문면의 "리버스 프록시·백업"이 로컬 기본 기동을 뜻하는지**는 planner·qa와 한 번 맞추는 것이 안전하다. **이 문서의 판정 정의로 충분한지 확인**을 R2에서 요청한다(§16 Q-9).

### 3.3 스케줄러 (D-8 확정 — 컨테이너 스케줄러)

| 작업 | 주기 | 1차 | 2차 | 명령 |
|---|---|---|---|---|
| 메일 아웃박스 플러시·재시도 | 1분 | ○ | ○ | `manage.py send_outbox` |
| **DB 백업 + 무결성 확인 + 회전** | **일 1회 03:00** | **○** | ○ | **`manage.py run_backup`** (devops R1 #1 — §12.5) |
| 보관 기간 경과 자동 파기 | 일 1회 03:10 | ○ (문의 내역) | ○ (9개 분류) | `manage.py purge_expired` |
| 빈도 제한 카운터 정리 | 시간 1회 | ○ | ○ | `manage.py prune_rate_limit` |
| **일일 운영 요약 알림** (구 `report_failures` 확장) | 일 1회 08:00 | ○ | ○ | **`manage.py report_failures`** — 아래 |
| 게시 기한 알림(25·28·말일) | 일 1회 | ✕ | ○ | `manage.py notify_unpublished` |
| 예약 상태 자동 전이 확인 | 일 1회 | ✕ | ○ | `manage.py roll_booking_states` |

- **호스트 crontab을 쓰지 않는 이유**: 로컬·스테이징·운영에서 동일하게 재현되지 않고(REQ-N-034 위반), 호스트에 우리 서비스의 지식이 새어 나간다.
- **앱 프로세스 내부 스케줄러(스레드)를 쓰지 않는 이유**: gunicorn 워커가 여러 개면 중복 실행되고, 재시작 시 실행이 누락된다.
- 모든 관리 명령은 **재실행 안전(idempotent)** 하게 만들고 `--dry-run`과 실행 기록(`core_jobrunlog`)을 둔다.
- **동시 실행 방지**: 각 명령은 `core_jobrunlog`에 **작업 이름 기준 어드바이저리 락**(`pg_try_advisory_lock`)을 잡고 시작한다. 이미 실행 중이면 즉시 종료하고 `status=skipped`로 남긴다(1분 주기 작업이 밀렸을 때의 중복 실행 차단).

**일일 운영 요약 메일 (devops R1 #9 — 장애 인지 수단)**

`report_failures`를 "실패가 있을 때만 보내는 알림"에서 **매일 1통 보내는 운영 요약**으로 확장한다. 외부 감시 도구를 도입하지 않는 대신(REQ-N-031 범위 밖), 운영자가 **메일 1통으로 상태를 인지**하는 것이 유일한 수단이기 때문이다.

| 포함 항목 | 출처 | 무엇을 알려 주는가 |
|---|---|---|
| ⓐ 앱 `/healthz` 폴링 결과(최근 24시간 성공/실패 횟수) | 스케줄러가 5분마다 `/healthz`를 호출해 `core_jobrunlog`에 기록. **호출 대상은 항상 앱에 직접(`http://app:8000/healthz`) — nginx 를 경유하지 않고 `SITE_BASE_URL`을 쓰지 않는다**(v0.3, devops R2 #3). 그래서 스테이징의 `auth_basic` 예외 0건 정책과 충돌하지 않는다 | **`unless-stopped`가 잡지 못하는 "살아 있지만 응답 실패" 상태**(devops R1 #15) |
| ⓑ 컨테이너 재시작 횟수 | `docker` 소켓을 마운트하지 않기 위해 **앱 기동 시각(프로세스 시작 시간)** 을 기록해 비교 | 반복 크래시 |
| ⓒ **최근 24시간 내 `run_backup` 성공 기록의 존재 여부**·파일 크기·소요 시간 | `core_jobrunlog`의 `run_backup` | REQ-N-032 ③. **v0.3 판정 반전(devops R2 #2 ①): "성공 기록이 없으면(실패·`skipped`·기록 자체 없음 전부) `[점검필요]`".** 실패가 아니라 **실행되지 않은 경우**를 잡기 위한 것이며, 같은 규칙을 `deploy.sh` 0단계 사전 점검에도 쓴다 |
| ⓓ 아웃박스 실패 건수·배치 실패 건수 · **`skipped` 건수(작업별 별도 집계)** | `mailer_outbox` · `core_jobrunlog` | REQ-N-037 · REQ-N-038. **`skipped` 반복은 락 경합/설계 문제의 신호**이므로 실패와 분리해 보여 준다(v0.3, devops R2 #2 ②) |
| ⓔ 디스크 여유율(`${BACKUP_DIR}`가 있는 파일시스템) | `shutil.disk_usage` | 백업 중단의 최다 원인 |
| ⓕ 빈도 제한 차단 건수(사용량 알림 임계 §5.3) | `core_ratelimitcounter` | REQ-N-019 |

- **스케줄러는 `app`과 별도 프로세스**라 **app이 죽어도 db·SMTP만 살아 있으면 이 메일은 발송된다** — 그래서 장애 인지 수단이 된다.
- 수신자는 `OPS_ALERT_TO`. 실패 항목이 하나라도 있으면 **제목 앞에 `[점검필요]`** 를 붙인다.
- 이 메일 1통이 **P8 운영 가이드의 "정기 점검" 절차를 대체**한다(devops R1 §5 목록 "일상" 항목).
- **`scheduler` 는 단일 실패점이다**(백업·아웃박스·요약이 한 컨테이너에 있다 — devops R2 #2 ③). 설계로 없애지 않고 **인지 수단으로 받는다**: ⓐ **"요약 메일이 오지 않는 날 자체가 이상 신호"** 를 P8 운영 가이드 1번 항목으로 쓰고 **수신 시각·제목 규칙을 고정**한다(부재를 인지할 수 있어야 한다) ⓑ `scheduler` 헬스 상태를 **§12.2 5단계 배포 확인 항목**에 넣는다.
- 공수: **+0.25작업일**(§11.1 #12에 포함).

### 3.4 헬스체크·재시작·로그 (REQ-N-031 · 033)

| 서비스 | 헬스체크 | 재시작 |
|---|---|---|
| `db` | `pg_isready -U $POSTGRES_USER` (10s/5s/10회) | `unless-stopped` |
| `app` | `GET /healthz` → DB 연결 1회 확인 + 200 (15s/5s/5회, `start_period` 20s) | `unless-stopped` |
| `scheduler` | **supercronic 프로세스 생존** + `core_jobrunlog`에 최근 10분 내 기록 1건 이상 | `unless-stopped` |
| `proxy`(로컬 프로필) | `nginx -t` 통과 + `:80` 응답 | `unless-stopped` |

- `/healthz`는 **`noindex` + 캐시 금지 + 개인정보·버전 정보 미노출**. **호출 주체가 셋(컨테이너 헬스체크 · 스케줄러 5분 폴링 · `deploy.sh` 5단계)인데 전부 앱에 직접 호출한다**(`http://app:8000/healthz` 또는 `http://127.0.0.1:${APP_PORT}/healthz`) — **nginx 를 경유하지 않으며 `SITE_BASE_URL`을 쓰지 않는다**(v0.3, devops R2 #3). 배포 스크립트가 이 엔드포인트로 기동 성공을 판정한다(§12.2). **`QA_CLOCK_OFFSET_SECONDS` 적용 여부를 `/healthz`에 노출하지 않는다**(qa R1 Q-4 — 확인은 기동 로그 1줄로 한다, §10.5).
- 로그: 전 서비스 `json-file` 드라이버 + `max-size: 10m`, `max-file: 5`(로그 회전).
- **`unless-stopped`는 "종료"만 잡고 "unhealthy"는 잡지 않는다**(devops R1 #15). 자동 복구기(autoheal)는 운영 요소를 늘리므로 도입하지 않고, **인지 수단만 §3.3의 일일 운영 요약 메일 ⓐ로 확보**한다. REQ-N-031 수용 기준(강제 종료 → 자동 재기동)은 `unless-stopped`로 충족된다.
- **`backup` 서비스는 없다** — 백업은 `scheduler`의 작업이다(§12.5).

### 3.5 파일 배치와 환경 분리 (REQ-N-034 · REQ-N-040)

```
site/
├── compose.yaml            # 공통 정의 (app·db·scheduler, 네트워크·볼륨·헬스체크)
├── compose.local.yaml      # 로컬 override  (runserver, 바인드 마운트, mail, 포트 게시,
│                           #                 선택 프로필: proxy · backup)
└── compose.prod.yaml       # 운영·스테이징 override (gunicorn, 이미지 태그, 포트 비게시)
```

| 환경 | 실행 | 구분 수단 |
|---|---|---|
| 로컬 | `docker compose -f compose.yaml -f compose.local.yaml up`<br>(프로필은 `.env`의 `COMPOSE_PROFILES` 가 켠다 — 플래그 불필요, v0.3/qa R2 #1) | `.env`(개발 값) |
| 스테이징 | `ENV_FILE=.env.staging docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-stg up -d` | **`COMPOSE_PROJECT_NAME=yogapass-stg` + 별도 `.env.staging` + 별도 볼륨 + 별도 포트 + 별도 서브도메인 + `X-Robots-Tag: noindex` 강제 + nginx `auth_basic`(아래)** |
| 운영 | `ENV_FILE=.env docker compose -f compose.yaml -f compose.prod.yaml -p yogapass up -d` | `.env`(운영 값, 서버에만 존재). **`COMPOSE_PROFILES` 를 비워 `mail` 을 띄우지 않는다**(qa R2 #2) |

- **세 환경의 `compose.yaml`은 같은 파일이다.** 차이는 override 파일 1개와 환경 변수뿐 → REQ-N-034의 "세 환경 compose 정의 diff" 검증이 `compose.local.yaml` vs `compose.prod.yaml` 한 쌍으로 끝난다. **판정 정의는 §3.2.1 말미**를 따른다.
- 볼륨: `pgdata`(DB) · `media`(2차 업로드) · 호스트 바인드 `${BACKUP_DIR}`(운영·스테이징은 호스트 경로, 로컬 프로필은 `./backups`). **백업 디렉토리는 `scheduler`(와 로컬 `backup` 프로필)에만 붙이고 `app` 에는 붙이지 않는다**(v0.3, devops R2 #5).
- **구현 사실(v0.3)**: 환경별 `.env` 선택은 `compose.yaml` 의 `env_file: ["${ENV_FILE:-.env}"]` 로 한다 — 파일은 그대로 두고 **`ENV_FILE` 값만 바꿔** 스테이징(`.env.staging`)·운영(`.env`)을 가른다. 이렇게 해야 §3.5 표의 "세 환경이 같은 `compose.yaml`" 이 실제로 성립한다.

#### 3.5.1 스테이징 접근 제어 (REQ-N-040 · REQ-N-039 — devops R1 #2 **Must**)

> **문제**: `X-Robots-Tag: noindex`만으로는 REQ-N-040 수용 기준("색인 차단 = `noindex` **+ 인증**")을 충족하지 못한다. 게다가 스테이징은 검증용 기능(임의 세션 발급·개인정보 조회·빈도 제한 해제)이 켜지는 환경이고 실데이터 **형태**의 시드가 들어간다. 무인증 공개 URL이면 §10.6이 스스로 "Critical"이라고 규정한 상태가 그대로 성립한다.

**① 네트워크 계층 — 인증을 필수로 둔다 (nginx, 스테이징 server 블록 한정)**

| 장치 | 내용 | 비고 |
|---|---|---|
| `auth_basic` | 스테이징 server 블록 전체에 **HTTP Basic 인증**을 건다. 예외 경로 **0건**. **v0.3 정정(devops R2 #3): "외부에서 오는 `/healthz` 는 인증 뒤에 둔다 — 내부 호출은 nginx 를 거치지 않는다."** 헬스체크·스케줄러 폴링·`deploy.sh` 5단계는 모두 앱에 직접 호출하므로 영향이 없다. 다만 **5단계의 "주요 4경로 200 확인"은 공개 화면이라 프록시 경유가 의미 있으므로 스테이징에서는 인증 자격으로 호출**한다 — 자격 취득·주입 방식은 devops 배포 계획서 소관이며 값은 스크립트·문서에 하드코딩하지 않고 환경 변수로 넣는다 | **server 레벨 지시어**라 운영·타 서비스 블록에 영향 없음(I-2-c 충돌 0건) |
| 출처 IP 제한 | 가능하면 `allow`/`deny`로 **운영팀·제작팀 출처만 허용**(2중 방어). 출처가 고정되지 않으면 basic auth 단독으로 둔다 | devops 판단 |
| `X-Robots-Tag` | `noindex, nofollow` 전 응답 강제(앱 + nginx 양쪽) | 기존 유지 |
| 계정 전달 | **`.htpasswd` 생성과 계정 전달 방식은 devops가 배포 계획서에 정한다. 값(아이디·비밀번호)은 이 문서를 포함한 어떤 산출물에도 쓰지 않는다** | CLAUDE.md §8 |
| 판정 | qa는 **인증 없이 스테이징 URL 요청 → 401** 응답을 증거로 REQ-N-040을 판정한다 | §13 #12 |

**② 애플리케이션 계층 — 검증용 기능은 "환경"이 아니라 "명시 스위치"로 켠다 (v0.2 변경)**

| 규칙 | v0.1 | **v0.2 확정** |
|---|---|---|
| `QA_*` 해석 조건 | `DJANGO_ENV`가 `production`이 아니면 해석 | **`QA_TOOLS_ENABLED=1`이 명시된 경우에만 해석한다. 기본값은 off이며 `staging`도 예외가 아니다** |
| 노출 형태 | 명시 없음 | **`qa_session`·`qa_show`·`qa_mail_log`·`qa_pii_columns`·`qa_purge_test_data`는 HTTP 경로로 노출하지 않는다. 전부 `manage.py` 관리 명령이며 컨테이너 셸 접근이 있어야 실행된다.** 웹으로 도달 가능한 검증용 엔드포인트는 **0개**다 |
| 운영 | `DJANGO_ENV=production` + `QA_*` → 기동 거부 | 유지 + **prod 이미지에는 파일 자체가 없다**(§10.6) |

**③ 규칙 — 검증용 기능이 켜진 환경은 외부에 열지 않는다 (1줄 원칙)**

> **`QA_TOOLS_ENABLED=1`인 환경은 반드시 인증(최소 basic auth) 뒤에 둔다.** 인증을 걸 수 없는 환경에서는 `QA_TOOLS_ENABLED`를 켜지 않는다.
> 이 원칙을 **기동 시 자체 점검**으로도 강제한다 — `QA_TOOLS_ENABLED=1`이면서 `DJANGO_ENV=production`이면 기동 거부, `QA_TOOLS_ENABLED=1`이면 **기동 로그에 `QA_TOOLS: ON — 이 환경은 인증 뒤에 있어야 합니다` 경고 1줄**을 남겨 배포 로그에 증거가 남게 한다.
> 실데이터(운영 DB 덤프)를 스테이징에 복제하지 않는다 — 스테이징 시드는 `TEST-` 접두어가 붙은 합성 데이터만 쓴다(§10 ⑤, REQ-N-039).

---

## 4. 디렉토리 구조 (`developer/site/`)

```
developer/site/
├── README.md                     # 설치·실행·빌드·배포 방법 (재현 가능해야 한다)
├── .env.example                  # 값 없는 키 목록만
├── .gitignore                    # .env, __pycache__, /staticfiles, /media, /backups
├── .dockerignore                 # qa/, .env, .git, 개발 전용 파일
├── Dockerfile                    # 멀티스테이지: base → dev / prod
├── compose.yaml / compose.local.yaml / compose.prod.yaml
├── requirements.txt              # 운영 의존성(버전·해시 고정)
├── requirements-dev.txt          # ruff 등
├── pyproject.toml                # ruff 설정
├── manage.py
│
├── config/                       # Django 프로젝트 설정
│   ├── settings/{base,local,staging,production,test}.py
│   ├── env.py                    # 환경 변수 해석 헬퍼 (v0.3 — 외부 의존성 대신 자체 구현)
│   └── urls.py · wsgi.py
│                                 # ⚠ v0.2: 검증 전용 설정 해석기를 config/에서 qa/로 옮겼다
│                                 #    (qa R1 #4 — prod 이미지에서 구조적으로 제외하기 위함)
│
├── apps/
│   ├── core/        # 공통: 레이아웃 헬퍼, /healthz, 시각 제공자(clock), 빈도 제한,
│   │                #       감사 로그, icon 템플릿 태그, 메타·canonical, 미들웨어(기본거부·보안헤더)
│   ├── content/     # [1차] 강사·수업유형·사이트 설정 + seed_content 명령
│   ├── inquiry/     # [1차] 문의 폼 (모델·폼·뷰·검증)
│   ├── mailer/      # [1차] 아웃박스·발송 로그·메일 템플릿·send_outbox
│   ├── accounts/    # [1차 최소: 사용자 모델] [2차: 가입·로그인·재설정·탈퇴]
│   ├── booking/     # [2차] 슬롯·월 편성·예약
│   ├── consult/     # [2차] 상담 신청·조회·해피콜
│   └── backoffice/  # [2차] 관리자 셸·커스텀 관리 화면
│
├── templates/
│   ├── base.html
│   ├── partials/    header.html · footer.html · fixed_bar.html · skip_link.html ·
│   │                noscript.html · meta.html · jsonld_localbusiness.html
│   ├── components/  button.html · card.html · form_field.html · error_summary.html ·
│   │                result_block.html · callout.html · map_placeholder.html · toc.html …
│   ├── pages/       home.html · instructors.html · location.html · privacy.html · terms.html
│   ├── errors/      404.html · 500.html · maintenance.html
│   └── mail/        inquiry_notify.txt …
│
├── static/
│   ├── css/         tokens.css · base.css · components/*.css · pages/*.css
│   ├── js/          menu.js · form.js · map.js · viewport.js · clipboard.js
│   ├── fonts/pretendard/  *.woff2 + OFL.txt
│   ├── icons/       *.svg (Lucide, ISC)
│   └── img/         logo · favicon · og
│
├── content/                      # 시드 데이터 (단일 원본)
│   └── instructors.yml · lesson_types.yml · site.yml · privacy.yml
│
├── deploy/
│   ├── entrypoint.sh · gunicorn.conf.py · crontab
│   ├── deploy.sh · rollback.sh · migrate.sh
│   ├── restore.sh                     # 복구(가드 포함, §12.5). 백업 생성은 manage.py run_backup
│   └── nginx/
│       ├── yogapass-prod.conf.sample  # 운영 server 블록 예시 (devops 확정)
│       ├── yogapass-stg.conf.sample   # 스테이징 server 블록 예시 (auth_basic·noindex 포함)
│       ├── local.conf                 # 로컬 proxy 프로필이 그대로 마운트해 쓰는 설정 (§3.2.1)
│       ├── htpasswd.dummy             # 검증 전용 더미 자격 (v0.3 — REQ-N-040 로컬 선검증, devops R2 #4)
│       └── maintenance.html           # 자립형 정적 점검·502 화면 (인라인 CSS, 외부 자산 0건)
│
├── qa/                           # 검증 지원 도구 (§10) — **운영 이미지에서 제외(.dockerignore)**
│   ├── qa_settings.py            # 검증 전용 설정 해석기 (v0.1의 config/qa_settings.py 이동)
│   └── seed_standard 관련 · concurrency.py · qa_session 관련 · fail-inject 절차 문서 ·
│       webkit_checklist.md       # 실기기(Safari·iOS) 체크리스트 (§10 ⑥)
│
└── tests/                        # Django 테스트 (모델 제약·폼 검증·URL·메타)
```

**2차 확장 시 바뀌는 것**: `apps/` 하위 3개 앱(booking·consult·backoffice)과 회원·관리자 템플릿 디렉토리가 추가될 뿐, **1차 구조는 유지된다.**

---

## 5. 데이터 모델

### 5.0 전 테이블 공통 규칙 (1차에 고정 — 되돌리지 않는다)

| 규칙 | 값 | 이유 |
|---|---|---|
| 내부 PK | `BIGSERIAL`(Django `BigAutoField`) | 조인·인덱스 효율. **URL·화면에 노출하지 않는다** |
| 외부 식별자 | 노출이 필요한 테이블에 **`public_ref UUID v4 UNIQUE`** 별도 컬럼 | REQ-N-R-010(연번 ID 금지). URL에는 이것만 쓴다 |
| 사용자 표시 번호 | `YP-XXXX-XXXX` **Crockford Base32 8자(40비트, I·L·O·U 제외)**, `secrets` CSPRNG, UNIQUE + 충돌 시 재생성 | D-6 확정. **URL에 넣지 않는다**(표시·전화 응대용) |
| 시각 | 전부 `timestamptz`(UTC 저장). 앱은 **단일 시각 진입점 `core.clock.now()`** 를 통해서만 현재 시각을 얻는다 | 검증 요건 ⑩(기준 시각 고정)을 나중에 끼워 넣으면 전 코드를 고쳐야 한다 |
| 공통 컬럼 | `created_at`·`updated_at`(전 테이블), 상태가 있는 테이블은 `status` + 전이 시각 컬럼 | — |
| 전화번호 | 원본 `phone` + **생성 컬럼 `phone_norm = regexp_replace(phone,'\D','','g')`** | 중복 판정·조회를 표기 형식과 무관하게 하기 위함(§5.4 ③) |
| 개인정보 | 보관 기간(D-19 잠정값)을 **테이블별 상수로 선언**하고 파기 배치가 그 값만 본다 | REQ-N-038 |
| 삭제 | 개인정보는 **물리 삭제**, 통계가 필요한 예약 이력은 **식별 정보 제거 + 익명 식별자 유지**(D-20 잠정) | — |
| 감사 | 관리자 작업은 `admin_action_log`에 append-only(UPDATE·DELETE는 **DB 트리거가 거부**) | REQ-F-A-030 |

**⚠ 1차에 반드시 만들어야 하는 것 — 커스텀 사용자 모델**
Django는 프로젝트 시작 시 `AUTH_USER_MODEL`을 정하지 않으면 **나중에 바꾸는 비용이 매우 크다**(전 외래키·마이그레이션 재작성). 회원 기능은 2차지만 **`accounts.User`(AbstractBaseUser + PermissionsMixin, 이메일 로그인, `role` ∈ {member, staff})를 1차 첫 마이그레이션에 포함**한다. 1차에는 운영자 계정만 존재하고 회원 가입 경로는 열지 않는다. **이것이 "1차에서 되돌릴 일"을 막는 가장 중요한 단일 결정이다.**

### 5.1 1차에 실제로 생성하는 테이블 `[1차 구현]`

| 테이블 | 용도 | 주요 컬럼 | 관련 REQ |
|---|---|---|---|
| `accounts_user` | 사용자(1차는 운영자 계정만) | `email`(unique) · `password`(Django 해시) · `name` · `role` · `is_active` · `is_staff` | 2차 기반, REQ-N-M-001 |
| `content_instructor` | 강사 | `public_ref` · `name` · `headline` · `bio` · `credentials` · `classes` · `display_order` · `is_active` (`photo`는 2차) | REQ-F-020~022, TR-02 |
| `content_lessontype` | 수업 유형 | `name` · `description` · `default_duration_min` · `default_capacity` · `display_order` · `is_active` | REQ-F-014, TR-03 |
| `content_sitesetting` | 상호·주소·전화·운영시간·SNS 등 표시 값 | `key` · `value`(jsonb) · `is_published` | REQ-F-064, TR-04 |
| `inquiry_inquiry` | **문의 접수(1차 유일한 쓰기 경로)** | `public_ref` · `name` · `phone`/`phone_norm` · `message` · `consent_at` · `status` · `source_ip_hash` · `submit_token` · `created_at` | REQ-F-040~046 |
| `mailer_outbox` | 메일 아웃박스 겸 발송 로그 | `kind` · `to_addr` · `subject` · `body_text` · `status` · `attempts` · `last_error` · `scheduled_at` · `sent_at` · `related_type`/`related_ref` | REQ-N-037, M-8 |
| `core_ratelimitcounter` | 빈도 제한 상태 (D-9) | `scope` · `identifier_hash` · `window_start` · `count` · `blocked_until` | REQ-N-019, M-3 |
| `core_jobrunlog` | 정기 작업 실행 기록 | `job` · `started_at` · `finished_at` · `status` · `detail` | REQ-N-032·038 실패 알림 |
| 프레임워크 기본 | 세션·권한 등 | — | — |

> **2차 테이블은 1차에 만들지 않는다.** 빈 테이블을 미리 만들면 상세 규칙이 2차 설계에서 바뀔 때 마이그레이션이 두 번 생기고 운영 DB에 죽은 스키마가 남는다. **대신 §5.0의 공통 규칙과 §5.2의 2차 스키마를 지금 확정해, 2차에서 1차 테이블·컬럼을 고칠 일이 없게 한다.**

### 5.1.1 콘텐츠 1차 저장 위치 — DB + 시드 파일 (요구사항 §10이 P4에 위임)

```
content/instructors.yml  (단일 원본, 저장소에 커밋)
        │  manage.py seed_content   ← upsert (키: 강사 slug / 설정 key)
        ▼
content_instructor 테이블  →  화면 렌더
```

| 판단 | 내용 |
|---|---|
| 왜 파일만 두지 않는가 | 2차에 관리자 CRUD로 옮길 때 **마이그레이션 작업(TR-02·TR-04)이 통째로 사라진다.** 요구사항 §10 말미가 "1차부터 DB 테이블 + 시드로 두면 전환 비용이 줄어든다"고 P4에 위임했다 |
| 왜 DB에만 두지 않는가 | 1차에는 관리자 화면이 없다. **파일이 사람이 고치는 유일한 창구**여야 한다(REQ-F-021·064의 1차 수용 기준) |
| 충돌 방지 | 1차에는 **파일 → DB 단방향**만 존재한다. 2차에 관리자 CRUD가 생기면 `seed_content`는 **초기 적재 전용**으로 역할을 바꾸고(운영 데이터 덮어쓰기 금지 플래그), 파일은 개발·스테이징 시드로만 쓴다 |
| **qa 확인 완료 (R1 Q-2)** | **"파일 수정 → `manage.py seed_content` 실행 → 3곳 반영"으로 판정 가능**하다는 회신을 받았다. 판정 기준선은 "재빌드 유무"가 아니라 **"관리자 화면에서 고칠 수 있는가"** 이며, 이 구분은 2차 기준("관리자 화면에서 재빌드 없이")과도 유지된다. 증거는 **전화번호 변경 → 명령 1회 → 헤더·푸터·오시는 길 3곳 캡처 + 명령 출력 + `qa_show`**. **planner에게 REQ-F-064 1차 수용 기준 문구 정렬을 권고**하되(오케스트레이터 경유), **정렬이 안 돼도 Pass 판정은 가능**하다 |
| **운영 가이드 연계 (qa Q-2 ④)** | 이 절차는 **P8 운영 가이드(REQ-N-026)의 "콘텐츠 수정 절차"와 같은 것이어야 한다.** **파일 수정만으로는 반영되지 않고 명령 1회 실행이 필요하다**는 사실을 운영 가이드에 반드시 적는다 — 적지 않으면 고객이 "고쳤는데 안 바뀐다"로 오해한다 |

### 5.2 2차 전체 스키마 `[2차 설계만]`

| # | 테이블 | 핵심 컬럼 | 주요 제약·인덱스 |
|---|---|---|---|
| 1 | `accounts_user`(확장) | `email_verified_at` · `phone`/`phone_norm` · `status`(active/withdrawn) · `withdrawn_at` · `last_login_at` | `UNIQUE(email)`. 탈퇴 시 식별 정보 제거 |
| 2 | `accounts_authtoken` | `user` · `purpose`(verify/reset) · `token_hash` · `expires_at` · `used_at` | 원문 미저장(해시만), `UNIQUE(token_hash)` |
| 3 | `accounts_loginattempt` | `identifier_hash` · `scope` · `at` · `result` | 시도 제한(M-3·D-34) |
| 4 | `booking_schedulemonth` | `year_month`(월 1일) · `status`(draft/published/closed) · `published_at` · `published_by` | `UNIQUE(year_month)` |
| 5 | **`booking_slot`** | `public_ref` · `month` FK · `lesson_type` FK · `instructor` FK **NULL 허용** · `starts_at` · `ends_at` · **`period tstzrange` 생성 컬럼** · `capacity` · `reserved_count` · `status`(open/closed) · `closed_reason` | **§5.4 ①②④⑤** |
| 6 | `booking_booking` | `public_ref` · `booking_no` · `slot` FK · `member` FK · `status`(confirmed/cancelled) · `cancelled_at` · `cancel_reason`(회원취소/슬롯폐쇄/관리자) | **§5.4 ⑥**, `UNIQUE(booking_no)` |
| 7 | `booking_scheduletemplate` / `…_templateslot` | 이름 · (요일 · 시작시각 · 유형 · 강사 · 정원) | 템플릿 내 요일+시각 유니크 |
| 8 | `consult_consultationtype` | `name` · `display_order` · `is_active` | 사용 중 유형은 삭제 불가(비활성만) |
| 9 | **`consult_consultation`** | `public_ref` · `request_no` · `type` FK · `desired_date` · `desired_time` · `name` · `phone`/`phone_norm` · `message` · `status`(received/confirmed/done/cancelled) · `confirmed_at` · `member` FK(nullable) · `consent_at` | **§5.4 ③**, `UNIQUE(request_no)` |
| 10 | `consult_happycall` | `consultation` FK · `called_at` · `result` · `memo` · `by` FK | 조회 창구 미노출 컬럼 표시 |
| 11 | `members_warning` | `member` FK · `reason`(noshow/repeat_cancel/closed_slot) · `memo` · `related_booking` FK · `created_by` · `created_at` | append-only |
| 12 | `backoffice_adminactionlog` | `actor` FK · `action` · `target_type` · `target_ref` · `summary` · `created_at` | **UPDATE·DELETE 거부 트리거**(REQ-F-A-030) |
| 13 | `content_notice` | `title` · `body` · `is_published` · `published_at` | REQ-F-A-028 |
| 14 | `content_sitesetting`(확장) | 운영시간·점심시간·리드타임·취소 마감·동시 예약 한도(D-24 기본 5) 등 | REQ-F-A-029 |
| 15 | `mailer_outbox`(확장) | `kind` 12종 | REQ-N-037 |
| 16 | `core_ratelimitcounter` · `core_jobrunlog` | 1차와 동일 | — |

> 1차 8테이블 + 2차 신규 약 12테이블 = **운영 20테이블 수준**(프레임워크 기본 테이블 제외).

### 5.3 빈도 제한 저장소(D-9) · 기준값(D-5·D-7·D-34) 확정

| 항목 | 확정값 | 근거 |
|---|---|---|
| 저장소 | **PostgreSQL 테이블 + UPSERT 원자 증가** | 앱 인스턴스 1개, 분당 수십 건 수준. Redis를 넣으면 compose·백업·장애 지점이 하나 늘어난다. 복제·성능 문제가 실제로 생기면 교체하도록 인터페이스를 1개로 추상화 |
| 식별 단위 | **출처 IP의 솔트 해시**(원본 IP 미저장) + 계정 기준이 필요한 항목은 계정 식별자 해시 | REQ-N-020 최소 수집 |
| 폼 제출(문의·상담) | **10분 5회 / 1일 20회**(M-3 잠정값 채택) | 실측 데이터가 없어 조정 여지를 남긴다 |
| **폼 차단 지속 시간 (v0.3 — qa R2 #3)** | **① 10분 창 초과 → `blocked_until` = 해당 창의 잔여 시간(최대 10분)** / **② 1일 한도 초과 → `blocked_until` = 익일 00:00(Asia/Seoul)** . 둘 다 걸리면 **더 늦은 쪽**을 쓴다 | `Retry-After` 값의 근거이자 "429 → 대기 → 200 복귀" TC 의 기대값 |
| **`Retry-After` 계산 (v0.3)** | **`ceil(blocked_until − clock.now())` 초**(최소 1). 응답 본문 문구는 여전히 사유를 구분하지 않는다 | `clock.now()` 를 쓰므로 `QA_CLOCK_OFFSET_SECONDS` 로 시간을 넘겨 **해제까지 판정**할 수 있다(§10.3) |
| 상담 조회 | 10분 10회, 초과 시 10분 차단 | M-3 |
| 로그인 | 계정당 10분 5회 / 출처당 10분 20회, 관리자 계정당 10분 3회 | D-34 |
| 재설정 요청 | 출처당 10분 3회 / 1일 10회 | D-34 |
| **조회 실패 최소 응답(D-7)** | **300ms 고정 하한**(성공·실패 동일). 실제 처리가 300ms를 넘으면 그대로 응답 | 번호 존재 여부의 타이밍 노출 차단. 체감과 방어 효과의 절충 |
| 차단 응답 | **사유를 구분해 알리지 않는다**(스팸 차단·빈도 초과 모두 일반 실패 문구) | REQ-F-044, 페이지 디자인 §4.3 |
| **사용량 알림 임계값 (qa R1 #9 — v0.2 확정)** | **다음 중 하나라도 넘으면 운영자 알림 메일 1통**(`kind=rate_limit_alert`):<br>ⓐ **동일 출처(해시 기준) 1일 차단 3회 이상**<br>ⓑ **전체 시간당 차단 20건 이상**<br>ⓒ **전체 1일 폼 제출 시도 500건 이상**(정상·차단 합산)<br>동일 사유의 알림은 **1시간에 1통으로 합산**(알림 폭주 방지) | REQ-N-019 |
| 사용량 알림 검증 | 임계값은 **`QA_RATE_LIMIT_ALERT_PER_SOURCE_DAY` · `QA_RATE_LIMIT_ALERT_PER_HOUR` · `QA_RATE_LIMIT_ALERT_TOTAL_DAY`** 로 하향할 수 있다(항목별 독립, 요건 ④). P5는 예: `…_PER_SOURCE_DAY=1`로 낮춰 **차단 1회 → 알림 메일 1통**을 Mailpit에서 확인한다 | REQ-N-019 판정 경로 |
| 일일 요약 병기 | 임계 미달이어도 **당일 차단 건수는 §3.3의 일일 운영 요약 메일 ⓕ에 항상 포함**된다 | 운영 인지 |

### 5.4 DB 제약 — "코드가 틀려도 DB가 막는다" `[2차 설계만 · 1차에 설계 고정]`

> 아래는 **개념을 보이기 위한 SQL 표기**이며, 실제로는 Django 모델의 `Meta.constraints`로 선언한다.

**① 슬롯 시간 겹침 금지 (공간 1개 — B-15)**

```sql
-- 전제: CREATE EXTENSION btree_gist;  (마이그레이션 BtreeGistExtension)
period tstzrange GENERATED ALWAYS AS (tstzrange(starts_at, ends_at, '[)')) STORED

ALTER TABLE booking_slot ADD CONSTRAINT slot_no_overlap
  EXCLUDE USING gist (period WITH &&)
  WHERE (status = 'open');
```
- `[)` 반열린 구간이라 **10:00~11:00과 11:00~12:00은 겹치지 않는다**(연속 배치 허용 — booking-rules §1).
- `WHERE (status='open')`: 닫힌 슬롯은 공간을 점유하지 않으므로 같은 시간에 새 슬롯을 열 수 있다.
- **공간이 늘어나면** `EXCLUDE USING gist (room_id WITH =, period WITH &&)`로 키만 추가한다(CR-001 R2 §2.2 ②).

**② 같은 강사 동시간대 중복 배정 금지 (B-12) — `IS NOT NULL` 부분 배제 제약**

```sql
ALTER TABLE booking_slot ADD CONSTRAINT slot_instructor_no_overlap
  EXCLUDE USING gist (instructor_id WITH =, period WITH &&)
  WHERE (instructor_id IS NOT NULL AND status = 'open');
```
- **왜 NULL을 허용하는가**: 편성 화면에서 슬롯을 먼저 놓고 강사를 뒤에 붙이는 흐름이 존재하고, **게시 전 "미배정 검사"(REQ-F-A-014)가 그 상태를 전제로 한다.** 컬럼을 `NOT NULL`로 잠그면 편성 중간 상태를 저장할 수 없다.
- **그럼 무엇이 "강사 배정 필수"를 보장하는가 — 3중이다.**
  1. **API 거부**: 슬롯 생성·수정 API는 `instructor_id`가 없으면 400으로 거부한다(정상 경로에서는 NULL이 생기지 않는다).
  2. **게시 차단**: 게시 트랜잭션이 `SELECT … FROM booking_schedulemonth WHERE id=%s FOR UPDATE`로 월을 잠근 뒤 `COUNT(*) WHERE instructor_id IS NULL AND status='open'`이 0이 아니면 **게시를 거부**한다(REQ-F-A-014).
  3. **DB 최종 안전망**: 위 부분 배제 제약 + (선택 강화) 게시 상태 월의 슬롯에 NULL 강사를 금지하는 `CONSTRAINT TRIGGER`. 트리거는 교차 테이블 조건이라 비용이 있어 **2차 구현 시 성능을 보고 결정**한다(T-5).

**③ 상담 중복 신청 차단 (C-6) — 취소·완료 제외 조건부 유니크**

```sql
phone_norm text GENERATED ALWAYS AS (regexp_replace(phone, '\D', '', 'g')) STORED

CREATE UNIQUE INDEX consult_no_dup
  ON consult_consultation (desired_date, desired_time, phone_norm)
  WHERE status IN ('received', 'confirmed');
```
- "일자 + 시간 + 연락처가 모두 같은" 신청만 막고 **취소·완료 건은 조건에서 빠져 다시 신청할 수 있다**(booking-rules §7).
- **전화번호 정규화가 없으면 이 제약은 뚫린다** — `010-1234-5678`과 `01012345678`이 서로 다른 값이 되기 때문이다. 생성 컬럼이 그 구멍을 막는다.
- 위반 시 사용자에게는 PM 확정 문구 **"이 연락처로 접수된 신청이 있습니다. 예약 확인 또는 전화로 문의주세요."** 만 보이고 **일자·시간·유형은 노출하지 않는다.**

**④ 30분 그리드 · 시간 정합성 (B-2)**

```sql
CHECK ((EXTRACT(EPOCH FROM starts_at)::bigint % 1800) = 0)   -- 30분 경계
CHECK (ends_at > starts_at)
```
- `timestamptz`에서 `EXTRACT(EPOCH …)`는 절대 시각 기준이라 **불변(immutable)** 이어서 CHECK에 쓸 수 있다. 한국 표준시는 **UTC+9:00 정시 오프셋이고 서머타임이 없으므로** 절대 시각의 30분 경계 = KST의 분이 0 또는 30이다. (`AT TIME ZONE`을 쓴 표현은 세션 타임존에 의존해 CHECK에 쓸 수 없다.)
- 운영 시간(06:00~20:00)·점심시간 기본값은 **관리자 설정값**이므로 DB 상수로 굳히지 않고 애플리케이션에서 검사한다.

**⑤ 정원 초과 방지 (동시 예약) — 원자적 test-and-set + CHECK**

```sql
ALTER TABLE booking_slot ADD CONSTRAINT slot_capacity_sane
  CHECK (reserved_count >= 0 AND reserved_count <= capacity);

-- 예약 트랜잭션 안 (명시적 락 없이 원자적)
UPDATE booking_slot
   SET reserved_count = reserved_count + 1
 WHERE id = %s AND status = 'open' AND reserved_count < capacity
RETURNING id;          -- 0행이면 "마감" 응답
INSERT INTO booking_booking (…);
```
- 정원은 단일 제약으로 표현할 수 없으므로 **한 문장짜리 조건부 UPDATE로 원자화**하고 `CHECK`를 최종 안전망으로 둔다. `SELECT … FOR UPDATE` 방식보다 잠금 보유 시간이 짧다.
- 취소는 같은 트랜잭션에서 `reserved_count - 1`.
- **역정합 위험**(카운터와 실제 예약 수 불일치)에 대비해 야간 정합성 점검(`manage.py check_counters`)이 불일치를 찾아 알린다.
- 검증: 요건 ⑧ 동시 요청 20건 스크립트로 "정원 초과 0건"을 확인한다(REQ-N-L-001).

**⑥ 같은 회원의 같은 슬롯 중복 예약 금지 (취소 제외)**

```sql
CREATE UNIQUE INDEX booking_no_dup
  ON booking_booking (slot_id, member_id)
  WHERE status = 'confirmed';
```
- 1인 동시 예약 한도(기본 5건, D-24)는 **관리자 설정값**이라 DB 제약이 아니라 예약 트랜잭션 안에서 검사한다.

**⑦ 감사 로그 변경 차단**

```sql
CREATE TRIGGER adminlog_no_change BEFORE UPDATE OR DELETE ON backoffice_adminactionlog
  FOR EACH ROW EXECUTE FUNCTION raise_immutable();   -- RAISE EXCEPTION
```
- REQ-F-A-030 "수정·삭제할 수 없다"를 애플리케이션 약속이 아니라 **DB가 강제**한다.

**⑧ 오류 번역** — 위 제약 위반은 DB 예외(`IntegrityError`·배제 제약 위반)로 올라온다. **제약 이름 → 사용자 문구 매핑 표를 `core/db_errors.py` 한 곳**에 두고, 화면은 "이미 그 시간에 수업이 있습니다" / "같은 일시로 이미 신청하셨습니다"로 번역한다. 매핑이 없는 제약 위반은 500이 아니라 **일반 실패 화면 + 서버 로그 경고**로 처리한다.

### 5.5 식별자 생성 규칙 (REQ-N-R-002 · D-6) `[1차에 공용 함수로 고정]`

| 대상 | 형식 | 생성 |
|---|---|---|
| URL 식별자 `{ref}`·`{slotRef}` | **UUID v4** | `uuid4()` — 시간 정렬·인접성 추론 불가(UUID v7을 쓰지 않는 이유) |
| 예약번호·신청번호 | `YP-XXXX-XXXX` (Crockford Base32 8자 = **40비트**, `I·L·O·U` 제외) | `secrets` 기반 → Base32 매핑. **공용 함수 1개**(`core/refs.py`)만 사용 |
| 검증 | 1,000건 생성 시 중복 0건, 연속 20건에 정렬 규칙 없음 | 요건 ⑧ 스크립트로 P5에서 재현 |

- 40비트는 이 규모(연간 수천 건)에서 충돌 확률이 무시할 수준이고 **전화 응대 시 읽어 주기 좋은 길이**다. **늘릴 수는 있어도 줄일 수 없으므로** 1차에 8자로 고정한다(D-6).

### 5.6 권한·소유자 검사 공통 레이어 (REQ-N-036) `[1차 골격 · 2차 확장]`

- **기본값은 거부**다. 미들웨어가 모든 요청을 가로채 **명시적으로 공개 등록된 경로 패턴만 통과**시킨다(`core/access.py`의 공개 경로표). 등록을 잊으면 **노출이 아니라 접근 거부**가 된다.
- 소유자 검사(IDOR 방지)는 **뷰가 아니라 조회 계층**에서 한다 — 소유자 필터가 기본으로 붙은 매니저(`Booking.objects.owned_by(user)`)만 쓰고, 원시 `get(pk=…)`는 코드 리뷰에서 금지한다.
- 1차에 만드는 것: 미들웨어 + 공개 경로 등록표 + `/healthz`·정적 경로 예외. 2차에 회원·관리자 규칙이 추가된다.

---

## 6. URL · 화면 · 컴포넌트 매핑

### 6.1 URL 규칙

| 항목 | 결정 |
|---|---|
| 후행 슬래시 | **없는 형태로 통일**(IA §6.1). 프레임워크 기본 동작(`APPEND_SLASH`)을 끄고 슬래시가 붙은 요청은 **301로 슬래시 없는 주소로 보낸다** |
| 예외 | 2차 Django 관리자(`/admin/…`)는 프레임워크 규약상 슬래시를 유지한다. **`noindex` 영역이라 색인·정규화에 영향 없음**(§14.2에 기록) |
| 대소문자·언어 | 소문자 kebab-case, 한글 경로 없음 |
| 날짜 경로(2차) | `\d{4}-\d{2}-\d{2}` / `\d{4}-\d{2}` 정규식으로 형식을 잠근다(IA §6.1) |
| 식별자 | UUID v4만 사용. **예약번호·신청번호·전화번호를 경로·쿼리에 넣지 않는다**(REQ-N-R-010) |
| canonical·OG·sitemap | `SITE_BASE_URL` 환경 변수로 절대 URL 생성. **도메인 미정 시 스테이징 값으로 동작하고 운영 전환 시 값만 바꾼다**(재빌드 불필요) |

### 6.2 1차 화면 ↔ 구현 파일

| SCR | 화면 | URL | 뷰·템플릿 | 상태 코드·색인 | 목업 |
|---|---|---|---|---|---|
| SCR-001 | 메인 | `/` | `pages/home.html` | 200 · 색인 | `design/mockups/scr-001.html` |
| SCR-002 | 요가 강사 소개 | `/instructors` | `pages/instructors.html` | 200 · 색인 | `scr-002.html` |
| SCR-003 | 오시는 길 + 문의 폼 | `/location`(`#contact`) | `pages/location.html` (GET·POST 동일 URL) | 200 · 색인 | `scr-003.html` |
| SCR-006 | 개인정보 처리방침 | `/privacy` | `pages/privacy.html`(`content/privacy.yml`) | 200 · 색인 | `scr-006.html` |
| SCR-008 | 404 | 없는 경로 | `errors/404.html` | **실제 404** · `noindex` | `scr-008.html` |
| SCR-009 | 공용 오류·점검 (Could) | 5xx · 점검 | `errors/500.html`·`maintenance.html` | 500 / 503 · `noindex` | `scr-008.html` 변형 |
| — | sitemap | `/sitemap.xml` | `django.contrib.sitemaps` (색인 대상만) | 200 | — |
| — | robots | `/robots.txt` | 정적 뷰(**Disallow 0건** + Sitemap 위치) | 200 | — |
| — | 헬스체크 | `/healthz` | `core` | 200 · `noindex` | — |
| (2차) | 이용약관 SCR-010 | `/terms` | `pages/terms.html` | 2차 | — |

- **404가 진짜 404여야 한다**(REQ-F-060): 앱이 404 상태로 템플릿을 렌더하고, **기존 nginx가 자체 오류 페이지로 가로채지 않도록** `proxy_intercept_errors off`를 요청한다(§12.3).
- 점검 화면(503)은 배포 중 잠깐 쓰며, 앱이 내려간 상태에서는 nginx의 `error_page 502 503` 설정이 필요하다 → devops 확인 항목.

### 6.3 컴포넌트 매핑 (CMP-001~030 → 구현)

| 구분 | CMP | 구현 |
|---|---|---|
| 레이아웃 | 003 Header · 006 Footer · 007 Bottom Fixed Bar · 008 Skip Link · 009 Container/Section | `templates/partials/*.html` + `css/components/layout.css` |
| 내비 | 004 GNB Item · 005 Mobile Menu Panel · 023 Anchor Chip · 028 TOC · 029 Back To Top | `partials/header.html`, `css/components/nav.css`, `js/menu.js` |
| 기본 요소 | 001 Button · 002 Link · 010 Card · 011 Icon Frame · 012 Eyebrow · 013 Callout · 014 Definition List · 027 Initial Avatar · 030 Divider | `components/*.html` + `css/components/base.css` |
| 폼 | 015 Text Input · 016 Textarea+카운터 · 017 Checkbox · 018 Form Field · 019 Error Summary · 020 Result Block · 021 Toast | `components/form_*.html` + `form.css` + `js/form.js` |
| 특수 | 022 Map Placeholder · 024 Page Header · 025 CTA Band · 026 Empty State | `components/*.html`, `js/map.js` |

- **CMP-005 모바일 패널은 디자인 시스템 명세(`<details>` 기반)를 정본으로 구현**한다(목업의 `button aria-expanded`가 아님). `<summary>`에 `aria-expanded`를 수동 부착하지 않는다(중복).
- 고정 바(CMP-007)의 **S1/S2/S3**와 헤더 CTA의 **H1/H2/H3** 상태는 **`현재 URL == 목적지 URL` 비교 + 대표 전화 데이터 유무** 두 값으로 템플릿에서 분기한다(페이지 디자인 §4.4). 화면 목록을 코드에 열거하지 않는다(G-7).
- `--fixed-bar-h`·`--header-h`는 **실제 높이를 `ResizeObserver`로 반영**하되, `≥1280px`·`max-height:420px` 구간에서는 **인라인 값을 제거(`removeProperty`)** 해 CSS 미디어 쿼리가 이기게 한다(P3 리뷰 R1 #2·#3).

---

## 7. 외부 연동 · 환경 변수

### 7.1 외부 서비스 표 (REQ-F-052 · REQ-N-021 — 처리방침 위탁 항목 초안 입력)

| 서비스 | 사업자 | 업무 | 처리하는 개인정보 | 저장 리전 | 상태 |
|---|---|---|---|---|---|
| SMTP 메일 발송 | **[TBD: I-5-b]** | 문의 접수 알림(1차) · 알림 메일 12종(2차) 발송 | 수신자 주소, 본문에 포함된 이름·연락처 | [TBD] | 계정 미연결(PM 지시) |
| 지도 | **[TBD: T-E 고객 선택]** | 오시는 길 지도 임베드·길찾기 | **없음**(클릭 투 로드 전 요청 0건, 로드 후에도 개인정보 전송 없음) | 사업자 기준 | 미확정 |
| 분석 도구 | **[TBD: 고객 명의 계정]** | 방문·전환 측정 | 페이지 경로·기기 정보(식별 정보 제외 — REQ-N-R-010) | 사업자 기준 | 오픈 이후 설치 가능 |
| 폰트(Pretendard) | — | **self-host — 외부 요청 0건** | 없음 | 자체 서버 | 확보 |
| 아이콘(Lucide) | — | **self-host — 외부 요청 0건** | 없음 | 자체 서버 | 확보 |
| **그 외 전부** | — | 회원·예약·상담·문의 데이터는 **자체 서버 PostgreSQL에만 저장**. 외부 위탁 없음 | — | 보유 서버 | 확정 |

### 7.2 환경 변수 (이름만 — 값은 어떤 문서·로그·커밋에도 기록하지 않는다)

| 그룹 | 이름 | 필수 | 비고 |
|---|---|---|---|
| 실행 환경 | `DJANGO_ENV`(local/staging/production) · `DJANGO_SETTINGS_MODULE` · `DJANGO_DEBUG` | ○ | `production`에서 `DEBUG=1`이면 **기동 거부** |
| 보안 | `DJANGO_SECRET_KEY` · `DJANGO_ALLOWED_HOSTS` · `DJANGO_CSRF_TRUSTED_ORIGINS` · `SECURE_SSL_REDIRECT` · `SESSION_COOKIE_SECURE` · `CSRF_COOKIE_SECURE` · `SECURE_HSTS_SECONDS` · `TRUSTED_PROXY_COUNT` | ○ | §13 |
| 사이트 | `SITE_BASE_URL` · `SITE_NAME` | ○ | canonical·OG·메일 링크 |
| DB | `POSTGRES_HOST` · `POSTGRES_PORT` · `POSTGRES_DB` · `POSTGRES_USER` · `POSTGRES_PASSWORD` | ○ | app·db·backup 공유 |
| 메일 | `EMAIL_HOST` · `EMAIL_PORT` · `EMAIL_HOST_USER` · `EMAIL_HOST_PASSWORD` · `EMAIL_USE_TLS` · `DEFAULT_FROM_EMAIL` · `INQUIRY_NOTIFY_TO` · `OPS_ALERT_TO` | ○ | 로컬은 Mailpit 값 |
| 외부 | `MAP_PROVIDER` · `MAP_API_KEY` · `ANALYTICS_ID` | △ | 미설정이면 해당 기능만 비활성(화면 오류 없음) |
| 운영 | `APP_VERSION` · `APP_PORT` · `COMPOSE_PROJECT_NAME` · `BACKUP_DIR` · `BACKUP_KEEP_DAILY` · `BACKUP_KEEP_WEEKLY` · `BACKUP_KEEP_MONTHLY` · `GUNICORN_WORKERS` | ○ | §12 |
| 정책값 | `SESSION_IDLE_MINUTES` · `SESSION_REMEMBER_DAYS` · `RESET_TOKEN_MINUTES` · `VERIFY_TOKEN_HOURS` · `RETENTION_DAYS__INQUIRY` · `RETENTION_DAYS__CONSULT` · `RETENTION_DAYS__BOOKING` … | ○ | 항목별 독립 키(요건 ④) |
| **검증 전용** | `QA_TOOLS_ENABLED`(**마스터 스위치 — 이 값이 `1`일 때만 나머지 `QA_*`를 해석**) · `QA_RATE_LIMIT_MODE` · `QA_RETENTION_MINUTES__*` · `QA_CLOCK_OFFSET_SECONDS`(**음수 허용**) · `QA_FAIL_INJECT`(smtp/backup/purge) · `QA_SESSION_TOKEN` · **`QA_RATE_LIMIT_ALERT_PER_SOURCE_DAY` · `QA_RATE_LIMIT_ALERT_PER_HOUR` · `QA_RATE_LIMIT_ALERT_TOTAL_DAY`**(§5.3) | ✕ | **§3.5.1 ② · §10.6 안전장치 필수** |
| 백업 | `BACKUP_DIR` · `BACKUP_KEEP_*`(위 "운영" 그룹) + **`BACKUP_MIN_FREE_GB`**(여유 미만이면 백업 전 경고 알림) | ○ | §12.5 |

- `.env.example`에는 **키와 설명만** 둔다. `.env`는 `.gitignore`에 포함한다(REQ-N-018).
- 이미지 빌드 시 시크릿을 넣지 않는다 — 전부 **런타임 환경 변수 주입**. 검증은 이미지 레이어 검색(M-4 패턴)으로 한다.

---

## 8. 로컬 개발 환경

| 항목 | 내용 |
|---|---|
| 요구 런타임 | **Docker Desktop(Windows) 또는 Docker Engine + compose v2.** 호스트에 Python·Node 설치 불필요 |
| 최초 설치 | `.env.example` → `.env` 복사 후 값 입력 → `docker compose -f compose.yaml -f compose.local.yaml build` |
| 기동 | `docker compose -f compose.yaml -f compose.local.yaml up` → **http://localhost:8000** |
| **프록시 경유 기동**(검증용) | `docker compose -f compose.yaml -f compose.local.yaml --profile proxy up` → **http://localhost:8080** (nginx → app). §12.3의 nginx 요청 설정을 로컬에서 선검증한다(§3.2.1) |
| **백업 실행**(검증용) | `… run --rm app python manage.py run_backup` (+`--dry-run`). 실패 주입은 `QA_TOOLS_ENABLED=1 QA_FAIL_INJECT=backup` |
| DB 초기화·시드 | `… exec app python manage.py migrate` → `… manage.py seed_content` → `… manage.py createsuperuser` |
| 메일 확인 | **http://localhost:8025** (Mailpit UI) |
| 운영 빌드 | `docker compose -f compose.yaml -f compose.prod.yaml build` (collectstatic·압축이 이미지 빌드 단계에 포함) |
| 빌드 결과 미리보기 | `docker compose -f compose.yaml -f compose.prod.yaml up` → `http://localhost:${APP_PORT}` (gunicorn + WhiteNoise 상태) |
| 테스트 | `… exec app python manage.py test` |
| 린트·포맷 | `… exec app ruff check .` / `ruff format .` |
| 자체 점검 | `manage.py check --deploy` · 링크 점검 · `[TBD]` 검색(M-5) · 비밀 정보 검색(M-4) |

- **모든 명령은 `developer/site/` 안에서 실행한다.** 틀 루트·프로젝트 루트에 `package.json`·`node_modules`·lock 파일을 만들지 않는다.
- Windows 바인드 마운트에서 파일 감시가 느릴 수 있어, 개발 서버의 폴링 옵션을 환경 변수로 켤 수 있게 둔다. 셸 스크립트는 `.gitattributes`로 LF 고정.
- **`site/README.md`에 위 표를 그대로 옮겨 재현 가능한 형태로 적는다**(P4-② 산출물 요건).

---

## 9. 품질 구현 방안

### 9.1 반응형 (REQ-N-001·002)

- **모바일 우선 `min-width` 미디어 쿼리**, 구간은 디자인 시스템 §1.5의 4구간(`~767` / `768~1023` / `1024~1279` / `1280~`).
- 고정 바·헤더·본문 하단 여백은 **토큰 계산식**(`--body-pad-bottom = calc(var(--fixed-bar-h) + env(safe-area-inset-bottom) + 16px)`)으로만 만든다. 76px 같은 파생값을 직접 쓰지 않는다.
- `height` 금지·`min-height` 사용(텍스트 200% 확대), 입력 `font-size` 16px 하한(iOS 자동 확대 방지), 400% 확대는 `@media (max-height:420px) and (max-width:400px)`에서 헤더·고정 바 정적 배치(G-11).
- 검증: 360/768/1024/1280px에서 가로 스크롤 0, 겹침 0.

### 9.2 접근성 (REQ-N-006·008·009)

| 항목 | 구현 |
|---|---|
| 랜드마크·구조 | `header`/`nav`/`main#main[tabindex="-1"]`/`footer`, h1 1개, 제목 단계 건너뜀 없음 |
| Skip link | `base.html` 최상단 CMP-008, 포커스 시 노출 → `#main` |
| 포커스 | `:focus-visible` 3px 링 + offset 2px. **`border-radius` 선언 제거**(§2.6). 포커스 규칙 블록은 스타일시트 맨 뒤 |
| 폼 | `label[for]`, `aria-describedby`(도움말·오류), `aria-invalid`, 오류 요약 `role="alert"` + `tabindex="-1"` + 항목 앵커, 필수 표시 3중(`*` + "(필수)" + `required`) |
| 터치 타깃 | 44×44px 이상, 인접 간격 8px 이상 |
| 색 | 색만으로 정보 전달 금지(상태색에 아이콘·텍스트 병기). 대비값은 디자인 시스템 §4.1을 그대로 따른다 |
| 동작 | `prefers-reduced-motion: reduce`에서 `scroll-behavior: auto`, 전환 효과 제거. **스크롤 등장 효과 미사용** |
| 새 창 | 외부 링크 접근 이름에 "(새 창 열림)" 포함 |
| 자체 점검 | 테스트 + 자동 점검 도구를 P4 자체 점검에 포함, 최종 판정은 P5 |

### 9.3 SEO (REQ-N-010~016)

| 항목 | 구현 |
|---|---|
| title·description | 뷰 컨텍스트 → `partials/meta.html`. IA §6.2·6.3 패턴 사용. **description은 색인 대상 공개 화면만**, 50~90자 |
| canonical | `SITE_BASE_URL` + 경로(슬래시 없는 정규 형태) |
| OG·twitter | `og:title/description/image/url` + `twitter:card`. **OG 이미지 미수령 시 태그를 빼고 빌드**하고 수령 시 추가 |
| 구조화 데이터 | `jsonld_localbusiness.html` — 상호·주소·전화·영업시간·URL을 `content_sitesetting`에서 읽어 생성. **`[TBD]` 값이면 해당 속성을 넣지 않는다**(빈 값·자리표시자 출력 금지) |
| sitemap | 프레임워크 sitemaps, **색인 대상 공개 화면만**(1차: `/`·`/instructors`·`/location`·`/privacy`) |
| robots.txt | **Disallow 규칙 0건** + `Sitemap:` 1줄(IA §6.5) |
| noindex | 404·500·`/healthz`에 메타 `noindex`. 스테이징은 전 응답 헤더로 강제 |
| 시맨틱 | W3C 검사 오류 0건 목표, 목록·정의 목록·표를 의미대로 사용 |

### 9.4 성능 (REQ-N-004·005)

| 항목 | 구현 |
|---|---|
| **폰트** | Pretendard **static 400·700** × **`unicode-range` 분할 subset woff2**. `font-display: swap`. **preload는 Latin + 한글 기본 chunk의 400 두 개만**. `--fw-medium: 500`은 1차에서 사용하지 않는다 |
| **폴백 메트릭 (디자인 D-7)** | 폴백용 `@font-face`(`local("Malgun Gothic")`·`local("Apple SD Gothic Neo")`)에 `size-adjust`·`ascent-override`·`descent-override` 지정. **실측 절차**: ① 360·768·1280px에서 `h1 2줄 + 서브카피 3줄` 블록 높이를 폴백 렌더/Pretendard 렌더로 각각 측정 ② `size-adjust`를 1% 단위로 조정해 차이를 디자인 시스템 §1.2 ⑤ 기준 이내로 수렴 ③ **designer 1회 확인**(개발 보고서에 측정표 첨부). 미수렴 시 대안은 preload 확대 또는 `font-display: optional` — 둘 다 designer 합의 필요 |
| 이미지 | **1차 사진 0장 전제**. 로고·아이콘은 인라인 SVG. 이미지가 들어오면 `width`/`height` 또는 `aspect-ratio` 고정(CLS 0), 첫 화면 외 `loading="lazy"` |
| 지도 | **클릭 투 로드**. 대체 영역 높이를 로드 후 iframe과 동일하게 고정 → CLS 0. 초기 로드 외부 도메인 요청 0건 |
| JS | 번들 없음, 총량 수 KB, `defer` |
| CSS | 단일 파일(해시·brotli 사전 압축), 예상 20KB 미만 |
| 캐시 | 정적 `immutable, max-age=31536000` / HTML `must-revalidate` + ETag |
| 측정 | M-1 조건(모바일 프리셋·3회 중앙값·확장 없는 프로필)으로 **P4 자체 점검에서 1차 측정**하고 결과를 개발 보고서에 남긴다. 최종 판정은 P5.<br>**측정은 `QA_*`를 전부 미설정한 prod 빌드에서 수행한다**(qa R1 #15 — 빈도 제한 off·클록 오프셋이 응답 경로에 붙으면 운영 동등성이 깨진다). 측정 기록에 `QA_TOOLS_ENABLED` 미설정 사실을 함께 남긴다 |
| 압축 측정 조건 | HTML 압축 주체가 nginx이므로(§12.3) **텍스트 압축 항목은 `--profile proxy`로 nginx를 경유해 측정**한다. `:8000` 직접 측정값과 `:8080` 경유 측정값을 둘 다 개발 보고서에 남긴다 |

### 9.5 보안 (REQ-N-017~020)

| 항목 | 구현 |
|---|---|
| HTTPS | nginx가 TLS 종료. 앱은 `SECURE_PROXY_SSL_HEADER`로 `X-Forwarded-Proto` 신뢰 + `SECURE_SSL_REDIRECT`(운영만) + HSTS |
| **HSTS 범위 (devops R1 #12)** | 1차는 **`SECURE_HSTS_SECONDS=86400`(1일)로 시작**하고 안정 확인 후 늘린다. **도메인 구조(I-2-c: 같은 상위 도메인의 다른 내부 서비스 존재 여부)를 확인하기 전에는 `includeSubDomains`·`preload`를 켜지 않는다** — 켜면 같은 상위 도메인의 http 전용 서비스가 접속 불가가 되고 되돌리기 어렵다 |
| 쿠키 | `Secure`(운영)·`HttpOnly`·`SameSite=Lax`. 세션 유휴 30분(D-33) |
| CSRF | 프레임워크 기본 + `CSRF_TRUSTED_ORIGINS` |
| 보안 헤더 | `X-Content-Type-Options: nosniff` · `Referrer-Policy: strict-origin-when-cross-origin`(재설정 토큰 화면은 `no-referrer`) · `Permissions-Policy` 최소 · **CSP**(`default-src 'self'`, 인라인 스크립트 금지, 지도 로드 시에만 `frame-src`에 해당 도메인 추가) |
| 입력 검증 | **서버 측이 정본**(REQ-F-042). 길이·형식·허용 문자 화이트리스트. 클라이언트 검증은 UX 보조 |
| 스팸 | honeypot(화면 밖 배치 + `tabindex=-1` + `aria-hidden`, 자동완성 유도 이름 회피) + 빈도 제한 + 서버 검증. **차단 사유 미노출** |
| 중복 제출 | 폼 렌더 시 **1회용 `submit_token`** 발급 → 서버가 소비. 제출 중 버튼 비활성은 보조 수단. **JS 없이 제출해도 동일하게 동작한다** |
| 개인정보 | IP는 솔트 해시로만 저장, 로그에 이름·전화·메일 본문 미기록, 관리 명령 출력은 마스킹(`010-****-5678`) |
| 컨테이너 | 비루트 실행, 슬림 베이스, 불필요 패키지 미설치, DB 포트 비게시, 시크릿 런타임 주입 |
| 의존성 | 버전 고정 + 취약점 점검을 배포 전 체크리스트에 포함 |

### 9.6 문의 폼 응답 형태 — **P5 판정 기준** (REQ-F-042·044·046 — qa R1 #1 **Must**)

> REQ-F-042의 수용 기준이 *"실제 응답 형태(상태 코드·본문)는 P4 기술 설계에 기록하고 **P5는 그 값으로 판정한다**"* 이므로, **이 표가 P5의 기대값 원본**이다. 여기 적힌 값과 구현이 다르면 그 자체가 결함이다.
> 대상 URL은 `POST /location`(SCR-003 `#contact`) 하나다. 응답은 모두 **같은 URL의 서버 렌더 HTML**이며(리다이렉트 없음 — JS 없이도 동작해야 한다, REQ-N-030), 결과 블록 상태 6종은 페이지 디자인 §4.3의 CMP-020 상태를 가리킨다.

| # | 상황 | **HTTP 상태 코드** | **응답 본문 형태** (결과 블록 상태 + 화면) | **DB 저장** | **메일 발송(아웃박스 INSERT)** | **서버 기록** |
|---|---|---|---|---|---|---|
| **①** | **정상 접수** | **200** | `result_block` **성공** 상태 + 접수 안내 문구. 폼은 비워지고 새 `submit_token` 미발급(재제출 유도 없음). `#contact-result`로 포커스 이동(`role="status"`) | **1건 INSERT** (`inquiry_inquiry`, `status=received`) | **1건 INSERT** (`mailer_outbox`, `kind=inquiry_notify`, `status=queued`) — 같은 트랜잭션(M-8) | `core` 로그 `INFO inquiry.created ref=<public_ref>` (**이름·전화·본문 미기록**) |
| **②** | **서버 검증 실패** (필수 누락·길이 초과·형식 오류·동의 미체크) | **200** (재렌더) | `error_summary`(CMP-019) **오류** 상태 + 항목별 `aria-invalid`·오류 메시지. **입력값 보존**, 기존 `submit_token` 유지(재제출 가능). `role="alert"` + `tabindex="-1"` 포커스 | **0건** | **0건** | `INFO inquiry.invalid fields=[name,consent]` (**필드 이름만**, 값 미기록) |
| **③** | **honeypot 채움** (봇 판정) | **200** | `result_block` **성공** 상태 — **①과 픽셀 단위로 동일한 화면**(차단 사실을 알리지 않는다, REQ-F-044) | **0건** | **0건** | `WARNING inquiry.blocked reason=honeypot ip_hash=<hash>` — **②③④⑤의 판정은 이 로그와 DB 건수 차이로만 구분된다** |
| **④** | **빈도 제한 초과** (10분 5회 / 1일 20회 초과, §5.3) | **429** | `result_block` **실패(일반)** 상태 + "잠시 후 다시 시도해 주세요" — **사유를 구분해 알리지 않는다**. `Retry-After` 헤더 포함 | **0건** | **0건** (단 사용량 알림 임계 초과 시 `kind=rate_limit_alert` **1건**, §5.3) | `WARNING inquiry.blocked reason=rate_limit ip_hash=<hash> scope=form` + `core_ratelimitcounter` `count` 증가·`blocked_until` 갱신 |
| **⑤** | **`submit_token` 재사용·만료** (중복 제출) | **200** | `result_block` **성공** 상태 — **①과 동일 화면**(사용자에게는 "이미 접수됨"과 구분 없이 접수 완료로 보인다). 새 토큰 미발급 | **0건 (추가 저장 없음)** → REQ-F-046 ②의 "저장 1건" 판정 지점. `qa_show inquiry --count-only`로 확인 | **0건 (추가 발송 없음)** | `INFO inquiry.duplicate token_state=used\|expired ref=<원본 public_ref 또는 none>` |
| **⑥** | **서버 오류** (DB·템플릿 예외 등 미처리 예외) | **500** | `errors/500.html`(SCR-009) — **폼 화면이 아닌 전용 오류 화면**. 입력값은 복원되지 않는다. `noindex` | **0건** (트랜잭션 롤백) | **0건** (같은 트랜잭션이므로 함께 롤백) | `ERROR` + 스택 트레이스(**개인정보 미포함**). 일일 운영 요약 메일 ⓓ에 집계 |

**판정 시 주의 (qa와 공유하는 해석)**

| 항목 | 내용 |
|---|---|
| **③ vs ①의 구분** | 화면·상태 코드가 같으므로 **`qa_show inquiry --count-only --since`(저장 0건)** + **`qa_mail_log --since`(발송 0건)** + 로그의 `reason=honeypot` 3개로 판정한다. 이것이 표에 "저장/발송/기록" 열을 둔 이유다 |
| **④만 429인 이유** | ②는 사용자가 고칠 수 있는 입력 오류라 `200` 재렌더가 접근성·JS 비활성 양쪽에 맞고, ③⑤는 **차단 사실을 숨겨야 하므로 상태 코드로도 드러내지 않는다**. ④는 숨길 대상이 아니라 **재시도 시점을 알려야 하는 상태**이므로 표준 `429 + Retry-After`를 쓴다. 화면 문구는 여전히 사유를 구분하지 않는다 |
| **결과 블록 6종과의 대응** | 페이지 디자인 §4.3의 6종 중 1차에서 실제로 나타나는 것은 **성공 · 오류(항목별) · 실패(일반) · 전송 중(JS 한정)** 4종이다. 나머지 2종(부분 실패·재시도 안내)은 2차 상담/예약 화면에서 쓰인다 — 1차 P5 판정 대상이 아님을 명시한다 |
| **JS 비활성 시** | ①~⑥ 전부 동일하다. 차이는 "전송 중" 상태가 표시되지 않는 것뿐이다(REQ-N-030) |
| **CSRF 토큰 불일치** | Django 기본 동작인 **403**이며 위 6종과 별개다. 정상 사용에서는 발생하지 않으므로 P5 판정 대상에 넣지 않는다(발생 시 결함) |
| **판정용 로그 형식 (v0.3 — qa R2 #4)** | 위 표의 "서버 기록" 열은 **`key=value` 형식으로 고정**한다: `inquiry.created ref=…` · `inquiry.invalid fields=[…]` · `inquiry.blocked reason=honeypot|rate_limit ip_hash=… scope=…` · `inquiry.duplicate token_state=used|expired ref=…`. 로그 포맷은 `%(asctime)s %(levelname)s %(name)s %(message)s` 이며 **③(honeypot) 과 ⑤(토큰 재사용)의 유일한 구분 증거**이므로 키 이름을 바꾸지 않는다 |
| **로그 조회 수단 (v0.3 — qa R2 #4)** | **로컬: `docker compose -f compose.yaml -f compose.local.yaml logs app`**(§3.4 의 json-file 드라이버·회전 설정으로 보존된다). **스테이징: qa 에게 셸 접근이 없으므로 devops 가 대행해 해당 구간 로그를 파일로 전달**한다(요청 창구는 티켓). 새 명령을 만들지 않는다 |

---

## 10. 검증 지원 도구 (qa P5 환경 요건 ①~⑩ + 신규 ⑪) — **별도 산정**

### 10.1 도구 목록과 공수

> 요구사항 §5.3 말미의 10항목은 **제작 산출물**이다. 기존 공수 추정에 녹아 있지 않으므로 **작업 단위로 분리해 산정**한다(qa R1 #6, developer R1 #5).

| 요건 | 구현 방식 | 1차 필요 | 1차 공수 | 2차 추가 |
|---|---|---|---|---|
| ① 스테이징 DB + qa 조회 수단 | `manage.py qa_show inquiry --masked` 등 **읽기 전용·마스킹 조회 명령**. 운영 DB 권한은 부여하지 않는다. **출력 규격은 §10.2** | ○ | **0.25** | 0.25 |
| ② 테스트 수신 주소·목 발송 + 발송 로그 조회 | Mailpit(로컬·스테이징) + `manage.py qa_mail_log` | ○ | **0.25** | 0.1 |
| ③ 로컬 HTTPS 또는 localhost | `http://localhost:8000`은 **보안 컨텍스트**라 클립보드 API가 동작한다. LAN·스테이징 http 접근 대비로 `execCommand` 폴백 병행 | ○ | 0.1 (§9 포함) | — |
| ④ 검증 전용 설정(보관·빈도·세션) **항목별 독립** | `qa/qa_settings.py`(경로는 `developer/site/` 기준 — v0.3, qa R2 #6)가 `QA_*` 키를 **각각 독립적으로** 해석. `QA_RETENTION_MINUTES__INQUIRY=10` + `QA_RATE_LIMIT_MODE=off` 조합 가능(단일 모드 스위치 금지) | ○ | **0.5** | 0.25 |
| ⑤ 테스트 데이터 삭제 규칙 | 시드에 `TEST-` 접두어 + `manage.py qa_purge_test_data --confirm` + **테이블별 삭제 건수 출력** + `--dry-run`. **삭제 대상 테이블과 식별 규칙은 §10.4**(qa R1 #10) | ○ | **0.35** | — |
| ⑥ 가상 키보드 검증 수단 | **기기 확보는 qa·PM 소관.** 제작 측은 ⓐ G-9 구현(메타 + WebKit `visualViewport` 폴백) ⓑ **폴백 적용 여부의 관측 신호**(`html[data-vk-fallback]`) ⓒ **WebKit 자동화 판정 절차 + 실기기 체크리스트 문서**(`developer/site/qa/webkit_checklist.md` — v0.3, qa R2 #7)를 제공 → **§10.5**(qa R1 #8) | ○ | **0.35** (§9 포함분 별도) | — |
| ⑦ **검증 전용 로그인 세션 수단** | `manage.py qa_session --role member1\|member2\|staff` → 세션 발급(스크립트가 쿠키 주입). 회원 2·관리자 1 계정 시드. **`QA_TOOLS_ENABLED=1`인 환경에서만 동작**하며 **HTTP 경로로 노출하지 않는다**(§3.5.1 ②) | **1차 = 골격만 / 본체 2차** (qa R1 #16 표기 정리) | **0.25**(골격) | **0.75~1.0** |
| ⑧ **표준 시드 + 동시 요청 스크립트** | `manage.py seed_standard`(2차: 슬롯 400·예약 200·상담 100) + `qa/concurrency.py`(동시 N건 발사·성공/거부 집계). 1차는 문의 폼 동시 제출·빈도 제한 재현 + 번호 1,000건 생성 스크립트 골격 | 일부 | **0.5** | **1.0~1.5** |
| ⑨ **실패 주입 수단** | `QA_FAIL_INJECT=smtp,backup,purge` — ⓐ SMTP 자격 증명 강제 오류 ⓑ **`run_backup` 강제 실패**(§12.5 — v0.2부터 **로컬 `backup` 프로필로도 재현 가능**) ⓒ 파기 배치 강제 예외. **각각 독립 토글**이며 실패 알림 경로(`core_jobrunlog` + `mailer_outbox`)까지 확인 가능. **주입이 걸리면 로그에 `QA_FAIL_INJECT: <대상> 주입됨` 1줄**(거짓 실패와 구분) | ○ (1차 REQ-N-032·037·038) | **0.5~0.75** | 0.25 |
| ⑩ **기준 시각 고정·이동** | **`core/clock.py`의 `now()` 단일 진입점** + `QA_CLOCK_OFFSET_SECONDS`(**음수 허용**). 코드에서 현재 시각 직접 호출 금지(린트 규칙으로 차단). **적용/비적용 범위는 §10.3** | ○ (진입점만) | **0.25~0.5** | 0.25 |
| **⑪ (신규)** **개인정보 컬럼 목록 출력** | `manage.py qa_pii_columns` — 모델 필드의 `pii=True` 선언에서 **테이블·컬럼·수집 목적·보관 기간 상수**를 표/ json으로 출력. §5.0이 이미 보관 기간을 테이블별 상수로 선언하므로 **같은 선언에서 뽑는다**. REQ-N-020(처리방침 수집 항목 ↔ 스키마 양방향 대조)과 REQ-N-038(항목별 보관) 판정 증거로 재사용 | ○ (qa R1 #11) | **0.25** | 0.1 |
| | **합계** | | **3.0 ~ 3.5작업일** (v0.1 2.7~3.2 + ⑤⑥⑪ 반영분 **+0.3**) | **2.9 ~ 3.7작업일** |

**⑩을 1차에 넣는 이유**: 시각 진입점을 나중에 한 곳으로 모으려면 **이미 작성된 모든 코드를 고쳐야 한다.** 1차에 0.25~0.5작업일을 쓰면 2차에는 오프셋 적용만 남는다.

### 10.2 도구 출력·동작 규격 (qa R1 Q-4 회신 반영 — **전건 수용**)

> qa가 §16 Q-4에서 요구한 출력 형식을 **그대로 확정**한다. 이 규격대로 만들면 P5에서 증거 가공(수작업 편집)이 사라진다. 명령 이름·환경 변수 이름은 v0.1 제안이 qa 수용으로 확정됐다.

| 도구 | 확정 규격 |
|---|---|
| `qa_show <model>` | ① 기본 출력에 **`public_ref` · `created_at`(ISO8601 + KST 병기) · `status` · 마스킹된 이름·연락처**(`홍*동` / `010-****-5678`) ② **`--count-only`** (건수만 정수 1줄 — REQ-F-046 ② "저장 1건" 판정) ③ **`--since <ISO8601>`** (TC 실행 구간 한정) ④ **`--format table\|json`** (json은 증거 파일로 그대로 첨부 가능한 단일 JSON 배열) ⑤ **결과 0건도 종료 코드 0** (오류 = 1과 구분) ⑥ `--masked` 기본 on, 해제 옵션 없음 |
| `qa_mail_log` | 열: `kind` · `to_addr`(마스킹) · `status` · `attempts` · `last_error` · **`scheduled_at`(요청 시각)** · **`sent_at`(발송 시각)** · `related_ref`. **`--kind`·`--since` 필터**, `--format table\|json`. **요청 시각과 발송 시각이 모두 보일 것**(M-8 "로그는 즉시, 발송은 5분 이내" 판정) |
| `qa_purge_test_data` | **테이블별 삭제 건수** 출력(§10.4) · **`--dry-run`**(삭제 없이 대상 건수만) · `--confirm` 없이는 실제 삭제하지 않음 · 종료 시 **총계 1줄**과 실행 시각을 `core_jobrunlog`에 기록 |
| `qa_pii_columns` | 열: 앱·모델·테이블·컬럼·타입·수집 목적·**보관 기간 상수(일)** · 마스킹 대상 여부. `--format table\|json` |
| `seed_standard` | **고정 시드(재실행 시 동일 결과)**. 1차분 = 문의 동시 제출·빈도 제한 재현 데이터 + 번호 1,000건 생성 스크립트. **1차분은 이월 대상에서 제외**(qa 요청 수용 — §11.2 ⓑ에서 제외 근거로 반영) |
| `QA_FAIL_INJECT` | 3종 **독립 토글**(콤마 목록). 주입 시 **로그 1줄**로 주입 사실 표시 |
| `QA_CLOCK_OFFSET_SECONDS` | **음수 허용**(과거로 이동). 적용 시 **기동 로그에 `CLOCK OFFSET: <n>s` 1줄**. **`/healthz`에는 노출하지 않는다**(REQ-N-031 — 헬스 응답에 부가 정보 금지) |
| 공통 | 모든 `qa_*` 명령은 **`QA_TOOLS_ENABLED=1`이 아니면 "이 환경에서는 사용할 수 없습니다" 메시지 + 종료 코드 2**로 끝난다. 운영 이미지에는 명령 자체가 없다(§10.6) |

### 10.3 기준 시각(clock) 적용 범위 (qa R1 #5)

> **오프셋이 "일부만" 적용되면 오판정이 난다.** 1차에 관계되는 경로를 전부 명시한다.

| 구분 | 대상 | v0.2 확정 |
|---|---|---|
| **적용(오프셋이 움직인다)** | `inquiry_inquiry.created_at` · `inquiry_inquiry.consent_at` · `core_ratelimitcounter.window_start`·`blocked_until` · `mailer_outbox.scheduled_at`·`sent_at` · `core_jobrunlog.started_at`·`finished_at` · 보관 기간 만료 판정 | **전부 `core.clock.now()` 경유로 구현한다.** `auto_now_add`·`auto_now`·`default=timezone.now`·DB `DEFAULT now()`를 **이 컬럼들에 쓰지 않는다**(린트 규칙 + 코드 리뷰 항목) |
| **비적용(오프셋과 무관)** | ⓐ **supercronic의 cron 스케줄 자체**(컨테이너 시스템 시계로 돈다) ⓑ `created_at`/`updated_at` 중 **감사·운영 목적 컬럼**(프레임워크 기본 테이블: 세션 만료 등) ⓒ HTTP 캐시 헤더·쿠키 만료(브라우저 시계) ⓓ nginx·PostgreSQL 로그 타임스탬프 | **cron은 오프셋 대상이 아니다.** 시간 의존 배치(파기·백업·요약)의 P5 판정은 **오프셋이 아니라 ⓐ 수동 실행(`manage.py purge_expired`) + ⓑ `--dry-run` + ⓒ `QA_RETENTION_MINUTES__INQUIRY` 단축**의 조합으로 한다 |
| 확인 수단 | 오프셋이 실제로 걸렸는지 | 기동 로그 `CLOCK OFFSET: <n>s` 1줄 + `qa_show … --format json`의 `created_at` 값 |

### 10.4 `qa_purge_test_data` 삭제 대상과 식별 규칙 (qa R1 #10)

| 테이블 | 식별 규칙 | 비고 |
|---|---|---|
| `inquiry_inquiry` | `name LIKE 'TEST-%'` **또는** `message LIKE 'TEST-%'` | 사용자 입력에 접두어가 붙는 유일한 테이블 |
| `mailer_outbox` | 위에서 삭제된 문의의 **`related_ref` 연계** + `to_addr`가 테스트 수신 도메인(`@example.test`) | 접두어가 없으므로 **연계와 수신 주소**로 잡는다 |
| `core_ratelimitcounter` | **`--since` 구간(TC 실행 구간) 내 레코드 전량** | 해시 식별자라 개별 매칭이 불가능 → 기간 기준 |
| `core_jobrunlog` | **`--since` 구간 + `job` 이름이 `qa_*`이거나 `QA_FAIL_INJECT` 주입 실행인 것** | 정상 운영 기록은 남긴다 |
| `accounts_user` (2차) | `email LIKE 'test-%@example.test'` | 1차에는 운영자 계정만 존재 |
| 출력 | **테이블별 삭제 건수 + 총계**, `--dry-run`이면 "삭제 예정 건수" | 요건 ⑤의 "전량 삭제 + 삭제 확인 기록"을 이 출력으로 증명한다 |

- **`--since`가 없으면 카운터·작업 로그는 건드리지 않는다**(안전 기본값). P5 종료 시 qa는 TC 실행 구간 전체를 `--since`로 주어 1회 실행한다.

### 10.5 Safari · iOS(WebKit) 검증 수단 (qa R1 #8 — G3a 조건 C1)

> pmo 권고인 **"WebKit 자동화 + 실기기 체크리스트 병행"** 을 설계에 반영한다. 자동화만으로는 가상 키보드를 재현할 수 없고, 실기기만으로는 재현성이 없다.

| 수단 | 내용 |
|---|---|
| **① 관측 신호(제작 구현)** | G-9 폴백이 실행되면 `<html>`에 **`data-vk-fallback="1"`** 을 설정한다(`visualViewport` 경로 진입 시). 미지원·미적용이면 속성 자체가 없다. 동시에 **`--fixed-bar-h`의 실측값**을 `document.documentElement.style`에 반영하므로 자동화에서 `getComputedStyle`로 읽을 수 있다 |
| **② WebKit 자동화 판정** | WebKit 엔진 자동화에서 ⓐ `html[data-vk-fallback="1"]` 존재 ⓑ `visualViewport` 크기 변경 이벤트 발생 시 `--fixed-bar-h`·`--body-pad-bottom`이 갱신되는지 ⓒ `scroll-padding-bottom`이 `--body-pad-bottom`과 같은지 를 확인한다. **"폴백 경로가 실제로 실행됐는가"를 판정**하는 것이 목적이며, 가상 키보드 자체의 재현이 아니다 |
| **③ 실기기 체크리스트(제작 제공, `developer/site/qa/webkit_checklist.md` — 이 문서의 다른 `qa/` 표기도 전부 `site/` 기준이다)** | 초안 항목: ⓐ iOS Safari 360px에서 문의 폼 입력란 포커스 → **키보드가 올라온 상태에서 고정 바가 입력란·전송 버튼을 가리지 않는가** ⓑ 키보드를 닫았을 때 레이아웃이 원복되는가 ⓒ 입력란 포커스 시 **자동 확대(zoom)가 일어나지 않는가**(`font-size` 16px 하한, §9.1) ⓓ 주소 복사(`execCommand` 폴백 포함) 동작 ⓔ `<details>` 기반 모바일 메뉴(CMP-005) 개폐와 포커스 순서 ⓕ Safari 하단 툴바가 겹치는 구간(`env(safe-area-inset-bottom)`) — 각 항목에 **기대 결과·캡처 지점**을 적는다 |
| **④ 뷰포트 축소로 대체하지 않는다** | 페이지 디자인 §8.5 D-12가 경고한 대로 **데스크톱 브라우저의 뷰포트 축소는 거짓 Pass**를 만든다. ②는 "폴백 실행 여부"만, ③은 "실제 가림 여부"만 판정한다 |
| 산출물 등록 | ①은 §11.1 작업 3·13에, ③ 문서는 **작업 13의 산출물 목록에 명시**한다 |

### 10.6 검증 도구 안전장치 (필수 — qa R1 #4 · devops R1 #2 반영으로 **v0.2에서 5중으로 강화**)

| # | 장치 | v0.2 내용 | qa가 밖에서 확인하는 증거 |
|---|---|---|---|
| **①** | **마스터 스위치** | **`QA_TOOLS_ENABLED=1`이 명시된 경우에만** `QA_*`를 해석한다. 환경 이름(`DJANGO_ENV`)에 의존하지 않는다 — **스테이징 `.env`를 운영에 복사하는 사고**가 정확히 `DJANGO_ENV` 오설정이기 때문이다(qa #4 ⓐ) | 기동 로그 `QA_TOOLS: off` / `QA_TOOLS: ON — 이 환경은 인증 뒤에 있어야 합니다` |
| **②** | **구조적 제외** | prod 타깃 빌드에서 **`qa/` 디렉토리 전체를 COPY하지 않는다**. v0.1의 `config/qa_settings.py`를 **`qa/qa_settings.py`로 옮겨**(§4) 설정 해석기까지 함께 빠지게 했다 | **이미지 레이어 파일 목록에 `qa/`·`qa_settings.py` 0건** (REQ-N-018의 이미지 검색과 같은 회차에 수행) |
| **③** | **존재하지 않으면 기동 거부** | prod 이미지에서 `QA_TOOLS_ENABLED=1`이면 `qa.qa_settings` **import가 실패해 기동이 거부된다**. 값 설정 실수와 무관하게 구조가 막는다. 추가로 `DJANGO_ENV=production` + `QA_*` 조합도 기동 거부(v0.1 유지) | 배포 로그의 기동 실패 메시지 |
| **④** | **명령 미등록** | `qa_*` 관리 명령은 `qa/` 안에 있으므로 prod 이미지에서 **등록 자체가 안 된다** | **`manage.py help` 출력에 `qa_` 명령 0건** |
| **⑤** | **HTTP 노출 0** | 검증 도구는 전부 관리 명령이며 **URL 라우팅에 어떤 `qa_*` 경로도 등록하지 않는다**(§3.5.1 ②). `QA_SESSION_TOKEN`이 없으면 `qa_session`은 동작하지 않는다 | URL 목록(`manage.py show_urls` 상당) 검사 — `qa` 경로 0건 |

- 위 5행의 **증거 열이 곧 P5 체크리스트**다(qa #4 ②). qa는 ②④⑤를 **1회차에 함께 수행**하고 결과를 테스트 결과서에 첨부한다.
- **스테이징은 인증 뒤에 둔다**(§3.5.1) — 도구가 켜진 환경이 무인증으로 열려 있으면 그 자체가 Critical이다.

---

## 11. 1차 구현 범위와 순서

### 11.1 작업 단위·예상 일수

| # | 작업 | 산출물 | 관련 SCR/REQ | 예상(작업일) |
|---|---|---|---|---|
| 1 | 프로젝트 스캐폴딩 · 설정 분리(local/staging/production) · **로컬 compose(app·db·mail)** · Dockerfile 멀티스테이지 · `/healthz` · `.env.example` | 기동 가능한 빈 앱 | REQ-N-034·031·018 | **1.5** |
| 2 | **커스텀 사용자 모델 + 초기 마이그레이션** · 콘텐츠 모델 3종 · `seed_content` · 시드 파일 | 데이터 기반 | §5.1, REQ-F-021·064 | **0.75** |
| 3 | 디자인 토큰 이식 · `base.html` · 헤더/푸터/고정 바/스킵링크 · 폰트 self-host · 아이콘 태그 · 반응형 4구간 | 공통 레이아웃 | CMP-001~009, §3.0 G-1~G-11 | **1.75** |
| 4 | SCR-001 메인 (Hero·강점·강사 미리보기·유형 소개·위치 요약·전환 섹션, 최소 구성 5섹션 대응) | `/` | REQ-F-010~015 | **0.75** |
| 5 | SCR-002 강사 소개 (0·1·3·12명 경계 레이아웃, 사진 없는 강사 이니셜 대체) | `/instructors` | REQ-F-020~023 | **0.5** |
| 6 | SCR-003 오시는 길 (지도 클릭 투 로드·대체 영역 높이 고정·길찾기·주소 복사) | `/location` | REQ-F-030~035 | **0.75** |
| 7 | **문의 폼** (서버·클라이언트 검증, honeypot, 빈도 제한, 동의, 중복 제출 방지, 상태 6종, DB 저장) | `/location#contact` | REQ-F-040~046, N-019·020 | **1.25** |
| 8 | **메일 아웃박스 + SMTP + 스케줄러 컨테이너** (문의 알림 1종, 재시도·실패 기록) | 알림 동작 | REQ-F-045, N-037 | **0.75** |
| 9 | SCR-006 처리방침(2단 TOC·표→카드 전환) · SCR-008 404(실제 404) · SCR-009 오류·점검 | 보조 화면 | REQ-F-050~053·060·065 | **0.75** |
| 10 | SEO 마감(메타·canonical·OG·sitemap·robots·구조화 데이터) · 접근성 마감 · `<noscript>` | 검증 통과 상태 | REQ-N-009~016·028·029 | **0.75** |
| 11 | 성능 마감(폰트 subset·**폴백 메트릭 실측**·압축·캐시 헤더) + Lighthouse 3회 측정 | 측정 기록 | REQ-N-004·005·007·015 | **0.75** |
| 12 | **운영 compose · 이미지 빌드·배포·롤백 스크립트 · `run_backup`/복구·회전 · 로그 회전 · 스테이징 구성 · nginx 설정 예시(운영·스테이징·로컬 3종) · 점검 화면 정적 파일 · 일일 운영 요약 메일 · 로컬 `proxy`/`backup` 프로필** | 배포 가능 상태 | REQ-N-031·032·033·034·040 | **2.0 ~ 2.25** (v0.1 1.5 + **R1 반영 +0.5~0.75**) |
| 13 | **검증 지원 도구 ①~⑪ (1차분)** | qa 인계 | §10 | **3.0 ~ 3.5** (v0.1 2.7~3.2 + **+0.3**) |
| 14 | 자체 점검(HTML·링크·`[TBD]` 검색·비밀 정보 검색·`check --deploy`) · **개발 보고서(P4-③)** | 보고 | M-4·M-5, REQ-N-023 | **0.5** |
| | **합계** | | | **15.7 ~ 16.45** (v0.1 14.9~15.4) |

**R1 반영으로 늘어난 공수의 내역 (+0.8 ~ 1.05작업일)**

| 항목 | 근거 | 공수 |
|---|---|---|
| `manage.py run_backup`(pg_dump 호출·무결성 확인·회전·`core_jobrunlog`·실패 시 아웃박스 INSERT) — 기존 `backup.sh`·별도 컨테이너 대체 | devops #1 | +0.1 (스크립트를 명령으로 옮기는 것이라 순증이 작다) |
| 로컬 `proxy`·`backup` 선택 프로필 + `deploy/nginx/local.conf` | qa #2 | **+0.5** |
| 자립형 정적 `maintenance.html` + `error_page` 배치 절차 | devops #5 | +0.1 |
| 일일 운영 요약 메일(`report_failures` 확장) | devops #9 | **+0.25** |
| 배포 절차 보강(스케줄러 정지 단계·이미지 존재 점검·다운타임 실측)·`restore.sh` 가드 | devops #6·#7·#8·#14 | +0.1 |
| `qa_pii_columns` 신설 · `qa_purge_test_data` 확장 · WebKit 관측 신호·체크리스트 문서 | qa #10·#11·#8 | **+0.3** (작업 13) |
| **소계** | | **+0.8 ~ 1.05** (반올림 정리 후 표 반영) |

### 11.2 ⚠ 일정 성립 여부 — **pmo·PM 확인 필요**

| 항목 | 값 |
|---|---|
| 계획서 WBS의 1차 구현 창 | 09-30(수) ~ 10-14(수) — 인프라 선착수 + 화면 구현 + 빌드 확인 |
| 그 구간의 실제 작업일 | **약 10작업일** (주말 제외, 10-09 한글날 제외) |
| 이 문서의 산정 (v0.1) | **약 15작업일** (검증 지원 도구 2.7~3.2 포함) |
| **이 문서의 산정 (v0.2 — R1 반영 후)** | **약 16작업일** (검증 지원 도구 3.0~3.5 포함) |
| **차이** | **약 6작업일 부족** (v0.1 기준 5일) |

**흡수 방안(권고 순)**

| 안 | 내용 | 효과 | 비용 |
|---|---|---|---|
| **ⓐ 기준 오픈일(11-06) 사용** | 조기 오픈(10-29)은 목표로만 두고 **버퍼 구간(11-02~11-12)을 계획대로 활용** | +5~7작업일 | 없음. 계획서 §4.2.2가 이미 "조기 오픈은 약속하지 않는다"로 정리했다 |
| ⓑ 검증 지원 도구 중 2차 전용분 이월 | ⑦(로그인 세션) 골격을 2차로 미루고 ⑧의 **2차 시드**만 제외 | +0.25~0.5 | **qa R1 회신으로 합의됨** — ⑦ 본체·⑧ 2차 시드는 이월 동의, **⑧의 1차분(문의 동시 제출·빈도 제한 재현)은 REQ-F-046 ② 판정에 직접 쓰이므로 이월 불가**, **④·⑨·⑩ 1차 필수에 전적 동의**. 이 셋을 빼면 1차 Must 최소 5건이 판정 불가가 된다 |
| ⓒ Could 3건 제외 | SCR-009 공용 오류 화면 · REQ-F-034 주소 복사 · REQ-N-030 | +0.3~0.5 | 효과가 작다. **REQ-N-030은 이 스택에서 사실상 공짜**이고 qa도 "제외하지 말고 Pass로 가져가는 편이 이득"으로 회신했다. **SCR-009는 devops #5로 오히려 필요성이 커졌다**(앱 다운 시 nginx가 낼 화면이 필요) |
| ⓓ 범위 축소 | — | — | **권고하지 않는다.** 1차 Must 60건은 줄일 수 없고 CR 대상이다 |

> **developer 권고: ⓐ**. 작업 속도가 아니라 **고객·운영자 측 확보 항목(도메인 10-16, 실제 값 10-16, SMTP 계정)** 이 조기 오픈의 실제 제약이라는 계획서 §4.2.2 판단과 방향이 같다.
> **devops·qa 모두 ⓐ를 지지**했다(R1 Q-7). devops 근거는 **직렬 의존성**(조기 오픈 경로는 도메인→인증서→DNS 전파→시크릿→배포 리허설→**복구 리허설(G7a 조건)**→배포→스모크가 4일에 직렬로 들어가 흡수 여유 0), qa 근거는 **검증 창 보호**(구현이 하루 밀리면 P5 창이 그대로 하루 줄어든다)다.
> **v0.2에서 차이가 6일로 커졌으므로 이 항목은 그대로 PM 결정 사항이다**(§14.4 PM-1). 10-14 체크포인트에서 진척을 보고 즉시 보고한다(TR-1).

---

## 12. 배포 · 백업 · 복구

### 12.1 이미지 빌드

- 멀티스테이지 `Dockerfile`: `base`(런타임 의존성) → `dev`(개발 도구·바인드 마운트) → `prod`(소스 COPY + `collectstatic` + 압축, 비루트 사용자, `qa/` 제외).
- 태그: `yogapass-app:${APP_VERSION}`(릴리스 태그 `release-v0.1.0`과 1:1) + `yogapass-app:<git-sha>`.
- **레지스트리를 쓰지 않는다** — 단일 서버이므로 서버에서 릴리스 태그를 체크아웃해 빌드한다. (레지스트리 도입 여부는 devops 판단 사항으로 남긴다.)
- **롤백용 이전 이미지 보존 (devops R1 #7 — 롤백의 전제)**: 이전 버전은 **서버 로컬 이미지에만** 존재하므로 `docker image prune -a` 한 번으로 롤백 경로가 사라진다. 3중으로 막는다.
  1. 모든 앱 이미지에 **보존 라벨** `org.yogapass.keep=release` 를 붙인다(`Dockerfile`의 `LABEL`).
  2. `deploy.sh` 0단계에서 **"롤백 대상 태그(= 현재 가동 중 이미지) 존재 확인"** 을 수행하고, 없으면 **배포를 중단**한다.
  3. P8 운영 가이드에 **"`docker image prune -a` 금지, 정리는 `docker image prune --filter 'label!=org.yogapass.keep=release'` 로만"** 을 명시한다(devops R1 §5 "롤백" 항목).
- 직전 **3개** 릴리스 이미지 태그를 보존한다(그 이전은 위 필터로 정리 가능).
- **소스 반입 수단은 미결이다** — §12.1이 "서버에서 릴리스 태그를 체크아웃해 빌드"를 전제하는데 **프로젝트 저장소에 원격이 없다**(원격 생성·push는 CLAUDE.md §8상 PM 승인 사항). 대안은 태그 스냅샷 아카이브 반입이다. **어느 쪽인지 10-16까지 정해져야 배포 계획서를 명령 단위로 쓸 수 있다** → **§14.4 PM-4**.

### 12.2 배포 절차 (`deploy/deploy.sh`)

```
0)   사전 점검 : 릴리스 태그 확인 · .env 존재 · 디스크 여유 5GB 이상(미만이면 중단)
                · 현재 이미지 태그 기록 · ★롤백 대상 이미지 존재 확인(없으면 중단)
                · # IRREVERSIBLE 마이그레이션 유무 확인
                · ★최근 24시간 내 run_backup 성공 기록 확인(없으면 경고 — devops R2 #2 ①)
0.5) ★스케줄러 정지 : docker compose … stop scheduler        ← v0.3에서 2.5단계를 여기로 앞당겼다
                     (정기 03:00 run_backup 과 1단계 라벨 백업의 락 경합 자체를 없앤다 — devops R2 #1 ①)
1)   백업      : docker compose … run --rm scheduler python manage.py run_backup --label pre-deploy
                ← 되돌릴 수 없는 마이그레이션이 있으면 필수
                ← ★라벨 백업은 락 충돌 시 skipped 를 성공으로 보지 않는다. 종료 코드 ≠ 0 이면 배포 중단
                  (devops R2 #1 ②). 실행 주체를 app 이 아니라 scheduler 로 둔 이유는 §3.5(devops R2 #5)
2)   빌드      : docker compose -f compose.yaml -f compose.prod.yaml build
3)   마이그레이션: docker compose … run --rm app python manage.py migrate --noinput
4)   기동      : docker compose … up -d --no-deps app scheduler   ← 스케줄러 재기동 포함
5)   확인      : /healthz 200 (★앱에 직접 호출 — nginx 비경유, devops R2 #3)
                · 주요 4경로 200 (프록시 경유. 스테이징은 인증 자격으로 호출)
                · 로그 오류 0 · 정적 파일 해시 응답 · ★scheduler 헬스 상태 확인(devops R2 #2 ③)
                · ★다운타임 실측값 기록(0.5단계 시작 ~ /healthz 최초 200)
6)   실패 시    : deploy/rollback.sh 자동 호출 (rollback.sh도 같은 정지→복귀→기동 순서)
```

**0.5단계(구 2.5단계)를 넣는 이유 (devops R1 #6 · v0.3에서 순서 변경 — devops R2 #1)**: 3단계 시점에 `scheduler`는 **구버전 이미지로 1분 주기 `send_outbox`·`purge_expired`를 계속 실행 중**이다. 스키마가 바뀌는 순간 배치가 실패해 **거짓 실패 알림**이 나가거나, 파괴적 변경 시 데이터에 손을 댈 수 있다. 1분 주기 작업이라 **정지 구간의 부작용은 없다**(다음 주기에 밀린 것이 처리된다 — 모든 명령이 재실행 안전이기 때문).
> **v0.3에서 2.5 → 0.5단계로 앞당긴 이유**: 락(§3.3)이 도입되면서 **03:00 정기 `run_backup` 이 도는 중에 배포가 시작되면 1단계 라벨 백업이 `skipped` 로 정상 종료**되어, `# IRREVERSIBLE` 마이그레이션의 유일한 복구 전제가 **무음으로 사라진다**(devops R2 #1). 정지를 백업보다 앞에 두면 경합 자체가 없어지고, 정지 구간이 빌드 시간만큼 늘 뿐이다. 보강으로 **라벨 백업은 `skipped` 를 실패로 다룬다**(§12.5.1 · `restore.sh` 도 동일).

**배포 창·다운타임 목표 (devops R1 #8 — TR-9)**

| 항목 | 값 |
|---|---|
| 배포 창(권고) | **평일 07:00 이전 또는 23:00 이후** — "트래픽이 적은 시간대"를 수치로 고정한다. 최종 확정은 devops 배포 계획서 |
| **목표 다운타임** | **60초 이내** (헬스체크 `start_period` 20s + 재기동 감안 시 실측 20~60초대 예상) |
| 초과 시 | **nginx `error_page`의 정적 점검 화면이 노출된다**(아래 §12.3 — 앱이 없어도 보이는 화면이다) |
| 기록 | 5단계에서 **실측 다운타임을 배포 기록에 남긴다.** 이 값이 배포 계획서의 롤백 판단 기준(권고: **5분 내 `/healthz` 미회복 시 롤백**)의 근거가 된다 |
| 무중단 아님 | TR-9 그대로 수용. 무중단이 요구되면 CR |

### 12.3 기존 nginx에 요청할 설정 — **9행** (devops 확정 · 샘플 2종 제공)

> **샘플 파일을 운영·스테이징 2개로 분리 제공**한다(devops R1 Q-5 권고): `deploy/nginx/yogapass-prod.conf.sample` · `yogapass-stg.conf.sample`. 여기에 **로컬 `proxy` 프로필이 그대로 쓰는 `local.conf`** 를 더해, **같은 지시어 집합을 로컬에서 먼저 검증**한다(§3.2.1).
> **요청 항목 전부가 `server`/`location` 레벨이며 전역(`http`) 블록 변경 요청은 0건이다** — I-2-c(다른 서비스 공유) 충돌 위험을 구조적으로 없앤 지점이므로 v0.2에서도 유지한다.

| # | 항목 | 요청 내용 | 운영 | 스테이징 | 로컬 프로필 |
|---|---|---|---|---|---|
| 1 | 라우팅 | `proxy_pass` → 앱(`127.0.0.1:${APP_PORT}` 또는 컨테이너 이름, I-2-a에 따름) | ○ | ○ | ○ (`app:8000`) |
| 2 | 헤더 | `X-Forwarded-Proto` · `X-Forwarded-For`(`$proxy_add_x_forwarded_for`) · `Host` 전달. **앞단에 또 다른 프록시(CDN 등)가 있으면 `TRUSTED_PROXY_COUNT` 값이 달라진다 → 스테이징에서 실측**(§13 #6) | ○ | ○ | ○ |
| 3 | 오류 가로채기 | **`proxy_intercept_errors off`** — 앱의 404·500 화면이 nginx 기본 화면으로 바뀌면 REQ-F-060·065가 깨진다. **nginx 기본값이 off이므로 이것은 "변경 요청"이 아니라 ⓐ 기존 `http` 블록에서 on으로 켜 두지 않았는지 확인 + ⓑ 켜져 있으면 우리 `server` 블록에서 off로 재정의**다(devops R1 Q-5). 재정의해도 **다른 서비스의 상속값은 유지**된다 | ○ | ○ | ○ |
| 4 | **압축 (v0.2 신설 — devops R1 #4)** | **우리 server 블록 한정**으로 `gzip on; gzip_proxied any; gzip_types text/html application/json application/xml image/svg+xml; gzip_min_length 1024;`<br>**이유**: "앱이 사전 압축본을 내려주므로 재압축 불필요"는 **WhiteNoise가 서빙하는 정적 자산에만** 맞다. **Django가 렌더하는 HTML은 압축 주체가 없고**, nginx의 `gzip_proxied` 기본값이 off라 프록시 응답에 적용되지 않는다 → 모바일 Lighthouse "텍스트 압축" 감점 | ○ | ○ | ○ |
| 5 | 로그 | **별도 access/error 로그 파일**(다른 서비스와 분리, I-2-c). **호스트 logrotate 대상에 새 파일 2개 등록 필요**(운영팀 작업 — 누락 시 디스크 증가) | ○ | ○ | ○ |
| 6 | **장애·점검 화면 (v0.2 보강 — devops R1 #5)** | `error_page 502 503 504 /maintenance.html;` + `location = /maintenance.html { root <정적 경로>; internal; }`<br>**대상 파일은 `deploy/nginx/maintenance.html`**(아래 설명) | ○ | ○ | ○ |
| 7 | HTTPS | HTTP→HTTPS 301, HSTS (REQ-N-017) — devops 소관. **`includeSubDomains`·`preload`는 도메인 구조 확인 전 금지**(§9.5, devops R1 #12) | ○ | ○ | ✕ (로컬 http) |
| 8 | **접근 제어 (v0.2 신설 — devops R1 #2 Must)** | **스테이징 server 블록 전체에 `auth_basic` + (가능하면) `allow`/`deny` 출처 제한.** 예외 경로 0건(외부 요청 기준 — 내부 `/healthz` 호출은 nginx 를 거치지 않는다, v0.3). 계정 생성·전달은 devops 배포 계획서(값은 문서에 쓰지 않는다) | **△ 선검증용 주석 블록** (v0.3, devops R2 #4) | **○ 필수** | ✕ |
| 9 | **색인 차단** | 스테이징 응답에 `add_header X-Robots-Tag "noindex, nofollow" always;` (앱에서도 강제 — 2중) | ✕ | ○ | ✕ |
| — | 업로드 | `client_max_body_size`(2차 사진 업로드 5MB 기준) — **1차에는 업로드가 없으므로 1차 요청 목록에서 제외**하고 2차에 요청한다(devops R1 Q-5) | 2차 | 2차 | 2차 |

**자립형 점검·502 화면 (devops R1 #5)**

- `templates/errors/maintenance.html`은 **앱이 살아 있어야 렌더된다.** 배포 중 다운타임(TR-9)이나 앱 크래시 구간에서는 렌더될 수 없으므로, **nginx 호스트 파일시스템에 놓는 정적 HTML 1개**를 별도 산출물로 만든다.
- 요건: **인라인 CSS, 외부 자산(폰트·이미지·JS) 요청 0건, 단일 파일, 빌드 없이 브라우저로 열린다.** 대표 전화 `tel:` 링크 포함. 디자인은 **SCR-008 변형 재사용**(design/mockups/scr-008.html).
- **배치에 `I-2-b`(nginx 쪽 파일 배치 권한)가 추가로 필요하다** — devops가 배포 계획서에서 경로와 반영 절차를 확정한다. 권한 확보가 안 되면 **배포 중 호스팅 기본 502 화면이 노출**되어 REQ-F-065 취지가 깨진다(리스크로 등록 — TR-13).
- **로컬 `proxy` 프로필에서 이 파일과 `error_page` 동작을 그대로 검증**한다(`app`을 내린 뒤 `:8080` 접근 → 점검 화면).

### 12.4 롤백 (`deploy/rollback.sh`)

| 상황 | 절차 |
|---|---|
| 코드만 문제 | `APP_VERSION=<이전 태그>` → `up -d` (수 초) |
| 되돌릴 수 있는 마이그레이션 | `migrate <app> <이전 번호>` 후 이미지 되돌리기 |
| **되돌릴 수 없는 마이그레이션** | 이미지 되돌리기 + **배포 직전 백업으로 DB 복구**(`restore.sh`). 데이터 손실 구간 = 배포 후 경과 시간 → **배포는 트래픽이 적은 시간대에** |
| 판단 기준 | 마이그레이션 파일의 `# IRREVERSIBLE` 표시(§2.4). 배포 전 체크리스트에서 확인 |
| **실행 순서 (devops R1 #6)** | `rollback.sh`도 배포와 같은 순서를 지킨다 — **① `scheduler` 정지 → ② 마이그레이션 되돌리기(필요 시) 또는 DB 복구 → ③ `APP_VERSION` 되돌려 `app`·`scheduler` 기동 → ④ `/healthz` 확인** |
| **전제 (devops R1 #7)** | **이전 이미지가 서버에 남아 있어야 한다.** `deploy.sh` 0단계에서 미리 확인하며(없으면 배포 자체를 중단), 라벨 필터로만 이미지를 정리한다(§12.1) |
| 롤백 판단 기준 | **배포 후 5분 내 `/healthz` 미회복 시 롤백**(권고값 — devops 배포 계획서에서 확정, §12.2) |

### 12.5 백업 · 복구 (REQ-N-032 — G7a 통과 조건) — **v0.2에서 실행 주체·알림 경로 확정 (devops R1 #1 Must)**

#### 12.5.1 실행 주체 — `scheduler`가 부르는 `manage.py run_backup` 하나로 일원화

> **v0.1의 문제**: `backup`이 `postgres:17-alpine` + 스크립트인 별도 상시 컨테이너여서 ⓐ 무엇이 일 1회를 트리거하는지 ⓑ 헬스체크 "프로세스 생존"이 무엇의 생존인지 ⓒ **실패를 누구에게 어떻게 알리는지**가 없었다. Django 앱이 아니라서 `mailer_outbox`·`core_jobrunlog`에 닿는 경로도 자명하지 않았다.
> **v0.2 결정**: devops 권고를 그대로 채택해 **백업을 앱 이미지의 관리 명령으로 만들고 스케줄러가 호출**한다. 앱 이미지에 **`postgresql-client` 17만 추가**한다(§2.7, 이미지 +~15MB).

```
[scheduler] supercronic (deploy/crontab)  ── 03:00 ──▶  manage.py run_backup
                                                          │
   ① pg_dump -Fc --file=${BACKUP_DIR}/yogapass-<env>-YYYYMMDD-HHMM.dump
   ② 무결성 확인 : 파일 크기 > 0  AND  pg_restore --list <파일> 성공
   ③ 회전       : 일 7 · 주 4 · 월 3 유지, 초과분 삭제
   ④ 기록       : core_jobrunlog (job='run_backup', status, detail=파일명·크기·소요초)
   ⑤ 실패 시     : mailer_outbox INSERT (kind='backup_failed', to=OPS_ALERT_TO)  ← 즉시 알림
   ⑥ 항상       : 결과가 다음 날 08:00 일일 운영 요약 메일 ⓒ에 포함                ← 성공도 보인다
```

| 이 방식이 닫는 것 | 내용 |
|---|---|
| **실행 주체** | `scheduler`(supercronic) — §3.3 표에 **행 1개 추가**로 끝났다. 별도 컨테이너·별도 cron·별도 헬스체크가 사라졌다 |
| **REQ-N-032 ③ 실패 알림 경로** | ⑤ `mailer_outbox` → `send_outbox`(1분 주기) → SMTP. **아웃박스 경로를 그대로 타므로 재시도·발송 로그가 공짜로 따라온다.** 알림이 안 나가도 ④의 `core_jobrunlog`에 남고 ⑥의 요약 메일에 다시 나타난다(**2중 통지**) |
| **검증 요건 ⑨ⓑ(백업 강제 실패) 충족 경로** | `QA_TOOLS_ENABLED=1 QA_FAIL_INJECT=backup` → `run_backup`이 ①에서 의도적으로 실패 → ④ `status=failed` → ⑤ `kind=backup_failed` INSERT. qa는 **`qa_mail_log --kind backup_failed`** 와 **Mailpit 수신**으로 판정한다. **v0.2부터 로컬 `backup` 프로필에서도 재현된다**(스테이징 의존 해소 — qa R1 #2 부수 영향) |
| **`--dry-run`·재실행 안전** | `run_backup --dry-run`은 대상 경로·여유 공간·회전 예정 파일만 출력한다. 같은 시각 중복 실행은 §3.3의 어드바이저리 락이 막는다 |
| **배포 직전 임시 백업** | `run_backup --label pre-deploy` (§12.2 1단계, 실행 주체는 `run --rm scheduler` — devops R2 #5). 라벨이 붙은 파일은 **회전 대상에서 제외**하고 최근 3개만 유지. **v0.3(devops R2 #1 ②): 라벨이 붙은 실행은 `required=True` 로 동작해 락 충돌 시 `skipped` 로 조용히 끝나지 않고 종료 코드 ≠ 0 으로 실패**하며, `deploy.sh`·`restore.sh` 는 이를 **중단 사유**로 처리한다 |

#### 12.5.2 백업 설정

| 항목 | 값 |
|---|---|
| 대상 | DB 논리 백업(`pg_dump -Fc`) + 미디어 볼륨(2차). **`.env`는 백업 대상에서 제외** — 아래 §12.5.4 |
| 주기 | **일 1회 03:00**(잠정, D-31) + 배포 직전 임시 백업 |
| 회전 | 일 7 · 주 4 · 월 3 (잠정). devops R1 Q-6: **1차 규모에서 과하지 않다**는 평가 수용 |
| 저장 위치·권한 | 호스트 `${BACKUP_DIR}` 바인드 마운트. **DB 데이터 볼륨과 다른 디렉토리**에 두고 **디렉토리 `0700` · 파일 `0600` · 소유자 = 배포 계정**. **웹 문서 루트·공유 디렉토리 아래에 두지 않는다**(개인정보 평문 파일 — 가장 흔한 유출 경로) |
| 사전 점검 | 여유 공간이 `BACKUP_MIN_FREE_GB` 미만이면 **백업을 시도하기 전에 경고 알림**을 보낸다(디스크 부족은 백업 중단의 최다 원인) |
| 무결성 | 백업 직후 파일 크기 > 0 + **`pg_restore --list` 성공** 확인. 실패 시 위 ⑤ 경로. **오프사이트가 없을수록 "그 파일이 실제로 읽히는가"가 중요하다**(devops R1 Q-6 부수 확인 — 설계 유지) |
| **권한자 목록·위치 문서화 시점 (qa R1 #13)** | REQ-N-039의 1차 수용 기준은 *"운영 DB 접근 권한자 목록이 배포 계획에 기록된 최소 인원과 일치 / qa 계정 0건"* + *"백업 파일 위치·접근 권한 문서화"* 인데 **배포 계획서는 P7 산출물**이라 P5 시점에 증거가 없을 수 있다. → **devops에게 "권한자 목록·백업 경로·퍼미션 초안을 P5 시작 전(10-14)까지 제공"을 요청한다**(티켓 발행은 오케스트레이터 경유 — §16 Q-10). qa는 그 문서를 증거로 인용해 판정한다 |

#### 12.5.3 복구 (`deploy/restore.sh`)

| 항목 | 값 |
|---|---|
| 절차 | `restore.sh <파일>` → 빈 DB 생성 → `pg_restore` → `migrate --check` → `/healthz` 확인까지 자동 |
| **안전 가드 (devops R1 #14)** | 실제 사용 시점은 **사고 직후, 운영자가 가장 긴장한 상태**다. 3중으로 막는다: ⓐ **대상 프로젝트명·DB명·백업 파일명을 출력하고 명시적 확인 입력**(`yes`)을 요구 ⓑ **대상이 운영이면 추가 플래그**(`--i-know-this-is-production`) 요구 ⓒ **복구 전 현재 DB를 자동 덤프**(`run_backup --label pre-restore`) — 잘못 복구해도 되돌릴 수 있다. **이 덤프도 라벨 실행이므로 락 충돌 시 실패로 끝나며, 실패하면 복구를 진행하지 않는다**(v0.3, devops R2 #1 ②) |
| **복구 리허설** | **스테이징에서 1회 이상 실제 수행**(10-28). **가능하면 운영자 입회·운영자 손으로 수행**한다(devops R1 Q-6 ③ — 막히는 지점이 곧 P8 운영 가이드에 더 써야 할 내용이다). 소요 시간·문제점을 기록해 P8 운영 가이드에 싣는다. ⚠ **복구해 본 적 없는 백업은 백업이 아니다** |
| 실행 예시 | 리허설 결과와 함께 P8 운영 가이드에 싣는다 |

#### 12.5.4 `.env` 보관·재발급 (devops R1 #10)

> **v0.1의 "별도 안전 보관, 운영자 소관"은 절차가 아니다.** 덤프가 있어도 `POSTGRES_PASSWORD`·`DJANGO_SECRET_KEY`가 없으면 재구축이 막히고, 백업이 같은 서버에만 있으므로 **서버 장애 시 DB 백업과 `.env`가 동시에 사라진다**.

| 항목 | v0.2 확정 |
|---|---|
| 백업 대상 | **`.env`는 DB 백업 파일에 포함하지 않는다**(암호화 없는 덤프에 시크릿을 섞지 않는다) |
| 보관 | **값의 보관처(운영자의 비밀번호 관리 수단)와 전달 방식을 devops가 배포 계획서·P8 운영 가이드에 기록한다. 값 자체는 어떤 문서에도 쓰지 않는다** |
| **재발급 가능성(운영자 불안 해소)** | `DJANGO_SECRET_KEY`: **교체 가능**. 교체 시 무효화되는 것은 **세션과 서명 토큰뿐**이며 데이터 손실은 없다(1차는 로그인 사용자가 운영자뿐이라 영향이 사실상 없다). `POSTGRES_PASSWORD`: **복구 시 재설정 가능**(덤프 복원은 새 비밀번호로 한다). `EMAIL_HOST_PASSWORD`: 메일 제공자에서 재발급. → **`.env` 소실이 "복구 불가"를 뜻하지 않는다**는 점을 P8 운영 가이드에 명시한다 |
| 오프사이트 | 같은 서버에만 두면 서버 장애 시 함께 잃는다 → **§14.4 PM-3**(devops 권고: 1차 = 같은 서버 다른 디스크 1차 복사 + 주 1회 **암호화** 반출, **암호화 없이 반출하지 않는다**. 클라우드 오브젝트 스토리지는 외부 계정·유료 결제라 CLAUDE.md §8상 PM 승인 사항이므로 1차 기본안에서 제외) |

### 12.6 스테이징 활용 (REQ-N-040) — **v0.2에서 일정 재배치 (qa R1 #3 Must · #6 · devops R1 #11)**

#### 12.6.1 일정

| 용도 | v0.1 | **v0.2** | 근거 |
|---|---|---|---|
| **스테이징 가용(앱 스택 기동 + TLS + `auth_basic`)** | 명시 없음 | **10-15 (기한)** | qa #6 — §13의 스테이징 판정 5건이 전부 여기에 걸려 있다 |
| P5 검증 환경(운영 DB 접근 금지의 대체) | 10-15 ~ 10-21 | 10-15 ~ 10-21 | 유지 |
| **§13 #6(프록시 뒤 실제 IP) 확인** | 명시 없음 | **10-15 (P5 착수와 동시, 최우선)** | TR-3 Critical급인데 v0.1에서는 가장 늦게 확인되는 순서였다(devops #11) |
| **★ 스테이징 배포 1회 + 롤백 1회 (REQ-N-033)** | 10-26~28 | **10-17까지** | qa #3 — **1차 Must의 판정 시점을 P5 창 안으로** |
| **★ 백업 실패 주입 + 회전 확인 (REQ-N-032 ③④)** | 10-26~28 | **10-20까지** | 상동. 로컬 `backup` 프로필로 **10-15 이전에 선검증**도 병행 |
| 배포 리허설(전체 예행) | 10-26 ~ 10-28 | 10-26 ~ 10-28 (**P7 예행으로 유지**) | 위 1회 실행과 별개 |
| **복구 리허설 (REQ-N-032 ②, G7a 조건)** | 10-28 | **10-28 유지** | 요구사항 §5.3이 **"P5 또는 P7"** 을 허용한다. 운영자 입회가 필요해 앞당기기 어렵다 |
| HTTPS·보안 쿠키·프록시 IP 등 로컬 재현 불가 항목 확인 | §13 | §13 | 유지 |
| 2차 개발 중 1차 회귀 확인 | 2차 전 기간 | 2차 전 기간 | 유지 |

#### 12.6.2 REQ-N-032 · 033의 G5 판정 경로 (qa R1 #3 Must)

> **문제**: v0.1은 배포·복구 리허설을 10-26~28에 두었는데 **P5 검증 창은 10-15~10-21**이다. 그대로면 **G5 보고서에 1차 Must 2건이 "미검증"으로 남아** G5 권고를 조건부로만 낼 수 있다.

| 안 | 내용 | 채택 |
|---|---|---|
| **ⓐ 선행 실행 (qa 권고 · developer 채택)** | **전체 리허설이 아니라 "절차 1회 실행"으로 충분하다.** 10-17까지 **스테이징 배포 1회 + 롤백 1회**, 10-20까지 **백업 실패 주입 + 회전 확인**을 P5 창 안에서 수행하고 결과를 qa가 판정한다. 10-26~28 리허설은 P7 예행으로 유지 | **○ 우선안** |
| ⓑ G7 이월 | ⓐ가 일정상 불가하면 **"REQ-N-032·033은 G5 판정 대상에서 제외하고 G7 조건으로 이월"** 을 **pmo·PM과 사전 합의**한다. 합의 없이 미검증으로 남기지 않는다 | △ 대안 |

**ⓐ가 성립하기 위한 선행 조건 (하나라도 깨지면 즉시 ⓑ로 전환하고 pmo에 보고한다)**

| # | 조건 | 기한 | 책임 | 미충족 시 |
|---|---|---|---|---|
| 1 | 스테이징 환경 제공(서버 자원·포트·호스트명) | 10-13 | 운영팀·devops | ⓑ |
| 2 | 스테이징 TLS + `auth_basic` 구성 | 10-15 | devops | ⓑ (§13 스테이징 5건도 함께 P7 이월) |
| 3 | 1차 구현이 배포 가능한 상태(§11.1 #12 완료) | 10-16 | developer | ⓑ |
| 4 | `run_backup` 구현 완료(§12.5.1) | 10-16 | developer | 백업분만 ⓑ |

- **스테이징 TLS는 도메인 확정(10-16)과 무관하게 선행한다**(devops R1 #11). **사설 인증서(self-signed) 또는 운영팀 보유 도메인의 임시 서브도메인**으로 먼저 세운다 — 브라우저 경고는 검증에 지장이 없고 **보안 쿠키·HSTS·`X-Forwarded-Proto`·프록시 IP·헤더 확인은 모두 성립**한다. 스테이징 TLS 선행 구성은 devops가 맡는다.
- **스테이징 가용 기한 10-15를 넘기면 §13의 스테이징 판정 5건 + 메일 판정이 통째로 P7로 밀린다**(qa #6). qa 테스트 계획에 같은 문장을 쓴다.
- **`mail`(Mailpit)은 스테이징 필수 배치**로 확정했다(§3.2) — 선택적이면 스테이징 메일 판정 수단이 사라진다. 실제 SMTP 계정이 연결되면 그때 `EMAIL_HOST`를 교체한다.
- **선행 조건 #3·#4(구현 배포 가능 · `run_backup` 완료)는 10-16 종료 시점에 재확인하고 결과를 즉시 pmo·qa 에 통지한다**(v0.3 체크포인트 — qa R2 #5). PM-5 결정 기한(10-14)과 이 조건들의 판명 시점(10-16) 사이에 이틀의 시차가 있어, **테스트 계획 확정 시점에는 판정 범위가 확정되지 않는다**. qa 는 그 사이 REQ-N-032·033 TC 를 **"조건부(10-16 재확인)"** 로 태깅하고 ⓐ·ⓑ 두 경로의 판정 문구를 미리 써 두기로 했다.
- **G5 판정 범위(REQ-N-032·033을 포함할지)는 최종적으로 pmo·PM 결정 사항**이다 → **§14.4 PM-5**.

---

## 13. 로컬 http / 운영 HTTPS 차이 — 재현되지 않는 항목과 검증 방법

| # | 항목 | 로컬(http) | 검증 방법 | REQ |
|---|---|---|---|---|
| 1 | HTTP→HTTPS 리다이렉트 | **재현 불가**(nginx 없음) | **P7 운영** 또는 스테이징(https)에서 응답 헤더 확인 | REQ-N-017 |
| 2 | 보안 쿠키(`Secure`) | 로컬은 off로 동작. 켜면 **로그인 자체가 안 된다** | 스테이징에서 `Set-Cookie`의 `Secure; HttpOnly; SameSite=Lax` 확인 | REQ-N-M-002(2차) |
| 3 | HSTS | 재현 불가 | 스테이징·운영 헤더 확인. **로컬에 HSTS를 켜면 브라우저가 localhost를 https로 고정해 개발이 막힌다** | REQ-N-017 |
| 4 | 혼합 콘텐츠 경고 | 부분 재현(외부 자원 0건이라 발생 여지 없음) | P5는 "외부 http 자원 0건" 정적 확인, 최종은 P7 | REQ-N-017 |
| 5 | 클립보드 API(주소 복사) | **`http://localhost`는 보안 컨텍스트라 동작한다.** 단 LAN IP·스테이징 http 접근에서는 실패 | `execCommand` 폴백 병행 + 스테이징 https에서 최종 확인 | REQ-F-034, 요건 ③ |
| 6 | **프록시 뒤 실제 IP**(빈도 제한 식별) — **최우선(10-15)** | **v0.2: `--profile proxy`로 로컬 선검증 가능** (직접 접속이면 항상 정확하므로 v0.1에서는 재현 불가였다) | **운영에서 `X-Forwarded-For` 처리를 잘못하면 모든 요청이 같은 IP로 집계돼 빈도 제한이 전체 차단으로 변한다.** **재현 절차는 아래 §13.1** — 서로 다른 출처 2곳을 물리적으로 확보하지 않고도 판정한다. 로컬 프로필에서 선검증 → 스테이징에서 최종 확인. **Major 위험(TR-3)** | REQ-N-019 |
| 7 | SMTP TLS | 로컬은 Mailpit 평문 | 스테이징에서 실제 SMTP 연결(계정 확보 후). 도달·SPF/DKIM은 **P7 운영** | REQ-N-022 |
| 8 | 캐시·압축 헤더 최종형 | 앱 응답까지만 확인 | nginx 통과 후 헤더를 스테이징에서 확인(중복 압축·헤더 덮어쓰기 여부) | REQ-N-004 |
| 9 | 404·502 화면 가로채기 | 재현 불가 | 스테이징에서 앱을 내린 뒤 502 화면, 없는 경로에서 404 상태 코드 확인 | REQ-F-060·065 |
| 10 | canonical·OG·sitemap 절대 URL | `SITE_BASE_URL`이 localhost | 도메인 확정 후 스테이징·운영에서 값 확인 | REQ-N-013 |
| **11** | **HTML 응답 압축**(신설 — devops R1 #4) | **v0.2: `--profile proxy`로 로컬 검증 가능**(nginx 없이 `:8000` 직접 접근에서는 HTML이 비압축) | `:8080` 응답의 `Content-Encoding: gzip` 확인(로컬) → 스테이징에서 기존 nginx 형태로 재확인. **Lighthouse "텍스트 압축" 항목이 여기에 달려 있다** | REQ-N-004 |
| **12** | **스테이징 접근 제어**(신설 — devops R1 #2) | **부분 재현 가능(v0.3, devops R2 #4)**: `deploy/nginx/local.conf` 의 `auth_basic` 블록 주석을 풀고 검증 전용 더미 `deploy/nginx/htpasswd.dummy` 를 쓰면 로컬 `:8080` 에서 **무인증 401 → 인증 후 200 + `X-Robots-Tag`** 를 선검증할 수 있다(더미는 운영·스테이징 계정과 무관) | **인증 없이 스테이징 URL 요청 → 401** + 인증 후 200 + 응답 헤더 `X-Robots-Tag: noindex, nofollow`. **로컬 선검증 + 스테이징 최종 확인** | REQ-N-040·039 |

> **정리 (v0.2 갱신)**
> - **P7(운영) 판정**: 1 · 3 · 7 · 10 — 4건
> - **스테이징 판정**: 2 · 5 · 8 · 9 — **4건** (**#6·#11·#12는 로컬 선검증 + 스테이징 최종 확인**으로 바뀌었다 — #12는 v0.3/devops R2 #4)
> - **로컬 선검증 가능(신규)**: 6 · 9 · 11 — `--profile proxy` 도입 효과. **스테이징 지연(TR-2·TR-5) 시의 방어선**이다
> - **스테이징 판정 항목은 도메인 확정과 무관하게 선행한다**(devops #11) — 사설 인증서·임시 서브도메인으로 TLS를 먼저 세운다(§12.6.2).
> - **로컬에서 "통과"로 보고하지 않는다.** 로컬 선검증은 "구현이 맞는지 먼저 본다"는 뜻이며, **판정 단계는 위 구분을 따른다.** qa 테스트 계획에 같은 구분으로 반영해 주기를 요청한다(§16 Q-3 — qa 수용 완료).

### 13.1 §13 #6(프록시 뒤 실제 IP) 재현 절차 (qa R1 #7)

> 목적: **서로 다른 출처 2곳을 물리적으로 확보하지 않고도** `X-Forwarded-For` 처리의 정오를 판정한다.

**앱의 기대 동작 (설계 확정)**

`TRUSTED_PROXY_COUNT = N` 일 때, 앱은 `X-Forwarded-For` 목록의 **오른쪽에서 N번째 값**을 클라이언트 IP로 채택한다(가장 오른쪽 = 우리 nginx가 붙인 값). 목록 길이가 N보다 짧으면 **가장 왼쪽 값**을 쓰지 않고 **연결 소켓의 원격 주소**로 대체한다(위조 방어 기본값). `TRUSTED_PROXY_COUNT=0`이면 `X-Forwarded-For`를 **전혀 신뢰하지 않는다**.

| # | 요청 | `TRUSTED_PROXY_COUNT=1` (기본안) | `TRUSTED_PROXY_COUNT=2` (앞단에 CDN 등이 더 있을 때) |
|---|---|---|---|
| ⓐ | 정상 요청 (클라이언트 → nginx → app) | 채택 IP = **실제 클라이언트 IP** | 목록이 짧아 소켓 주소로 대체 → **오설정 신호** |
| ⓑ | 클라이언트가 `X-Forwarded-For: 1.2.3.4`를 **위조**해 보냄 (nginx가 `$proxy_add_x_forwarded_for`로 뒤에 실제 IP를 덧붙임 → `1.2.3.4, <실제>`) | 채택 IP = **실제 클라이언트 IP** (위조값 무시) ✔ | 채택 IP = `1.2.3.4` (**위조 성공** — 이 조합이 틀렸음을 보여 준다) |
| ⓒ | 위조값을 여러 개 넣음 (`1.2.3.4, 5.6.7.8`) | 실제 IP ✔ | `5.6.7.8` ✘ |

**확인 지점 (증거)**

1. `core_ratelimitcounter`의 **`identifier_hash`가 요청별로 어떻게 갈라지는지**를 `qa_show ratelimit --since --format json`으로 관측한다.
   - **정상**: ⓐ와 ⓑ가 **같은 해시**(= 위조를 무시하고 실제 IP를 썼다).
   - **결함**: ⓐ와 ⓑ가 **다른 해시**(= 위조 헤더로 빈도 제한을 우회할 수 있다) **또는** 서로 다른 실제 출처의 요청이 **같은 해시**(= 전 사용자 공동 차단 — TR-3의 Critical 시나리오).
2. 빈도 제한 임계를 낮춘 상태(`QA_RATE_LIMIT_MODE`)에서 **ⓑ를 임계 초과까지 반복** → 차단되면 "위조로 우회 불가"가 실증된다.
3. **로컬**: `--profile proxy`로 nginx를 끼우고 위 ⓐ~ⓒ를 `curl -H 'X-Forwarded-For: …'`로 재현한다. **스테이징**: 같은 절차 + 실제 출처 1곳으로 최종 확인.
4. **`TRUSTED_PROXY_COUNT` 실측 확정**: 스테이징에서 ⓐ가 실제 IP를 채택하는 최소값을 찾아 확정하고 배포 계획서에 기록한다(기존 nginx 앞에 또 다른 프록시가 있는지에 따라 달라진다 — devops R1 Q-5).

---

## 14. 결정 사항 · 미확정 항목

### 14.1 이 문서에서 확정한 "결정 대기 항목"(요구사항 §8.5)

| # | 항목 | **확정값** | 위치 |
|---|---|---|---|
| D-5 | 빈도 제한 값 | M-3 잠정값 그대로 채택 | §5.3 |
| D-6 | 번호 길이 | **Crockford Base32 8자(40비트) 확정** | §5.5 |
| D-7 | 조회 실패 최소 응답 시간 | **300ms 하한 확정** | §5.3 |
| D-8 | 파기 배치 실행 수단 | **스케줄러 컨테이너(supercronic) 확정** | §3.3 |
| D-9 | 빈도 제한 저장소 | **PostgreSQL 테이블 확정**(Redis 미도입) | §5.3 |
| D-13 | G-9 WebKit 폴백 구현 방식 | `visualViewport` 기반 보정 + `requestAnimationFrame` 스로틀 + 키보드 닫힘 시 복원 + `scroll-padding-bottom` = `--body-pad-bottom` | §6.3 · §9.1 |
| D-28 | DB | **PostgreSQL 17 확정** | §2.3 |
| D-29 | 스택 구성안 | **구성 ②계열(서버 렌더 프레임워크) — Django 5.2 LTS 확정** | §2.1 |
| D-33 | 세션·비밀번호 정책 수치 | 잠정값 채택(회원 유휴 30분 / 유지 14일 / 관리자 30분 / 재설정 30분 / 인증 24시간 / 최소 10자 2종). **전부 환경 변수** | §7.2 |
| D-34 | 로그인·재설정 시도 제한 | M-3 잠정값 채택 | §5.3 |

**v0.2에서 추가로 확정한 값** (R1 지적에 따라 P4 권한으로 확정 — 전부 조정 가능하도록 환경 변수 또는 설계 표로 둔다)

| 항목 | 확정값 | 출처 | 위치 |
|---|---|---|---|
| 문의 폼 **응답 형태 6종**(상태 코드·본문·저장·발송·기록) | 표 1개로 확정 — **P5 판정 기준 원본** | qa #1 | §9.6 |
| REQ-N-019 **사용량 알림 임계값** | 출처당 1일 차단 3회 / 시간당 차단 20건 / 1일 시도 500건, 사유별 1시간 1통 합산 | qa #9 | §5.3 |
| **백업 실행 주체** | `scheduler` → `manage.py run_backup` (별도 컨테이너 없음) | devops #1 | §12.5.1 |
| **목표 다운타임 · 배포 창** | 60초 이내 / 평일 07:00 이전 또는 23:00 이후, 5분 내 미회복 시 롤백 | devops #8 | §12.2 |
| **HSTS 초기값** | `SECURE_HSTS_SECONDS=86400`, `includeSubDomains`·`preload` 미적용 | devops #12 | §9.5 |
| **HTML 압축 주체** | nginx `gzip`(우리 server 블록 한정). Django `GZipMiddleware` 미사용 | devops #4 | §12.3 #4 |
| **`QA_*` 해석 조건** | `QA_TOOLS_ENABLED=1` 명시 시에만(환경 이름에 의존하지 않음) | qa #4 · devops #2 | §3.5.1 ② |
| **clock 오프셋 적용/비적용 범위** | 표 1개로 확정(cron은 비적용) | qa #5 | §10.3 |

### 14.2 2차 착수 전에 결정할 항목 (지금 결정하지 않아도 1차가 막히지 않는다)

| # | 항목 | 기한 | 영향 |
|---|---|---|---|
| T-1 | **Django 관리자 채택 범위** — 저부가 CRUD에 쓸지, 전 화면 직접 제작할지 | 2차 P3 착수 전(D-27과 함께) | -2.0~-3.25작업일 / 관리자 UI 일관성 |
| T-2 | **Django 6.1 LTS(+ PostgreSQL 18) 전환 여부** | 2026-12 | 지원 종료 2028-04 → 2029-08. 전환 0.25~0.5작업일 |
| T-3 | 캘린더·편성 그리드용 경량 JS 수단(htmx·Alpine) 도입 여부 | 2차 기술 설계 | 2차 프런트 공수 ±0.5~1.0 |
| T-4 | 2차 미디어(강사 사진) 서빙 경로 — 앱 경유 / nginx 직접 | 2차 기술 설계 | nginx 설정 추가 여부 |
| T-5 | 게시 시 강사 미배정 차단용 `CONSTRAINT TRIGGER` 추가 여부 | 2차 구현 | 안전성 ↔ 편성 성능 |
| T-6 | `/admin/` 경로의 후행 슬래시 예외 유지 | 2차 구현 | `noindex` 영역이라 SEO 영향 없음(기록용) |

### 14.3 `[TBD]` — 외부 확보 대기 (제작이 결정할 수 없음)

| # | 항목 | 막히는 것 | 기한 |
|---|---|---|---|
| **O-1** | **운영자가 PostgreSQL 백업·복구 절차에 익숙한가**(I-7-a 연계) | 익숙하지 않으면 운영 가이드 절차를 더 상세히 쓰고 리허설을 1회 더 한다(+0.25작업일). **DB 선택을 뒤집을 사유는 아니다** | P7 전 |
| O-2 | I-2-a~d (nginx 형태·권한·공유·인증서) | 운영 compose의 네트워크 형태 확정(§3.1) | P4 검토 중 |
| O-3 | 백업 **오프사이트 보관** 여부·위치 | 서버 전체 장애 시 복구 가능성. **devops 위험도 평가: 1차 "중" · 2차 "높음"** — 1차는 소실 자산이 문의 접수 수십 건이고 SMTP 연결 시 알림 메일이 사본으로 남는다(**1차 오픈은 이대로 진행 가능**). 2차는 회원·예약·상담·경고·해피콜이 **대체 사본 없이 소실 = 서비스 재개 불가** → **2차 착수 전 필수 전환 권고** | 배포 계획 / **§14.4 PM-3** |
| O-4 | I-9 도메인 | canonical·OG·sitemap·구조화 데이터·HTTPS·SPF/DKIM **최종 확인이 전부 이월** | 10-16 |
| O-5 | I-5-b·I-5-c SMTP 계정과 1차 문의 알림 공백 | **1차 오픈 시 문의가 들어와도 아무도 모른다**(관리자 화면은 2차). infra §8.3 **ⓐ(오픈 전 SMTP 연결) 권고에 동의한다**.<br>**추가(qa R1 #12)**: 이것은 "운영 편의" 문제가 아니라 **G7 판정 가능성** 문제다 — **미연결로 오픈하면 P7 스모크에서 REQ-N-022(도달·SPF/DKIM, Must)와 REQ-F-045의 운영 판정이 불가해 G7 스모크 보고서가 조건부가 된다.** qa도 ⓐ를 지지한다 → **§14.4 PM-2** | 10-26 |
| O-6 | T-E 지도 서비스·업체 등록 | 지도 임베드·길찾기 목적지·정적 지도 대체(D-4) | 10-16 |
| O-7 | 고객 실제 값 8묶음(주소·전화·운영시간·강사 등) | `[TBD]` 0건 판정(REQ-N-023) — 미확보 시 해당 행을 렌더하지 않는 규칙으로 오픈은 가능하지만 사이트 가치가 크게 떨어진다 | 10-16 |
| O-8 | 파비콘·OG 이미지 | 미수령 시 해당 태그를 빼고 빌드 후 교체 | 구현 착수 시 |

### 14.4 PM 결정이 필요한 항목 — **설계에서 확정하지 않는다** (선택지와 영향만)

> R1 검토에서 **developer·devops·qa의 기술 판단이 일치**했으나, **일정·비용·범위·권한에 걸린 결정**이라 제작이 확정할 수 없는 5건이다. 각 항목은 **선택지 / 영향 / 기한 / 미결정 시 기본 동작**만 적는다.

| # | 항목 | 선택지 | 영향 | 기한 | 미결정 시 이 설계의 기본 동작 |
|---|---|---|---|---|---|
| **PM-1** | **1차 구현 일정 차이 (약 6작업일)** — 계획 창 약 10작업일 vs 산정 약 16작업일(§11.2) | ⓐ **기준 오픈일 11-06 사용**(조기 오픈 10-29는 목표로만) / ⓑ 검증 도구 2차 전용분 이월(+0.25~0.5) / ⓒ Could 3건 제외(+0.3~0.5) / ⓓ 범위 축소 | ⓐ: 비용 0(계획서 §4.2.2가 이미 "조기 오픈은 약속하지 않는다"). **developer·devops·qa 3팀 모두 ⓐ 지지** — devops는 직렬 의존성(도메인→인증서→DNS 전파→리허설→**G7a 조건인 복구 리허설**이 4일에 직렬), qa는 검증 창 보호(구현 1일 지연 = P5 1일 감소). ⓓ는 **1차 Must 60건 = G5 판정 모수**라 CR 필요 | **G4 전** | ⓐ를 전제로 §11.1 순서대로 진행하고 **10-14 체크포인트에서 진척을 즉시 보고**(TR-1) |
| **PM-2** | **오픈 전 SMTP 계정 연결 여부** (O-5·TR-6) | ⓐ **오픈 전 연결**(infra §8.3 ⓐ — developer·qa 지지) / ⓑ 미연결 오픈 / ⓒ 간이 확인 화면 추가(+0.5~1작업일, 1차 범위 확대) | ⓑ 선택 시: **1차 오픈 후 문의가 들어와도 아무도 모른다**(관리자 화면은 2차) **+ P7 스모크에서 REQ-N-022·REQ-F-045 운영 판정 불가 → G7 스모크 보고서가 조건부**(qa #12). ⓒ는 1차 Must가 아닌 기능을 추가하는 것이라 범위 판단이 필요 | **10-26** | 설계는 ⓐ·ⓑ 어느 쪽이든 **코드 변경 없이 환경 변수만으로 전환**되게 만든다(계정 미연결 상태로도 1차 구현·P5 판정은 Mailpit로 완결) |
| **PM-3** | **백업 오프사이트 보관** (O-3·TR-10) | ⓐ 하지 않음(현 설계) / ⓑ **같은 서버의 다른 디렉토리·디스크로 1차 복사**(비용 0, 즉시) / ⓒ **주 1회 암호화 반출**(`gpg`/`age` → 운영팀 보유 다른 호스트) / ⓓ 클라우드 오브젝트 스토리지 | devops 위험도: **1차 "중" · 2차 "높음"**. devops 권고는 **ⓑ+ⓒ 조합**. **암호화 없이 반출하지 않는다**(개인정보 파일이 서버 밖으로 나가는 순간 유출 경로가 하나 는다). ⓓ는 **외부 계정 생성·유료 결제라 CLAUDE.md §8상 PM 명시 승인 사항**이며 1차 데이터 규모 대비 부담이 크다. **반출 대상 호스트·암호화 키 보관 주체는 PM·운영팀 소관** | 배포 계획 확정 전 | ⓐ(같은 서버 보관)로 1차 오픈. **2차 착수 전 필수 전환을 배포 계획서·운영 가이드에 권고로 남긴다** |
| **PM-4** | **릴리스 소스의 서버 반입 수단** (I-6 미회신) | ⓐ **원격 저장소 생성 + push 후 서버에서 태그 체크아웃** / ⓑ **태그 스냅샷 아카이브 반입**(`git archive` 등) | §12.1이 "서버에서 릴리스 태그를 체크아웃해 빌드"를 전제하는데 **프로젝트 저장소에 원격이 없다.** ⓐ는 **원격 생성·push가 CLAUDE.md §8상 PM 승인 사항**이다. 어느 쪽인지 정해져야 **devops가 배포 계획서를 명령 단위로 쓸 수 있고**, 롤백 시 재빌드 경로(devops #7)도 확정된다 | **10-16** | 설계는 **두 경로 모두를 지원**한다(`deploy.sh`가 소스 위치를 전제하지 않고 "현재 체크아웃된 트리"를 빌드한다). 결정 전까지 배포 계획서의 해당 절이 비어 있게 된다 |
| **PM-5** | **G5 판정 범위 — REQ-N-032·033을 포함하는가** | ⓐ **선행 실행해 G5에 포함**(§12.6.2 ⓐ — qa·developer 권고) / ⓑ **G7 조건으로 이월**(pmo·PM 사전 합의 필요) | ⓐ: 스테이징 배포·롤백 1회(10-17)와 백업 실패 주입·회전(10-20)을 P5 창 안으로 당긴다. **선행 조건 4건**(§12.6.2)이 깨지면 자동으로 ⓑ. ⓑ: **G5 보고서에 1차 Must 2건이 "미검증"으로 남아 G5 권고가 조건부**가 된다 — **합의 없이 미검증으로 남기지 않는다**는 것이 qa·developer의 공통 요구다 | **10-14** (P5 테스트 계획 확정 전) | ⓐ를 목표로 진행하고, 선행 조건이 깨지는 즉시 pmo에 보고해 ⓑ 합의를 요청한다 |

---

## 15. 기술 리스크

| # | 리스크 | 영향 | 확률 | 대응 |
|---|---|---|---|---|
| **TR-1** | **1차 구현 창(약 10작업일) < 산정(약 15작업일)** | 조기 오픈 10-29 불가, 기준 11-06도 압박 | **높음** | §11.2 ⓐ 권고. 10-14 체크포인트에서 진척을 보고 PM에 즉시 보고 |
| **TR-2** | 운영 nginx 설정 변경 권한·절차 미확인(I-2-b·c) + 다른 서비스 공유 | 배포 당일에 막히면 오픈이 밀린다 | 중 | 요청 항목을 §12.3으로 **최소화**하고 스테이징에서 동일 구성 선검증. devops가 P7 계획에 반영 |
| **TR-3** | 프록시 뒤 실제 IP 처리 오류 → 빈도 제한이 전 사용자 차단 | 문의 폼 전면 불가(Critical급) | 중 | `TRUSTED_PROXY_COUNT` 명시 + **스테이징 필수 검증 항목**(§13 #6) |
| **TR-4** | 폴백 폰트 메트릭이 designer 기준(블록 높이 차)에 수렴하지 않음 | CLS·디자인 QA 지적 | 중 | 실측 절차 §9.4. 미수렴 시 preload 확대 / `font-display: optional` 중 designer 합의로 선택 |
| **TR-5** | 도메인 미정으로 HTTPS·SPF/DKIM·구조화 데이터 최종 확인이 P7 말로 몰림 | 오픈 직전 리스크 집중 | **높음** | 스테이징 서브도메인으로 선검증, 운영 전환 시 `SITE_BASE_URL`만 교체(재빌드 불필요하도록 설계) |
| **TR-6** | SMTP 미연결 상태로 1차 오픈 → 문의 접수 인지 불가 | 고객 신뢰·기회 손실 | 중 | infra §8.3 **ⓐ 권고**. 미채택 시 ⓒ(간이 확인 화면, +0.5~1작업일)를 1차 범위에 넣어야 한다 → PM 결정 |
| TR-7 | `reserved_count` 카운터와 실제 예약 수 불일치(2차) | 정원 오류 | 낮음 | 조건부 UPDATE + CHECK + 야간 정합성 점검(§5.4 ⑤) |
| TR-8 | Django 관리자 UI와 디자인 시스템 불일치(2차) | 고객 인상·D-27 충돌 | 중 | 채택 범위를 저부가 CRUD로 한정(T-1), 고부가 화면은 직접 제작 |
| TR-9 | 단일 서버·단일 앱 인스턴스 — 무중단 배포가 아니다 | 배포 중 수 초~수십 초 중단 | 낮음 | 트래픽 적은 시간대 배포 + 점검 화면(503). 무중단이 요구되면 CR |
| TR-10 | 백업이 같은 서버에만 존재 | 서버 장애 시 동시 소실 | 중 | O-3 결정 요청 |
| TR-11 | Windows 로컬 바인드 마운트 성능·줄바꿈(CRLF) | 개발 속도·셸 스크립트 오동작 | 낮음 | `.gitattributes`로 `sh` 파일 LF 고정, 폴링 옵션 제공 |
| TR-12 | 검증 전용 설정이 운영에 켜진 채 배포 | **Critical 보안 사고** | 낮음 | **v0.2에서 5중으로 강화**(§10.6): 마스터 스위치 · 구조적 제외 · import 실패 기동 거부 · 명령 미등록 · HTTP 노출 0. **qa가 밖에서 확인할 증거 열까지 정의**했다 |
| **TR-13** | **nginx 호스트에 정적 점검 화면을 배치할 권한(I-2-b)이 확보되지 않음** | 배포 중·앱 다운 시 **호스팅 기본 502 화면 노출** → REQ-F-065 취지 깨짐 | 중 | §12.3 #6. devops가 배포 계획서에서 경로·절차 확정. 미확보 시 **다운타임을 60초 목표 안으로 줄이는 것이 유일한 완화**(§12.2) |
| **TR-14** | **스테이징 가용(10-15)·TLS·`auth_basic` 구성 지연** | §13 스테이징 판정 5건 + 메일 판정 + REQ-N-032·033 선행 실행이 **통째로 P7 이월** → G5 미검증 증가 | 중 | 사설 인증서·임시 서브도메인으로 **도메인 확정과 무관하게 선행**(§12.6.2). **로컬 `proxy`·`backup` 프로필이 1차 방어선**(§3.2.1) |
| **TR-15** | **운영자가 `docker image prune -a`로 롤백용 이미지를 삭제** | 롤백 경로 소실 → 재빌드(소스 반입 + 빌드 시간)가 유일한 복구 수단 | 중 | 보존 라벨 + `deploy.sh` 0단계 존재 확인(없으면 중단) + P8 운영 가이드 금지 문구(§12.1) |

---

## 16. 검토자에게 요청하는 확인 사항

> **대상별 번호는 연속이 아니다**(qa R1 #14 — R1에서 번호 혼선이 있었다). **devops 앞: Q-1 · Q-5 · Q-6 · Q-7 · Q-11 / qa 앞: Q-2 · Q-3 · Q-4 · Q-7 · Q-8 · Q-9 · Q-10 · Q-12.**

**R1(Q-1 ~ Q-8) — 전건 회신 완료. 처리 결과만 남긴다.**

| # | 대상 | 내용 | **R1 회신 결과** |
|---|---|---|---|
| Q-1 | devops | §3.1 I-2-a 전제(운영 nginx = 호스트 설치) | **미확인 — 운영팀 미회신**(O-2). 기본안 유지가 옳고 **전환 비용 0.25작업일 평가에 devops 동의**. devops가 **10-09까지 추적**하며 **구현 착수는 막지 않는다**. 추가 확인 1건 수용: 운영·스테이징이 같은 서버이므로 **`APP_PORT`가 2개 필요**하고 값은 devops가 배포 계획서에서 지정한다 → **설계에는 환경 변수로만 두고 숫자를 박지 않는다(현 설계 유지)** |
| Q-2 | qa | REQ-F-064를 `seed_content` 경로로 판정 가능한가 | **가능**. 판정 기준선은 "재빌드 유무"가 아니라 **"관리자 화면에서 고칠 수 있는가"**. 증거는 전화번호 변경 → 명령 1회 → **헤더·푸터·오시는 길 3곳 캡처 + 명령 출력 + `qa_show`**. **planner에게 REQ-F-064 1차 수용 기준 문구 정렬을 권고**(오케스트레이터 경유)하되 **정렬이 안 돼도 Pass 판정 가능**. 부수: **명령 실행이 필요하다는 사실을 P8 운영 가이드 "콘텐츠 수정 절차"에 반드시 적는다**(§2.8·§5.1.1에 반영) |
| Q-3 | qa | §13 판정 단계 구분을 테스트 계획에 반영 | **반영 확정.** qa가 `qa/05_test-plan.md`에 "검증 환경별 판정 구분" 절을 두고 TC 단위로 태깅해 **"미검증"이 아니라 "P7 판정 예정(이월)"** 으로 보고한다. 전제 2건은 v0.2에서 해소(#6 재현 절차 → §13.1 / 스테이징 전제 → §12.6.1) |
| Q-4 | qa | 검증 도구 구현 형태가 테스트 계획과 맞는가 | **명령·환경 변수 이름 전부 수용.** 출력·동작 형식 요구는 **§10.2에 전건 확정 반영**, 신규 요청 `qa_pii_columns`는 **⑪로 신설** |
| Q-5 | devops | `proxy_intercept_errors off` · 별도 로그 파일 충돌 여부 | **충돌 없음.** 요청 목록 전체가 `server`/`location` 레벨이고 전역 변경 0건. `proxy_intercept_errors`는 nginx 기본값이 off이므로 **"요청"이 아니라 "확인 + 필요 시 우리 블록에서 재정의"** → §12.3 #3에 반영. 별도 로그는 **호스트 logrotate 등록 필요**(운영팀 작업) → §12.3 #5. 샘플 파일 **운영·스테이징 2종 분리** 권고 수용. `client_max_body_size`는 **1차 목록에서 제외**(2차로) |
| Q-6 | devops | 백업 보관 위치·퍼미션·오프사이트(O-3) · O-1 | **보관·퍼미션 회신을 §12.5.2에 반영**(0700/0600, DB 볼륨과 분리, 웹 루트 금지). **오프사이트 = §14.4 PM-3**. **O-1은 DB 선택을 뒤집을 사유가 아니라는 판단에 devops 동의** — 대체 확인 수단으로 **10-28 복구 리허설을 운영자 입회·운영자 손으로** 수행(§12.5.3). 미숙련 판명 시 +0.25작업일은 **devops 일정 안에서 흡수 가능** |
| Q-7 | devops·qa | 일정 차이에 대한 의견 | **양 팀 모두 ⓐ(기준 오픈일 11-06) 지지.** §11.2에 근거 반영, **§14.4 PM-1로 승격** |
| Q-8 | qa | 96건 중 충족 경로가 안 보이는 항목 | **구현 자체가 불가능한 1차 Must는 0건.** 지적된 공백 7건은 v0.2에서 전부 대응: 판정 기준 4건(§9.6 · §3.2.1 · §12.6.2) · 증거 수단 2건(§10.2 ⑪ · §5.3 임계값) · 수단 미결 1건(§10.5 Safari) |

**R2에서 새로 요청하는 확인 사항 (Q-9 ~ Q-12)**

| # | 대상 | 내용 |
|---|---|---|
| **Q-9** | **qa** | **§3.2.1 말미의 "세 환경 동일 구성" 판정 정의**로 REQ-N-034를 **Pass로 판정할 수 있는가**. 로컬 `--profile proxy`로 "앱·DB·프록시가 모두 뜬다"를 충족한다고 보는지, 그래도 planner에게 수용 기준 문구 정렬을 요청해야 하는지 알려 달라(요청이 필요하면 오케스트레이터 경유로 티켓을 올린다) |
| **Q-10** | **qa·devops** | **§12.5.2 말미** — REQ-N-039 판정 증거인 **"운영 DB 권한자 목록 · 백업 파일 위치 · 퍼미션" 초안을 P5 시작 전(10-14)까지 devops가 제공**하는 안에 동의하는가. 동의하면 developer가 티켓을 올린다 |
| **Q-11** | **devops** | **§12.6.2 ⓐ의 선행 조건 4건**(스테이징 제공 10-13 / TLS·`auth_basic` 10-15 / 구현 배포 가능 10-16 / `run_backup` 10-16)이 devops 일정에서 성립하는가. 특히 **10-15 TLS 선행 구성**이 Q-7 답변의 작업표(스테이징 수령~TLS 구성 10-13~10-15, 0.5~0.75작업일)와 맞는지 확인해 달라 |
| **Q-12** | **qa** | **§9.6의 응답 형태 표**(6행 × 5열)로 REQ-F-042·044·046의 TC 기대값을 확정할 수 있는가. 특히 **④만 429**로 두고 ③⑤를 200 성공 화면으로 두는 판단(차단 사실 미노출 vs 재시도 시점 안내)에 이견이 없는지, 그리고 **③·⑤의 판정을 "저장 0건 + 발송 0건 + 로그 reason"** 3개로 하는 절차가 실행 가능한지 확인해 달라 |

---

## 17. R1 리뷰 처리 대장 (v0.2)

> 리뷰 문서의 "처리 결과" 열에도 같은 내용을 기입했다. 여기서는 **반영 위치**를 한눈에 본다.
> **Must 5건 · Should 19건 전건 반영 — 미반영 0건.** Could 7건 중 6건 반영 · 1건(devops #13)은 설계 범위 밖 부분을 devops 문서로 이관했다.

### 17.1 Must (5건)

| 출처 | 요지 | 반영 | 위치 |
|---|---|---|---|
| devops #1 | 백업 실행 주체·실패 알림 경로 부재 | **반영** — `backup` 상시 컨테이너 폐지, `scheduler` → `manage.py run_backup` 일원화. `core_jobrunlog` 기록 + 실패 시 `mailer_outbox`(`kind=backup_failed`) + 일일 요약 ⓒ **2중 통지**. ⑨ⓑ 실패 주입 경로 명시 | §3.2 · §3.3 · **§12.5.1** |
| devops #2 | 스테이징 접근 제어 미설계 | **반영** — nginx `auth_basic`(+IP 제한) 필수, `QA_*`는 `QA_TOOLS_ENABLED=1` 명시 시에만 해석, 검증 도구 **HTTP 노출 0**, "도구가 켜진 환경은 인증 뒤에 둔다" 원칙 + 기동 로그 경고 | **§3.5.1** · §10.6 · §12.3 #8·#9 |
| qa #1 | REQ-F-042 실패·차단 응답 형태 표 부재 | **반영** — 6행(정상·검증 실패·honeypot·빈도 제한·토큰 재사용·서버 오류) × 5열(상태 코드·본문 형태·저장·발송·기록) + 판정 주의 5건 | **§9.6(신설)** |
| qa #2 | REQ-N-034 수용 기준과 구성 충돌 | **반영(권고 ⓐ 채택)** — 로컬 compose에 `proxy`·`backup` **선택 프로필** 추가(+0.5작업일), "동일 구성" 판정 정의 명문화, **ⓑ(planner 문구 정렬) 경로와 비용도 기록** | **§3.2.1** · §3.5 |
| qa #3 | REQ-N-032·033 실행 시점이 P5 창 밖 | **반영(ⓐ 우선)** — 스테이징 배포·롤백 1회 **10-17**, 백업 실패 주입·회전 **10-20**으로 선행. 선행 조건 4건과 **깨질 때 ⓑ(G7 이월)로 전환하는 규칙**을 명시하고 **PM-5로 승격** | **§12.6.2** · §14.4 PM-5 |

### 17.2 Should (19건 — 전건 반영)

| 출처 | 요지 | 반영 위치 |
|---|---|---|
| devops #3 | REQ-N-034 "동일 구성" 판정 정의 | §3.2.1 말미 (+ Q-9로 qa 확인 요청) |
| devops #4 | HTML 압축 주체 부재 | §2.0 · §12.3 #4(nginx `gzip`, 우리 server 블록 한정) · §13 #11 신설 · §9.4 측정 조건 |
| devops #5 | 앱 다운 시 점검·502 화면 | §12.3 #6 + 자립형 `deploy/nginx/maintenance.html` · §4 · TR-13 |
| devops #6 | 마이그레이션 중 스케줄러 동시 실행 | §12.2 **2.5단계 스케줄러 정지** (rollback.sh 동일) |
| devops #7 | 롤백용 이전 이미지 보존 미보장 | §12.1 3중 장치(라벨·0단계 존재 확인·`prune -a` 금지) · TR-15 |
| devops #8 | 다운타임·배포 창 수치 부재 | §12.2 배포 창/목표 60초/실측 기록/5분 룰 |
| devops #9 | 장애 인지 수단 부재 | §3.3 **일일 운영 요약 메일**(ⓐ~ⓕ 6항목, +0.25작업일) |
| devops #10 | `.env` 보관·재발급 절차 부재 | §12.5.4 (보관처·전달은 devops 문서, **재발급 가능성**까지 명시) |
| devops #11 | 스테이징 HTTPS가 도메인에 묶임 | §12.6.2(사설 인증서·임시 서브도메인 선행) · §13 정리 · TR-14 |
| devops Q-5 | nginx 요청 항목 8행 → 9행 | §12.3(9행 + 샘플 2종 분리 + `client_max_body_size` 2차 이월) |
| qa #4 | 운영에서 QA 도구 차단의 **판정 수단** 부재 | §10.6 5중 장치 + **증거 열**, `qa_settings.py`를 `qa/`로 이동(§4) |
| qa #5 | clock 진입점 우회 경로 미정리 | **§10.3** 적용/비적용 표 |
| qa #6 | 스테이징 전제 미명시 · `mail` "선택적" | §3.2(`mail` **스테이징 필수**) · §12.3(스테이징 동일 적용) · §12.6.1(가용 기한 10-15) |
| qa #7 | §13 #6 재현 절차 부재 | **§13.1** (기대 동작 표 + 확인 지점 4단계) |
| qa #8 | Safari·iOS 검증 수단 미반영 | **§10.5** (관측 신호 `data-vk-fallback` + WebKit 자동화 판정 + 실기기 체크리스트 문서) |
| qa #9 | REQ-N-019 사용량 알림 임계값 부재 | §5.3 (ⓐⓑⓒ 임계값 + 하향용 `QA_*` 3키) |
| qa #10 | `qa_purge_test_data` 삭제 범위·식별 방법 | **§10.4** (테이블별 규칙 + 건수 출력 + `--dry-run`) |
| qa #11 | REQ-N-020 개인정보 컬럼 출력 수단 | §10 **⑪ `qa_pii_columns` 신설** · §10.2 |
| qa #12 | O-5의 영향에 "G7 판정 불가" 보강 | §14.3 O-5 · **§14.4 PM-2** |
| qa #13 | REQ-N-039 증거 문서의 제공 시점 | §12.5.2 말미 (10-14 초안 제공 요청 → Q-10) |

> 표에 20행이 있는 것은 devops Q-5 회신분(요청 항목 9행화)을 별도 행으로 적었기 때문이며, **Should 판정 건수는 devops 9 + qa 10 = 19건**이다.

### 17.3 Could (7건)

| 출처 | 요지 | 처리 |
|---|---|---|
| devops #12 | HSTS `includeSubDomains` 파급 | **반영** — §9.5(1일로 시작, 도메인 구조 확인 전 `includeSubDomains`·`preload` 금지) |
| devops #13 | 운영+스테이징 동거 시 디스크 산정 | **부분 반영** — §12.2 0단계에 **여유 5GB 미만 중단**을 수치로 명시. 잔여 용량·증가량 기록은 **devops 배포 계획서 소관**(설계 밖) |
| devops #14 | `restore.sh` 운영 DB 덮어쓰기 위험 | **반영** — §12.5.3 안전 가드 3중 |
| devops #15 | `unless-stopped`가 unhealthy를 재시작하지 않음 | **반영(기록용)** — §3.4에 사실과 판단 명시. **autoheal 미도입**(운영 요소 증가)에 동의하고 인지 수단만 §3.3 ⓐ로 확보 |
| qa #14 | §16 Q 번호 대상 혼선 | **반영** — §16 상단에 대상별 번호 비연속 안내 + 대상 열 유지 |
| qa #15 | Lighthouse 측정 시 `QA_*` 설정 영향 | **반영** — §9.4 측정 행(전부 미설정 상태의 prod 빌드에서 측정, 미설정 사실을 기록에 남김) |
| qa #16 | §10 ⑦ "1차 필요 ✕"와 공수 0.25 불일치 | **반영** — "1차 = 골격만 / 본체 2차"로 표기 정리 |

**미반영: 0건** (Must·Should 전건 반영, Could 7건 중 6건 반영 · 1건(devops #13)은 설계 범위 밖 부분을 devops 문서로 이관)

### 17.4 R2 리뷰 처리 대장 (v0.3 — 신규 Must 0건 · Should 8 · Could 4, **전건 반영 · 미반영 0건**)

| 출처 | 등급 | 요지 | 반영 | 위치 |
|---|---|---|---|---|
| devops #1 | Should | 배포 직전 백업이 락 경합으로 `skipped` 되어 조용히 건너뛰어질 수 있다 | **반영(① ② 모두)** — 스케줄러 정지를 **0.5단계**로, 라벨 백업은 `required=True` 로 **`skipped`를 실패로** 처리하고 `deploy.sh`·`restore.sh` 가 중단한다 | §12.2 · §12.5.1 · §12.5.3 |
| devops #2 | Should | 백업 "미실행"이 2중 통지 어디에도 걸리지 않는다 · `scheduler` 단일 실패점 | **반영(①②③)** — 요약 메일 ⓒ 판정을 **"24시간 내 성공 기록 없음 = `[점검필요]`"** 로 반전, `skipped` 를 ⓓ에 별도 집계, `deploy.sh` 0단계에도 같은 규칙. ③(단일 실패점)은 **"요약 메일이 오지 않는 날 = 이상 신호" + 수신 시각·제목 규칙 고정 + 5단계 scheduler 헬스 확인**으로 받는다 | §3.3 · §12.2 |
| devops #3 | Should | `auth_basic` 예외 0건과 `/healthz` 호출 주체가 충돌 → 스테이징 알림 피로 + 자동 롤백 오발동 | **반영** — **"`/healthz` 호출은 항상 앱에 직접, nginx 비경유, `SITE_BASE_URL` 미사용"** 을 §3.3 ⓐ·§3.4·§12.2 5단계에 명시하고 §3.5.1 ① 근거 문장을 정정. 5단계의 주요 4경로 확인은 프록시 경유(스테이징은 인증 자격, 값은 환경 변수) | §3.3 · §3.4 · §3.5.1 · §12.2 |
| devops #4 | Could | REQ-N-040 판정만 스테이징 단독 의존 | **반영(채택)** — `local.conf` 에 `auth_basic` 주석 블록 + 검증 전용 더미 `htpasswd.dummy`. §13 #12 가 **로컬 선검증 + 스테이징 최종**으로 내려와 스테이징 판정이 5건 → **4건** | §3.2.1 · §12.3 #8 · §13 #12 |
| devops #5 | Could | 웹 프로세스 이미지에 `pg_dump` 가 들어간다 | **반영(권고분 채택)** — 이미지는 나누지 않고, **`${BACKUP_DIR}` 바인드를 `scheduler` 에만** 두고 배포 직전 백업도 `run --rm scheduler` 로 실행한다(비용 0) | §3.5 · §12.2 1단계 |
| qa #1 | Should | REQ-N-034 수용 기준 문면과 프로필 기동 명령의 간극 | **반영(채택)** — `.env.example` 의 **`COMPOSE_PROFILES`** 로 플래그 없는 `docker compose up` 이 프록시까지 띄운다. **2026-09-13 실행 확인**(5개 서비스 healthy). 작업 12 완료 시 값에 `backup` 을 추가한다 | §3.2.1 · §3.5 · §8 |
| qa #2 | Should | 스테이징·운영이 같은 override 를 쓰는데 `mail` 을 갈라내는 수단이 없다 | **반영** — `mail` 을 `compose.prod.yaml` 에 **프로필 `mail`** 로 정의하고 스테이징 `.env.staging` 에서만 켠다. 판정 지점 = **운영 `ps` 에 `mail` 0건 / 스테이징 1건**(운영 미리보기 실행으로 0건 확인) | §3.2 · §3.5 |
| qa #3 | Should | `Retry-After` 의 근거인 폼 차단 지속 시간이 없다 | **반영** — ① 10분 창 초과 → 창 잔여 시간 ② 1일 한도 초과 → 익일 00:00(Asia/Seoul), 둘 다면 늦은 쪽 ③ `Retry-After = ceil(blocked_until − clock.now())` | §5.3 · §9.6 ④ |
| qa #4 | Should | honeypot ↔ 토큰 재사용을 구분할 로그 형식·조회 수단이 없다 | **반영** — 판정용 로그를 **`key=value` 로 고정**(`inquiry.blocked reason=…` / `inquiry.duplicate token_state=…`)하고 조회 수단(로컬 `docker compose logs app` / 스테이징 devops 대행)을 명시. 로그 포맷은 구현에서 이미 적용했다 | §9.6 · §10.2 |
| qa #5 | Should | PM-5 기한(10-14)과 선행 조건 판명(10-16)의 시차 | **반영** — **"선행 조건 #3·#4는 10-16 종료 시점에 재확인하고 즉시 pmo·qa 통지"** 체크포인트 신설 | §12.6.2 |
| qa #6 | Could | `config/qa_settings.py` ↔ `qa/qa_settings.py` 표기 불일치 | **반영** — §10.1 ④ 경로 정정 | §10.1 |
| qa #7 | Could | `qa/webkit_checklist.md` 가 `{PROJECT}/qa/` 로 읽힐 수 있다 | **반영** — `developer/site/qa/webkit_checklist.md` 로 명시하고 "이 문서의 `qa/` 표기는 전부 `site/` 기준"을 덧붙였다 | §10.5 ③ |

**미반영: 0건.** 구현 1단계에서 확정된 사실(의존성 PyYAML 추가, 패치 버전 고정, `ENV_FILE` 로 환경별 `.env` 선택)도 §2.7·§3.5·§4에 반영했다.

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.1 | 2026-09-12 | developer | 최초 작성 — 스택(Django 5.2 LTS + PostgreSQL 17) 확정, 로컬·운영 compose 구성, 1차/2차 데이터 모델과 DB 제약, 검증 지원 도구 ①~⑩ 별도 산정, 배포·백업·복구 설계, 로컬/운영 차이 10건, 기술 리스크 12건. 결정 대기 항목 10건(D-5·6·7·8·9·13·28·29·33·34) 확정 | CR-001, `shared/reviews/CR-001_impact_developer_r2.md`, `shared/reviews/P3_design-docs_developer_r1.md`, `interviews/2026-09-12_infra-constraints.md` v0.5 |
| **0.2** | **2026-09-12** | developer | **R1 교차 검토 반영 (Must 5 · Should 19 전건 반영, 미반영 0건 — §17 처리 대장).** ① 백업을 `scheduler`의 `manage.py run_backup`으로 일원화하고 실행 기록·실패 알림(`kind=backup_failed`)·실패 주입 경로를 확정(§12.5.1, `backup` 상시 컨테이너 폐지) ② 스테이징 접근 제어 신설 — nginx `auth_basic`·`QA_TOOLS_ENABLED` 마스터 스위치·검증 도구 HTTP 노출 0(§3.5.1·§10.6 5중 장치) ③ **문의 폼 응답 형태 표 6행×5열 신설**(§9.6 — REQ-F-042의 P5 판정 기준) ④ 로컬 compose에 `proxy`·`backup` **선택 프로필** 추가 + "세 환경 동일 구성" 판정 정의(§3.2.1) ⑤ REQ-N-032·033을 P5 창 안(10-17·10-20)으로 선행 배치하고 선행 조건·G7 이월 전환 규칙 명시(§12.6.2). 그 밖에 nginx 요청 9행화·HTML 압축 주체·정적 점검 화면·배포 절차 2.5단계·이미지 보존·다운타임 목표·일일 운영 요약 메일·`.env` 재발급·clock 적용 범위(§10.3)·`qa_purge_test_data` 규칙(§10.4)·Safari 검증 수단(§10.5)·도구 출력 규격(§10.2)·`qa_pii_columns`(⑪ 신설)·빈도 제한 알림 임계값·§13 #11·#12 신설과 #6 재현 절차(§13.1). 기술 리스크 12 → 15건, 1차 산정 약 15 → **약 16작업일**. **PM 결정 5건을 §14.4로 분리**(일정·SMTP 선연결·오프사이트 백업·소스 반입 수단·G5 판정 범위) | `shared/reviews/P4a_tech-design_devops_r1.md`, `shared/reviews/P4a_tech-design_qa_r1.md` |
| **0.3** | **2026-09-13** | developer | **R2 교차 검토 반영 (신규 Must 0건 · Should 8 · Could 4 — 전건 반영, 미반영 0건 — §17.4).** ① 배포 절차의 **스케줄러 정지를 0.5단계로 앞당기고 라벨 백업의 `skipped` 를 배포 중단 사유로** 확정(§12.2·§12.5.1·§12.5.3) ② 일일 운영 요약의 백업 판정을 **"24시간 내 성공 기록 없음 = 점검 필요"로 반전**하고 `skipped` 별도 집계(§3.3) ③ **`/healthz` 호출은 항상 앱에 직접(nginx 비경유)** 을 명시해 스테이징 `auth_basic` 과의 충돌·자동 롤백 오발동을 차단(§3.3·§3.4·§3.5.1·§12.2) ④ `.env.example` 의 **`COMPOSE_PROFILES`** 로 플래그 없는 로컬 기동 = REQ-N-034 문면 충족(§3.2.1·§3.5) ⑤ **`mail` 을 프로필로 분리**해 운영·스테이징 판정 지점 확정(§3.2) ⑥ **폼 차단 지속 시간·`Retry-After` 계산식** 확정(§5.3) ⑦ **판정용 로그 `key=value` 형식·조회 수단** 명시(§9.6) ⑧ 선행 조건 **10-16 재확인 체크포인트**(§12.6.2) ⑨ 로컬 `auth_basic` 선검증(더미 자격)으로 **스테이징 단독 판정 5건 → 4건**(§13) ⑩ `${BACKUP_DIR}` 를 `scheduler` 에만 마운트(§3.5). **구현 1단계 착수에 따른 사실 반영**: PyYAML 6.0.3 의존성 추가·패치 버전 고정(§2.7), `config/env.py`·`deploy/nginx/htpasswd.dummy` 추가(§4), 환경별 `.env` 선택을 `ENV_FILE` 로 처리(§3.5) | `shared/reviews/P4a_tech-design_devops_r2.md`, `shared/reviews/P4a_tech-design_qa_r2.md` |
