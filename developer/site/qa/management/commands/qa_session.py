"""요건 ⑦ — 검증 전용 로그인 세션 (기술 설계 §10.1 ⑦).

**1차는 골격이다.** 1차에는 로그인 화면이 없으므로 만들 수 있는 역할은 운영자(staff)뿐이고,
회원 역할(member1·member2)은 2차 회원 기능과 함께 본체를 만든다.

    manage.py qa_session --role staff --token <QA_SESSION_TOKEN 값>

· **HTTP 경로로 노출하지 않는다** — 관리 명령 전용이다(§3.5.1 ②).
· `QA_SESSION_TOKEN` 이 설정되어 있지 않으면 동작하지 않는다(§10.1 ⑦).
· 출력은 쿠키 이름·값·만료다. 스크립트가 이 값을 브라우저·요청에 주입한다.
"""

from __future__ import annotations

import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore

from apps.core import qaflags
from qa.base import QaCommand

ROLES = ("staff", "member1", "member2")
SECOND_PHASE = ("member1", "member2")


class Command(QaCommand):
    help = "검증용 세션을 발급한다 (1차: staff 만)"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--role", choices=ROLES, required=True)
        parser.add_argument("--token", default="", help="QA_SESSION_TOKEN 과 일치해야 한다")

    def handle(self, *args, **options) -> None:
        expected = qaflags.session_token()
        if not expected:
            self.stderr.write("QA_SESSION_TOKEN 이 설정되지 않아 세션을 발급할 수 없습니다.")
            sys.exit(2)
        if options["token"] != expected:
            self.stderr.write("토큰이 일치하지 않습니다.")
            sys.exit(2)

        role = options["role"]
        if role in SECOND_PHASE:
            self.stderr.write(
                f"회원 역할({role})은 2차 회원 기능과 함께 제공됩니다. 1차는 staff 만 발급합니다."
            )
            sys.exit(2)

        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        lookup = {username_field: "qa-staff@example.test"}
        user, created = user_model.objects.get_or_create(
            **lookup, defaults={"is_staff": True, "is_active": True}
        )
        if created:
            user.set_unusable_password()
            user.is_staff = True
            user.save()

        session = SessionStore()
        session["_auth_user_id"] = str(user.pk)
        session["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
        session["_auth_user_hash"] = user.get_session_auth_hash()
        session["qa_session"] = True
        session.create()

        rows = [
            {
                "role": role,
                "user": getattr(user, username_field),
                "cookie_name": settings.SESSION_COOKIE_NAME,
                "cookie_value": session.session_key,
                "expires_in_seconds": settings.SESSION_COOKIE_AGE,
            }
        ]
        self.emit(
            rows,
            ["role", "user", "cookie_name", "cookie_value", "expires_in_seconds"],
            options["format"],
        )
