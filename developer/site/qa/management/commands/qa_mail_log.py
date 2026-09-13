"""요건 ② — 발송 로그 조회 (기술 설계 §10.2).

    manage.py qa_mail_log [--kind ...] [--since ISO8601] [--format table|json]

**요청 시각(`scheduled_at`)과 발송 시각(`sent_at`)이 모두 보인다** — M-8 판정
("로그는 즉시, 발송은 5분 이내")을 이 두 열의 차이로 한다.
수신자는 마스킹한다.
"""

from __future__ import annotations

from apps.mailer.models import Outbox
from qa.base import QaCommand, mask_email, parse_since, stamp

COLUMNS = [
    "kind",
    "to_addr",
    "status",
    "attempts",
    "scheduled_at",
    "sent_at",
    "related_ref",
    "last_error",
]


class Command(QaCommand):
    help = "메일 아웃박스(=발송 로그) 조회"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--kind", default=None, choices=[c[0] for c in Outbox.Kind.choices])
        parser.add_argument("--since", default=None)
        parser.add_argument("--status", default=None, choices=[c[0] for c in Outbox.Status.choices])
        parser.add_argument("--count-only", action="store_true")
        parser.add_argument("--limit", type=int, default=200)

    def handle(self, *args, **options) -> None:
        queryset = Outbox.objects.all()
        if options["kind"]:
            queryset = queryset.filter(kind=options["kind"])
        if options["status"]:
            queryset = queryset.filter(status=options["status"])
        since = parse_since(options["since"])
        if since:
            queryset = queryset.filter(scheduled_at__gte=since)
        if options["count_only"]:
            self.stdout.write(str(queryset.count()))
            return
        rows = [
            {
                "kind": item.kind,
                "to_addr": mask_email(item.to_addr),
                "status": item.status,
                "attempts": item.attempts,
                "scheduled_at": stamp(item.scheduled_at),
                "sent_at": stamp(item.sent_at),
                "related_ref": item.related_ref,
                "last_error": (item.last_error or "")[:120],
            }
            for item in queryset.order_by("-scheduled_at")[: options["limit"]]
        ]
        self.emit(rows, COLUMNS, options["format"])
