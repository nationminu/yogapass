"""문의 폼 응답 형태 7종 — 기술 설계 §9.6 표가 기대값의 원본이다 (REQ-F-040~046).

표의 5열(상태 코드 · 본문 · DB 저장 · 아웃박스 INSERT · 서버 기록)을 전부 확인한다.
③honeypot 과 ⑤토큰 재사용은 **화면이 ①과 같으므로** 저장·발송 건수와 로그로만 구분된다.
⑦토큰 만료는 v0.4(PM 결정 2026-09-13)에서 ⑤와 분리됐다 — 화면·로그가 모두 다르다.
"""

from __future__ import annotations

import os
import re
from unittest import mock

from django.test import TestCase, override_settings

from apps.content.models import SiteSetting
from apps.inquiry.forms import HONEYPOT_FIELD, MESSAGE_MAX, NAME_MAX
from apps.inquiry.models import Inquiry
from apps.mailer.models import Outbox

URL = "/location"
VALID = {
    "name": "홍길동",
    "phone": "010-1234-5678",
    "message": "수업 시간이 궁금합니다.",
    "consent": "on",
}


class InquiryFormBase(TestCase):
    def token(self) -> str:
        response = self.client.get(URL)
        match = re.search(r'name="submit_token" value="([^"]+)"', response.content.decode())
        assert match, "폼에 submit_token 이 없다"
        return match.group(1)

    def post(self, **overrides):
        data = dict(VALID)
        data["submit_token"] = overrides.pop("submit_token", self.token())
        data.update(overrides)
        return self.client.post(URL, data)


class ResponseFormTests(InquiryFormBase):
    """§9.6 ①~⑤ (⑥은 ServerErrorTests · ⑦은 ExpiredTokenTests)"""

    def test_1_accepted(self):
        with self.assertLogs("core.inquiry", level="INFO") as logs:
            response = self.post()
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("문의가 접수되었습니다.", body)
        self.assertNotIn('id="contact-form"', body)  # 폼을 결과 블록으로 교체한다
        self.assertIn('id="contact-result"', body)
        self.assertIn('role="status"', body)
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertEqual(Outbox.objects.filter(kind=Outbox.Kind.INQUIRY_NOTIFY).count(), 1)
        inquiry = Inquiry.objects.get()
        self.assertEqual(inquiry.status, Inquiry.Status.RECEIVED)
        self.assertEqual(inquiry.phone_norm, "01012345678")  # DB 생성 컬럼
        self.assertTrue(inquiry.source_ip_hash)
        self.assertIsNotNone(inquiry.consent_at)
        joined = "\n".join(logs.output)
        self.assertIn(f"inquiry.created ref={inquiry.public_ref}", joined)
        # 개인정보는 로그에 남기지 않는다
        self.assertNotIn(VALID["name"], joined)
        self.assertNotIn(VALID["phone"], joined)

    def test_1_outbox_body_has_required_fields(self):
        """REQ-F-045 — 본문에 이름·연락처·문의 내용·접수 일시가 있다."""
        self.post()
        mail = Outbox.objects.get(kind=Outbox.Kind.INQUIRY_NOTIFY)
        for expected in (VALID["name"], VALID["phone"], VALID["message"], "접수 일시"):
            self.assertIn(expected, mail.body_text)
        self.assertEqual(mail.status, Outbox.Status.QUEUED)

    def test_2_validation_failure(self):
        with self.assertLogs("core.inquiry", level="INFO") as logs:
            response = self.post(name="", phone="010-12", consent="")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("입력 내용을 확인해 주세요", body)
        self.assertIn('role="alert"', body)
        self.assertIn('tabindex="-1"', body)
        self.assertIn("이름을 입력해 주세요.", body)
        self.assertIn("휴대폰 번호 형식이 올바르지 않습니다.", body)
        self.assertIn("개인정보 수집·이용에 동의해 주세요.", body)
        self.assertIn('aria-invalid="true"', body)
        self.assertIn('id="contact-form"', body)  # 폼이 남아 재제출 가능
        self.assertIn(VALID["message"], body)  # 입력값 보존
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)
        self.assertIn("inquiry.invalid fields=[name,phone,consent]", "\n".join(logs.output))

    def test_2_boundary_lengths(self):
        """경계값 20/21자 · 500/501자 (REQ-F-040)."""
        self.assertEqual(self.post(name="가" * NAME_MAX).status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 1)
        response = self.post(name="가" * (NAME_MAX + 1))
        self.assertIn("입력 내용을 확인해 주세요", response.content.decode())
        response = self.post(message="가" * (MESSAGE_MAX + 1))
        self.assertIn("최대 500자까지 입력할 수 있습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)  # 경계 초과분은 저장되지 않는다

    def test_3_honeypot_looks_like_success(self):
        with self.assertLogs("core.inquiry", level="WARNING") as logs:
            response = self.post(**{HONEYPOT_FIELD: "http://spam.example"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)
        self.assertIn("inquiry.blocked reason=honeypot", "\n".join(logs.output))

    def test_3_screen_is_identical_to_success(self):
        """③은 ①과 화면이 같아야 한다 — 차단 사실을 알리지 않는다(REQ-F-044)."""
        success = self.post().content.decode()
        blocked = self.post(**{HONEYPOT_FIELD: "bot"}).content.decode()
        strip = lambda html: re.sub(r'value="[^"]*"', "", html)  # noqa: E731 - 토큰만 제거
        self.assertEqual(strip(success), strip(blocked))

    @override_settings(
        RATE_LIMIT={"FORM_WINDOW_MINUTES": 10, "FORM_WINDOW_MAX": 2, "FORM_DAY_MAX": 20}
    )
    def test_4_rate_limited(self):
        for _ in range(2):
            self.post()
        with self.assertLogs("core.inquiry", level="WARNING") as logs:
            response = self.post()
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)
        self.assertGreaterEqual(int(response["Retry-After"]), 1)
        body = response.content.decode()
        self.assertIn("문의를 접수하지 못했습니다.", body)
        # 사유(스팸·빈도)를 구분해 알리지 않는다
        self.assertNotIn("빈도", body)
        self.assertNotIn("차단", body)
        self.assertEqual(Inquiry.objects.count(), 2)
        self.assertIn("inquiry.blocked reason=rate_limit", "\n".join(logs.output))
        self.assertIn("scope=form", "\n".join(logs.output))

    @override_settings(
        RATE_LIMIT={"FORM_WINDOW_MINUTES": 10, "FORM_WINDOW_MAX": 1, "FORM_DAY_MAX": 20},
        QA_TOOLS_ENABLED=True,
    )
    def test_4_recovers_after_window(self):
        """429 → (기준 시각을 창 밖으로 밀어) → 200 복귀 (qa R2 #3)."""
        self.post()
        self.assertEqual(self.post().status_code, 429)
        with mock.patch.dict(os.environ, {"QA_CLOCK_OFFSET_SECONDS": str(11 * 60)}):
            self.assertEqual(self.post().status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 2)

    def test_5_concurrent_same_token_does_not_500(self):
        """동시 이중 제출 — 조회를 둘 다 통과해도 UNIQUE 가 막고 화면은 ⑤가 된다.

        실제 동시 요청(qa/concurrency.py --same-token)에서 **500 이 나던 경로**다.
        여기서는 조회를 빈 결과로 만들어(경합 상태 재현) INSERT 충돌을 일으킨다.
        """
        token = self.token()
        self.post(submit_token=token)  # 1회차 저장
        with mock.patch("apps.inquiry.services.find_existing", return_value=""):
            with self.assertLogs("core.inquiry", level="INFO") as logs:
                response = self.post(submit_token=token)
        self.assertEqual(response.status_code, 200)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)  # 저장 1건
        self.assertEqual(Outbox.objects.filter(kind=Outbox.Kind.INQUIRY_NOTIFY).count(), 1)
        self.assertIn("inquiry.duplicate token_state=used", "\n".join(logs.output))

    def test_5_token_reuse_is_silent(self):
        token = self.token()
        self.post(submit_token=token)
        with self.assertLogs("core.inquiry", level="INFO") as logs:
            response = self.post(submit_token=token)
        self.assertEqual(response.status_code, 200)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)  # REQ-F-046 ② 저장 1건
        self.assertEqual(Outbox.objects.count(), 1)  # 알림도 1건
        self.assertIn("inquiry.duplicate token_state=used", "\n".join(logs.output))


class ExpiredTokenTests(InquiryFormBase):
    """⑦ 토큰 만료·부재·변조 — **저장하지 않고 다시 작성하도록 안내**한다 (PM 결정 2026-09-13).

    ⑤(재사용)와 달리 성공 화면을 주지 않는다. 한 번도 저장된 적 없는 제출이기 때문이다.
    """

    NOTICE = "시간이 지나 문의가 접수되지 않았습니다."

    def test_7_missing_token_asks_to_rewrite(self):
        with self.assertLogs("core.inquiry", level="INFO") as logs:
            response = self.post(submit_token="")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(self.NOTICE, body)
        self.assertNotIn("문의가 접수되었습니다.", body)  # ⑤와 구분된다
        self.assertIn('id="contact-form"', body)  # 폼이 다시 보인다
        self.assertIn('role="alert"', body)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)
        self.assertIn("inquiry.expired token_state=missing ref=none", "\n".join(logs.output))

    def test_7_expired_token_preserves_input_and_issues_new_token(self):
        with mock.patch("apps.inquiry.services.TOKEN_MAX_AGE", -1):
            with self.assertLogs("core.inquiry", level="INFO") as logs:
                response = self.post()
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.NOTICE, body)
        # 입력값 보존 — 이름·전화·문의 내용이 폼에 그대로 있다
        self.assertIn(f'value="{VALID["name"]}"', body)
        self.assertIn(f'value="{VALID["phone"]}"', body)
        self.assertIn(VALID["message"], body)
        self.assertIn("checked", body)  # 동의 체크도 유지
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)
        self.assertIn("inquiry.expired token_state=expired ref=none", "\n".join(logs.output))

    def test_7_invalid_token_is_logged_separately(self):
        with self.assertLogs("core.inquiry", level="INFO") as logs:
            response = self.post(submit_token="tampered.value.here")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.NOTICE, response.content.decode())
        self.assertIn("inquiry.expired token_state=invalid ref=none", "\n".join(logs.output))

    def test_7_resubmit_with_the_new_token_is_accepted_once(self):
        """재작성 안내 화면의 새 토큰으로 다시 제출하면 정상 접수된다(저장 1건)."""
        with mock.patch("apps.inquiry.services.TOKEN_MAX_AGE", -1):
            body = self.post().content.decode()
        match = re.search(r'name="submit_token" value="([^"]+)"', body)
        assert match, "재작성 안내 화면에 새 submit_token 이 없다"
        response = self.post(submit_token=match.group(1))
        self.assertEqual(response.status_code, 200)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertEqual(Outbox.objects.filter(kind=Outbox.Kind.INQUIRY_NOTIFY).count(), 1)

    def test_7_validation_error_takes_precedence(self):
        """검증 실패가 먼저다 — 만료 토큰 + 빈 이름이면 ②(오류 요약)가 나온다."""
        response = self.post(submit_token="", name="")
        body = response.content.decode()
        self.assertIn("입력 내용을 확인해 주세요", body)
        self.assertNotIn(self.NOTICE, body)


class ServerErrorTests(InquiryFormBase):
    """⑥ 서버 오류 — 500 + 전용 오류 화면, 저장·발송 0건(같은 트랜잭션 롤백)."""

    def test_6_server_error(self):
        self.client.raise_request_exception = False
        with mock.patch(
            "apps.inquiry.services.Inquiry.objects.create", side_effect=RuntimeError("boom")
        ):
            response = self.post()
        self.assertEqual(response.status_code, 500)
        body = response.content.decode()
        self.assertIn("일시적으로 문제가 발생했습니다", body)
        self.assertIn("noindex", body)
        self.assertNotIn("boom", body)  # 스택 트레이스·내부 정보 미노출
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)


class UsageAlertTests(InquiryFormBase):
    """REQ-N-019 사용량 알림 — 임계 초과 시 운영자 메일 1통."""

    @override_settings(
        RATE_LIMIT={"FORM_WINDOW_MINUTES": 10, "FORM_WINDOW_MAX": 1, "FORM_DAY_MAX": 20},
        QA_TOOLS_ENABLED=True,
    )
    def test_alert_enqueued_once(self):
        with mock.patch.dict(os.environ, {"QA_RATE_LIMIT_ALERT_PER_SOURCE_DAY": "1"}):
            self.post()
            self.post()  # 차단 1회 → 임계 도달
            self.post()  # 두 번째 차단 — 알림은 1시간에 1통
        self.assertEqual(Outbox.objects.filter(kind=Outbox.Kind.RATE_LIMIT_ALERT).count(), 1)


class NoScriptAndAccessibilityTests(TestCase):
    def test_form_page_has_noscript_and_honeypot_offscreen(self):
        body = self.client.get(URL).content.decode()
        self.assertIn("<noscript>", body)
        self.assertIn(f'name="{HONEYPOT_FIELD}"', body)
        self.assertIn('class="hp"', body)  # display:none 이 아니라 화면 밖 배치
        self.assertIn('tabindex="-1" autocomplete="off"', body)

    def test_required_marks_are_not_color_only(self):
        body = self.client.get(URL).content.decode()
        self.assertEqual(body.count('class="req-text">(필수)'), 4)  # 3필드 + 동의
        self.assertEqual(body.count("required"), 4)

    def test_privacy_link_opens_in_new_tab_with_notice(self):
        body = self.client.get(URL).content.decode()
        self.assertIn('href="/privacy" target="_blank" rel="noopener noreferrer"', body)
        self.assertIn("(새 창 열림)", body)

    def test_consent_text_has_items_purpose_and_retention(self):
        body = self.client.get(URL).content.decode()
        self.assertIn("수집 항목: 이름, 휴대폰 번호, 문의 내용", body)
        self.assertIn("목적: 문의 답변", body)
        self.assertIn("보관 기간: 1년", body)  # D-19 잠정값

    def test_map_button_hidden_until_service_confirmed(self):
        """지도 서비스 미확정 상태에서 버튼을 렌더하지 않고 오류도 노출하지 않는다."""
        body = self.client.get(URL).content.decode()
        self.assertNotIn("지도 불러오기", body)
        self.assertNotIn("불러오지 못했습니다", body)

    def test_map_button_appears_when_embed_url_confirmed(self):
        SiteSetting.objects.create(
            key="map_embed_url", value="https://map.example/embed", is_published=True
        )
        SiteSetting.objects.create(key="map_service_name", value="지도 서비스", is_published=True)
        body = self.client.get(URL).content.decode()
        self.assertIn("지도 불러오기", body)
        self.assertIn('data-map-src="https://map.example/embed"', body)
        self.assertIn("지도를 불러오면 지도 서비스으로 연결됩니다.", body)


class ClockOffsetTokenExpiryTests(InquiryFormBase):
    """DEF-008 — `QA_CLOCK_OFFSET_SECONDS` 가 submit_token 만료 판정에도 적용된다.

    §9.6 ⑦의 `token_state=expired` 를 **검증 환경에서 실제로 유발할 수 있는지**를 본다.
    (종전에는 `TOKEN_MAX_AGE` 를 직접 패치해야만 재현할 수 있어 qa 가 판정할 수 없었다.)
    """

    OFFSET_25H = {"QA_CLOCK_OFFSET_SECONDS": "90000"}  # +25시간

    @override_settings(QA_TOOLS_ENABLED=True)
    def test_offset_beyond_ttl_expires_the_token(self):
        token = self.token()  # 실제 시각에 발급
        with mock.patch.dict(os.environ, self.OFFSET_25H):
            with self.assertLogs("core.inquiry", level="INFO") as logs:
                response = self.post(submit_token=token)
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("시간이 지나 문의가 접수되지 않았습니다.", body)
        self.assertIn('id="contact-form"', body)  # 폼 재렌더(입력값 보존)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertEqual(Outbox.objects.count(), 0)
        self.assertIn("inquiry.expired token_state=expired ref=none", "\n".join(logs.output))

    @override_settings(QA_TOOLS_ENABLED=True)
    def test_offset_inside_ttl_keeps_the_token_valid(self):
        token = self.token()
        with mock.patch.dict(os.environ, {"QA_CLOCK_OFFSET_SECONDS": "3600"}):  # +1시간
            response = self.post(submit_token=token)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)

    @override_settings(QA_TOOLS_ENABLED=False)
    def test_offset_is_ignored_without_the_master_switch(self):
        """운영 이미지에는 해석기가 없다 — 오프셋 변수가 있어도 동작이 같다(§10.6)."""
        token = self.token()
        with mock.patch.dict(os.environ, self.OFFSET_25H):
            response = self.post(submit_token=token)
        self.assertIn("문의가 접수되었습니다.", response.content.decode())
        self.assertEqual(Inquiry.objects.count(), 1)
