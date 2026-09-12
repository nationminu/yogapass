"""화면이 쓰는 콘텐츠 조회 계층.

DB 가 아직 비어 있거나(마이그레이션 전) 테이블이 없더라도 화면이 죽지 않게 한다.
"""

from __future__ import annotations

import logging

from django.db import DatabaseError

from apps.content.models import Instructor, LessonType, SiteSetting

logger = logging.getLogger("content")

NAV = [
    ("홈", "/"),
    ("강사 소개", "/instructors"),
    ("오시는 길", "/location"),
    ("문의하기", "/location#contact"),
]


def site_settings() -> dict:
    """확정(is_published=True) 된 값만 돌려준다 — 미확정 항목은 키 자체가 없다."""
    try:
        rows = SiteSetting.objects.filter(is_published=True)
        return {row.key: row.value for row in rows}
    except DatabaseError:
        logger.warning("content.settings_unavailable reason=db")
        return {}


def lesson_types() -> list[LessonType]:
    try:
        return list(LessonType.objects.filter(is_active=True).exclude(description=""))
    except DatabaseError:
        return []


def featured_instructors(limit: int = 3) -> list[Instructor]:
    try:
        return list(Instructor.objects.filter(is_active=True)[:limit])
    except DatabaseError:
        return []


def nav_items(current_path: str) -> list[dict]:
    items = []
    for label, url in NAV:
        base = url.split("#")[0]
        is_current = base == current_path and "#" not in url
        items.append({"label": label, "url": url, "is_current": is_current})
    return items


def all_instructors() -> list[Instructor]:
    """SCR-002 전체 목록 — 비활성 강사는 공개 목록에서 제외한다(REQ-F-020)."""
    try:
        return list(Instructor.objects.filter(is_active=True))
    except DatabaseError:
        return []
