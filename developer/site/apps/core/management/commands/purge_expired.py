"""보관 기간 경과 개인정보 자동 파기 (REQ-N-038 · 기술 설계 §3.3).

· 1차 대상은 `inquiry_inquiry` 한 종류다(2차에 9개 분류로 늘어난다).
· 보관 기간은 **항목별 독립 설정**이다 — `settings.RETENTION_DAYS[<KEY>]`.
  검증에서는 `QA_RETENTION_MINUTES__INQUIRY` 로 **분 단위로 단축**할 수 있다(요건 ④).
· 시각 판정은 전부 `clock.now()` 를 쓴다(§10.3).
· `--dry-run` 은 삭제하지 않고 대상 건수만 출력한다.

검증: `QA_FAIL_INJECT=purge` 로 강제 실패시킬 수 있다(요건 ⑨ⓒ).
"""

from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core import qaflags
from apps.core.clock import now
from apps.core.jobs import run_job
from apps.inquiry.models import Inquiry

JOB = "purge_expired"


def cutoff_for(key: str):
    """(기준 시각, 사용한 기준 문자열) — 검증 단축값이 있으면 그쪽이 우선한다."""
    minutes = qaflags.retention_minutes(key)
    if minutes is not None:
        return now() - dt.timedelta(minutes=minutes), "%d분(검증 전용)" % minutes
    days = int(settings.RETENTION_DAYS.get(key, 365))
    return now() - dt.timedelta(days=days), "%d일" % days


class Command(BaseCommand):
    help = "보관 기간이 지난 개인정보를 파기한다 (REQ-N-038)"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options) -> None:
        dry = options["dry_run"]
        with run_job(JOB) as job:
            if job.skipped:
                self.stdout.write("이미 실행 중이라 건너뜁니다.")
                return
            if qaflags.fail_injected("purge"):
                raise CommandError("QA_FAIL_INJECT=purge 에 의한 의도된 실패 (검증 요건 ⑨ⓒ)")

            cutoff, basis = cutoff_for(Inquiry.RETENTION_KEY)
            queryset = Inquiry.objects.filter(created_at__lt=cutoff)
            count = queryset.count()
            if dry:
                job.note("dry_run inquiry=%d basis=%s" % (count, basis))
                self.stdout.write(
                    "삭제 예정 inquiry=%d (기준 %s, cutoff=%s)" % (count, basis, cutoff)
                )
                return
            deleted = queryset.delete()[0] if count else 0
            job.note("inquiry=%d basis=%s cutoff=%s" % (deleted, basis, cutoff.isoformat()))
            self.stdout.write(
                self.style.SUCCESS("purge_expired inquiry=%d basis=%s" % (deleted, basis))
            )
