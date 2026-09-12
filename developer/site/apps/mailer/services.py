"""아웃박스 적재 헬퍼 — 요청 트랜잭션 안에서 부른다."""

from __future__ import annotations

from apps.core.clock import now
from apps.mailer.models import Outbox


def enqueue(kind, to_addrs, subject, body, *, related_type="", related_ref=""):
    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    rows = [
        Outbox(
            kind=kind,
            to_addr=addr,
            subject=subject,
            body_text=body,
            scheduled_at=now(),
            related_type=related_type,
            related_ref=related_ref,
        )
        for addr in to_addrs
        if addr
    ]
    return Outbox.objects.bulk_create(rows)
