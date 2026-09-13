"""검증 전용 설정에 접근하는 **얇은 창구** (기술 설계 §10.6).

애플리케이션 코드는 `QA_*` 환경 변수를 직접 읽지 않고 이 모듈만 부른다.

구조적 안전장치
  · 해석기 본체(`qa/qa_settings.py`)는 **운영 이미지에 존재하지 않는다.**
  · `QA_TOOLS_ENABLED` 가 꺼져 있으면 해석기를 import 조차 하지 않는다.
  · 켜져 있는데 해석기가 없으면 **기동 시점에 거부된다**(`config/settings/base.py`).
    따라서 런타임에 이 모듈이 조용히 기본값으로 넘어가는 경로는 없다.
"""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger("core.qa")

_WARNED: set[str] = set()


def enabled() -> bool:
    return bool(getattr(settings, "QA_TOOLS_ENABLED", False))


def _interpreter():
    if not enabled():
        return None
    from qa import qa_settings  # 기동 시점에 존재가 보장된다(§10.6 ③)

    return qa_settings


def clock_offset_seconds() -> int:
    module = _interpreter()
    return module.clock_offset_seconds() if module else 0


def fail_injected(target: str) -> bool:
    """실패 주입 여부. 주입이 걸리면 **로그 1줄**로 알린다(거짓 실패와 구분 — §10.2)."""
    module = _interpreter()
    if not module:
        return False
    if target in module.fail_inject():
        if target not in _WARNED:  # 프로세스당 1줄만 남긴다(§10.2)
            _WARNED.add(target)
            logger.warning("QA_FAIL_INJECT: %s 주입됨", target)
        return True
    return False


def retention_minutes(key: str) -> int | None:
    module = _interpreter()
    return module.retention_minutes(key) if module else None


def rate_limit_disabled() -> bool:
    module = _interpreter()
    return module.rate_limit_disabled() if module else False


def alert_thresholds(defaults: dict[str, int]) -> dict[str, int]:
    module = _interpreter()
    return module.alert_thresholds(defaults) if module else dict(defaults)


def session_token() -> str:
    module = _interpreter()
    return module.session_token() if module else ""
