import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("core")


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "공통"

    def ready(self) -> None:
        # 기술 설계 §3.5.1 ② — 검증 도구가 켜진 환경은 인증 뒤에 있어야 한다.
        if getattr(settings, "QA_TOOLS_ENABLED", False):
            logger.warning("QA_TOOLS: ON — 이 환경은 인증 뒤에 있어야 합니다")
