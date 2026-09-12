"""{% icon "phone" %} — SVG 아이콘 인라인 삽입 (기술 설계 §2.6).

· HTTP 요청 0건, currentColor 상속, 기본 aria-hidden="true".
· 파일은 static/icons/<name>.svg (Lucide, ISC).
"""

from __future__ import annotations

import functools
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICON_DIR = Path(settings.BASE_DIR) / "static" / "icons"


@functools.lru_cache(maxsize=64)
def _read(name: str) -> str:
    path = ICON_DIR / f"{name}.svg"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


@register.simple_tag
def icon(name: str, css_class: str = "icon", label: str = "") -> str:
    raw = _strip_comments(_read(name))
    if not raw:
        return ""
    attrs = f'class="{css_class}"'
    if label:
        attrs += f' role="img" aria-label="{label}"'
    else:
        attrs += ' aria-hidden="true" focusable="false"'
    return mark_safe(raw.replace("<svg", f"<svg {attrs}", 1))  # noqa: S308 - 저장소 내 정적 파일


@register.simple_tag
def tel_href(number: str) -> str:
    digits = "".join(ch for ch in number if ch.isdigit() or ch == "+")
    return format_html("tel:{}", digits)


@register.simple_tag
def inline_svg(path: str, css_class: str = "") -> str:
    """static/ 아래의 SVG 를 인라인 삽입한다 (로고 등 currentColor 상속이 필요한 자산)."""
    full = Path(settings.BASE_DIR) / "static" / path
    if not full.is_file():
        return ""
    raw = _strip_comments(full.read_text(encoding="utf-8").strip())
    if css_class:
        raw = raw.replace("<svg", f'<svg class="{css_class}"', 1)
    return mark_safe(raw)  # noqa: S308 - 저장소 내 정적 파일


def _strip_comments(raw: str) -> str:
    """자산 파일의 제작 메모(<!-- ... -->)가 HTML 로 새어 나가지 않게 한다.

    (M-5 자체 점검의 '[TBD]' 검색과 REQ-N-023 의 취지)
    """
    while "<!--" in raw:
        start = raw.index("<!--")
        end = raw.find("-->", start)
        if end == -1:
            return raw[:start].rstrip()
        raw = raw[:start] + raw[end + 3 :]
    return raw
