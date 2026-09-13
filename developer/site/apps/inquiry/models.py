"""문의 접수 — 1차의 유일한 쓰기 경로 (기술 설계 §5.1 · REQ-F-040~046).

· 개인정보는 이름·휴대폰·문의 내용 3개뿐이고, 출처 IP 는 **솔트 해시만** 저장한다(REQ-N-020).
· submit_token 은 중복 제출 판정 키다(UNIQUE) — 같은 토큰으로는 두 번 저장되지 않는다.
· phone_norm 은 DB 생성 컬럼이다(§5.0) — 표기 형식과 무관하게 비교·조회한다.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.db.models import F, Func, Value


class Inquiry(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "접수"
        DONE = "done", "처리 완료"

    #: 보관 기간 설정 키 (settings.RETENTION_DAYS) — 파기 배치가 이 값만 본다(REQ-N-038)
    RETENTION_KEY = "INQUIRY"

    #: 개인정보 컬럼 선언 — `manage.py qa_pii_columns` 가 여기서 목록을 만든다(검증 요건 ⑪).
    #: 형식: 필드명 → (수집 목적, 조회 시 마스킹 대상 여부)
    #: ⚠ 처리방침(content/privacy.yml)의 수집 항목과 **이 선언이 곧 대조 기준**이다(REQ-N-020).
    PII_FIELDS = {
        "name": ("문의 답변을 위한 문의자 식별", True),
        "phone": ("문의 답변 연락", True),
        "phone_norm": ("표기 형식과 무관한 조회·중복 판정(생성 컬럼)", True),
        "message": ("문의 내용 확인·답변", False),
        "consent_at": ("수집·이용 동의 시각 증빙", False),
        "source_ip_hash": (
            "악용 방지 — **솔트 해시만 저장하고 원본 IP 는 저장하지 않는다**",
            False,
        ),
    }

    #: 개인정보 컬럼 ↔ **처리방침 수집 항목 표에 실제로 적힌 표현** (REQ-N-020 · DEF-009)
    #: `content/privacy.yml` p2 표에 이 문자열이 없으면 자동 테스트가 실패한다
    #: (tests/test_privacy_policy.py). 컬럼을 추가하면 방침 표와 이 표를 함께 고친다.
    PII_POLICY_TERMS = {
        "name": "이름",
        "phone": "휴대폰 번호",
        "phone_norm": "정규화 표기",
        "message": "문의 내용",
        "consent_at": "동의 시각",
        "source_ip_hash": "출처 IP 의 해시값",
    }

    public_ref = models.UUIDField("외부 식별자", default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("이름", max_length=20)
    phone = models.CharField("휴대폰 번호", max_length=20)
    phone_norm = models.GeneratedField(
        expression=Func(F("phone"), Value(r"\D"), Value(""), Value("g"), function="regexp_replace"),
        output_field=models.CharField(max_length=20),
        db_persist=True,
        verbose_name="휴대폰 번호(숫자만)",
    )
    message = models.TextField("문의 내용", max_length=500)
    consent_at = models.DateTimeField("개인정보 수집·이용 동의 시각")
    status = models.CharField(
        "상태", max_length=16, choices=Status.choices, default=Status.RECEIVED, db_index=True
    )
    source_ip_hash = models.CharField("출처 해시", max_length=64, blank=True, default="")
    submit_token = models.CharField("제출 단위 식별 키", max_length=64, unique=True)
    created_at = models.DateTimeField("접수 일시", db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inquiry_inquiry"
        ordering = ["-created_at", "-id"]
        verbose_name = "문의"

    def __str__(self) -> str:  # 개인정보를 문자열 표현에 넣지 않는다
        return f"inquiry/{self.public_ref}"

    @property
    def masked_phone(self) -> str:
        """관리 명령·메일 본문 밖에서 쓰는 마스킹 표기 (기술 설계 §9.5)."""
        digits = "".join(ch for ch in self.phone if ch.isdigit())
        if len(digits) < 7:
            return "***"
        return f"{digits[:3]}-****-{digits[-4:]}"
