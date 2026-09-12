"""템플릿 공통 컨텍스트 — 사이트 설정 · 내비게이션 · CTA 상태."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.templatetags.static import static

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
        "og_image": _og_image(),
    }


def _og_image() -> str:
    """OG 대표 이미지 경로 — **래스터 파일이 있을 때만** 돌려준다.

    파일이 없으면 og:image 계열 태그를 통째로 빼고 빌드한다(TKT-DSN-002 · 디자인 시스템 §6.3 ②).
    placeholder 이미지를 만들지 않는다.
    """
    if not (Path(settings.BASE_DIR) / "static" / "img" / "og-image.png").is_file():
        return ""
    return static("img/og-image.png")
