"""요건 ① — 읽기 전용·마스킹 조회 (기술 설계 §10.2).

    manage.py qa_show inquiry [--count-only] [--since ISO8601] [--format table|json]

· **마스킹은 기본 on 이고 해제 옵션이 없다** — qa 는 원본 개인정보를 보지 않는다(REQ-N-039).
· `--count-only` 는 **정수 1줄**만 출력한다(REQ-F-046 ② "저장 1건" 판정용).
· 결과 0건도 종료 코드 0 이다.
"""

from __future__ import annotations

from apps.core.models import JobRunLog
from apps.inquiry.models import Inquiry
from qa.base import QaCommand, mask_name, mask_phone, parse_since, stamp

MODELS = ("inquiry", "joblog")


class Command(QaCommand):
    help = "검증용 읽기 전용 조회 (마스킹)"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument("model", choices=MODELS)
        parser.add_argument("--since", default=None, help="ISO8601 (예: 2026-10-15T09:00)")
        parser.add_argument("--count-only", action="store_true")
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument(
            "--masked", action="store_true", default=True, help="기본 on (해제 불가)"
        )

    def handle(self, *args, **options) -> None:
        since = parse_since(options["since"])
        if options["model"] == "inquiry":
            queryset = Inquiry.objects.all()
            if since:
                queryset = queryset.filter(created_at__gte=since)
            if options["count_only"]:
                self.stdout.write(str(queryset.count()))
                return
            rows = [
                {
                    "public_ref": str(item.public_ref),
                    "created_at": stamp(item.created_at),
                    "status": item.status,
                    "name": mask_name(item.name),
                    "phone": mask_phone(item.phone),
                    "message_len": len(item.message),
                }
                for item in queryset.order_by("-created_at")[: options["limit"]]
            ]
            columns = ["public_ref", "created_at", "status", "name", "phone", "message_len"]
        else:
            queryset = JobRunLog.objects.all()
            if since:
                queryset = queryset.filter(started_at__gte=since)
            if options["count_only"]:
                self.stdout.write(str(queryset.count()))
                return
            rows = [
                {
                    "job": item.job,
                    "started_at": stamp(item.started_at),
                    "finished_at": stamp(item.finished_at),
                    "status": item.status,
                    "detail": item.detail,
                }
                for item in queryset.order_by("-started_at")[: options["limit"]]
            ]
            columns = ["job", "started_at", "finished_at", "status", "detail"]

        self.emit(rows, columns, options["format"])
