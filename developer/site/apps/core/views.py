"""공개 화면 · 헬스체크 · robots (기술 설계 §6.2).

화면 매핑
· SCR-001 메인       → home()        → pages/home.html
· SCR-008 404        → page_not_found
· SCR-009 5xx        → server_error
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from apps.content.services import featured_instructors, lesson_types, site_settings

logger = logging.getLogger("core")


def home(request):
    """SCR-001 메인. 섹션 3·4 는 데이터가 없으면 렌더하지 않는다(조건부 렌더)."""
    context = {
        "meta_title": None,  # base.html 이 SITE_NAME 기본 패턴을 쓴다
        "meta_description": (
            "강남 요가 스튜디오 요가패스의 위치와 수업 안내, 문의 방법을 안내합니다."
        ),
        "canonical_path": "/",
        "lesson_types": lesson_types(),
        "instructors": featured_instructors(limit=3),
        "features": site_settings().get("features") or [],
        "page_id": "home",
    }
    return render(request, "pages/home.html", context)


@never_cache
def healthz(request):
    """컨테이너 헬스체크·배포 확인 전용 (기술 설계 §3.4).

    ⚠ 호출은 항상 앱에 직접 한다 — nginx 를 경유하지 않는다(devops R2 #3).
    개인정보·버전 정보를 노출하지 않는다.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001
        logger.exception("healthz.db_error")
        return HttpResponse("db error", status=503, content_type="text/plain; charset=utf-8")
    response = HttpResponse("ok", content_type="text/plain; charset=utf-8")
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def robots_txt(request):
    """Disallow 규칙 0건 + Sitemap 위치 1줄 (IA §6.5)."""
    if getattr(settings, "FORCE_NOINDEX", False):
        body = "User-agent: *\nDisallow: /\n"
    else:
        body = f"User-agent: *\nDisallow:\n\nSitemap: {settings.SITE_BASE_URL}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def page_not_found(request, exception=None):
    """SCR-008 — 실제 404 상태 코드로 응답한다(REQ-F-060)."""
    context = {"page_id": "error-404", "meta_title": "페이지를 찾을 수 없습니다", "noindex": True}
    return render(request, "errors/404.html", context, status=404)


def server_error(request):
    """SCR-009 — 전용 오류 화면."""
    context = {
        "page_id": "error-500",
        "meta_title": "일시적인 오류가 발생했습니다",
        "noindex": True,
    }
    return render(request, "errors/500.html", context, status=500)


def permission_denied(request, exception=None):
    context = {"page_id": "error-404", "meta_title": "페이지를 찾을 수 없습니다", "noindex": True}
    return render(request, "errors/404.html", context, status=404)
