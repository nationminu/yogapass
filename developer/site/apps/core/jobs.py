"""정기 작업 공통 실행기 (기술 설계 §3.3).

· 작업 이름 기준 어드바이저리 락으로 중복 실행을 막는다.
· 모든 실행을 core_jobrunlog 에 남긴다(success·failed·skipped 전부).
· required=True(라벨 백업 등)이면 락 충돌을 **성공으로 보지 않고** JobSkipped 를 올린다
  — devops R2 #1 ②(배포 직전 백업이 조용히 건너뛰어지는 경로 차단).
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
from dataclasses import dataclass, field

from django.db import connection

from apps.core.clock import now
from apps.core.models import JobRunLog

logger = logging.getLogger("core.jobs")


class JobSkipped(RuntimeError):
    """다른 실행이 락을 쥐고 있어 이번 실행을 수행하지 못했다."""


def _lock_key(job: str) -> int:
    digest = hashlib.sha256(job.encode()).digest()
    return int.from_bytes(digest[:8], "big", signed=True)


@dataclass
class JobRun:
    log: JobRunLog | None = None
    skipped: bool = False
    detail_parts: list[str] = field(default_factory=list)

    def note(self, message: str) -> None:
        self.detail_parts.append(message)


@contextlib.contextmanager
def run_job(job: str, *, required: bool = False):
    key = _lock_key(job)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s)", [key])
        acquired = cursor.fetchone()[0]

    if not acquired:
        stamp = now()
        JobRunLog.objects.create(
            job=job,
            started_at=stamp,
            finished_at=stamp,
            status=JobRunLog.Status.SKIPPED,
            detail="advisory lock busy",
        )
        logger.warning("job.skipped job=%s reason=lock_busy required=%s", job, required)
        if required:
            raise JobSkipped(f"{job} 이(가) 이미 실행 중입니다. 이번 실행은 수행되지 않았습니다.")
        yield JobRun(skipped=True)
        return

    log = JobRunLog.objects.create(job=job, started_at=now(), status=JobRunLog.Status.RUNNING)
    state = JobRun(log=log)
    try:
        yield state
    except Exception as exc:  # noqa: BLE001 - 기록을 남기고 그대로 올린다
        log.status = JobRunLog.Status.FAILED
        state.note(f"error={exc}")
        raise
    else:
        log.status = JobRunLog.Status.SUCCESS
    finally:
        log.finished_at = now()
        log.detail = " ".join(state.detail_parts)[:4000]
        log.save(update_fields=["status", "finished_at", "detail", "updated_at"])
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock(%s)", [key])
        logger.info("job.finished job=%s status=%s detail=%s", job, log.status, log.detail)


def has_recent_success(job: str, hours: int = 24) -> bool:
    """최근 N시간 내 성공 기록이 있는가 (devops R2 #2 ① — '없음 = 점검 필요')."""
    import datetime as dt

    since = now() - dt.timedelta(hours=hours)
    return JobRunLog.objects.filter(
        job=job, status=JobRunLog.Status.SUCCESS, started_at__gte=since
    ).exists()
