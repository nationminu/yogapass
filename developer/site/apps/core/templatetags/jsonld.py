"""JSON-LD 값 이스케이프 필터."""

from __future__ import annotations

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="json_script_safe")
def json_script_safe(value) -> str:
    text = json.dumps(str(value), ensure_ascii=False)
    return mark_safe(text.replace("<", "\u003c").replace(">", "\u003e"))  # noqa: S308
