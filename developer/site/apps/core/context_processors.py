"""템플릿 공통 컨텍스트 — 사이트 설정 · 내비게이션 · CTA 상태."""

from __future__ import annotations

from django.conf import settings

from apps.content.services import nav_items, site_settings
from apps.core.cta import cta_state


def site(request):
    values = site_settings()
    phone = values.get("phone") or ""
    has_phone = bool(phone)
    return {
        "site_name": values.get("name") or settings.SITE_NAME,
        "site_tagline": values.get("tagline") or "",
        "site": values,
        "site_phone": phone,
        "has_phone": has_phone,  # 미확정이면 전화 요소를 어디에도 렌더하지 않는다
        "site_base_url": settings.SITE_BASE_URL,
        "nav_items": nav_items(request.path),
        "cta": cta_state(request.path, has_phone),
        "app_version": settings.APP_VERSION,
        "force_noindex": getattr(settings, "FORCE_NOINDEX", False),
    }
