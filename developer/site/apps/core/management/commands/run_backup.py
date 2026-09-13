"""DB 백업 — 스케줄러가 03:00 에 부르고 배포·복구 스크립트가 라벨 실행으로 부른다.

기술 설계 §12.5.1 의 6단계를 그대로 구현한다.

    ① pg_dump -Fc  → ${BACKUP_DIR}/yogapass-<env>-YYYYMMDD-HHMM[.label-<라벨>].dump
    ② 무결성 확인  : 파일 크기 > 0  AND  pg_restore --list 성공
    ③ 회전        : 일 7 · 주 4 · 월 3 (라벨 파일은 회전 대상에서 제외하고 최근 3개만 유지)
    ④ 기록        : core_jobrunlog (job='run_backup')
    ⑤ 실패 시     : mailer_outbox INSERT (kind=backup_failed) → send_outbox 가 발송
    ⑥ 사전 점검   : 여유 공간 < BACKUP_MIN_FREE_GB 이면 **백업을 시도하지 않고** 알림 후 실패

⚠ **라벨 실행(--label)은 required 실행이다** (devops R2 #1 ②).
   락 충돌 시 `skipped` 로 조용히 끝나지 않고 **종료 코드 ≠ 0** 으로 실패한다.
   배포(`deploy.sh` 1단계)·복구(`restore.sh`)는 이 종료 코드를 중단 사유로 쓴다.

검증: `QA_TOOLS_ENABLED=1 QA_FAIL_INJECT=backup` 이면 ① 에서 의도적으로 실패한다(요건 ⑨ⓑ).
"""

from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.core import qaflags
from apps.core.clock import now
from apps.core.jobs import JobSkipped, run_job
from apps.mailer.models import Outbox
from apps.mailer.services import enqueue

JOB = "run_backup"
STAMP_FORMAT = "%Y%m%d-%H%M"
PREFIX = "yogapass-"
LABEL_MARK = ".label-"


class BackupError(RuntimeError):
    pass


def backup_dir() -> Path:
    return Path(settings.BACKUP_DIR)


def _pg_env() -> dict[str, str]:
    db = settings.DATABASES["default"]
    env = dict(os.environ)
    env["PGPASSWORD"] = db["PASSWORD"]
    return env


def _pg_args() -> list[str]:
    db = settings.DATABASES["default"]
    return ["-h", str(db["HOST"]), "-p", str(db["PORT"]), "-U", str(db["USER"])]


def file_stamp(path: Path) -> dt.datetime | None:
    """파일명에서 생성 시각을 읽는다(파일시스템 시각에 의존하지 않는다)."""
    name = path.name.split(LABEL_MARK)[0]
    parts = name.removesuffix(".dump").split("-")
    if len(parts) < 3:
        return None
    try:
        return dt.datetime.strptime(parts[-2] + "-" + parts[-1], STAMP_FORMAT)
    except ValueError:
        return None


def is_labeled(path: Path) -> bool:
    return LABEL_MARK in path.name


def plan_rotation(
    files: list[Path], keep_daily: int, keep_weekly: int, keep_monthly: int
) -> list[Path]:
    """삭제 대상 목록을 돌려준다 (일 N · 주 N · 월 N 유지).

    · 같은 날/주/월에 여러 개가 있으면 **가장 최근 것**을 남긴다.
    · 라벨 파일은 이 계산에 넣지 않는다(호출자가 따로 다룬다).
    """
    dated = []
    for path in files:
        stamp = file_stamp(path)
        if stamp is not None:
            dated.append((path, stamp))
    dated.sort(key=lambda item: item[1], reverse=True)

    keep: set[Path] = set()
    buckets = (
        (keep_daily, lambda s: s.date()),
        (keep_weekly, lambda s: s.isocalendar()[:2]),
        (keep_monthly, lambda s: (s.year, s.month)),
    )
    for size, key in buckets:
        seen: list = []
        for path, stamp in dated:
            bucket = key(stamp)
            if bucket in seen:
                continue
            if len(seen) >= size:
                break
            seen.append(bucket)
            keep.add(path)
    return [path for path, _ in dated if path not in keep]


class Command(BaseCommand):
    help = "PostgreSQL 논리 백업 + 무결성 확인 + 회전 (기술 설계 §12.5)"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--label", default="", help="pre-deploy 등. 라벨 실행은 required 다")
        parser.add_argument(
            "--dry-run", action="store_true", help="대상·여유 공간·회전 예정만 출력"
        )

    def handle(self, *args, **options) -> None:
        label = (options["label"] or "").strip()
        dry = options["dry_run"]
        required = bool(label)

        if dry:
            self._dry_run(label)
            return

        try:
            with run_job(JOB, required=required) as job:
                if job.skipped:
                    self.stdout.write("이미 실행 중이라 건너뜁니다(status=skipped).")
                    return
                detail = self._run(label)
                job.note(detail)
                self.stdout.write(self.style.SUCCESS("run_backup " + detail))
        except JobSkipped as exc:
            # 라벨 실행이 락 충돌로 수행되지 못했다 → 배포·복구를 중단시켜야 한다
            self._alert("건너뜀(락 충돌)", str(exc), label)
            raise CommandError("라벨 백업이 수행되지 않았습니다: " + str(exc)) from exc
        except BackupError as exc:
            self._alert("실패", str(exc), label)
            raise CommandError(str(exc)) from exc

    # ------------------------------------------------------------------ 본체
    def _run(self, label: str) -> str:
        directory = backup_dir()
        directory.mkdir(parents=True, exist_ok=True)

        free_gb = shutil.disk_usage(directory).free / (1024**3)
        if free_gb < settings.BACKUP_MIN_FREE_GB:
            raise BackupError(
                f"여유 공간 부족: {free_gb:.1f}GB < "
                f"BACKUP_MIN_FREE_GB={settings.BACKUP_MIN_FREE_GB}GB"
            )

        started = now()
        # 파일명 시각은 **KST 표기**다 — 운영자가 파일명만 보고 언제 것인지 알아야 하고,
        # 회전의 일·주·월 경계도 KST 기준이어야 한다.
        stamp = timezone.localtime(started).strftime(STAMP_FORMAT)
        env_name = getattr(settings, "DJANGO_ENV", "local")
        suffix = LABEL_MARK + label if label else ""
        target = directory / (PREFIX + env_name + "-" + stamp + suffix + ".dump")

        # ① pg_dump
        if qaflags.fail_injected("backup"):
            raise BackupError("QA_FAIL_INJECT=backup 에 의한 의도된 실패 (검증 요건 ⑨ⓑ)")
        db = settings.DATABASES["default"]
        result = subprocess.run(  # noqa: S603,S607 - 리스트 인자(셸 미사용) · PATH 는 우리 이미지에서 고정이다
            ["pg_dump", *_pg_args(), "-Fc", "--file", str(target), str(db["NAME"])],  # noqa: S607
            env=_pg_env(),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise BackupError(
                f"pg_dump 실패(rc={result.returncode}): {result.stderr.strip()[:400]}"
            )

        # ② 무결성 확인 — 크기 > 0 AND pg_restore --list 성공
        size = target.stat().st_size if target.exists() else 0
        if size <= 0:
            raise BackupError("백업 파일이 비어 있습니다: " + target.name)
        listing = subprocess.run(  # noqa: S603,S607
            ["pg_restore", "--list", str(target)],  # noqa: S607
            capture_output=True,
            text=True,
        )
        if listing.returncode != 0:
            raise BackupError(
                f"pg_restore --list 실패(rc={listing.returncode}): {listing.stderr.strip()[:400]}"
            )

        # ③ 회전
        removed = self._rotate()

        elapsed = (now() - started).total_seconds()
        return "file={} bytes={} elapsed={:.1f}s rotated={} label={} free_gb={:.1f}".format(
            target.name, size, elapsed, len(removed), label or "-", free_gb
        )

    def _rotate(self) -> list[Path]:
        directory = backup_dir()
        every = sorted(directory.glob(PREFIX + "*.dump"))
        plain = [p for p in every if not is_labeled(p)]
        labeled = sorted(
            (p for p in every if is_labeled(p)),
            key=lambda p: file_stamp(p) or dt.datetime.min,
            reverse=True,
        )
        doomed = plan_rotation(
            plain,
            settings.BACKUP_KEEP_DAILY,
            settings.BACKUP_KEEP_WEEKLY,
            settings.BACKUP_KEEP_MONTHLY,
        )
        doomed += labeled[3:]  # 라벨 파일은 회전에서 제외하되 최근 3개만 유지
        for path in doomed:
            path.unlink(missing_ok=True)
        return doomed

    # ------------------------------------------------------------------ 부가
    def _dry_run(self, label: str) -> None:
        directory = backup_dir()
        directory.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(directory)
        every = sorted(directory.glob(PREFIX + "*.dump"))
        doomed = plan_rotation(
            [p for p in every if not is_labeled(p)],
            settings.BACKUP_KEEP_DAILY,
            settings.BACKUP_KEEP_WEEKLY,
            settings.BACKUP_KEEP_MONTHLY,
        )
        self.stdout.write("대상 디렉토리 : " + str(directory))
        self.stdout.write(
            f"여유 공간     : {usage.free / (1024**3):.1f}GB (하한 {settings.BACKUP_MIN_FREE_GB}GB)"
        )
        self.stdout.write(f"라벨          : {label or '-'} (라벨 실행은 required)")
        self.stdout.write(f"보유 백업     : {len(every)}개")
        self.stdout.write(f"회전 예정     : {len(doomed)}개")
        for path in doomed:
            self.stdout.write("  - " + path.name)
        self.stdout.write("실제 백업은 수행하지 않았습니다(--dry-run).")

    def _alert(self, title: str, detail: str, label: str) -> None:
        """⑤ 실패 알림 — 아웃박스를 타므로 재시도·발송 로그가 따라온다(REQ-N-032 ③)."""
        enqueue(
            Outbox.Kind.BACKUP_FAILED,
            settings.OPS_ALERT_TO,
            "[점검필요] DB 백업 " + title,
            (
                "DB 백업이 정상적으로 끝나지 않았습니다.\n\n시각: {}\n".format(
                    now().strftime("%Y-%m-%d %H:%M:%S %z")
                )
                + "환경: {}\n".format(getattr(settings, "DJANGO_ENV", "local"))
                + "라벨: %s\n" % (label or "-")
                + f"내용: {detail}\n\n"
                + "조치: 백업 디렉토리 여유 공간과 DB 접속을 확인한 뒤 "
                "`manage.py run_backup` 을 수동으로 다시 실행하십시오.\n"
            ),
            related_type="job",
            related_ref=JOB,
        )
