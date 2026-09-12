"""로컬 개발 설정 — runserver + 바인드 마운트 + Mailpit."""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR  # noqa: F401

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "app", "0.0.0.0", "[::1]"]  # noqa: S104 - 로컬 컨테이너 전용
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
