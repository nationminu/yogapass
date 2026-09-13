"""{% icon "phone" %} — SVG 아이콘 인라인 삽입 (기술 설계 §2.6).

· HTTP 요청 0건, currentColor 상속, 기본 aria-hidden="true".
· 파일은 static/icons/<name>.svg (Lucide, ISC).
"""

from __future__ import annotations

import functools
import re
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
def inline_svg(path: str, css_class: str = "", uid: str = "") -> str:
    """static/ 아래의 SVG 를 인라인 삽입한다 (로고 등 currentColor 상속이 필요한 자산).

    `uid` — **같은 SVG 를 한 문서에 두 번 이상 넣을 때 반드시 준다**(DEF-002).
    파일 안의 `id` 와 그 참조(`aria-labelledby`·`href="#…"`·`url(#…)`)에 접미사를 붙여
    문서 안에서 유일하게 만든다. 중복 id 는 HTML 검증 오류이고(REQ-N-016), `aria-labelledby`
    가 문서상 첫 요소만 참조해 **두 번째 로고의 접근 이름이 어긋난다**(REQ-N-006 ④).
    """
    full = Path(settings.BASE_DIR) / "static" / path
    if not full.is_file():
        return ""
    raw = _strip_comments(full.read_text(encoding="utf-8").strip())
    if uid:
        raw = _namespace_ids(raw, uid)
    if css_class:
        raw = raw.replace("<svg", f'<svg class="{css_class}"', 1)
    return mark_safe(raw)  # noqa: S308 - 저장소 내 정적 파일


def _namespace_ids(raw: str, uid: str) -> str:
    """SVG 안의 id 와 그 참조 전부에 `-{uid}` 접미사를 붙인다."""
    ids = re.findall(r'\sid="([^"]+)"', raw)
    for name in dict.fromkeys(ids):  # 중복 제거 · 순서 유지
        new = f"{name}-{uid}"
        raw = raw.replace(f'id="{name}"', f'id="{new}"')
        raw = raw.replace(f'="#{name}"', f'="#{new}"')  # href · xlink:href
        raw = raw.replace(f"url(#{name})", f"url(#{new})")
        # aria-labelledby · aria-describedby 는 공백으로 구분된 토큰 목록이다
        pattern = r'(aria-(?:labelledby|describedby)="[^"]*)\b' + re.escape(name) + r"\b"
        raw = re.sub(pattern, r"\g<1>" + new, raw)
    return raw


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
