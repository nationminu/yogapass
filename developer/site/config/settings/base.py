"""공통 설정 — 환경별 설정(local/staging/production/test)이 이 모듈을 상속한다.

기술 설계 §2 · §7.2 · §9.5 를 구현한다. 값은 전부 환경 변수에서 읽고
어떤 비밀 정보도 이 파일에 쓰지 않는다(REQ-N-018).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from config.env import env, env_bool, env_int, env_list

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------- 실행 환경
DJANGO_ENV = env("DJANGO_ENV", "local")  # local | staging | production
APP_VERSION = env("APP_VERSION", "0.0.0-dev")

# ------------------------------------------- 검증 지원 도구 마스터 스위치 (기술 설계 §3.5.1 ②)
QA_TOOLS_ENABLED = env_bool("QA_TOOLS_ENABLED", False)
if QA_TOOLS_ENABLED and DJANGO_ENV == "production":
    raise ImproperlyConfigured(
        "QA_TOOLS_ENABLED=1 과 DJANGO_ENV=production 은 함께 쓸 수 없습니다 (기술 설계 §10.6)."
    )
if QA_TOOLS_ENABLED:
    # §10.6 ③ 구조적 차단 — 운영 이미지에는 qa/ 가 없으므로 여기서 기동이 거부된다.
    try:
        import qa.qa_settings  # noqa: F401
    except ImportError as exc:  # pragma: no cover - 운영 이미지 전용 경로
        raise ImproperlyConfigured(
            "QA_TOOLS_ENABLED=1 이지만 검증 도구(qa/)가 이 이미지에 없습니다. "
            "운영 이미지에서는 검증 도구를 켤 수 없습니다 (기술 설계 §10.6)."
        ) from exc

# ---------------------------------------------------------------- 보안
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# 프록시 뒤 실제 IP·프로토콜 판정 (기술 설계 §13.1)
TRUSTED_PROXY_COUNT = env_int("TRUSTED_PROXY_COUNT", 0)
if TRUSTED_PROXY_COUNT > 0:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # 기술 설계 §9.5 — 도메인 구조 확인 전 금지
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_AGE = env_int("SESSION_IDLE_MINUTES", 30) * 60
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------------------------------------------------- 사이트
SITE_NAME = env("SITE_NAME", "강남 요가패스")
SITE_BASE_URL = env("SITE_BASE_URL", "http://localhost:8000").rstrip("/")

# ---------------------------------------------------------------- 애플리케이션
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "apps.core",
    "apps.accounts",
    "apps.content",
    "apps.inquiry",
    "apps.mailer",
]

# 검증 도구 앱 등록 (§10.6 ④)
#   · 운영 이미지에는 qa/ 가 **없으므로** 아래 조건이 거짓이 되어
#     `qa_*` 명령이 존재조차 하지 않는다.
#   · 로컬·스테이징 이미지에는 있으므로 등록되고, `QA_TOOLS_ENABLED` 가 꺼져 있으면
#     각 명령이 "이 환경에서는 사용할 수 없습니다" + **종료 코드 2** 로 끝난다(§10.2 공통 행).
if importlib.util.find_spec("qa") is not None:
    INSTALLED_APPS = [*INSTALLED_APPS, "qa"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # --- 프로젝트 공통 레이어 (기술 설계 §5.6 · §6.1 · §9.5)
    "apps.core.middleware.TrailingSlashRedirectMiddleware",
    "apps.core.middleware.AccessControlMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
        },
    },
]

# ---------------------------------------------------------------- 데이터베이스
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "NAME": env("POSTGRES_DB", "yogapass"),
        "USER": env("POSTGRES_USER", "yogapass"),
        "PASSWORD": env("POSTGRES_PASSWORD", ""),
        "CONN_MAX_AGE": 60,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": env_int("PASSWORD_MIN_LENGTH", 10)},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- 국제화·시각
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------- 정적 파일 (기술 설계 §2.6)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
WHITENOISE_MAX_AGE = 31536000  # 해시 파일명 + immutable
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------- URL 규칙 (기술 설계 §6.1)
APPEND_SLASH = False

# ---------------------------------------------------------------- 메일 (기술 설계 §2.5)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", "mail")
EMAIL_PORT = env_int("EMAIL_PORT", 1025)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", False)
EMAIL_TIMEOUT = env_int("EMAIL_TIMEOUT", 10)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@localhost")
INQUIRY_NOTIFY_TO = env_list("INQUIRY_NOTIFY_TO", "ops@localhost")
OPS_ALERT_TO = env_list("OPS_ALERT_TO", "ops@localhost")
OUTBOX_MAX_ATTEMPTS = env_int("OUTBOX_MAX_ATTEMPTS", 5)

# ------------------------------------------- 외부 연동 (미설정이면 해당 기능만 비활성)
MAP_PROVIDER = env("MAP_PROVIDER", "")
MAP_API_KEY = env("MAP_API_KEY", "")
ANALYTICS_ID = env("ANALYTICS_ID", "")

# ---------------------------------------------------------------- 백업 (기술 설계 §12.5)
BACKUP_DIR = env("BACKUP_DIR", "/backups")
BACKUP_KEEP_DAILY = env_int("BACKUP_KEEP_DAILY", 7)
BACKUP_KEEP_WEEKLY = env_int("BACKUP_KEEP_WEEKLY", 4)
BACKUP_KEEP_MONTHLY = env_int("BACKUP_KEEP_MONTHLY", 3)
BACKUP_MIN_FREE_GB = env_int("BACKUP_MIN_FREE_GB", 5)

# ------------------------------------- 개인정보 보관 기간 (항목별 독립 키 — 기술 설계 §7.2)
RETENTION_DAYS = {
    "INQUIRY": env_int("RETENTION_DAYS__INQUIRY", 365),
}

# ---------------------------------------------------------------- 빈도 제한 (기술 설계 §5.3)
RATE_LIMIT = {
    "FORM_WINDOW_MINUTES": env_int("RATE_LIMIT_FORM_WINDOW_MINUTES", 10),
    "FORM_WINDOW_MAX": env_int("RATE_LIMIT_FORM_WINDOW_MAX", 5),
    "FORM_DAY_MAX": env_int("RATE_LIMIT_FORM_DAY_MAX", 20),
}
RATE_LIMIT_SALT = env("RATE_LIMIT_SALT", SECRET_KEY)

# ------------------------------------------- 로깅 (qa R2 #4 — key=value 판정 로그 형식)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "kv": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "kv"},
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
