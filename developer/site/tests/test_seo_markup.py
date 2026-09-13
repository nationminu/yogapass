"""SEO 메타·마크업 회귀 테스트 (P5 1차 결함 DEF-001·002·003·006·010).

여기 있는 테스트는 **다시 같은 결함이 나지 않게 막는 것**이 목적이다.
판정 기준은 전부 승인된 산출물이다 — IA §6.2·§6.3(title·description), REQ-N-016(HTML 검증),
REQ-N-015(CSP 안에서 동작), REQ-F-003 ②(고정 바 없는 화면의 하단 여백).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from apps.content.models import SiteSetting
from apps.core import seo

#: 색인 대상 공개 화면 (경로 → SCR ID)
INDEXED = {
    "/": "SCR-001",
    "/instructors": "SCR-002",
    "/location": "SCR-003",
    "/privacy": "SCR-006",
}
#: `noindex` 화면 — title 은 있어야 하고 description 은 없어야 한다
NOINDEX = {"/nope": "SCR-008"}


def body_of(client, path: str) -> str:
    return client.get(path).content.decode()


class TitleAndDescriptionTests(TestCase):
    """DEF-001 — IA §6.2·§6.3 표와 **문자열 단위**로 일치해야 한다 (REQ-N-010)."""

    def test_title_matches_ia_table_exactly(self):
        for path, screen in {**INDEXED, **NOINDEX}.items():
            with self.subTest(path=path):
                match = re.search(r"<title>(.*?)</title>", body_of(self.client, path), re.S)
                self.assertIsNotNone(match, f"{path} 에 title 이 없다")
                self.assertEqual(match.group(1), seo.TITLES[screen])

    def test_title_pattern_and_separator(self):
        """구분자는 `|` 한 글자이고 브랜드는 '강남 요가패스' 다(IA §6.2)."""
        for screen, value in seo.TITLES.items():
            with self.subTest(screen=screen):
                self.assertIn(seo.SEPARATOR, value)
                self.assertNotIn(" · ", value)
                self.assertIn(seo.BRAND, value)

    def test_titles_are_unique(self):
        titles = [
            re.search(r"<title>(.*?)</title>", body_of(self.client, path), re.S).group(1)
            for path in {**INDEXED, **NOINDEX}
        ]
        self.assertEqual(len(titles), len(set(titles)))

    def test_description_matches_ia_table_exactly(self):
        for path, screen in INDEXED.items():
            with self.subTest(path=path):
                match = re.search(
                    r'<meta name="description" content="([^"]*)"', body_of(self.client, path)
                )
                self.assertIsNotNone(match, f"{path} 에 description 이 없다")
                self.assertEqual(match.group(1), seo.DESCRIPTIONS[screen])

    def test_description_length_is_between_50_and_90(self):
        """길이 판정은 실측(문자 단위)이다 — IA §6.3."""
        for screen, value in seo.DESCRIPTIONS.items():
            with self.subTest(screen=screen, length=len(value)):
                self.assertGreaterEqual(len(value), seo.DESCRIPTION_MIN)
                self.assertLessEqual(len(value), seo.DESCRIPTION_MAX)

    def test_descriptions_are_unique(self):
        values = list(seo.DESCRIPTIONS.values())
        self.assertEqual(len(values), len(set(values)))

    def test_noindex_screen_has_no_description(self):
        for path in NOINDEX:
            with self.subTest(path=path):
                self.assertNotIn('<meta name="description"', body_of(self.client, path))

    def test_local_keywords_on_home_and_location(self):
        """REQ-N-011 — 메인·오시는 길의 메타에 '강남'·'요가' 가 문장 안에 들어 있다."""
        for path in ("/", "/location"):
            with self.subTest(path=path):
                head = body_of(self.client, path).split("</head>")[0]
                title = re.search(r"<title>(.*?)</title>", head, re.S).group(1)
                desc = re.search(r'<meta name="description" content="([^"]*)"', head).group(1)
                for keyword in ("강남", "요가"):
                    self.assertIn(keyword, title)
                    self.assertIn(keyword, desc)

    def test_brand_string_is_not_taken_from_db(self):
        """콘텐츠 적재 상태가 달라도 title 은 IA 표 값이다(DEF-001 원인 ②)."""
        SiteSetting.objects.update_or_create(
            key="name", defaults={"value": "다른 이름", "is_published": True}
        )
        match = re.search(r"<title>(.*?)</title>", body_of(self.client, "/"), re.S)
        self.assertEqual(match.group(1), seo.TITLES["SCR-001"])


class StructuredDataTests(TestCase):
    """DEF-001 ④ · REQ-N-012 — IA §6.4(메인: WebSite / 오시는 길: LocalBusiness)."""

    def blocks(self, path: str) -> list[dict]:
        found = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            body_of(self.client, path),
            re.S,
        )
        return [json.loads(item) for item in found]

    def test_home_has_website_and_localbusiness(self):
        types = [block["@type"] for block in self.blocks("/")]
        self.assertIn("WebSite", types)
        self.assertIn("HealthAndBeautyBusiness", types)

    def test_location_has_localbusiness_only(self):
        types = [block["@type"] for block in self.blocks("/location")]
        self.assertEqual(types, ["HealthAndBeautyBusiness"])

    def test_website_block_is_valid_json_with_brand_name(self):
        website = next(b for b in self.blocks("/") if b["@type"] == "WebSite")
        self.assertEqual(website["name"], seo.BRAND)
        self.assertTrue(website["url"].endswith("/"))


class MarkupRulesTests(TestCase):
    """DEF-002(중복 id) · DEF-003(인라인 style)."""

    ALL_PATHS = [*INDEXED, *NOINDEX]

    def test_no_duplicate_ids(self):
        """중복 id 는 HTML 검증 오류이고 aria-labelledby 참조를 어긋나게 한다(REQ-N-016)."""
        for path in self.ALL_PATHS:
            with self.subTest(path=path):
                ids = re.findall(r'\sid="([^"]+)"', body_of(self.client, path))
                duplicated = {value for value in ids if ids.count(value) > 1}
                self.assertEqual(duplicated, set(), f"{path} 중복 id: {duplicated}")

    def test_logo_titles_are_referenced_by_their_own_svg(self):
        """헤더·푸터 로고가 서로 다른 id 로 자기 title 을 참조한다."""
        body = body_of(self.client, "/")
        pairs = re.findall(r'aria-labelledby="([^"]+)"[^>]*>\s*<title id="([^"]+)"', body)
        self.assertTrue(pairs)
        for labelledby, title_id in pairs:
            self.assertIn(title_id, labelledby.split())

    def test_no_inline_style_attribute(self):
        """CSP 가 `style-src 'self'` 라 인라인 style 은 적용되지 않는다(DEF-003)."""
        for path in self.ALL_PATHS:
            with self.subTest(path=path):
                found = re.findall(r'<[^>]+\sstyle="[^"]*"', body_of(self.client, path))
                self.assertEqual(found, [], f"{path} 인라인 style: {found}")


class FixedBarPaddingTests(TestCase):
    """DEF-006 — 고정 바가 없는 화면에서는 본문 하단 여백도 두지 않는다(REQ-F-003 ②)."""

    def test_self_reference_without_phone_marks_bar_off(self):
        self.assertNotIn('<div class="barwrap">', body_of(self.client, "/location"))
        self.assertIn('data-fixed-bar="off"', body_of(self.client, "/location"))

    def test_other_screens_mark_bar_on(self):
        for path in ("/", "/instructors", "/privacy"):
            with self.subTest(path=path):
                self.assertIn('data-fixed-bar="on"', body_of(self.client, path))

    def test_self_reference_with_phone_marks_bar_on(self):
        SiteSetting.objects.update_or_create(
            key="phone", defaults={"value": "02-000-0000", "is_published": True}
        )
        self.assertIn('data-fixed-bar="on"', body_of(self.client, "/location"))

    def test_stylesheet_clears_padding_when_bar_is_off(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "tokens.css").read_text("utf-8")
        rule = re.search(r'html\[data-fixed-bar="off"\]\s*\{(.*?)\}', css, re.S)
        self.assertIsNotNone(rule, "고정 바 미노출 화면의 여백 해제 규칙이 없다")
        self.assertIn("--body-pad-bottom: 0px", rule.group(1))


class StaticAssetHygieneTests(TestCase):
    """DEF-010 — 배포되는 정적 자산에 작업 중간 파일을 두지 않는다(REQ-N-024)."""

    def test_no_temp_working_files_under_static(self):
        static_dir = Path(settings.BASE_DIR) / "static"
        leftovers = [str(p.relative_to(static_dir)) for p in static_dir.rglob("*TEMP*")]
        self.assertEqual(leftovers, [], f"static/ 안의 작업 파일: {leftovers}")

    def test_dockerignore_excludes_working_copies(self):
        rules = (Path(settings.BASE_DIR) / ".dockerignore").read_text("utf-8").splitlines()
        self.assertIn("assets-work/", rules)
        self.assertIn("*.TEMP-*", rules)


class ViewportMetaTests(TestCase):
    """DEF-011 — G-9 3단 구현 중 ①(viewport 메타)이 전 화면에 있어야 한다.

    근거: REQ-F-003 ⑤-1(Must · 정적 확인 필수 — "전 화면 `<head>` 에
    `interactive-widget=resizes-content` 포함, 누락 0건"), 요구사항 §3.0 G-9,
    `design/03_page-design.md` §2.5.
    ②(WebKit `visualViewport` 폴백)·③(`scroll-padding-bottom`)도 함께 본다 —
    셋 중 하나만 빠져도 G-9 는 성립하지 않는다.
    """

    #: 정본 문자열. 순서·공백까지 이 값이다(`templates/base.html`).
    VIEWPORT = "width=device-width, initial-scale=1, interactive-widget=resizes-content"
    ALL_PATHS = [*INDEXED, *NOINDEX]

    def viewport_of(self, path: str) -> str | None:
        match = re.search(r'<meta name="viewport" content="([^"]*)"', body_of(self.client, path))
        return match.group(1) if match else None

    def test_every_screen_has_interactive_widget_token(self):
        """누락 0건 — 빠진 화면을 전부 모아서 보고한다(REQ-F-003 ⑤-1)."""
        missing = [
            path
            for path in self.ALL_PATHS
            if "interactive-widget=resizes-content" not in (self.viewport_of(path) or "")
        ]
        self.assertEqual(missing, [], f"viewport 메타에 G-9 ① 토큰이 없는 화면: {missing}")

    def test_viewport_content_matches_canonical_string(self):
        for path in self.ALL_PATHS:
            with self.subTest(path=path):
                self.assertEqual(self.viewport_of(path), self.VIEWPORT)

    def test_only_one_viewport_meta_per_page(self):
        """두 개가 있으면 뒤엣것이 이깁니다 — 토큰 없는 쪽이 이기는 사고를 막는다."""
        for path in self.ALL_PATHS:
            with self.subTest(path=path):
                found = re.findall(r'<meta name="viewport"', body_of(self.client, path))
                self.assertEqual(len(found), 1, f"{path} viewport 메타 {len(found)}개")

    def test_standalone_error_templates_also_carry_the_token(self):
        """viewport 메타를 직접 선언하는 템플릿(base.html · 점검 안내)을 전부 훑는다.

        `{% extends %}` 로 base 를 상속하지 않는 독립 화면이 늘어나도 자동으로 대상이 된다.
        """
        templates_dir = Path(settings.BASE_DIR) / "templates"
        standalone = [
            p
            for p in templates_dir.rglob("*.html")
            if "{% extends" not in p.read_text("utf-8")
            and '<meta name="viewport"' in p.read_text("utf-8")
        ]
        self.assertTrue(standalone, "독립 오류 템플릿을 찾지 못했다")
        for path in standalone:
            with self.subTest(template=path.name):
                self.assertIn(f'content="{self.VIEWPORT}"', path.read_text("utf-8"))

    def test_webkit_fallback_and_scroll_padding_are_in_the_bundle(self):
        """G-9 ②③ — 번들에 남아 있는지 같이 본다(DEF-011 티켓 기대 결과 ②③)."""
        base_dir = Path(settings.BASE_DIR)
        script = (base_dir / "static" / "js" / "viewport.js").read_text("utf-8")
        self.assertIn("visualViewport", script)
        self.assertIn("data-vk-fallback", script)

        css = (base_dir / "static" / "css" / "tokens.css").read_text("utf-8")
        self.assertRegex(css, r"scroll-padding-bottom:\s*var\(--scroll-pad-bottom\)")
