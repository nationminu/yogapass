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

- `COMPOSE_PROFILES` 를 비우면 `proxy` 없이 앱만 뜬다. `backup` 프로필은 **작업 12(`manage.py run_backup`) 완료 후** 값에 추가한다.
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
```

## 5. 운영 빌드 미리보기

```bash
cp .env .env.prodcheck   # DJANGO_ENV=production, DJANGO_DEBUG=0, APP_PORT=8001, COMPOSE_PROFILES= 로 수정
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
tests/       스모크 · 화면 · 문의 폼 응답 형태 6종 테스트
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
- OG 대표 이미지(`static/img/og-image.png`)는 **파일이 있을 때만** `og:image` 계열 태그가 붙는다. placeholder 를 만들지 않는다.
