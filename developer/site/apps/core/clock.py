"""단일 시각 진입점 (기술 설계 §5.0 · §10.3).

애플리케이션 코드는 django.utils.timezone.now() 를 직접 부르지 않고
반드시 이 모듈의 now() 를 쓴다. 검증 시 기준 시각을 한 곳에서 밀 수 있다.

오프셋 해석은 `apps.core.qaflags` → `qa/qa_settings.py` 가 한다(§10.6 ②).
운영 이미지에는 해석기가 없으므로 오프셋이 걸릴 수 없다.
"""

from __future__ import annotations

import datetime as _dt
import logging

from django.utils import timezone

from apps.core import qaflags

logger = logging.getLogger("core.clock")

_LOGGED = False


def offset_seconds() -> int:
    """적용 중인 오프셋(초). 음수 허용 — 과거로 이동할 수 있다(§10.2)."""
    return qaflags.clock_offset_seconds()


def now() -> _dt.datetime:
    offset = offset_seconds()
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
