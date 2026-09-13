"""일일 운영 요약 메일 — 매일 08:00 **1통** (기술 설계 §3.3 · devops R1 #9 · R2 #2).

외부 감시 도구를 도입하지 않는 대신, 운영자가 **메일 1통으로 상태를 인지**하는 것이 유일한 수단이다.
따라서 **실패가 없어도 매일 보낸다** — "요약 메일이 오지 않는 날 자체가 이상 신호"라는 규칙
(P8 운영 가이드 1번 항목)이 성립하려면 제목·수신 시각이 고정되어야 한다.

포함 항목 (§3.3 표)
    ⓐ /healthz 폴링 결과(최근 24시간 성공·실패)
    ⓑ 재시작 신호 — **실패 → 성공 전환 횟수**
       ※ 설계 원안은 "앱 기동 시각(프로세스 시작 시간) 비교"였으나, 스케줄러 컨테이너에서
         앱 프로세스를 볼 수 없고 docker 소켓은 마운트하지 않기로 했으므로(§3.3),
         같은 신호를 **폴링 기록의 회복 전환**으로 계산한다. 기술 설계 v0.4 §3.3 에 반영했다.
    ⓒ run_backup — **최근 24시간 내 성공 기록이 없으면 점검 필요**(실패·skipped·기록 없음 전부)
    ⓓ 아웃박스 실패 · 배치 실패 · **skipped(작업별 별도 집계)**
    ⓔ 디스크 여유율(${BACKUP_DIR})
    ⓕ 빈도 제한 차단 건수

실패 항목이 하나라도 있으면 제목 앞에 **[점검필요]** 를 붙인다.
"""

from __future__ import annotations

import datetime as dt
import shutil
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from apps.core.clock import now
from apps.core.jobs import has_recent_success, run_job
from apps.core.models import JobRunLog, RateLimitCounter
from apps.mailer.models import Outbox
from apps.mailer.services import enqueue

JOB = "report_failures"
SUBJECT_BASE = "요가패스 일일 운영 요약"
ALERT_PREFIX = "[점검필요] "
DISK_WARN_PERCENT = 10.0


class Command(BaseCommand):
    help = "일일 운영 요약 메일을 아웃박스에 넣는다 (기술 설계 §3.3)"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run", action="store_true", help="본문만 출력하고 발송하지 않는다"
        )
        parser.add_argument("--hours", type=int, default=24)

    def handle(self, *args, **options) -> None:
        hours = options["hours"]
        lines, alerts = self.build(hours)
        subject = (
            (ALERT_PREFIX if alerts else "")
            + SUBJECT_BASE
            + timezone.localtime(now()).strftime(" %Y-%m-%d")
        )
        body = "\n".join(lines) + "\n"

        if options["dry_run"]:
            self.stdout.write(subject)
            self.stdout.write(body)
            return

        with run_job(JOB) as job:
            if job.skipped:
                self.stdout.write("이미 실행 중이라 건너뜁니다.")
                return
            enqueue(
                Outbox.Kind.OPS_DAILY,
                settings.OPS_ALERT_TO,
                subject,
                body,
                related_type="job",
                related_ref=JOB,
            )
            job.note("alerts=%d" % len(alerts))
        self.stdout.write(self.style.SUCCESS("report_failures alerts=%d" % len(alerts)))

    # ------------------------------------------------------------------ 본문
    def build(self, hours: int) -> tuple[list[str], list[str]]:
        moment = now()
        since = moment - dt.timedelta(hours=hours)
        alerts: list[str] = []
        lines = [
            "%s (%s KST 기준 최근 %d시간)"
            % (SUBJECT_BASE, timezone.localtime(moment).strftime("%Y-%m-%d %H:%M"), hours),
            "환경: {}".format(getattr(settings, "DJANGO_ENV", "local")),
            "",
        ]

        # ⓐ /healthz 폴링
        pings = list(
            JobRunLog.objects.filter(job="ping_health", started_at__gte=since).order_by(
                "started_at"
            )
        )
        ok = sum(1 for row in pings if row.status == JobRunLog.Status.SUCCESS)
        ng = sum(1 for row in pings if row.status == JobRunLog.Status.FAILED)
        lines.append("ⓐ /healthz 폴링 : 성공 %d · 실패 %d (기록 %d건)" % (ok, ng, len(pings)))
        if ng:
            alerts.append("healthz 폴링 실패 %d건" % ng)
        if not pings:
            lines.append("   ⚠ 폴링 기록이 없습니다 — 스케줄러 상태를 확인하십시오.")
            alerts.append("healthz 폴링 기록 없음")

        # ⓑ 재시작 신호 (실패 → 성공 전환)
        recoveries = 0
        previous = None
        for row in pings:
            if previous == JobRunLog.Status.FAILED and row.status == JobRunLog.Status.SUCCESS:
                recoveries += 1
            previous = row.status
        lines.append("ⓑ 응답 회복 전환 : %d회 (재시작·일시 장애 신호)" % recoveries)
        if recoveries:
            alerts.append("응답 회복 전환 %d회" % recoveries)

        # ⓒ 백업 — "최근 24시간 내 성공 기록이 없으면 점검 필요"
        backup_ok = has_recent_success("run_backup", hours=hours)
        last = (
            JobRunLog.objects.filter(job="run_backup", status=JobRunLog.Status.SUCCESS)
            .order_by("-started_at")
            .first()
        )
        if backup_ok and last:
            lines.append(
                "ⓒ DB 백업      : 성공 ({} KST)".format(
                    timezone.localtime(last.started_at).strftime("%Y-%m-%d %H:%M")
                )
            )
            lines.append("   %s" % (last.detail or "-"))
        else:
            marker = (
                timezone.localtime(last.started_at).strftime("%Y-%m-%d %H:%M KST")
                if last
                else "기록 없음"
            )
            lines.append(
                "ⓒ DB 백업      : ⚠ 최근 %d시간 내 성공 기록이 없습니다 (마지막 성공: %s)"
                % (hours, marker)
            )
            alerts.append("백업 성공 기록 없음")

        # ⓓ 아웃박스·배치 실패 · skipped(작업별)
        mail_failed = Outbox.objects.filter(
            status=Outbox.Status.FAILED, updated_at__gte=since
        ).count()
        job_failed = JobRunLog.objects.filter(
            status=JobRunLog.Status.FAILED, started_at__gte=since
        ).count()
        skipped = Counter(
            {
                row["job"]: row["n"]
                for row in JobRunLog.objects.filter(
                    status=JobRunLog.Status.SKIPPED, started_at__gte=since
                )
                .values("job")
                .annotate(n=Count("id"))
            }
        )
        lines.append("ⓓ 메일 실패    : %d건 / 배치 실패 : %d건" % (mail_failed, job_failed))
        if skipped:
            detail = ", ".join("%s=%d" % (job, n) for job, n in sorted(skipped.items()))
            lines.append(f"   건너뜀(skipped) : {detail}  ← 반복되면 락 경합·설계 문제 신호")
        else:
            lines.append("   건너뜀(skipped) : 없음")
        if mail_failed:
            alerts.append("메일 실패 %d건" % mail_failed)
        if job_failed:
            alerts.append("배치 실패 %d건" % job_failed)

        # ⓔ 디스크 여유
        target = Path(settings.BACKUP_DIR)
        try:
            usage = shutil.disk_usage(target if target.exists() else Path(settings.BASE_DIR))
            percent = usage.free / usage.total * 100
            lines.append(
                f"ⓔ 디스크 여유  : {percent:.1f}% "
                f"({usage.free / (1024**3):.1f}GB / {usage.total / (1024**3):.1f}GB)"
            )
            if percent < DISK_WARN_PERCENT or usage.free / (1024**3) < settings.BACKUP_MIN_FREE_GB:
                alerts.append(f"디스크 여유 부족 {percent:.1f}%")
        except OSError as exc:  # pragma: no cover - 경로 문제
            lines.append(f"ⓔ 디스크 여유  : 확인 실패 ({exc})")
            alerts.append("디스크 확인 실패")

        # ⓕ 빈도 제한 차단
        blocked = RateLimitCounter.objects.filter(
            window_start__gte=since, blocked_until__isnull=False
        ).count()
        lines.append("ⓕ 빈도 제한 차단 : %d건" % blocked)

        lines.append("")
        if alerts:
            lines.append("점검이 필요한 항목: " + " / ".join(alerts))
        else:
            lines.append("점검이 필요한 항목이 없습니다.")
        lines.append("")
        lines.append(
            "※ 이 메일은 매일 같은 시각에 1통 발송됩니다. **오지 않는 날 자체가 이상 신호**입니다."
        )
        return lines, alerts
