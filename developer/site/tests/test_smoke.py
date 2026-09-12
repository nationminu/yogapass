"""1단계 구현 스모크 테스트 (URL·상태 코드·공통 레이아웃·CTA 상태 판정)."""

from django.test import SimpleTestCase, TestCase

from apps.core.cta import cta_state
from apps.core.refs import new_display_no


class UrlTests(TestCase):
    def test_home_renders_single_h1(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertEqual(body.count("<h1"), 1)
        self.assertIn('<main id="main" tabindex="-1">', body)
        self.assertIn('class="skip"', body)
        self.assertNotIn("TBD", body)  # REQ-N-023

    def test_unknown_path_returns_real_404(self):
        self.assertEqual(self.client.get("/no-such-page").status_code, 404)

    def test_trailing_slash_redirects_permanently(self):
        response = self.client.get("/location/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/location")

    def test_healthz_is_not_indexed(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertIn("noindex", response["X-Robots-Tag"])

    def test_robots_and_sitemap(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)

    def test_security_headers_present(self):
        response = self.client.get("/")
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_unregistered_view_is_denied_by_default(self):
        """공개 경로표에 없는 경로는 '노출'이 아니라 '거부'가 된다 (REQ-N-036)."""
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)


class CtaStateTests(SimpleTestCase):
    def test_header_and_bar_states(self):
        # 자기 참조가 아닌 화면 + 전화 확정 → H1 / S1(2분할)
        state = cta_state("/", has_phone=True)
        self.assertEqual((state["header"], state["bar"]), ("H1", "S1"))
        self.assertTrue(state["bar_two_up"])

        # 자기 참조가 아닌 화면 + 전화 미확정 → 바 유지, 우측 전폭
        state = cta_state("/", has_phone=False)
        self.assertEqual((state["header"], state["bar"]), ("H1", "S1"))
        self.assertFalse(state["bar_two_up"])
        self.assertTrue(state["show_bar"])

        # 자기 참조 + 전화 확정 → H2 / S2
        self.assertEqual(cta_state("/location", True)["header"], "H2")
        self.assertEqual(cta_state("/location", True)["bar"], "S2")

        # 자기 참조 + 전화 미확정 → H3(미노출) / S3(바 미노출)
        state = cta_state("/location", has_phone=False)
        self.assertEqual((state["header"], state["bar"]), ("H3", "S3"))
        self.assertFalse(state["show_bar"])


class RefTests(SimpleTestCase):
    def test_display_no_format_and_alphabet(self):
        value = new_display_no()
        self.assertRegex(value, r"^YP-[0-9A-HJKMNP-TV-Z]{4}-[0-9A-HJKMNP-TV-Z]{4}$")
        self.assertEqual(len({new_display_no() for _ in range(1000)}), 1000)
