"""검증 전용 설정 해석기 (기술 설계 §10.2 · §10.6).

· **항목별 독립 토글**이다 — 단일 "검증 모드 스위치"를 만들지 않는다(qa R1 #4).
· 여기 있는 어떤 값도 `QA_TOOLS_ENABLED=1` 이 아닌 환경에서는 읽히지 않는다.
  (마스터 스위치 판정은 `config/settings/base.py` 와 `apps/core/qaflags.py` 가 한다.)
· 이 모듈은 **django.conf.settings 를 import 하지 않는다** — 설정 로딩 중에 import 되기 때문이다.

해석하는 환경 변수

    QA_CLOCK_OFFSET_SECONDS          기준 시각 오프셋(초, **음수 허용**)            요건 ⑩
    QA_FAIL_INJECT                   smtp,backup,purge 콤마 목록(독립 토글)         요건 ⑨
    QA_RETENTION_MINUTES__<KEY>      보관 기간을 '분' 단위로 단축 (예: __INQUIRY)   요건 ④
    QA_RATE_LIMIT_MODE               off 이면 빈도 제한을 적용하지 않는다           요건 ④
    QA_RATE_LIMIT_ALERT_*            사용량 알림 임계값 하향                        요건 ④
    QA_SESSION_TOKEN                 qa_session 명령 사용 조건                      요건 ⑦
"""

from __future__ import annotations

import os

#: 실패 주입 대상 (§10.2 — 3종 독립 토글)
FAIL_INJECT_TARGETS = {"smtp", "backup", "purge"}


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def clock_offset_seconds() -> int:
    """기준 시각 오프셋. 음수(과거로 이동)를 허용한다."""
    raw = _env("QA_CLOCK_OFFSET_SECONDS", "0")
    try:
        return int(raw)
    except ValueError:
        return 0


def fail_inject() -> set[str]:
    """주입할 실패 대상 집합. 알 수 없는 이름은 무시한다."""
    raw = _env("QA_FAIL_INJECT")
    return {item.strip().lower() for item in raw.split(",") if item.strip()} & FAIL_INJECT_TARGETS


def retention_minutes(key: str) -> int | None:
    """보관 기간 단축값(분). 없으면 None → 운영 값(일 단위)을 그대로 쓴다."""
    raw = _env(f"QA_RETENTION_MINUTES__{key.upper()}")
    return int(raw) if raw.isdigit() else None


def rate_limit_disabled() -> bool:
    return _env("QA_RATE_LIMIT_MODE").lower() == "off"


def alert_thresholds(defaults: dict[str, int]) -> dict[str, int]:
    """사용량 알림 임계값 하향 (§5.3)."""
    values = dict(defaults)
    for key, name in (
        ("per_source_day", "QA_RATE_LIMIT_ALERT_PER_SOURCE_DAY"),
        ("per_hour", "QA_RATE_LIMIT_ALERT_PER_HOUR"),
        ("total_day", "QA_RATE_LIMIT_ALERT_TOTAL_DAY"),
    ):
        raw = _env(name)
        if raw.isdigit():
            values[key] = int(raw)
    return values


def session_token() -> str:
    return _env("QA_SESSION_TOKEN")
