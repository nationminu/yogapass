---
doc_id: DEV-TECH
title: 기술 설계서 — 1차(2026-11-06 오픈 범위) + 2차 스키마 선설계
phase: P4
owner: developer
version: 0.1
status: in-review
reviewers: [devops, qa]
inputs: [planning/02_requirements.md, planning/02_information-architecture.md, planning/02_storyboard.md, design/03_design-system.md, design/03_page-design.md, design/mockups/, interviews/2026-09-12_infra-constraints.md, interviews/2026-09-12_booking-rules.md, pm/01_project-plan.md, pm/gates/G3a_design.md, shared/reviews/CR-001_impact_developer_r2.md, shared/reviews/P3_design-docs_developer_r1.md]
updated: 2026-09-12
---

# 기술 설계서 — 강남 요가패스

> **읽는 법**
> 1. 이 문서는 **1차(2026-11-06 오픈: 소개 6화면 + 문의 폼 + full compose)를 구현하기 위한 확정 설계**이고, 동시에 **2차(회원·레슨 예약·상담·관리자 39화면)에서 1차 결정을 되돌리지 않기 위한 선설계**다. 두 목적이 섞이지 않도록 각 절에 **`[1차 구현]` / `[2차 설계만]`** 을 표시했다.
> 2. **§2(스택)·§3(compose)·§5(데이터 모델)·§12(배포·백업)가 이 문서의 본체**다. 나머지는 그 결정의 전개다.
> 3. 이 문서가 **검토를 통과하기 전에는 구현에 착수하지 않는다**(CLAUDE.md §2 P4 체크포인트). 현재 `developer/site/`는 비어 있고, 이번 작업에서 코드 작성·의존성 설치·명령 실행은 하지 않았다.
> 4. 확정 권한이 없는 값은 `[TBD]`로 두고 **무엇이 막히는지**를 함께 적었다(§14).

---

## 0. 이 문서가 확정하는 것 / 확정하지 않는 것

| 구분 | 항목 |
|---|---|
| **확정한다** | 애플리케이션 프레임워크·렌더링 방식·DB·마이그레이션 도구·메일 발송 구조·템플릿/정적 파일 파이프라인(§2) · 로컬/운영 compose 구성(§3) · 디렉토리 구조(§4) · 1차 생성 테이블과 2차 전체 스키마·DB 제약(§5) · URL 규칙과 화면 매핑(§6) · 환경 변수 이름(§7) · 품질 구현 방법(§9) · 검증 지원 도구 ①~⑩의 구현 방식과 공수(§10) · 1차 구현 순서와 일수(§11) · 배포·백업·복구·롤백 절차의 설계(§12) |
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
| 정기 실행 | **스케줄러 컨테이너**(앱 이미지 재사용 + supercronic) | 호스트 crontab / 앱 내부 스레드 스케줄러 | §3.3 (D-8 확정) |
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
| Django | **5.2 LTS** (5.2.x 최신 패치) | pip |
| psycopg | 3.x (binary) | pip |
| Gunicorn | 23.x 이상 | pip |
| WhiteNoise | 6.x (`[brotli]`) | pip |
| Pillow | 11.x **(2차 강사 사진 리사이즈용, 1차 미설치)** | pip |
| PostgreSQL | **17** | `postgres:17-alpine` |
| Mailpit (로컬·스테이징만) | 최신 안정 | `axllent/mailpit` |
| supercronic (스케줄러) | 최신 안정 | 앱 이미지에 바이너리 포함 |
| ruff (개발만) | 최신 | pip (dev) |

> 의존성은 `requirements.txt`에 **정확한 버전 + 해시**로 고정하고, 업그레이드는 별도 작업 단위로 한다. 정확한 패치 버전은 구현 착수 시점에 확정해 `site/README.md`와 개발 보고서에 기록한다.

### 2.8 고객 운영 관점 (콘텐츠 수정 난이도·비용)

| 항목 | 1차 | 2차 |
|---|---|---|
| 강사·수업 유형·주소·전화·운영시간 수정 | `content/*.yml` 수정 → `manage.py seed_content` 1회 실행 | **관리자 화면에서 직접, 재빌드 없이**(TR-02·TR-03·TR-04) |
| 문구·레이아웃 수정 | 소스 수정 → 배포 | 동일 |
| 월 비용 | 보유 서버 외 **추가 비용 0원**(폰트 OFL·아이콘 ISC, 외부 관리형 서비스 없음). 도메인·SMTP는 고객 기존 자산 | 동일 |
| 운영자가 해야 하는 일 | 백업 확인, 보안 패치, 인증서 갱신 확인 — 절차는 P8 운영 가이드에 기재(REQ-N-026) | 동일 + 월 스케줄 게시 |

---

## 3. 시스템 구성 — docker compose

### 3.1 전제와 확인 항목 (I-2-a ~ I-2-d)

> infra §9가 남긴 파생 확인 4건은 **설계 착수를 막지 않지만 운영 compose의 최종 형태를 가른다.** 아래처럼 **기본안을 정하고 분기만 남긴다.**

| # | 확인 항목 | 이 설계의 **전제(기본안)** | 회신이 다를 때의 영향 |
|---|---|---|---|
| **I-2-a** | 운영 nginx가 **호스트 설치**인가 **컨테이너**인가 | **호스트 설치로 가정.** 앱을 `127.0.0.1:${APP_PORT}`에만 게시하고 nginx가 `proxy_pass http://127.0.0.1:${APP_PORT}` | 컨테이너면 포트 게시를 없애고 **외부 네트워크(`external: true`)에 앱을 참여**시켜 `proxy_pass http://yogapass-app:8000`. compose 한 블록 차이, **0.25작업일 이내** |
| **I-2-b** | nginx 설정 **수정 권한·반영 절차** | devops가 반영한다고 가정. 우리는 `deploy/nginx/yogapass.conf.sample`(서버 블록 예시)만 제공하고 **직접 고치지 않는다** | 우리가 반영해야 하면 P7 devops 작업에 권한 확보가 선행. 설계 변경은 없음 |
| **I-2-c** | 같은 nginx를 **다른 서비스도 쓰는가** | 쓴다고 가정하고 **설정 충돌을 만들지 않는 형태**로만 요청한다(server 블록 1개 추가, `http` 전역 지시어 변경 요청 없음, 별도 로그 파일) | 전역 설정 변경이 필요해지면 devops·운영자 합의 필요. 요청 목록은 §12.3 |
| **I-2-d** | 인증서 **발급·갱신 방식** | devops·운영자 소관. 앱은 `X-Forwarded-Proto`만 신뢰한다 | 앱 설계 영향 없음. 도메인(I-9) 확정 후 P7 |

### 3.2 서비스 구성

```
[로컬]                                  [운영 · 스테이징]
 브라우저 → http://localhost:8000        인터넷 → (기존) nginx :443  TLS 종료
     │                                        │  proxy_pass
  ┌──▼───────┐  ┌──────────┐            ┌─────▼────┐  ┌──────────┐
  │   app    │──│    db    │            │   app    │──│    db    │
  │ runserver│  │ postgres │            │ gunicorn │  │ postgres │
  └──┬───────┘  └──────────┘            └─────┬────┘  └────┬─────┘
     │                                        │            │
  ┌──▼───────┐  ┌──────────┐            ┌─────▼────┐  ┌────▼─────┐
  │ scheduler│  │   mail   │            │ scheduler│  │  backup  │
  │supercronic│ │ Mailpit  │            │supercronic│ │ pg_dump  │
  └──────────┘  └──────────┘            └──────────┘  └──────────┘
```

| 서비스 | 로컬 | 운영·스테이징 | 이미지 | 비고 |
|---|---|---|---|---|
| `app` | ○ (`runserver`, 소스 바인드 마운트, 자동 리로드) | ○ (`gunicorn`, 이미지 내 소스) | 같은 Dockerfile의 `dev`/`prod` 타깃 | 운영은 비루트 사용자로 실행 |
| `db` | ○ (포트 `127.0.0.1:5432` 게시 — 로컬 조회용) | ○ (**포트 게시 없음**, 내부 네트워크만) | `postgres:17-alpine` | 명명 볼륨 |
| `mail` | ○ (Mailpit, SMTP 1025 / UI `localhost:8025`) | 스테이징만 선택적 | `axllent/mailpit` | 운영 미배치 |
| `scheduler` | ○ | ○ | app 이미지 재사용 | supercronic + `deploy/crontab` |
| `backup` | ✕ | ○ (운영·스테이징) | `postgres:17-alpine` + 스크립트 | `pg_dump -Fc` + 회전. 호스트 바인드 마운트 |
| `proxy` | ✕ (**로컬은 nginx 없이 http 직접**) | ✕ (**기존 nginx 재사용 — 우리 compose에 포함하지 않는다**) | — | infra §9.1 |

### 3.3 스케줄러 (D-8 확정 — 컨테이너 스케줄러)

| 작업 | 주기 | 1차 | 2차 | 명령 |
|---|---|---|---|---|
| 메일 아웃박스 플러시·재시도 | 1분 | ○ | ○ | `manage.py send_outbox` |
| 보관 기간 경과 자동 파기 | 일 1회 03:10 | ○ (문의 내역) | ○ (9개 분류) | `manage.py purge_expired` |
| 빈도 제한 카운터 정리 | 시간 1회 | ○ | ○ | `manage.py prune_rate_limit` |
| 발송 실패·배치 실패 요약 알림 | 일 1회 | ○ | ○ | `manage.py report_failures` |
| 게시 기한 알림(25·28·말일) | 일 1회 | ✕ | ○ | `manage.py notify_unpublished` |
| 예약 상태 자동 전이 확인 | 일 1회 | ✕ | ○ | `manage.py roll_booking_states` |

- **호스트 crontab을 쓰지 않는 이유**: 로컬·스테이징·운영에서 동일하게 재현되지 않고(REQ-N-034 위반), 호스트에 우리 서비스의 지식이 새어 나간다.
- **앱 프로세스 내부 스케줄러(스레드)를 쓰지 않는 이유**: gunicorn 워커가 여러 개면 중복 실행되고, 재시작 시 실행이 누락된다.
- 모든 관리 명령은 **재실행 안전(idempotent)** 하게 만들고 `--dry-run`과 실행 기록(`core_jobrunlog`)을 둔다.

### 3.4 헬스체크·재시작·로그 (REQ-N-031 · 033)

| 서비스 | 헬스체크 | 재시작 |
|---|---|---|
| `db` | `pg_isready -U $POSTGRES_USER` (10s/5s/10회) | `unless-stopped` |
| `app` | `GET /healthz` → DB 연결 1회 확인 + 200 (15s/5s/5회, `start_period` 20s) | `unless-stopped` |
| `scheduler` · `backup` | 프로세스 생존 | `unless-stopped` |

- `/healthz`는 **`noindex` + 캐시 금지 + 개인정보·버전 정보 미노출**. 배포 스크립트가 이 엔드포인트로 기동 성공을 판정한다(§12.2).
- 로그: 전 서비스 `json-file` 드라이버 + `max-size: 10m`, `max-file: 5`(로그 회전).

### 3.5 파일 배치와 환경 분리 (REQ-N-034 · REQ-N-040)

```
site/
├── compose.yaml            # 공통 정의 (서비스·네트워크·볼륨·헬스체크)
├── compose.local.yaml      # 로컬 override  (runserver, 바인드 마운트, mail, 포트 게시)
└── compose.prod.yaml       # 운영·스테이징 override (gunicorn, 이미지 태그, backup, 포트 비게시)
```

| 환경 | 실행 | 구분 수단 |
|---|---|---|
| 로컬 | `docker compose -f compose.yaml -f compose.local.yaml up` | `.env`(개발 값) |
| 스테이징 | `docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-stg up -d` | **`COMPOSE_PROJECT_NAME=yogapass-stg` + 별도 `.env.staging` + 별도 볼륨 + 별도 포트 + 별도 서브도메인 + `X-Robots-Tag: noindex` 강제** |
| 운영 | `docker compose -f compose.yaml -f compose.prod.yaml -p yogapass up -d` | `.env`(운영 값, 서버에만 존재) |

- **세 환경의 `compose.yaml`은 같은 파일이다.** 차이는 override 파일 1개와 환경 변수뿐 → REQ-N-034의 "세 환경 compose 정의 diff" 검증이 `compose.local.yaml` vs `compose.prod.yaml` 한 쌍으로 끝난다.
- 스테이징은 `DJANGO_ENV=staging`에서 **전 응답에 `X-Robots-Tag: noindex, nofollow`** 를 강제한다(운영 색인 오염 방지, REQ-N-040).
- 볼륨: `pgdata`(DB) · `media`(2차 업로드) · 호스트 바인드 `./backups`(운영·스테이징).

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
│   ├── urls.py · wsgi.py
│   └── qa_settings.py            # 검증 전용 설정 해석기 (§10)
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
│   ├── backup.sh · restore.sh · rotate.sh
│   └── nginx/yogapass.conf.sample     # 기존 nginx에 붙일 server 블록 예시 (devops 확정)
│
├── qa/                           # 검증 지원 도구 (§10) — 운영 이미지에서 제외
│   └── seed_standard 관련 · concurrency.py · qa_session 관련 · fail-inject 절차 문서
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
| **qa 확인 요청** | REQ-F-064의 1차 검증 수단이 "데이터 파일 값 변경 → **재빌드** → 3곳 반영"인데, 이 설계에서는 **"파일 수정 → `manage.py seed_content` 실행 → 3곳 반영"**(재빌드 불필요)이 된다. 같은 취지로 판정 가능한지 **qa 의견을 요청**한다(§16 Q-2) |

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
| 상담 조회 | 10분 10회, 초과 시 10분 차단 | M-3 |
| 로그인 | 계정당 10분 5회 / 출처당 10분 20회, 관리자 계정당 10분 3회 | D-34 |
| 재설정 요청 | 출처당 10분 3회 / 1일 10회 | D-34 |
| **조회 실패 최소 응답(D-7)** | **300ms 고정 하한**(성공·실패 동일). 실제 처리가 300ms를 넘으면 그대로 응답 | 번호 존재 여부의 타이밍 노출 차단. 체감과 방어 효과의 절충 |
| 차단 응답 | **사유를 구분해 알리지 않는다**(스팸 차단·빈도 초과 모두 일반 실패 문구) | REQ-F-044, 페이지 디자인 §4.3 |
| 사용량 알림 | 임계 초과 시 운영자 알림 메일(`kind=rate_limit_alert`) | REQ-N-019 |

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
| **검증 전용** | `QA_TOOLS_ENABLED` · `QA_RATE_LIMIT_MODE` · `QA_RETENTION_MINUTES__*` · `QA_CLOCK_OFFSET_SECONDS` · `QA_FAIL_INJECT`(smtp/backup/purge) · `QA_SESSION_TOKEN` | ✕ | **§10.6 안전장치 필수** |

- `.env.example`에는 **키와 설명만** 둔다. `.env`는 `.gitignore`에 포함한다(REQ-N-018).
- 이미지 빌드 시 시크릿을 넣지 않는다 — 전부 **런타임 환경 변수 주입**. 검증은 이미지 레이어 검색(M-4 패턴)으로 한다.

---

## 8. 로컬 개발 환경

| 항목 | 내용 |
|---|---|
| 요구 런타임 | **Docker Desktop(Windows) 또는 Docker Engine + compose v2.** 호스트에 Python·Node 설치 불필요 |
| 최초 설치 | `.env.example` → `.env` 복사 후 값 입력 → `docker compose -f compose.yaml -f compose.local.yaml build` |
| 기동 | `docker compose -f compose.yaml -f compose.local.yaml up` → **http://localhost:8000** |
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
| 측정 | M-1 조건(모바일 프리셋·3회 중앙값·확장 없는 프로필)으로 **P4 자체 점검에서 1차 측정**하고 결과를 개발 보고서에 남긴다. 최종 판정은 P5 |

### 9.5 보안 (REQ-N-017~020)

| 항목 | 구현 |
|---|---|
| HTTPS | nginx가 TLS 종료. 앱은 `SECURE_PROXY_SSL_HEADER`로 `X-Forwarded-Proto` 신뢰 + `SECURE_SSL_REDIRECT`(운영만) + HSTS |
| 쿠키 | `Secure`(운영)·`HttpOnly`·`SameSite=Lax`. 세션 유휴 30분(D-33) |
| CSRF | 프레임워크 기본 + `CSRF_TRUSTED_ORIGINS` |
| 보안 헤더 | `X-Content-Type-Options: nosniff` · `Referrer-Policy: strict-origin-when-cross-origin`(재설정 토큰 화면은 `no-referrer`) · `Permissions-Policy` 최소 · **CSP**(`default-src 'self'`, 인라인 스크립트 금지, 지도 로드 시에만 `frame-src`에 해당 도메인 추가) |
| 입력 검증 | **서버 측이 정본**(REQ-F-042). 길이·형식·허용 문자 화이트리스트. 클라이언트 검증은 UX 보조 |
| 스팸 | honeypot(화면 밖 배치 + `tabindex=-1` + `aria-hidden`, 자동완성 유도 이름 회피) + 빈도 제한 + 서버 검증. **차단 사유 미노출** |
| 중복 제출 | 폼 렌더 시 **1회용 `submit_token`** 발급 → 서버가 소비. 제출 중 버튼 비활성은 보조 수단. **JS 없이 제출해도 동일하게 동작한다** |
| 개인정보 | IP는 솔트 해시로만 저장, 로그에 이름·전화·메일 본문 미기록, 관리 명령 출력은 마스킹(`010-****-5678`) |
| 컨테이너 | 비루트 실행, 슬림 베이스, 불필요 패키지 미설치, DB 포트 비게시, 시크릿 런타임 주입 |
| 의존성 | 버전 고정 + 취약점 점검을 배포 전 체크리스트에 포함 |

---

## 10. 검증 지원 도구 (qa P5 환경 요건 ①~⑩) — **별도 산정**

> 요구사항 §5.3 말미의 10항목은 **제작 산출물**이다. 기존 공수 추정에 녹아 있지 않으므로 **작업 단위로 분리해 산정**한다(qa R1 #6, developer R1 #5).

| 요건 | 구현 방식 | 1차 필요 | 1차 공수 | 2차 추가 |
|---|---|---|---|---|
| ① 스테이징 DB + qa 조회 수단 | `manage.py qa_show inquiry --masked` 등 **읽기 전용·마스킹 조회 명령**. 운영 DB 권한은 부여하지 않는다 | ○ | **0.25** | 0.25 |
| ② 테스트 수신 주소·목 발송 + 발송 로그 조회 | Mailpit(로컬·스테이징) + `manage.py qa_mail_log` | ○ | **0.25** | 0.1 |
| ③ 로컬 HTTPS 또는 localhost | `http://localhost:8000`은 **보안 컨텍스트**라 클립보드 API가 동작한다. LAN·스테이징 http 접근 대비로 `execCommand` 폴백 병행 | ○ | 0.1 (§9 포함) | — |
| ④ 검증 전용 설정(보관·빈도·세션) **항목별 독립** | `config/qa_settings.py`가 `QA_*` 키를 **각각 독립적으로** 해석. `QA_RETENTION_MINUTES__INQUIRY=10` + `QA_RATE_LIMIT_MODE=off` 조합 가능(단일 모드 스위치 금지) | ○ | **0.5** | 0.25 |
| ⑤ 테스트 데이터 삭제 규칙 | 시드에 `TEST-` 접두어 + `manage.py qa_purge_test_data --confirm` + 삭제 건수 기록 | ○ | 0.25 | — |
| ⑥ 가상 키보드 검증 수단 | **qa·PM 소관(기기 확보)**. 제작 측은 G-9 구현(메타 + WebKit `visualViewport` 폴백)과 재현 절차 문서를 제공 | ○ | 0.1 (§9 포함) | — |
| ⑦ **검증 전용 로그인 세션 수단** | `manage.py qa_session --role member1|member2|staff` → 세션 발급(스크립트가 쿠키 주입). 회원 2·관리자 1 계정 시드. **`QA_TOOLS_ENABLED`가 켜진 환경에서만 동작** | ✕ (2차) | **0.25**(골격) | **0.75~1.0** |
| ⑧ **표준 시드 + 동시 요청 스크립트** | `manage.py seed_standard`(2차: 슬롯 400·예약 200·상담 100) + `qa/concurrency.py`(동시 N건 발사·성공/거부 집계). 1차는 문의 폼 동시 제출·빈도 제한 재현 + 번호 1,000건 생성 스크립트 골격 | 일부 | **0.5** | **1.0~1.5** |
| ⑨ **실패 주입 수단** | `QA_FAIL_INJECT=smtp,backup,purge` — ⓐ SMTP 자격 증명 강제 오류 ⓑ 백업 강제 실패 ⓒ 파기 배치 강제 예외. **각각 독립 토글**이며 실패 알림 경로까지 확인 가능 | ○ (1차 REQ-N-032·037·038) | **0.5~0.75** | 0.25 |
| ⑩ **기준 시각 고정·이동** | **`core/clock.py`의 `now()` 단일 진입점** + `QA_CLOCK_OFFSET_SECONDS`. 코드에서 현재 시각 직접 호출 금지(린트 규칙으로 차단) | ○ (진입점만) | **0.25~0.5** | 0.25 |
| | **합계** | | **2.7 ~ 3.2작업일** | **2.8 ~ 3.6작업일** |

**⑩을 1차에 넣는 이유**: 시각 진입점을 나중에 한 곳으로 모으려면 **이미 작성된 모든 코드를 고쳐야 한다.** 1차에 0.25~0.5작업일을 쓰면 2차에는 오프셋 적용만 남는다.

### 10.6 검증 도구 안전장치 (필수)

- `DJANGO_ENV=production`인데 `QA_*` 키가 하나라도 설정되어 있으면 **애플리케이션이 기동을 거부**한다.
- `qa/` 디렉토리와 `qa_*` 관리 명령은 **운영 이미지 빌드에서 제외**한다(`.dockerignore`).
- `QA_SESSION_TOKEN`이 없으면 `qa_session` 명령은 동작하지 않는다.
- 이 3가지를 **P5 체크리스트 항목으로 qa에 전달**한다 — 검증 도구가 운영에 열려 있으면 그 자체가 Critical 결함이다.

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
| 12 | **운영 compose · 이미지 빌드·배포·롤백 스크립트 · 백업/복구·회전 · 로그 회전 · 스테이징 구성 · nginx 설정 예시** | 배포 가능 상태 | REQ-N-032·033·040 | **1.5** |
| 13 | **검증 지원 도구 ①~⑩ (1차분)** | qa 인계 | §10 | **2.7 ~ 3.2** |
| 14 | 자체 점검(HTML·링크·`[TBD]` 검색·비밀 정보 검색·`check --deploy`) · **개발 보고서(P4-③)** | 보고 | M-4·M-5, REQ-N-023 | **0.5** |
| | **합계** | | | **14.9 ~ 15.4** |

### 11.2 ⚠ 일정 성립 여부 — **pmo·PM 확인 필요**

| 항목 | 값 |
|---|---|
| 계획서 WBS의 1차 구현 창 | 09-30(수) ~ 10-14(수) — 인프라 선착수 + 화면 구현 + 빌드 확인 |
| 그 구간의 실제 작업일 | **약 10작업일** (주말 제외, 10-09 한글날 제외) |
| 이 문서의 산정 | **약 15작업일** (검증 지원 도구 2.7~3.2 포함) |
| **차이** | **약 5작업일 부족** |

**흡수 방안(권고 순)**

| 안 | 내용 | 효과 | 비용 |
|---|---|---|---|
| **ⓐ 기준 오픈일(11-06) 사용** | 조기 오픈(10-29)은 목표로만 두고 **버퍼 구간(11-02~11-12)을 계획대로 활용** | +5~7작업일 | 없음. 계획서 §4.2.2가 이미 "조기 오픈은 약속하지 않는다"로 정리했다 |
| ⓑ 검증 지원 도구 중 2차 전용분 이월 | ⑦(로그인 세션) 골격을 2차로 미루고 ⑧의 2차 시드 제외 | +0.25~0.5 | qa와 합의 필요. **1차 필수분(④·⑨·⑩)은 미룰 수 없다** |
| ⓒ Could 3건 제외 | SCR-009 공용 오류 화면 · REQ-F-034 주소 복사 · REQ-N-030 | +0.3~0.5 | 효과가 작다. **REQ-N-030은 이 스택에서 사실상 공짜라 제외 실익이 없다** |
| ⓓ 범위 축소 | — | — | **권고하지 않는다.** 1차 Must 60건은 줄일 수 없고 CR 대상이다 |

> **developer 권고: ⓐ**. 작업 속도가 아니라 **고객·운영자 측 확보 항목(도메인 10-16, 실제 값 10-16, SMTP 계정)** 이 조기 오픈의 실제 제약이라는 계획서 §4.2.2 판단과 방향이 같다.

---

## 12. 배포 · 백업 · 복구

### 12.1 이미지 빌드

- 멀티스테이지 `Dockerfile`: `base`(런타임 의존성) → `dev`(개발 도구·바인드 마운트) → `prod`(소스 COPY + `collectstatic` + 압축, 비루트 사용자, `qa/` 제외).
- 태그: `yogapass-app:${APP_VERSION}`(릴리스 태그 `release-v0.1.0`과 1:1) + `yogapass-app:<git-sha>`.
- **레지스트리를 쓰지 않는다** — 단일 서버이므로 서버에서 릴리스 태그를 체크아웃해 빌드한다. 직전 3개 이미지 태그를 보존해 롤백에 쓴다. (레지스트리 도입 여부는 devops 판단 사항으로 남긴다.)

### 12.2 배포 절차 (`deploy/deploy.sh`)

```
0) 사전 점검 : 릴리스 태그 확인 · .env 존재 · 디스크 여유 · 현재 이미지 태그 기록
1) 백업      : deploy/backup.sh --label pre-deploy    ← 되돌릴 수 없는 마이그레이션이 있으면 필수
2) 빌드      : docker compose -f compose.yaml -f compose.prod.yaml build
3) 마이그레이션: docker compose … run --rm app python manage.py migrate --noinput
4) 기동      : docker compose … up -d --no-deps app scheduler
5) 확인      : /healthz 200 · 주요 4경로 200 · 로그 오류 0 · 정적 파일 해시 응답
6) 실패 시    : deploy/rollback.sh 자동 호출
```

### 12.3 기존 nginx에 요청할 설정 (devops 확정 · `deploy/nginx/yogapass.conf.sample` 제공)

| 항목 | 요청 내용 |
|---|---|
| 라우팅 | `proxy_pass` → 앱(`127.0.0.1:${APP_PORT}` 또는 컨테이너 이름, I-2-a에 따름) |
| 헤더 | `X-Forwarded-Proto` · `X-Forwarded-For` · `Host` 전달 |
| 오류 | **`proxy_intercept_errors off`** — 앱의 404·500 화면이 nginx 기본 화면으로 바뀌면 REQ-F-060·065가 깨진다 |
| 업로드 | `client_max_body_size`(2차 사진 업로드 5MB 기준) |
| 압축 | 앱이 사전 압축본을 내려주므로 nginx의 재압축 불필요(중복 압축 방지) |
| 로그 | **별도 access/error 로그 파일**(다른 서비스와 분리, I-2-c) |
| 장애 화면 | `error_page 502 503` → 점검 안내(SCR-009) |
| HTTPS | HTTP→HTTPS 301, HSTS (REQ-N-017) — devops 소관 |

### 12.4 롤백 (`deploy/rollback.sh`)

| 상황 | 절차 |
|---|---|
| 코드만 문제 | `APP_VERSION=<이전 태그>` → `up -d` (수 초) |
| 되돌릴 수 있는 마이그레이션 | `migrate <app> <이전 번호>` 후 이미지 되돌리기 |
| **되돌릴 수 없는 마이그레이션** | 이미지 되돌리기 + **배포 직전 백업으로 DB 복구**(`restore.sh`). 데이터 손실 구간 = 배포 후 경과 시간 → **배포는 트래픽이 적은 시간대에** |
| 판단 기준 | 마이그레이션 파일의 `# IRREVERSIBLE` 표시(§2.4). 배포 전 체크리스트에서 확인 |

### 12.5 백업 · 복구 (REQ-N-032 — G7a 통과 조건)

| 항목 | 값 |
|---|---|
| 대상 | DB 논리 백업(`pg_dump -Fc`) + 미디어 볼륨(2차). **`.env`는 백업 대상에서 제외**(별도 안전 보관, 운영자 소관) |
| 주기 | **일 1회 03:00**(잠정, D-31) + 배포 직전 임시 백업 |
| 회전 | 일 7 · 주 4 · 월 3 (잠정) |
| 저장 위치 | 호스트 `${BACKUP_DIR}` 바인드 마운트. **개인정보 포함 파일이므로 퍼미션 600·소유자 제한·위치를 배포 계획에 기록**(REQ-N-039) |
| 무결성 | 백업 직후 파일 크기·`pg_restore --list` 성공 여부 확인, 실패 시 **운영자 알림 메일** |
| **복구 스크립트** | `restore.sh <파일>` → 빈 DB 생성 → `pg_restore` → `migrate --check` → `/healthz` 확인까지 자동 |
| **복구 리허설** | **스테이징에서 1회 이상 실제 수행**(계획서 10-28). 소요 시간·문제점을 기록해 P8 운영 가이드에 싣는다. ⚠ **복구해 본 적 없는 백업은 백업이 아니다** |
| 오프사이트 | 같은 서버에만 두면 서버 장애 시 함께 잃는다 → **외부 보관 여부는 devops·PM 결정**(§14.3 O-3) |

### 12.6 스테이징 활용 (REQ-N-040)

| 용도 | 시점 |
|---|---|
| P5 검증 환경(운영 DB 접근 금지의 대체) | 10-15 ~ 10-21 |
| 배포 리허설 | 10-26 ~ 10-28 |
| **복구 리허설** | 10-28 |
| HTTPS·보안 쿠키·프록시 IP 등 로컬 재현 불가 항목 확인 | §13 |
| 2차 개발 중 1차 회귀 확인 | 2차 전 기간 |

---

## 13. 로컬 http / 운영 HTTPS 차이 — 재현되지 않는 항목과 검증 방법

| # | 항목 | 로컬(http) | 검증 방법 | REQ |
|---|---|---|---|---|
| 1 | HTTP→HTTPS 리다이렉트 | **재현 불가**(nginx 없음) | **P7 운영** 또는 스테이징(https)에서 응답 헤더 확인 | REQ-N-017 |
| 2 | 보안 쿠키(`Secure`) | 로컬은 off로 동작. 켜면 **로그인 자체가 안 된다** | 스테이징에서 `Set-Cookie`의 `Secure; HttpOnly; SameSite=Lax` 확인 | REQ-N-M-002(2차) |
| 3 | HSTS | 재현 불가 | 스테이징·운영 헤더 확인. **로컬에 HSTS를 켜면 브라우저가 localhost를 https로 고정해 개발이 막힌다** | REQ-N-017 |
| 4 | 혼합 콘텐츠 경고 | 부분 재현(외부 자원 0건이라 발생 여지 없음) | P5는 "외부 http 자원 0건" 정적 확인, 최종은 P7 | REQ-N-017 |
| 5 | 클립보드 API(주소 복사) | **`http://localhost`는 보안 컨텍스트라 동작한다.** 단 LAN IP·스테이징 http 접근에서는 실패 | `execCommand` 폴백 병행 + 스테이징 https에서 최종 확인 | REQ-F-034, 요건 ③ |
| 6 | **프록시 뒤 실제 IP**(빈도 제한 식별) | 로컬은 직접 접속이라 항상 정확 | **운영에서 `X-Forwarded-For` 처리를 잘못하면 모든 요청이 같은 IP로 집계돼 빈도 제한이 전체 차단으로 변한다.** 스테이징에서 서로 다른 출처 2곳으로 제한 동작 확인 — **Major 위험, 스테이징 필수 검증** | REQ-N-019 |
| 7 | SMTP TLS | 로컬은 Mailpit 평문 | 스테이징에서 실제 SMTP 연결(계정 확보 후). 도달·SPF/DKIM은 **P7 운영** | REQ-N-022 |
| 8 | 캐시·압축 헤더 최종형 | 앱 응답까지만 확인 | nginx 통과 후 헤더를 스테이징에서 확인(중복 압축·헤더 덮어쓰기 여부) | REQ-N-004 |
| 9 | 404·502 화면 가로채기 | 재현 불가 | 스테이징에서 앱을 내린 뒤 502 화면, 없는 경로에서 404 상태 코드 확인 | REQ-F-060·065 |
| 10 | canonical·OG·sitemap 절대 URL | `SITE_BASE_URL`이 localhost | 도메인 확정 후 스테이징·운영에서 값 확인 | REQ-N-013 |

> **정리**: 위 10건 중 **1·3·7·10은 P7(운영)**, **2·5·6·8·9는 스테이징**에서 판정한다. **로컬에서 "통과"로 보고하지 않는다.** qa 테스트 계획에 같은 구분으로 반영해 주기를 요청한다(§16 Q-3).

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
| O-3 | 백업 **오프사이트 보관** 여부·위치 | 서버 전체 장애 시 복구 가능성 | 배포 계획 |
| O-4 | I-9 도메인 | canonical·OG·sitemap·구조화 데이터·HTTPS·SPF/DKIM **최종 확인이 전부 이월** | 10-16 |
| O-5 | I-5-b·I-5-c SMTP 계정과 1차 문의 알림 공백 | **1차 오픈 시 문의가 들어와도 아무도 모른다**(관리자 화면은 2차). infra §8.3 **ⓐ(오픈 전 SMTP 연결) 권고에 동의한다** | 10-26 |
| O-6 | T-E 지도 서비스·업체 등록 | 지도 임베드·길찾기 목적지·정적 지도 대체(D-4) | 10-16 |
| O-7 | 고객 실제 값 8묶음(주소·전화·운영시간·강사 등) | `[TBD]` 0건 판정(REQ-N-023) — 미확보 시 해당 행을 렌더하지 않는 규칙으로 오픈은 가능하지만 사이트 가치가 크게 떨어진다 | 10-16 |
| O-8 | 파비콘·OG 이미지 | 미수령 시 해당 태그를 빼고 빌드 후 교체 | 구현 착수 시 |

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
| TR-12 | 검증 전용 설정이 운영에 켜진 채 배포 | **Critical 보안 사고** | 낮음 | §10.6 기동 거부 + 이미지 제외 + P5 체크리스트 |

---

## 16. 검토자에게 요청하는 확인 사항

| # | 대상 | 내용 |
|---|---|---|
| **Q-1** | **devops** | §3.1 I-2-a 전제(운영 nginx = 호스트 설치, 앱은 `127.0.0.1:${APP_PORT}` 게시)가 맞는가. 컨테이너면 외부 네트워크 참여 방식으로 바꾼다 |
| **Q-2** | **qa** | §5.1.1 — REQ-F-064의 1차 검증을 **"데이터 파일 수정 → `seed_content` 실행 → 3곳 반영"** 으로 판정할 수 있는가(수용 기준 문구는 "재빌드") |
| **Q-3** | **qa** | §13의 10건 중 **로컬에서 판정하지 않는 항목 구분**을 테스트 계획에 그대로 반영해 달라. 특히 #6(프록시 IP)은 스테이징 필수 항목이다 |
| **Q-4** | **qa** | §10의 검증 도구 ①~⑩ 구현 형태(관리 명령 이름·환경 변수 이름·출력 형식)가 테스트 계획과 맞는가. 형식 요구가 있으면 지금 알려 달라 |
| **Q-5** | **devops** | §12.3 nginx 요청 목록 중 **`proxy_intercept_errors off`** 와 별도 로그 파일이 기존 운영 정책과 충돌하지 않는가 |
| **Q-6** | **devops** | §12.5 백업 보관 위치·퍼미션·**오프사이트 여부(O-3)**, 그리고 **O-1(운영자의 PostgreSQL 숙련도)** |
| **Q-7** | **devops·qa** | §11.2의 일정 차이(약 5작업일)에 대한 의견. pmo·PM 보고 전에 검토자 시각을 반영하고 싶다 |
| **Q-8** | **qa** | 1차 판정 모수 96건 중 **이 설계로 충족 경로가 보이지 않는 항목**이 있으면 지적해 달라(설계 단계에서 잡는 것이 가장 싸다) |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.1 | 2026-09-12 | developer | 최초 작성 — 스택(Django 5.2 LTS + PostgreSQL 17) 확정, 로컬·운영 compose 구성, 1차/2차 데이터 모델과 DB 제약, 검증 지원 도구 ①~⑩ 별도 산정, 배포·백업·복구 설계, 로컬/운영 차이 10건, 기술 리스크 12건. 결정 대기 항목 10건(D-5·6·7·8·9·13·28·29·33·34) 확정 | CR-001, `shared/reviews/CR-001_impact_developer_r2.md`, `shared/reviews/P3_design-docs_developer_r1.md`, `interviews/2026-09-12_infra-constraints.md` v0.5 |
