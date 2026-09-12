"""URL 규칙 — 후행 슬래시 없는 형태로 통일 (기술 설계 §6.1)."""

from django.contrib.sitemaps.views import sitemap
from django.urls import path

from apps.core import views
from apps.core.sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap()}

urlpatterns = [
    path("", views.home, name="home"),
    path("instructors", views.instructors, name="instructors"),
    path("location", views.location, name="location"),
    path("privacy", views.privacy, name="privacy"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
handler403 = "apps.core.views.permission_denied"
