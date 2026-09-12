"""단일 시각 진입점 (기술 설계 §5.0 · §10.3).

애플리케이션 코드는 django.utils.timezone.now() 를 직접 부르지 않고
반드시 이 모듈의 now() 를 쓴다. 검증 시 기준 시각을 한 곳에서 밀 수 있다.
"""

from __future__ import annotations

import datetime as _dt
import logging
import os

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("core.clock")

_LOGGED = False


def _offset_seconds() -> int:
    if not getattr(settings, "QA_TOOLS_ENABLED", False):
        return 0
    raw = os.environ.get("QA_CLOCK_OFFSET_SECONDS", "0").strip()
    try:
        return int(raw)
    except ValueError:
        logger.warning("clock.offset_invalid value=%s", raw)
        return 0


def now() -> _dt.datetime:
    offset = _offset_seconds()
    value = timezone.now()
    if offset:
        global _LOGGED
        if not _LOGGED:
            logger.warning("clock.offset_applied seconds=%s", offset)
            _LOGGED = True
        value = value + _dt.timedelta(seconds=offset)
    return value


def today() -> _dt.date:
    return timezone.localtime(now()).date()
