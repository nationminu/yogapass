"""아웃박스 플러시 — 스케줄러가 1분마다 실행한다 (기술 설계 §2.5 · §3.3)."""

from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.core.management.base import BaseCommand

from apps.core.clock import now
from apps.core.jobs import run_job
from apps.mailer.models import Outbox

BACKOFF_MINUTES = [1, 5, 15, 60, 240]


class Command(BaseCommand):
    help = "mailer_outbox 의 대기 메일을 SMTP 로 발송하고 결과를 기록한다."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options) -> None:
        limit = options["limit"]
        dry = options["dry_run"]
        with run_job("send_outbox") as job:
            if job.skipped:
                self.stdout.write("이미 실행 중이라 건너뜁니다.")
                return
            pending = list(
                Outbox.objects.filter(
                    status=Outbox.Status.QUEUED, scheduled_at__lte=now()
                ).order_by("scheduled_at")[:limit]
            )
            if dry:
                job.note(f"dry_run pending={len(pending)}")
                self.stdout.write(f"대기 {len(pending)}건 (발송하지 않음)")
                return
            sent = failed = 0
            connection = get_connection(fail_silently=False)
            for row in pending:
                row.attempts += 1
                try:
                    EmailMessage(
                        subject=row.subject,
                        body=row.body_text,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[row.to_addr],
                        connection=connection,
                    ).send()
                except Exception as exc:  # noqa: BLE001 - 실패를 기록하고 재시도한다
                    row.last_error = str(exc)[:1000]
                    if row.attempts >= settings.OUTBOX_MAX_ATTEMPTS:
                        row.status = Outbox.Status.FAILED
                    else:
                        index = min(row.attempts - 1, len(BACKOFF_MINUTES) - 1)
                        row.scheduled_at = now() + dt.timedelta(minutes=BACKOFF_MINUTES[index])
                    failed += 1
                else:
                    row.status = Outbox.Status.SENT
                    row.sent_at = now()
                    row.last_error = ""
                    sent += 1
                row.save()
            job.note(f"sent={sent} failed={failed} scanned={len(pending)}")
            self.stdout.write(self.style.SUCCESS(f"send_outbox sent={sent} failed={failed}"))
