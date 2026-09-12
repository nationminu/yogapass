---
doc_id: DEV-REPORT
title: 개발 보고서 — 1차 구현 (2단계 · 전 화면 + 문의 폼)
phase: P4
owner: developer
version: 0.2
status: draft
reviewers: [designer, planner]
inputs: [developer/04_tech-design.md, planning/02_requirements.md, planning/02_storyboard.md, design/03_design-system.md, design/03_page-design.md, design/mockups/, shared/tickets/TKT-DSN-002_to-developer_favicon-og-raster.md, shared/reviews/P4a_tech-design_devops_r2.md, shared/reviews/P4a_tech-design_qa_r2.md]
updated: 2026-09-13
---

# 개발 보고서 (초안) — 1차 구현 2단계

> **이 문서의 상태**: `draft`. 1차 구현 **14개 작업 중 작업 1~10 + 작업 14 일부**를 마친 시점의 중간 보고다.
> **규칙**: 이 문서에는 **직접 실행해 확인한 것만** 적는다. 실행하지 않은 항목은 "미확인"으로 적고 "완료"로 쓰지 않는다.
> 설계 근거는 `developer/04_tech-design.md` v0.3, 실행 절차는 `developer/site/README.md`.
> v0.1(1단계) 대비 달라진 곳은 **▲** 로 표시했다.

---

## 1. 요약

| 항목 | 내용 |
|---|---|
| 이번 범위 | ▲ 기술 설계 §11.1 **작업 5(SCR-002) · 6(SCR-003 지도) · 7(문의 폼) · 8(문의 알림 본문) · 9(SCR-006·008·009) · 10(SEO·접근성·`<noscript>` 마감)** + TKT-DSN-002(파비콘·OG 래스터) 처리 |
| 진척(작업 단위) | ▲ **10 / 14 작업** (남은 것: 11 성능 측정 · 12 배포/백업 · 13 검증 지원 도구 · 14 자체 점검 마감) |
| 1차 화면 | ▲ **6화면 전부 구현** — SCR-001·002·003·006·008·009 |
| Must REQ 구현률 | ▲ 1차 Must 60건 기준 **추정** — **완료 약 34 · 부분 약 14 · 미착수 약 12** (§2 표가 근거. **확정 집계는 qa 추적 매트릭스가 한다** — 이 숫자를 게이트 판정에 그대로 쓰지 않는다) |
| 로컬 빌드 · 실행 | **성공** — `docker compose … up` 으로 app·db·mail·scheduler·proxy **5개 서비스 healthy**, 4개 공개 화면 200 / 없는 경로 404 (§4) |
| 운영 빌드 | **성공** — prod 이미지 빌드 + gunicorn 기동 + 해시·brotli·`immutable` 확인, 새 화면 4종 200 (§4) |
| 문의 폼 | ▲ **설계 §9.6 응답 형태 6종을 전부 구현하고 6종 모두 실행 확인**(자동 테스트 + curl) |
| 자동 테스트 | ▲ **48건 전부 통과** (v0.1 9건 → 48건), `ruff check` 통과 |
| 검증팀 전달 가능 여부 | ▲ **부분 가능.** 화면·폼·SEO·접근성 마크업은 지금 검증할 수 있다. 백업·배포·검증 지원 도구(작업 12·13)는 아직 없다 |

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
| REQ-N-010~016 | SEO | ▲ 완료(값 제외) | `templates/partials/meta.html`(title·description·canonical·OG) · `apps/core/sitemaps.py`(색인 4화면) · `views.robots_txt`(Disallow 0건) · `jsonld_localbusiness.html`. **도메인은 `SITE_BASE_URL` 교체만으로 전환된다**(§4 #12) |
| REQ-N-017·022 | HTTPS · 메일 발신 인증 | 미착수 | 운영 nginx·도메인 확정 후(§13) |
| REQ-N-018 | 비밀 정보 분리 | 완료 | `.env` 커밋 제외 확인, 운영 이미지 레이어 비밀 문자열 0건(1단계 확인 유지) |
| REQ-N-019 | 폼 악용 방지 **단일 구현** | ▲ 완료 | `apps/core/ratelimit.py`(10분 5회 / 1일 20회, 차단 지속·`Retry-After` 계산, **사용량 알림 3임계 + 1시간 합산**) · honeypot · 서버 검증 |
| REQ-N-020 | 개인정보 최소 수집 | ▲ 완료 | 저장 항목 3개 + `source_ip_hash`(**원본 IP 미저장**). 로그에 이름·전화·본문 미기록(테스트로 고정) |
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
| REQ-N-032·033·038·039·040 | 백업·배포/롤백·파기·스테이징 | 미착수 | 작업 12 |

---

## 3. 화면별 구현 현황 (SCR ID ↔ 페이지 파일)

| SCR ID | 화면 | URL | 상태 | 구현 파일 | 디자인 명세와 차이 (사유) |
|---|---|---|---|---|---|
| — (공통) | 헤더·푸터·고정 바·스킵 링크·메타 | — | 완료 | `templates/base.html` · `partials/*` | ▲ `<link rel="icon">`(ico)·`apple-touch-icon` 추가. `og:image` 는 **래스터 미보유라 태그를 빼고 빌드**(§7) |
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
| ⑤ | 토큰 재사용·만료 | **200** | **①과 동일 화면** | 0건(추가 없음) | 0건 | `INFO inquiry.duplicate token_state=used\|expired ref=…` | 자동 테스트 + curl(§4 #7) |
| ⑥ | 서버 오류 | **500** | `errors/500.html`, 스택 트레이스 미노출 | 0건(롤백) | 0건(롤백) | `ERROR` + 트레이스(개인정보 없음) | 자동 테스트(예외 주입) |

- **설계와 다른 점 0건.** 구현이 표를 벗어난 곳은 없다.
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

**확인하지 않은 것(중요)**

| 항목 | 사유 |
|---|---|
| Lighthouse 4지표 측정 | 측정 조건(M-1)을 만족할 브라우저 실행 환경이 없다. **작업 11** |
| 실제 뷰포트 렌더(360/768/1024/1280px)·가로 스크롤·요소 겹침 | 위와 동일. CSS 구간은 작성했으나 **눈으로 확인하지 않았다** |
| 브라우저에서의 JS 동작(카운터·blur 검증·전송 중·지도 로드·주소 복사 토스트) | **코드 경로만 작성**했고 브라우저 실행 확인은 못 했다. 서버 경로(JS 없음)는 curl 로 전부 확인했다 |
| W3C HTML 검사 · 축 기반 접근성 자동 점검 | 도구 미설치. 작업 13·P5 |
| Safari·iOS 실기기 | 설계 §10.5 대로 P5 구간 |
| 지도 실제 임베드·길찾기 동작 | 지도 서비스·URL 미확정(T-E). 값이 오면 코드 변경 없이 동작한다 |

---

## 5. 자체 테스트

| 파일 | 건수 | 내용 |
|---|---|---|
| `tests/test_smoke.py` | 9 | URL·상태 코드·공통 레이아웃·CTA 상태(H1~H3/S1~S3)·식별자 규칙·보안 헤더 |
| ▲ `tests/test_pages.py` | 19 | 화면 공통 규칙(h1 1개·랜드마크·canonical·OG·sitemap·robots·**템플릿 주석 누출 0**) · SCR-002 인원 경계값 · 경력 접기 · SCR-006 목차 11항목·표 라벨·`<details>` · 404·500 · 전화 확정 전후 렌더 · **배포 사전 점검** |
| ▲ `tests/test_inquiry.py` | 20 | **응답 형태 6종 전건** + 경계값 + 아웃박스 본문 + 사용량 알림 + honeypot 화면 동일성 + 필수 표시 3중 + 동의 문구 + `<noscript>` + 지도 버튼 조건부 렌더 |
| **합계** | **48** | `manage.py test` **전건 통과** |

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
| 6 | ▲ **`og-image.png` 미생성** — OG 이미지 태그가 빠진 채 빌드된다 | 링크 공유 시 대표 이미지 없음 | §7 참조. Pretendard 설치 환경이 필요하다 |
| 7 | ▲ `submit_token` 만료(24시간)는 **저장 없이 성공 화면**을 돌려준다(설계 §9.6 ⑤ 그대로) | 폼을 24시간 이상 열어 둔 이용자의 제출이 조용히 버려진다 | 설계가 정한 동작이라 그대로 구현했다. **만료 시간을 늘릴지 / ⑤를 재렌더로 바꿀지**는 설계 개정 사항으로 qa·planner 의견을 받고 싶다(§8) |
| 8 | 폰트 폴백 메트릭 잠정값 · `requirements.lock` 미도입 · nginx 운영 샘플 미작성 | v0.1 #2·#3·#7 그대로 | 작업 11·12 |
| 9 | 지도·주소·전화·강사·처리방침 본문이 전부 `[TBD]` | **현재 화면 대부분이 "값 없음" 상태로 보인다** — 디자인 검토 시 목업과 달라 보인다 | 코드 변경 없이 `content/*.yml` 수정(+`seed_content`)으로 반영된다. 수령 일정은 pmo 추적(T-C·T-E·T-F·T-G) |

---

## 7. TKT-DSN-002 (파비콘·OG 래스터) 처리 결과

| 산출물 | 결과 | 크기 |
|---|---|---|
| `favicon.ico` (32+48 멀티사이즈) | ✅ 생성 | 13.9KB |
| `icon-192.png` | ✅ 생성 | 3.1KB |
| `icon-512.png` | ✅ 생성 | 8.8KB |
| `apple-touch-icon.png` (180) | ✅ 생성 | 3.0KB |
| `og-image.png` (1200×630) | ❌ **보류** | — |

- 변환은 **일회용 컨테이너**에서 했다(틀·프로젝트에 도구를 설치하지 않았다):
  `docker run --rm -v …:/in -v …:/out alpine:3.20 sh -c "apk add --no-cache rsvg-convert imagemagick && rsvg-convert -w 192 -h 192 /in/icon-master-512.svg -o /out/icon-192.png … && magick /tmp/f32.png /tmp/f48.png /out/favicon.ico"`
- 산출물 위치: `developer/site/static/img/`. `base.html` 에 `<link rel="icon" …ico>` · `<link rel="apple-touch-icon" …>` 를 추가했다.
- **`og-image.png` 보류 사유**: 원본 `og-image.svg` 는 `font-family: Pretendard` 로 조판돼 있고, 우리가 가진 Pretendard 는 **`unicode-range` 분할 woff2 서브셋**뿐이라 fontconfig 가 로드하지 못한다. 폴백 폰트로 구우면 글자 폭이 달라져 **좌우 96px 여백을 넘을 수 있다**(티켓이 경고한 바로 그 상황)고 판단했고, 육안 확인 수단도 없다. 티켓의 방침 ②대로 **placeholder 를 만들지 않고 `og:image` 계열 태그를 빼고 빌드**했다. 파일이 `static/img/og-image.png` 에 놓이면 **코드 변경 없이** 태그 5줄(`og:image`·width·height·alt·`twitter:card`)이 붙는다(`apps/core/context_processors._og_image`).
- **designer 에게 알릴 사항 1건(결함)**: `design/assets/favicon.svg` 는 **XML 로 파싱되지 않는다.** 6행 주석 안의 `--color-primary` 가 XML 주석 규칙(연속 하이픈 금지)을 어긴다. 브라우저는 `image/svg+xml` 을 XML 로 파싱하므로 **파비콘이 표시되지 않는다.** 우리 사본(`static/img/favicon.svg`)은 문구를 고쳐 해소했고 변환도 그 사본으로 했다. **원본 수정은 designer 소관**이라 티켓 처리 결과에 적었다.

---

## 8. 검증팀 전달 사항

- **실행 방법**: `developer/site/README.md` (설치 → 기동 → 자주 쓰는 명령 → 화면·콘텐츠 표 → 운영 빌드 미리보기)
- **지금 검증할 수 있는 것**: 1차 6화면 전부 · **문의 폼 응답 형태 6종**(§3.1 이 기대값) · SEO(메타·canonical·sitemap·robots·JSON-LD) · 접근성 마크업(랜드마크·라벨·오류 요약·포커스 이동·색 외 병기) · **JS 비활성 동작**(브라우저 JS 끄기 또는 curl) · 콘텐츠 시드 반영 절차 · 빈도 제한과 복귀(`QA_CLOCK_OFFSET_SECONDS`)
- **아직 검증할 수 없는 것**: 성능·Lighthouse(작업 11) · 백업/배포/롤백(작업 12) · **검증 지원 도구 ①~⑪ 전부**(작업 13) · 지도 실제 동작(T-E)
- **판정용 로그 조회**: `docker compose -f compose.yaml -f compose.local.yaml logs app` — `inquiry.created` / `inquiry.invalid` / `inquiry.blocked reason=…` / `inquiry.duplicate token_state=…`
- **빈도 제한 조정**: `.env` 의 `RATE_LIMIT_FORM_WINDOW_MAX`·`RATE_LIMIT_FORM_DAY_MAX` 로 낮춘다. 사용량 알림 임계는 `QA_TOOLS_ENABLED=1` 일 때만 `QA_RATE_LIMIT_ALERT_*` 로 낮아진다
- **의견을 받고 싶은 것 2건**: ⓐ §6 #7(토큰 만료 시 조용한 성공) 처리 방침 ⓑ §6 #3(경력 접기 기준을 항목 수로 근사)

---

## 9. 발행·처리한 티켓

| ID | 내용 | 상태 |
|---|---|---|
| TKT-DSN-002 | 파비콘·OG 래스터 변환 요청 | **부분 처리** — 래스터 4종 생성, `og-image.png` 보류(사유 기재) + `favicon.svg` XML 오류 1건 회신 (§7) |
| — | 이번 작업에서 신규 발행한 티켓 없음 | — |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.2 | 2026-09-13 | developer | **구현 2단계** — 1차 6화면 완성(SCR-002·003·006 신규, 008·009 디자인 반영) · **문의 폼과 응답 형태 6종**(§3.1) · 빈도 제한·사용량 알림 · SEO/접근성/`<noscript>` 마감 · 파비콘 래스터 4종(TKT-DSN-002) · **템플릿 주석 누출 결함 수정** · 자동 테스트 9 → 48건 | TKT-DSN-002 |
| 0.1 | 2026-09-13 | developer | 최초 작성(초안) — 구현 1단계(작업 1~3 + SCR-001 뼈대)와 실행 명령 28건의 확인 결과 | `shared/reviews/P4a_tech-design_devops_r2.md`, `shared/reviews/P4a_tech-design_qa_r2.md` |
