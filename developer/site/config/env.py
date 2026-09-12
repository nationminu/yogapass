"""환경 변수 해석 헬퍼.

외부 의존성(django-environ 등)을 쓰지 않는다 — 기술 설계 §2.1 ⑤(의존성 최소).
"""

from __future__ import annotations

import os

from django.core.exceptions import ImproperlyConfigured

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


class _Missing:
    pass


MISSING = _Missing()


def env(name: str, default=MISSING) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        if isinstance(default, _Missing):
            raise ImproperlyConfigured(
                f"환경 변수 {name} 가 설정되지 않았습니다. .env.example 을 참고하세요."
            )
        return default
    return value


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise ImproperlyConfigured(
        f"환경 변수 {name} 의 값 {raw!r} 을(를) 참·거짓으로 해석할 수 없습니다."
    )


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - 설정 오류 경로
        raise ImproperlyConfigured(f"환경 변수 {name} 은(는) 정수여야 합니다: {raw!r}") from exc


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default) or ""
    return [item.strip() for item in raw.split(",") if item.strip()]
