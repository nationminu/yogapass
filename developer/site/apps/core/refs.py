"""외부 식별자 생성 (기술 설계 §5.5).

· URL 식별자: UUID v4
· 사용자 표시 번호: YP-XXXX-XXXX (Crockford Base32 8자 = 40비트, I·L·O·U 제외)
"""

from __future__ import annotations

import secrets
import uuid

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford: I, L, O, U 제외
_BITS = 40
_CHARS = 8


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


def new_display_no(prefix: str = "YP") -> str:
    """예약번호·신청번호용 표시 번호. 충돌 시 호출 측에서 재생성한다."""
    value = secrets.randbits(_BITS)
    chars = []
    for _ in range(_CHARS):
        chars.append(ALPHABET[value & 0x1F])
        value >>= 5
    body = "".join(reversed(chars))
    return f"{prefix}-{body[:4]}-{body[4:]}"
