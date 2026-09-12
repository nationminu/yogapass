"""1차 공개 화면 — SCR-002 · 003 · 006 · 008 · 009 와 SEO·접근성 공통 규칙."""

from __future__ import annotations

from django.test import TestCase, override_settings

from apps.content.models import Instructor, SiteSetting

INDEXED_PATHS = ["/", "/instructors", "/location", "/privacy"]


def make_instructors(count: int) -> None:
    for index in range(count):
        Instructor.objects.create(
            slug=f"i{index}",
            name=f"강사{index}",
            headline="담당 수업 안내",
            classes=["그룹 요가"],
            credentials=["자격 1"],
            display_order=index,
        )


class CommonPageRulesTests(TestCase):
    def test_each_page_has_single_h1_and_landmarks(self):
        for path in INDEXED_PATHS:
            with self.subTest(path=path):
                body = self.client.get(path).content.decode()
                self.assertEqual(body.count("<h1"), 1)
                self.assertIn('<main id="main" tabindex="-1">', body)
                self.assertIn('class="skip"', body)
                self.assertIn("<header", body)
                self.assertIn("<footer", body)

    def test_title_description_canonical_and_og(self):
        for path in INDEXED_PATHS:
            with self.subTest(path=path):
                body = self.client.get(path).content.decode()
                self.assertIn("<title>", body)
                self.assertIn('<meta name="description"', body)
                self.assertIn(f'rel="canonical" href="http://localhost:8000{path}"', body)
                self.assertIn('property="og:title"', body)
                self.assertNotIn('name="robots"', body)  # 색인 대상 화면

    def test_tbd_is_not_rendered_on_public_screens(self):
        """REQ-N-023 ① — /privacy 는 고객 확정 전까지 [TBD] 를 **의도적으로** 보인다
        (REQ-F-050 1차 수용 기준). 그 상태의 운영 배포는 manage.py check_release 가 막는다."""
        for path in ["/", "/instructors", "/location"]:
            with self.subTest(path=path):
                self.assertNotIn("TBD", self.client.get(path).content.decode())

    def test_sitemap_contains_only_indexed_pages(self):
        body = self.client.get("/sitemap.xml").content.decode()
        for path in INDEXED_PATHS:
            self.assertIn(f"<loc>http://localhost:8000{path}</loc>", body)
        self.assertNotIn("healthz", body)
        self.assertEqual(body.count("<url>"), len(INDEXED_PATHS))

    def test_robots_has_no_disallow_rule(self):
        body = self.client.get("/robots.txt").content.decode()
        self.assertIn("Disallow:\n", body)
        self.assertNotIn("Disallow: /", body)
        self.assertIn("Sitemap: http://localhost:8000/sitemap.xml", body)

    def test_no_page_leaks_template_comments(self):
        for path in INDEXED_PATHS + ["/nope"]:
            with self.subTest(path=path):
                body = self.client.get(path).content.decode()
                self.assertNotIn("{#", body)
                self.assertNotIn("{%", body)


class InstructorsPageTests(TestCase):
    """SCR-002 — 인원 경계값 0·1·2·3·12명 (REQ-F-021)."""

    def test_empty_state_without_the_word_preparing(self):
        body = self.client.get("/instructors").content.decode()
        self.assertIn("강사 소개는 공개되면 안내드립니다.", body)
        self.assertNotIn("준비 중", body)
        self.assertIn('class="empty"', body)

    def test_grid_columns_follow_headcount(self):
        expectations = {1: "g-1c", 2: "g-2c", 3: "g-3", 12: "g-3"}
        for count, grid in expectations.items():
            with self.subTest(count=count):
                Instructor.objects.all().delete()
                make_instructors(count)
                body = self.client.get("/instructors").content.decode()
                self.assertIn(f'class="grid {grid} card-list"', body)
                self.assertEqual(body.count("card--instructor"), count)

    def test_initial_avatar_is_decorative(self):
        make_instructors(1)
        body = self.client.get("/instructors").content.decode()
        self.assertIn('<div class="avatar" aria-hidden="true">강</div>', body)
        self.assertNotIn("<img", body)  # 인물 스톡 사진 0장


class PrivacyPageTests(TestCase):
    """SCR-006 — 목차 구조는 제작이, 본문은 고객이 확정한다 (REQ-F-050)."""

    def test_toc_items_match_section_headings(self):
        body = self.client.get("/privacy").content.decode()
        titles = [
            "총칙·적용 범위",
            "수집하는 개인정보 항목과 수집 방법",
            "수집·이용 목적",
            "보유·이용 기간과 파기 절차·방법",
            "제3자 제공",
            "개인정보 처리 위탁",
            "정보주체의 권리와 행사 방법",
            "만 14세 미만 아동의 개인정보 처리",
            "개인정보 보호책임자",
            "안전성 확보 조치",
            "시행일·개정 이력",
        ]
        for index, title in enumerate(titles, start=1):
            self.assertIn(f'<a href="#p{index}">{title}</a>', body)
            self.assertIn(f'<h2 id="p{index}">{index}. {title}</h2>', body)

    def test_unconfirmed_sections_show_placeholder(self):
        body = self.client.get("/privacy").content.decode()
        self.assertIn("[TBD: 고객 확인 필요 — T-F]", body)

    def test_tables_carry_labels_for_card_layout(self):
        body = self.client.get("/privacy").content.decode()
        self.assertIn('data-label="수집 항목"', body)
        self.assertIn('data-label="보관 기간"', body)

    def test_toc_works_without_js(self):
        body = self.client.get("/privacy").content.decode()
        self.assertIn('<details class="toc-d" open>', body)

    def test_release_check_blocks_unconfirmed_policy(self):
        """REQ-N-023 ① — 미확정 본문이 남아 있으면 배포 사전 점검이 종료 코드 1 로 끝난다."""
        from django.core.management import call_command

        with self.assertRaises(SystemExit) as raised:
            call_command("check_release")
        self.assertEqual(raised.exception.code, 1)
        # 스테이징은 미확정 본문 그대로 판정해야 하므로 막지 않는다
        call_command("check_release", warn_only=True)

    @override_settings(DJANGO_ENV="production")
    def test_release_warning_is_reported_by_system_check(self):
        from django.core.checks import run_checks

        warnings = [item for item in run_checks() if item.id == "content.W001"]
        self.assertEqual(len(warnings), 1)


class ErrorPageTests(TestCase):
    def test_404_keeps_navigation_and_is_noindex(self):
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)
        body = response.content.decode()
        self.assertIn("요청하신 페이지를 찾을 수 없습니다", body)
        self.assertIn('content="noindex, nofollow"', body)
        self.assertIn('href="/instructors"', body)
        self.assertIn('href="/location"', body)
        self.assertIn("<header", body)
        self.assertIn("<footer", body)

    def test_500_template_renders_without_dynamic_data(self):
        from django.template.loader import render_to_string

        body = render_to_string("errors/500.html", {"noindex": True})
        self.assertIn("일시적으로 문제가 발생했습니다", body)
        self.assertNotIn("TBD", body)


class PhoneDependentRenderingTests(TestCase):
    """대표 전화가 확정되면 전화 요소가 한꺼번에 나타난다 (REQ-F-004 · G-6 ②)."""

    def test_no_tel_links_while_phone_is_unset(self):
        for path in INDEXED_PATHS:
            self.assertNotIn("tel:", self.client.get(path).content.decode())

    def test_tel_links_appear_when_phone_is_confirmed(self):
        SiteSetting.objects.create(key="phone", value="02-000-0000", is_published=True)
        body = self.client.get("/instructors").content.decode()
        self.assertIn("tel:020000000", body)
        # 자기 참조 화면(/location)은 헤더 주 CTA·고정 바가 "전화 문의"로 바뀐다(H2·S2)
        location = self.client.get("/location").content.decode()
        self.assertIn("전화 문의", location)


class InstructorCareerFoldTests(TestCase):
    """경력이 3줄을 넘으면 접는다 (페이지 디자인 §3.1) — JS 없이 동작해야 한다."""

    def _create(self, credentials: list[str]) -> None:
        Instructor.objects.create(slug="a", name="강사", credentials=credentials)

    def test_three_or_fewer_is_not_folded(self):
        self._create(["자격 1", "자격 2", "자격 3"])
        body = self.client.get("/instructors").content.decode()
        self.assertNotIn('<details class="more">', body)

    def test_more_than_three_is_folded_with_details(self):
        self._create(["자격 1", "자격 2", "자격 3", "자격 4"])
        body = self.client.get("/instructors").content.decode()
        self.assertIn('<details class="more">', body)
        self.assertIn("더 보기", body)
        self.assertIn("접기", body)
        self.assertIn("자격 4", body)
        self.assertNotIn("aria-expanded", body)  # <summary> 가 상태를 스스로 노출한다
