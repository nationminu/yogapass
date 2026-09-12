"""공통 미들웨어 — URL 정규화 · 기본 거부 접근 제어 · 보안 헤더."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponsePermanentRedirect
from django.urls import Resolver404, resolve

from apps.core.access import is_public


class TrailingSlashRedirectMiddleware:
    """후행 슬래시 없는 형태로 통일 (기술 설계 §6.1).

    APPEND_SLASH=False 와 짝이며, 슬래시가 붙은 요청은 301 로 정규 주소로 보낸다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if len(path) > 1 and path.endswith("/") and not path.startswith("/admin/"):
            target = path.rstrip("/") or "/"
            query = request.META.get("QUERY_STRING", "")
            if query:
                target = f"{target}?{query}"
            return HttpResponsePermanentRedirect(target)
        return self.get_response(request)


class AccessControlMiddleware:
    """기본값 거부 (기술 설계 §5.6).

    공개 경로표에 등록되지 않은 경로는 인증된 직원만 접근할 수 있다.
    등록을 잊으면 '노출'이 아니라 '거부'가 된다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if is_public(path):
            return self.get_response(request)
        try:
            resolve(path)
        except Resolver404:
            # 존재하지 않는 경로는 접근 제어가 아니라 404 로 처리한다(REQ-F-060).
            return self.get_response(request)
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff:
            return self.get_response(request)
        raise PermissionDenied("공개 경로로 등록되지 않은 경로입니다.")


class SecurityHeadersMiddleware:
    """CSP · Permissions-Policy · 색인 차단 헤더 (기술 설계 §9.5 · §3.5.1)."""

    def __init__(self, get_response):
        self.get_response = get_response
        frame_src = "'none'"
        if getattr(settings, "MAP_PROVIDER", ""):
            frame_src = settings.MAP_PROVIDER
        self.csp = "; ".join(
            [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self'",
                "img-src 'self' data:",
                "font-src 'self'",
                "connect-src 'self'",
                f"frame-src {frame_src}",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'",
            ]
        )
        self.permissions_policy = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", self.csp)
        response.setdefault("Permissions-Policy", self.permissions_policy)
        if getattr(settings, "FORCE_NOINDEX", False):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
