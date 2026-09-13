import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("core")


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "공통"

    def ready(self) -> None:
        """기동 로그 — qa 가 **밖에서** 환경 상태를 확인하는 증거다 (기술 설계 §10.2 · §10.6 ①)."""
        if not getattr(settings, "QA_TOOLS_ENABLED", False):
            logger.info("QA_TOOLS: off")
            return
        # §3.5.1 ② — 검증 도구가 켜진 환경은 인증 뒤에 있어야 한다.
        logger.warning("QA_TOOLS: ON — 이 환경은 인증 뒤에 있어야 합니다")

        from apps.core import qaflags

        offset = qaflags.clock_offset_seconds()
        if offset:
            logger.warning("CLOCK OFFSET: %ss", offset)
        injected = sorted(t for t in ("smtp", "backup", "purge") if qaflags.fail_injected(t))
        if injected:
            logger.warning("QA_FAIL_INJECT: 기동 시점 주입 대상 = %s", ",".join(injected))
