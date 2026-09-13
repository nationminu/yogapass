# 강남 요가패스 — 사이트 소스 (`developer/site/`)

Django 5.2 LTS + PostgreSQL 17 + docker compose. **모든 명령은 이 디렉토리에서 실행한다.**
설계 근거는 `../04_tech-design.md`(기술 설계서)이고, 이 문서는 **재현 절차**만 다룬다.

> 현재 구현 범위: **2단계까지 — 1차 6화면(SCR-001·002·003·006·008·009) + 문의 폼**.
> 남은 작업(성능 측정 · 배포/백업 스크립트 · 검증 지원 도구)과 미확인 항목은 `../04_dev-report.md` §4·§7 을 본다.

---

## 1. 요구 사항

| 항목 | 값 |
|---|---|
| 런타임 | **Docker Desktop(Windows) 또는 Docker Engine + compose v2** — 호스트에 Python·Node 설치 불필요 |
| 확인된 버전 | Docker 24.0.2 · Docker Compose v2.19.1 (2026-09-13 실행 확인) |
| 포트 | 8000(앱) · 8080(nginx 프로필) · 8025(Mailpit UI) · 5432(DB, 로컬만) |

## 2. 최초 설치

```bash
cp .env.example .env
# .env 에서 최소 2개를 채운다: DJANGO_SECRET_KEY, POSTGRES_PASSWORD
docker compose -f compose.yaml -f compose.local.yaml build
docker compose -f compose.yaml -f compose.local.yaml run --rm app python manage.py migrate --noinput
docker compose -f compose.yaml -f compose.local.yaml run --rm app python manage.py seed_content
docker compose -f compose.yaml -f compose.local.yaml run --rm app python manage.py createsuperuser
```

## 3. 기동

```bash
docker compose -f compose.yaml -f compose.local.yaml up
```

| 주소 | 내용 |
|---|---|
| http://localhost:8000 | 앱 직접 (runserver, 자동 리로드) |
| http://localhost:8080 | **nginx 경유** — `.env` 의 `COMPOSE_PROFILES=proxy` 로 켜진다(플래그 불필요) |
| http://localhost:8025 | Mailpit UI (발송 메일 확인) |
| http://localhost:8000/healthz | 헬스체크 (호출은 **항상 앱에 직접** 한다 — nginx 경유 금지) |

- `COMPOSE_PROFILES` 를 비우면 `proxy` 없이 앱만 뜬다. 기본값은 **`proxy,backup`** 이다 — `backup` 은 기동 시 `run_backup` 을 1회 실행하고 끝나는 일회용 서비스다(상시 컨테이너가 아니다).
- 스테이징·운영은 같은 `compose.yaml` 에 override 1개만 바꿔 쓴다:
  ```bash
  ENV_FILE=.env.staging docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-stg up -d
  ENV_FILE=.env          docker compose -f compose.yaml -f compose.prod.yaml -p yogapass     up -d
  ```
  스테이징만 `mail`(Mailpit)을 띄운다 — `.env.staging` 의 `COMPOSE_PROFILES=mail`. 운영은 비운다.

## 4. 자주 쓰는 명령

```bash
C="docker compose -f compose.yaml -f compose.local.yaml"

$C exec app python manage.py migrate            # 마이그레이션
$C exec app python manage.py makemigrations     # 모델 변경 후
$C exec app python manage.py seed_content       # content/*.yml -> DB  (★ 파일만 고치면 반영되지 않는다)
$C exec app python manage.py check_release      # 배포 사전 점검 — [TBD] 잔존 시 종료 코드 1 (REQ-N-023 ①)
$C exec app python manage.py send_outbox        # 메일 아웃박스 수동 플러시
$C exec app python manage.py scheduler_health   # 스케줄러 생존 판정
$C exec -e DJANGO_SETTINGS_MODULE=config.settings.test app python manage.py test
$C exec app ruff check .                        # 린트
$C exec app ruff format .                       # 포맷
$C logs -f scheduler                            # 정기 작업 로그

# 레이아웃 회귀 점검 (실제 렌더 측정 — 가로 스크롤·터치 타깃·글꼴 하한·인라인 style·콘솔 오류)
#   Chrome 과 puppeteer-core 가 필요하다(저장소에 두지 않는다). NODE_PATH 로 위치를 알려준다.
BASE=http://localhost:8000 NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js

# --- 운영 작업 (스케줄러가 자동 실행한다. 아래는 수동 실행법) ---
$C exec scheduler python manage.py run_backup            # DB 백업 + 무결성 확인 + 회전
$C exec scheduler python manage.py run_backup --dry-run  # 대상·여유 공간·회전 예정만
$C exec scheduler python manage.py run_backup --label pre-deploy   # 라벨 백업(락 충돌 시 실패)
$C exec scheduler python manage.py purge_expired --dry-run         # 보관 기간 경과 파기
$C exec scheduler python manage.py prune_rate_limit --dry-run      # 빈도 제한 카운터 정리
$C exec scheduler python manage.py report_failures --dry-run       # 일일 운영 요약 본문 확인
$C exec scheduler python manage.py ping_health                     # /healthz 폴링(앱 직접)

# --- 배포·롤백·복구 (서버에서 실행한다. 로컬 재현은 COMPOSE_FILES 로) ---
APP_VERSION=0.1.0 ./deploy/deploy.sh --dry-run     # 0단계 사전 점검만
APP_VERSION=0.1.0 ./deploy/deploy.sh               # 배포
ROLLBACK_VERSION=0.0.9 ./deploy/rollback.sh        # 롤백
./deploy/restore.sh /backups/<파일>.dump           # 복구(확인 입력 yes · 운영은 추가 플래그)
COMPOSE_FILES="-f compose.yaml -f compose.local.yaml" ./deploy/restore.sh /backups/<파일>.dump  # 로컬 리허설

# --- 검증 지원 도구 (QA_TOOLS_ENABLED=1 인 환경에서만 동작) ---
$C exec app python manage.py qa_show inquiry --count-only --since 2026-10-15T09:00
$C exec app python manage.py qa_mail_log --kind inquiry_notify --format json
$C exec app python manage.py qa_pii_columns
$C exec app python manage.py qa_purge_test_data --since <ISO> --confirm
$C exec app python manage.py seed_standard --count 20 --refs 1000
$C exec app python manage.py qa_session --role staff --token "$QA_SESSION_TOKEN"
$C exec app python qa/concurrency.py --url http://127.0.0.1:8000/location --count 20
```

## 5. 운영 빌드 미리보기

```bash
cp .env .env.prodcheck   # DJANGO_ENV=production, DJANGO_DEBUG=0, APP_PORT=8001, COMPOSE_PROFILES= 로 수정
#  ★ DJANGO_SETTINGS_MODULE 도 config.settings.production 으로 바꾼다 — env_file 값이 이미지 기본값을 덮으므로
#     그냥 복사하면 local 설정으로 뜨고 404 가 디버그 화면으로 나온다.
ENV_FILE=.env.prodcheck docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck \
  --env-file .env.prodcheck up -d --build
# http://localhost:8001 (gunicorn + WhiteNoise: 해시 파일명 · brotli · immutable 캐시)
ENV_FILE=.env.prodcheck docker compose -f compose.yaml -f compose.prod.yaml -p yogapass-prodcheck \
  --env-file .env.prodcheck down -v && rm -f .env.prodcheck
```

## 6. 디렉토리

```
config/      설정(base/local/staging/production/test) · URL · WSGI
apps/core/   공통(미들웨어·접근 제어·시각·식별자·아이콘 태그·정기 작업 실행기·/healthz·화면 뷰)
apps/content/ 강사·수업 유형·사이트 설정 + 처리방침 본문 로더 + seed_content · check_release
apps/inquiry/ 문의 접수(모델·폼·응답 형태 6종) — 1차의 유일한 쓰기 경로
apps/accounts/ 커스텀 사용자 모델(1차는 운영자 계정만)
apps/mailer/ 메일 아웃박스 + send_outbox
templates/   base.html · partials/ · pages/ · errors/
static/      css(tokens·base·components·pages) · js · fonts(Pretendard) · icons(Lucide) · img
content/     시드 데이터(*.yml) — 사람이 고치는 단일 원본
deploy/      entrypoint · gunicorn · crontab · nginx 설정·점검 화면
tests/       스모크 · 화면 · 문의 폼 응답 형태 7종 · SEO/마크업 · 처리방침 대조 테스트
tests/browser/ 실제 렌더 측정 도구(layout-check.js — Chrome + puppeteer-core 필요, 배포 대상 아님)
             · /nope 는 사양상 404 라 **문서 자신의 404 콘솔 메시지만** 위반에서 뺀다(하위 리소스 404 는 위반)
assets-work/ 자산 작업 사본(임시 OG 원본 등). **static/ 에 두지 않는다** — 이미지·배포 산출물에서 제외
```

## 7. 폰트 (Pretendard) 재생성

`static/css/fonts.css` 는 **생성물**이다. 업스트림 버전을 올릴 때만 다시 만든다.

```bash
V=v1.3.9
B="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@$V/packages/pretendard/dist/web/static"
for w in Regular Bold; do for i in $(seq 0 91); do \
  curl -sS -O --output-dir static/fonts/pretendard "$B/woff2-dynamic-subset/Pretendard-$w.subset.$i.woff2"; done; done
curl -sS -o /tmp/pdyn.css "$B/pretendard-dynamic-subset.css"
# 400/700 블록만 추출하고 src 를 woff2 단일 포맷·상대 경로로 재작성 (기존 fonts.css 머리말·폴백 블록은 보존한다)
```

- 라이선스: SIL OFL 1.1 (`static/fonts/pretendard/OFL.txt`). 아이콘은 Lucide ISC (`static/icons/SOURCES.md`).
- `<link rel="preload">` 대상은 **chunk 91(Latin+상용 한글) · chunk 90(한글 기본)** 의 400 두 개뿐이다.

## 8. 화면과 콘텐츠

| URL | 화면 | 콘텐츠 원본 |
|---|---|---|
| `/` | SCR-001 메인 | `content/site.yml` · `instructors.yml` · `lesson_types.yml` |
| `/instructors` | SCR-002 요가 강사 소개 | `content/instructors.yml` |
| `/location` (`#contact`) | SCR-003 오시는 길 + 문의 폼 | `content/site.yml` |
| `/privacy` | SCR-006 개인정보 처리방침 | **`content/privacy.yml`** (DB를 거치지 않고 파일을 직접 읽는다) |
| 없는 경로 | SCR-008 404 (실제 404 상태 코드) | — |
| 5xx | SCR-009 공용 오류 | — |

- `content/*.yml` 중 **`privacy.yml` 만 `seed_content` 가 필요 없다**(파일이 곧 화면). 나머지는 고친 뒤 `seed_content` 1회 실행이 필요하다.
- 문의 폼의 응답 형태 6종(정상·검증 실패·honeypot·빈도 제한·토큰 재사용·서버 오류)은 **기술 설계 §9.6 표**가 정본이고 `tests/test_inquiry.py` 가 그 값을 그대로 검사한다.

## 9. 주의

- **비밀 정보는 `.env` 에만 둔다.** `.env`·`.env.*` 는 저장소에서 제외된다(`.env.example` 만 커밋).
- `[TBD]` 값은 화면에 출력하지 않는다 — 값이 미확정이면 **해당 요소·행 자체를 렌더하지 않는다**(REQ-N-023).
- 포커스 링 규칙은 `static/css/tokens.css` 맨 뒤에 있다. 이후 CSS 에서 `outline` 을 덮지 않는다.
- **템플릿의 여러 줄 주석은 `{% comment %}` 를 쓴다.** Django 의 `{# … #}` 는 한 줄 전용이라 여러 줄로 쓰면 주석이 HTML 로 새어 나간다.
- `static/img/*.svg` 는 브라우저가 **XML 로 파싱**한다. 주석 안에 `--`(연속 하이픈)를 넣으면 파싱 오류로 이미지가 뜨지 않는다.
- OG 대표 이미지(`static/img/og-image.png`)는 **파일이 있을 때만** `og:image` 계열 태그가 붙는다.
- **viewport 메타 문자열을 바꾸지 않는다** — `width=device-width, initial-scale=1, interactive-widget=resizes-content`. 마지막 토큰이 가상 키보드 대응(G-9)의 **Chromium 쪽 유일한 수단**이다(WebKit 은 `static/js/viewport.js` 폴백이 담당). 정본은 기술 설계 **§9.1 표**이고 `tests/test_seo_markup.py` `ViewportMetaTests` 가 전 화면을 대조한다.
  현재 파일은 **임시본**이다(PM 결정 2026-09-13). 출처·교체 절차는 `static/img/SOURCES.md`.
- **`.env` 의 값 줄에 인라인 주석을 쓰지 않는다.** `docker run --env-file` 과 셸 파서가 주석을 값의 일부로 읽어
  숫자 해석 실패·가드 우회가 생긴다. 설명은 값 줄 **위**에 둔다.

---

## 10. 백업 · 복구 · 배포 (작업 12 · 기술 설계 §12)

| 항목 | 내용 |
|---|---|
| 정기 백업 | 스케줄러가 **매일 03:00** `run_backup` 실행 → `${BACKUP_DIR}`(로컬 기본 `./backups`)에 `yogapass-<env>-YYYYMMDD-HHMM.dump`(KST 표기) |
| 무결성 | 파일 크기 > 0 **AND `pg_restore --list` 성공**. 실패하면 종료 코드 ≠ 0 + `mailer_outbox(kind=backup_failed)` 알림 |
| 회전 | **일 7 · 주 4 · 월 3**. `--label` 이 붙은 파일은 회전 대상에서 제외하고 최근 3개만 유지 |
| ⚠ 라벨 백업 | `--label` 실행은 **required** 다. 다른 백업이 돌고 있어 락을 못 잡으면 `skipped` 가 아니라 **종료 코드 ≠ 0 으로 실패**하고, `deploy.sh`·`restore.sh` 는 그것을 중단 사유로 쓴다 |
| 복구 | `deploy/restore.sh <파일>` — ⓐ 대상 출력 + `yes` 입력 ⓑ 운영이면 `--i-know-this-is-production` ⓒ **복구 전 현재 DB 자동 덤프(`pre-restore`)**. 덤프가 실패하면 복구하지 않는다 |
| 배포 | `deploy/deploy.sh` — 0 사전 점검 → **0.5 스케줄러 정지** → 1 라벨 백업 → 2 빌드 → 3 마이그레이션 → 4 기동 → 5 `/healthz`(**앱 직접**) 확인·다운타임 실측 → 실패 시 `rollback.sh` 자동 호출 |
| ⚠ 이미지 정리 | **`docker image prune -a` 금지.** 롤백 경로가 사라진다. 정리는 `docker image prune --filter "label!=org.yogapass.keep=release"` 로만 한다 |
| nginx | 호스트 nginx 요청안은 `deploy/nginx/yogapass-prod.conf.sample` · `yogapass-stg.conf.sample`. 로컬 `local.conf` 가 같은 지시어 집합을 먼저 검증한다 |

## 11. 검증 지원 도구 (작업 13 · 기술 설계 §10)

- 전부 **관리 명령**이다. **HTTP 경로로 노출되지 않는다.**
- `QA_TOOLS_ENABLED=1` 이 아니면 각 명령이 **"이 환경에서는 사용할 수 없습니다" + 종료 코드 2** 로 끝난다.
- **운영 이미지에는 `qa/` 디렉토리 자체가 없다.** 그 이미지에서 `QA_TOOLS_ENABLED=1` 을 주면 **기동이 거부**된다.

| 환경 변수 | 용도 |
|---|---|
| `QA_TOOLS_ENABLED` | 마스터 스위치. **이 값 없이는 아래 어떤 것도 해석되지 않는다** |
| `QA_CLOCK_OFFSET_SECONDS` | 기준 시각 이동(**음수 허용**). 적용 시 기동 로그에 `CLOCK OFFSET: <n>s` |
| `QA_FAIL_INJECT` | `smtp,backup,purge` 콤마 목록(**독립 토글**). 주입되면 로그 1줄 |
| `QA_RETENTION_MINUTES__INQUIRY` | 보관 기간을 **분 단위**로 단축(파기 배치 검증) |
| `QA_RATE_LIMIT_MODE=off` | 빈도 제한만 끈다(다른 항목에 영향 없음) |
| `QA_RATE_LIMIT_ALERT_*` | 사용량 알림 임계값 하향 |
| `QA_SESSION_TOKEN` | `qa_session` 사용 조건 |

- WebKit(Safari·iOS) 실기기 체크리스트: **`qa/webkit_checklist.md`**
