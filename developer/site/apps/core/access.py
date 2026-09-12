"""공개 경로 등록표 — 기본값은 "거부"다 (기술 설계 §5.6 / REQ-N-036).

여기에 등록되지 않은 경로는 **노출이 아니라 접근 거부**가 된다.
2차(회원·관리자)에서는 소유자 검사를 조회 계층에서 추가한다.
"""

from __future__ import annotations

import re

# 1차 공개 경로 (정규식, 경로 전체 일치)
PUBLIC_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^/$"),
    re.compile(r"^/instructors$"),
    re.compile(r"^/location$"),
    re.compile(r"^/privacy$"),
    re.compile(r"^/healthz$"),
    re.compile(r"^/robots\.txt$"),
    re.compile(r"^/sitemap\.xml$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/static/.*$"),
    re.compile(r"^/media/.*$"),
]


def is_public(path: str) -> bool:
    return any(pattern.match(path) for pattern in PUBLIC_PATTERNS)
