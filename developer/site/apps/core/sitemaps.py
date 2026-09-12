"""sitemap.xml — 색인 대상 공개 화면만 (기술 설계 §9.3).

절대 URL 은 요청 호스트가 아니라 **SITE_BASE_URL** 로 만든다(§6.1).
도메인 확정 전에는 스테이징 값으로 동작하고 운영 전환 시 값만 바꾼다(재빌드 불필요).
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap


class _BaseUrlSite:
    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.name = domain


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"

    def items(self) -> list[str]:
        # 작업 5~9 에서 화면이 열릴 때마다 이 목록에 추가한다.
        return ["/"]

    def location(self, item: str) -> str:
        return item

    def priority(self, item: str) -> float:
        return 1.0 if item == "/" else 0.7

    def get_urls(self, page=1, site=None, protocol=None):
        parts = urlsplit(settings.SITE_BASE_URL)
        return super().get_urls(
            page=page,
            site=_BaseUrlSite(parts.netloc),
            protocol=parts.scheme or "https",
        )
