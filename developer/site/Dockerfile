# syntax=docker/dockerfile:1
# 멀티스테이지: base -> dev / prod (기술 설계 §12.1)
# ⚠ 시크릿을 이미지에 넣지 않는다. 전부 런타임 환경 변수로 주입한다(REQ-N-018).

# ------------------------------------------------------------------ base
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# postgresql-client: manage.py run_backup 이 pg_dump / pg_restore --list 를 부른다(§12.5.1)
# supercronic      : scheduler 컨테이너의 cron 실행기(§3.3)
ARG SUPERCRONIC_VERSION=v0.2.49
ARG SUPERCRONIC_SHA1=e63c11a9726b775a6a11801e81af4f3fb926aa68
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends postgresql-client curl ca-certificates; \
    curl -fsSLo /usr/local/bin/supercronic \
      "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/supercronic-linux-amd64"; \
    echo "${SUPERCRONIC_SHA1}  /usr/local/bin/supercronic" | sha1sum -c -; \
    chmod +x /usr/local/bin/supercronic; \
    apt-get purge -y curl; \
    apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*; \
    pg_dump --version

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN useradd --create-home --uid 10001 app

# ------------------------------------------------------------------ dev
FROM base AS dev
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
ENV DJANGO_SETTINGS_MODULE=config.settings.local
COPY deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ------------------------------------------------------------------ prod
FROM base AS prod
LABEL org.yogapass.keep=release
ENV DJANGO_SETTINGS_MODULE=config.settings.production
COPY --chown=app:app . /app
# 검증 지원 도구는 운영 이미지에 존재하지 않는다 (기술 설계 §10.6)
RUN rm -rf /app/qa /app/tests /app/.env /app/.env.* || true
RUN DJANGO_SECRET_KEY=build-only-not-a-secret \
    POSTGRES_PASSWORD=build-only \
    DJANGO_ENV=production \
    python manage.py collectstatic --noinput
RUN chmod +x /app/deploy/*.sh
USER app
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["gunicorn", "-c", "deploy/gunicorn.conf.py", "config.wsgi:application"]
