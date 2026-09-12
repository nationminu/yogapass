"""scheduler 컨테이너 헬스체크 (기술 설계 §3.4).

supercronic 프로세스 생존만으로는 '돌고 있다'를 보장하지 못하므로
core_jobrunlog 에 최근 N분 기록이 1건 이상 있는지로 판정한다.
"""

from __future__ import annotations

import datetime as dt
import sys

from django.core.management.base import BaseCommand

from apps.core.clock import now
from apps.core.models import JobRunLog


class Command(BaseCommand):
    help = "최근 N분 내 작업 실행 기록이 있으면 0, 없으면 1로 종료한다."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--minutes", type=int, default=10)

    def handle(self, *args, **options) -> None:
        since = now() - dt.timedelta(minutes=options["minutes"])
        if JobRunLog.objects.filter(started_at__gte=since).exists():
            self.stdout.write("ok")
            return
        self.stderr.write("최근 실행 기록이 없습니다.")
        sys.exit(1)
