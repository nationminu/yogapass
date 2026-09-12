"""출처 IP 판정과 해시 (기술 설계 §13.1 · §5.3).

TRUSTED_PROXY_COUNT 만큼만 X-Forwarded-For 오른쪽에서 건너뛴다.
값이 0이면 REMOTE_ADDR 만 신뢰한다(프록시 스푸핑 방지).
"""

from __future__ import annotations

import hashlib

from django.conf import settings


def client_ip(request) -> str:
    count = int(getattr(settings, "TRUSTED_PROXY_COUNT", 0) or 0)
    if count <= 0:
        return request.META.get("REMOTE_ADDR", "") or ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    parts = [part.strip() for part in forwarded.split(",") if part.strip()]
    if not parts:
        return request.META.get("REMOTE_ADDR", "") or ""
    index = len(parts) - count
    if index < 0:
        index = 0
    return parts[index]


def ip_hash(value: str) -> str:
    """원본 IP 를 저장하지 않는다 — 솔트 해시만 남긴다(REQ-N-020)."""
    salt = getattr(settings, "RATE_LIMIT_SALT", "")
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:32]
