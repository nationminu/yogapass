"""운영 설정 — gunicorn + WhiteNoise(압축·해시) + 보안 옵션 강제."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import DEBUG, DJANGO_ENV

if DJANGO_ENV == "production" and DEBUG:
    raise ImproperlyConfigured("DJANGO_ENV=production 에서는 DJANGO_DEBUG 를 켤 수 없습니다.")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

FORCE_NOINDEX = False
