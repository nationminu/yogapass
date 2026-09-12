"""공개 화면 · 헬스체크 · robots (기술 설계 §6.2).

화면 매핑
· SCR-001 메인             → home()         → pages/home.html
· SCR-002 요가 강사 소개    → instructors()  → pages/instructors.html
· SCR-003 오시는 길 + 문의  → location()     → pages/location.html   (GET·POST 동일 URL)
· SCR-006 개인정보 처리방침 → privacy()      → pages/privacy.html
· SCR-008 404              → page_not_found
· SCR-009 5xx              → server_error
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from apps.content.privacy import privacy_document
from apps.content.services import (
    all_instructors,
    featured_instructors,
    lesson_types,
    site_settings,
)
from apps.inquiry.forms import HONEYPOT_FIELD, MESSAGE_MAX, NAME_MAX, InquiryForm
from apps.inquiry.services import TOKEN_FIELD, handle_submission, issue_token

logger = logging.getLogger("core")

#: 오시는 길 정보 목록 — (설정 키, 라벨) 순서가 화면 표시 순서다. 값이 없는 행은 렌더하지 않는다.
LOCATION_ROWS = [
    ("address", "주소"),
    ("subway", "지하철"),
    ("bus", "버스"),
    ("parking", "주차"),
    ("hours", "운영시간"),
    ("closed_days", "휴무일"),
    ("phone", "대표 전화"),
]


def home(request):
    """SCR-001 메인. 섹션 2·3·4 는 데이터가 없으면 렌더하지 않는다(조건부 렌더)."""
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


def instructors(request):
    """SCR-002 — 인원 수에 따라 그리드 열 수를 맞춘다(빈 칸 방치 금지, 페이지 디자인 §3.2)."""
    people = all_instructors()
    count = len(people)
    if count == 1:
        grid_class = "g-1c"
    elif count == 2:
        grid_class = "g-2c"
    else:
        grid_class = "g-3"
    context = {
        "meta_title": "요가 강사 소개",
        "meta_description": "요가패스에서 수업을 진행하는 강사와 담당 수업을 소개합니다.",
        "canonical_path": "/instructors",
        "instructors": people,
        "grid_class": grid_class,
        "page_id": "instructors",
    }
    return render(request, "pages/instructors.html", context)


def _retention_label(values: dict) -> str:
    """동의 문구의 보관 기간 표기 (REQ-F-043).

    고객 확정값이 있으면 그대로 쓰고, 없으면 **§8.5 D-19 잠정값**(settings.RETENTION_DAYS)을 쓴다.
    요구사항이 "보관 기간 값은 D-19 잠정값"으로 정해 두었으므로 공개 화면에 [TBD] 를 내지 않는다.
    """
    confirmed = values.get("retention_inquiry_label")
    if confirmed:
        return str(confirmed)
    days = int(settings.RETENTION_DAYS.get("INQUIRY", 365))
    if days % 365 == 0:
        return f"{days // 365}년"
    return f"{days}일"


def _location_context(request):
    values = site_settings()
    rows = [
        {"key": key, "label": label, "value": values.get(key)}
        for key, label in LOCATION_ROWS
        if values.get(key)
    ]
    return {
        "meta_title": "오시는 길",
        "meta_description": ("강남 요가패스의 위치와 찾아오시는 방법, 문의하기를 안내합니다."),
        "canonical_path": "/location",
        "page_id": "location",
        "info_rows": rows,
        "map_service_name": values.get("map_service_name") or "",
        "map_embed_url": values.get("map_embed_url") or "",
        "map_directions_url": values.get("map_directions_url") or "",
        "retention_label": _retention_label(values),
        "honeypot_field": HONEYPOT_FIELD,
        "token_field": TOKEN_FIELD,
        "name_max": NAME_MAX,
        "message_max": MESSAGE_MAX,
    }


@csrf_protect
def location(request):
    """SCR-003 — 오시는 길 + 문의 폼. 응답 형태 6종은 기술 설계 §9.6 표가 원본이다."""
    context = _location_context(request)

    if request.method == "POST":
        result = handle_submission(request)
        context.update(
            {
                "form": result.form or InquiryForm(),
                "result_state": result.result_state,
                "show_form": result.show_form,
                "submit_token": result.submit_token,
                "retry_after": result.retry_after,
                "submitted": True,
            }
        )
        response = render(request, "pages/location.html", context, status=result.status_code)
        for header, value in result.extra_headers.items():
            response[header] = value
        return response

    context.update(
        {
            "form": InquiryForm(),
            "result_state": None,
            "show_form": True,
            "submit_token": issue_token(),
            "submitted": False,
        }
    )
    return render(request, "pages/location.html", context)


def privacy(request):
    """SCR-006 — 본문은 content/privacy.yml 이 단일 원본이다(기술 설계 §6.2)."""
    document = privacy_document()
    context = {
        "meta_title": "개인정보 처리방침",
        "meta_description": (
            "요가패스가 수집하는 개인정보의 항목과 이용 목적, 보관 기간, 파기 절차를 안내합니다."
        ),
        "canonical_path": "/privacy",
        "page_id": "privacy",
        "document": document,
    }
    return render(request, "pages/privacy.html", context)


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
    """SCR-009 — 전용 오류 화면. DB 장애 상태에서도 렌더되므로 동적 데이터에 의존하지 않는다."""
    context = {
        "page_id": "error-500",
        "meta_title": "일시적인 오류가 발생했습니다",
        "noindex": True,
    }
    return render(request, "errors/500.html", context, status=500)


def permission_denied(request, exception=None):
    context = {"page_id": "error-404", "meta_title": "페이지를 찾을 수 없습니다", "noindex": True}
    return render(request, "errors/404.html", context, status=404)
