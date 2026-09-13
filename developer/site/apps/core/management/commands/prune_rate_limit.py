"""빈도 제한 카운터 정리 — 시간 1회 (기술 설계 §3.3).

지난 창의 카운터 행은 판정에 쓰이지 않는다. 남겨 두면 테이블만 커진다.
**차단이 아직 유효한 행(`blocked_until` 이 미래)은 지우지 않는다** — 지우면 차단이 풀린다.
"""

from __future__ import annotations

import datetime as dt

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.core.clock import now
from apps.core.jobs import run_job
from apps.core.models import RateLimitCounter

JOB = "prune_rate_limit"
KEEP_HOURS = 48  # 사용량 알림(1일 창) 판정에 쓰이므로 하루보다 넉넉히 남긴다


class Command(BaseCommand):
    help = "지난 빈도 제한 카운터 행을 정리한다"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--hours", type=int, default=KEEP_HOURS)

    def handle(self, *args, **options) -> None:
        moment = now()
        cutoff = moment - dt.timedelta(hours=options["hours"])
        queryset = RateLimitCounter.objects.filter(window_start__lt=cutoff).filter(
            Q(blocked_until__isnull=True) | Q(blocked_until__lt=moment)
        )
        with run_job(JOB) as job:
            if job.skipped:
                self.stdout.write("이미 실행 중이라 건너뜁니다.")
                return
            count = queryset.count()
            if options["dry_run"]:
                job.note("dry_run rows=%d" % count)
                self.stdout.write("삭제 예정 rows=%d (cutoff=%s)" % (count, cutoff))
                return
            deleted = queryset.delete()[0] if count else 0
            job.note("rows=%d cutoff=%s" % (deleted, cutoff.isoformat()))
            self.stdout.write(self.style.SUCCESS("prune_rate_limit rows=%d" % deleted))
