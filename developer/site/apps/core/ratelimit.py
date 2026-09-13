"""빈도 제한 — PostgreSQL 테이블 저장 (기술 설계 §5.3 · D-9 / REQ-N-019 · M-3).

· 저장은 **출처 IP 의 솔트 해시**만 한다(원본 IP 미저장 — REQ-N-020).
· 창은 2개다: ① 고정 길이 창(기본 10분 5회) ② 하루 창(기본 20회, Asia/Seoul 자정 경계).
· 차단 지속 시간(§5.3):
    ① 10분 창 초과 → 해당 창의 잔여 시간
    ② 1일 한도 초과 → 익일 00:00(Asia/Seoul)
    둘 다 걸리면 **더 늦은 쪽**을 쓴다.
· Retry-After = ceil(blocked_until − clock.now()) 초, 최소 1.
  clock.now() 를 쓰므로 QA_CLOCK_OFFSET_SECONDS 로 해제까지 판정할 수 있다(§10.3).
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.core import qaflags
from apps.core.clock import now
from apps.core.models import RateLimitCounter

WINDOW_SCOPE = "form"
DAY_SCOPE = "form_day"


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    blocked_until: dt.datetime | None = None

    @property
    def retry_after(self) -> int:
        if not self.blocked_until:
            return 1
        return max(1, math.ceil((self.blocked_until - now()).total_seconds()))


def _window_start(moment: dt.datetime, minutes: int) -> dt.datetime:
    """고정 길이 창의 시작 시각 (UTC 기준 정렬 — 한국은 서머타임이 없어 경계가 흔들리지 않는다)."""
    seconds = minutes * 60
    epoch = int(moment.timestamp())
    return dt.datetime.fromtimestamp(epoch - (epoch % seconds), tz=dt.UTC)


def _day_start(moment: dt.datetime) -> dt.datetime:
    local = timezone.localtime(moment)
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(dt.UTC)


def _next_midnight(moment: dt.datetime) -> dt.datetime:
    return _day_start(moment) + dt.timedelta(days=1)


def _bump(scope: str, identifier_hash: str, window_start: dt.datetime) -> RateLimitCounter:
    """원자적 증가 — 행이 없으면 만들고 있으면 count 를 +1 한다."""
    try:
        with transaction.atomic():
            row, _ = RateLimitCounter.objects.get_or_create(
                scope=scope,
                identifier_hash=identifier_hash,
                window_start=window_start,
                defaults={"count": 0},
            )
    except IntegrityError:  # 동시 생성 경합
        row = RateLimitCounter.objects.get(
            scope=scope, identifier_hash=identifier_hash, window_start=window_start
        )
    RateLimitCounter.objects.filter(pk=row.pk).update(count=F("count") + 1)
    row.refresh_from_db(fields=["count", "blocked_until"])
    return row


def check_form_submission(identifier_hash: str) -> RateLimitDecision:
    """폼 제출 1회를 계상하고 허용 여부를 돌려준다.

    시도 자체를 세므로 **차단된 요청도 계상**된다(연속 시도를 창 안에서 계속 막기 위함).

    검증 전용 `QA_RATE_LIMIT_MODE=off` 는 **계상과 판정 자체를 건너뛴다**(요건 ④ 독립 토글).
    다른 항목(보관 기간·시각 오프셋)과 서로 영향을 주지 않는다.
    """
    if qaflags.rate_limit_disabled():
        return RateLimitDecision(allowed=True)
    config = settings.RATE_LIMIT
    minutes = int(config["FORM_WINDOW_MINUTES"])
    window_max = int(config["FORM_WINDOW_MAX"])
    day_max = int(config["FORM_DAY_MAX"])
    moment = now()

    window_row = _bump(WINDOW_SCOPE, identifier_hash, _window_start(moment, minutes))
    day_row = _bump(DAY_SCOPE, identifier_hash, _day_start(moment))

    # 한도를 넘긴 행에만 blocked_until 을 남긴다 — qa 가 어느 창이 걸렸는지 표에서 바로 본다
    blocks: list[tuple[RateLimitCounter, dt.datetime]] = []
    if window_row.count > window_max:
        blocks.append((window_row, _window_start(moment, minutes) + dt.timedelta(minutes=minutes)))
    if day_row.count > day_max:
        blocks.append((day_row, _next_midnight(moment)))

    if not blocks:
        return RateLimitDecision(allowed=True)

    for row, until in blocks:
        if row.blocked_until != until:
            RateLimitCounter.objects.filter(pk=row.pk).update(blocked_until=until)
    # 둘 다 걸리면 더 늦은 쪽을 쓴다 (§5.3)
    return RateLimitDecision(allowed=False, blocked_until=max(until for _, until in blocks))


# ------------------------------------------------------------------ 사용량 알림 (REQ-N-019)
def _alert_thresholds() -> dict[str, int]:
    """기본 임계값. QA_TOOLS_ENABLED=1 일 때만 QA_* 로 낮출 수 있다(기술 설계 §5.3 · §10.6)."""
    defaults = {"per_source_day": 3, "per_hour": 20, "total_day": 500}
    return qaflags.alert_thresholds(defaults)


def usage_alert_reasons(identifier_hash: str) -> list[str]:
    """임계 초과 사유 목록 (빈 목록이면 알림 대상 아님)."""
    from django.db.models import Sum

    moment = now()
    day_start = _day_start(moment)
    hour_start = moment - dt.timedelta(hours=1)
    limits = _alert_thresholds()
    reasons: list[str] = []

    per_source = RateLimitCounter.objects.filter(
        scope=WINDOW_SCOPE,
        identifier_hash=identifier_hash,
        window_start__gte=day_start,
        blocked_until__isnull=False,
    ).count()
    if per_source >= limits["per_source_day"]:
        reasons.append(f"per_source_day={per_source}/{limits['per_source_day']}")

    per_hour = RateLimitCounter.objects.filter(
        scope=WINDOW_SCOPE, window_start__gte=hour_start, blocked_until__isnull=False
    ).count()
    if per_hour >= limits["per_hour"]:
        reasons.append(f"per_hour={per_hour}/{limits['per_hour']}")

    total = (
        RateLimitCounter.objects.filter(scope=DAY_SCOPE, window_start__gte=day_start).aggregate(
            total=Sum("count")
        )["total"]
        or 0
    )
    if total >= limits["total_day"]:
        reasons.append(f"total_day={total}/{limits['total_day']}")
    return reasons
