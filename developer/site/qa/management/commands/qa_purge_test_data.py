"""요건 ⑤ — 검증 데이터 삭제 (기술 설계 §10.4).

    manage.py qa_purge_test_data [--since ISO8601] [--dry-run] [--confirm]

삭제 대상과 식별 규칙(§10.4)

    inquiry_inquiry        name LIKE 'TEST-%' 또는 message LIKE 'TEST-%'
    mailer_outbox          위에서 삭제된 문의의 related_ref 연계 + 테스트 수신 도메인(@example.test)
    core_ratelimitcounter  --since 구간 내 레코드 전량
    core_jobrunlog         --since 구간 + job 이름이 qa_ 로 시작

· **`--since` 가 없으면 카운터·작업 로그는 건드리지 않는다**(안전 기본값).
· `--confirm` 없이는 실제로 삭제하지 않는다.
· **테이블별 삭제 건수 + 총계**를 출력하고 실행 기록을 `core_jobrunlog` 에 남긴다.
"""

from __future__ import annotations

from django.db.models import Q

from apps.core.jobs import run_job
from apps.core.models import JobRunLog, RateLimitCounter
from apps.inquiry.models import Inquiry
from apps.mailer.models import Outbox
from qa.base import QaCommand, parse_since

TEST_PREFIX = "TEST-"
TEST_MAIL_DOMAIN = "@example.test"
JOB = "qa_purge_test_data"


class Command(QaCommand):
    help = "검증용 테스트 데이터를 삭제한다 (테이블별 건수 출력)"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--since", default=None, help="TC 실행 구간 시작(ISO8601)")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--confirm", action="store_true")

    def handle(self, *args, **options) -> None:
        since = parse_since(options["since"])
        dry = options["dry_run"] or not options["confirm"]

        inquiries = Inquiry.objects.filter(
            Q(name__startswith=TEST_PREFIX) | Q(message__startswith=TEST_PREFIX)
        )
        refs = [str(ref) for ref in inquiries.values_list("public_ref", flat=True)]
        outbox = Outbox.objects.filter(
            Q(related_ref__in=refs) | Q(to_addr__endswith=TEST_MAIL_DOMAIN)
        )
        counters = RateLimitCounter.objects.none()
        joblogs = JobRunLog.objects.none()
        if since:
            counters = RateLimitCounter.objects.filter(window_start__gte=since)
            joblogs = JobRunLog.objects.filter(started_at__gte=since, job__startswith="qa_")

        # ⚠ 대상 PK 를 **먼저 확정**한다 — 이 명령 자신의 실행 기록(job=qa_purge_test_data)이
        #    삭제 대상에 섞이면 실행 기록을 남기는 단계에서 깨진다.
        targets = [
            (
                "inquiry_inquiry",
                Inquiry.objects.filter(pk__in=list(inquiries.values_list("pk", flat=True))),
            ),
            (
                "mailer_outbox",
                Outbox.objects.filter(pk__in=list(outbox.values_list("pk", flat=True))),
            ),
            (
                "core_ratelimitcounter",
                RateLimitCounter.objects.filter(pk__in=list(counters.values_list("pk", flat=True))),
            ),
            (
                "core_jobrunlog",
                JobRunLog.objects.filter(pk__in=list(joblogs.values_list("pk", flat=True))),
            ),
        ]
        counts = {table: queryset.count() for table, queryset in targets}
        total = sum(counts.values())

        if dry:
            for table, count in counts.items():
                self.stdout.write("%-24s 삭제 예정 %d건" % (table, count))
            self.stdout.write("합계 삭제 예정 %d건" % total)
            if not since:
                self.stdout.write("(--since 가 없어 카운터·작업 로그는 대상에서 제외했습니다)")
            if not options["confirm"]:
                self.stdout.write("실제 삭제하려면 --confirm 을 주십시오.")
            return

        with run_job(JOB) as job:
            for _, queryset in targets:
                queryset.delete()
            detail = " ".join("%s=%d" % (table, count) for table, count in counts.items())
            job.note(detail + " total=%d" % total)
        for table, count in counts.items():
            self.stdout.write("%-24s 삭제 %d건" % (table, count))
        self.stdout.write(self.style.SUCCESS("합계 삭제 %d건" % total))
