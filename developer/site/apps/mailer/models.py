"""메일 아웃박스 겸 발송 로그 (기술 설계 §2.5 · §5.1).

요청 처리 트랜잭션에서는 INSERT 만 하고 실제 SMTP 발송은 스케줄러가 한다.
"""

from __future__ import annotations

import uuid

from django.db import models


class Outbox(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "대기"
        SENT = "sent", "발송"
        FAILED = "failed", "실패"
        CANCELLED = "cancelled", "취소"

    class Kind(models.TextChoices):
        INQUIRY_NOTIFY = "inquiry_notify", "문의 접수 알림"
        BACKUP_FAILED = "backup_failed", "백업 실패"
        OPS_DAILY = "ops_daily", "일일 운영 요약"
        RATE_LIMIT_ALERT = "rate_limit_alert", "빈도 제한 사용량 알림"

    public_ref = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kind = models.CharField("종류", max_length=32, choices=Kind.choices, db_index=True)
    to_addr = models.CharField("수신자", max_length=320)
    subject = models.CharField("제목", max_length=200)
    body_text = models.TextField("본문")
    status = models.CharField(
        "상태", max_length=16, choices=Status.choices, default=Status.QUEUED, db_index=True
    )
    attempts = models.PositiveSmallIntegerField("시도 횟수", default=0)
    last_error = models.TextField("마지막 오류", blank=True, default="")
    scheduled_at = models.DateTimeField("발송 예정", db_index=True)
    sent_at = models.DateTimeField("발송 시각", null=True, blank=True)
    related_type = models.CharField("연관 종류", max_length=40, blank=True, default="")
    related_ref = models.CharField("연관 식별자", max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mailer_outbox"
        ordering = ["scheduled_at", "id"]
        indexes = [models.Index(fields=["status", "scheduled_at"])]
        verbose_name = "메일 아웃박스"

    def __str__(self) -> str:
        return f"{self.kind}/{self.status}"
