"""정기 작업 실행 기록 · 빈도 제한 카운터 (기술 설계 §5.1)."""

from __future__ import annotations

from django.db import models


class JobRunLog(models.Model):
    """core_jobrunlog — 모든 정기 작업의 실행 기록(성공·실패·skipped)."""

    class Status(models.TextChoices):
        RUNNING = "running", "실행 중"
        SUCCESS = "success", "성공"
        FAILED = "failed", "실패"
        SKIPPED = "skipped", "건너뜀"

    job = models.CharField("작업 이름", max_length=64, db_index=True)
    started_at = models.DateTimeField("시작", db_index=True)
    finished_at = models.DateTimeField("종료", null=True, blank=True)
    status = models.CharField("상태", max_length=16, choices=Status.choices)
    detail = models.TextField("상세", blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_jobrunlog"
        indexes = [models.Index(fields=["job", "status", "started_at"])]
        verbose_name = "작업 실행 기록"

    def __str__(self) -> str:
        return f"{self.job}/{self.status}@{self.started_at:%Y-%m-%d %H:%M}"


class RateLimitCounter(models.Model):
    """core_ratelimitcounter — 빈도 제한 상태(D-9: PostgreSQL 테이블)."""

    scope = models.CharField("범위", max_length=32)
    identifier_hash = models.CharField("식별자 해시", max_length=64)
    window_start = models.DateTimeField("창 시작")
    count = models.PositiveIntegerField("횟수", default=0)
    blocked_until = models.DateTimeField("차단 해제 시각", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_ratelimitcounter"
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "identifier_hash", "window_start"],
                name="uq_ratelimit_scope_id_window",
            )
        ]
        indexes = [models.Index(fields=["scope", "identifier_hash"])]
        verbose_name = "빈도 제한 카운터"

    def __str__(self) -> str:
        return f"{self.scope}/{self.identifier_hash[:8]}"
