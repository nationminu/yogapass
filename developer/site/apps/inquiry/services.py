"""문의 접수 처리 — 기술 설계 §9.6 의 응답 형태 6종을 만드는 곳.

응답 형태(상태 코드·본문·저장·발송·기록)는 **§9.6 표가 원본**이고 P5 가 그 값으로 판정한다.
이 모듈을 고치면 §9.6 표도 함께 고쳐야 한다.

    ① 정상 접수          200 · 성공 블록 · 저장 1 · 발송 1 · inquiry.created
    ② 서버 검증 실패      200 · 오류 요약 · 저장 0 · 발송 0 · inquiry.invalid
    ③ honeypot          200 · 성공 블록(①과 동일) · 저장 0 · 발송 0 · blocked reason=honeypot
    ④ 빈도 제한 초과     429 · 실패(일반)+Retry-After · 저장 0 · 발송 0 · blocked reason=rate_limit
    ⑤ 토큰 **재사용**     200 · 성공 블록(①과 동일) · 저장 0 · 발송 0 · inquiry.duplicate
    ⑥ 서버 오류         500 · errors/500.html · 저장 0 · 발송 0 · ERROR (뷰에서 예외를 올린다)
    ⑦ 토큰 **만료·부재**  200 · 재작성 안내 + 폼 재렌더(입력값 보존·새 토큰)
                        · 저장 0 · 발송 0 · inquiry.expired

⚠ **⑤(중복 제출)와 ⑦(만료)은 다른 처리다** — PM 결정(2026-09-13).
  ⑤ 는 "이미 접수된 제출의 재전송"이라 사용자에게 접수 완료로 보여 주는 것이 맞지만,
  ⑦ 은 **아직 한 번도 저장되지 않은 제출**이다. v0.3 까지는 ⑦ 도 성공 화면을 돌려주어
  실제 이용자의 문의가 조용히 버려질 수 있었다. v0.4 부터 ⑦ 은 저장하지 않되
  **다시 작성해 달라고 안내하고, 입력값을 보존한 폼을 새 토큰과 함께 다시 보여 준다.**
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from django.conf import settings
from django.core import signing
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.clock import now
from apps.core.net import client_ip, ip_hash
from apps.core.ratelimit import check_form_submission, usage_alert_reasons
from apps.inquiry.forms import HONEYPOT_FIELD, InquiryForm
from apps.inquiry.models import Inquiry
from apps.mailer.models import Outbox
from apps.mailer.services import enqueue

logger = logging.getLogger("core.inquiry")

TOKEN_SALT = "inquiry.submit"  # noqa: S105 - 서명 salt(비밀값 아님)
TOKEN_MAX_AGE = 60 * 60 * 24  # 24시간 — 넘으면 ⑦(만료 → 재작성 안내)로 처리한다
TOKEN_FIELD = "submit_token"  # noqa: S105 - 폼 필드 이름

#: 결과 블록 상태 (페이지 디자인 §4.3 CMP-020)
SUCCESS = "success"
ERROR = "error"
FAILED = "failed"
EXPIRED = "expired"  # ⑦ — CMP-020 실패 블록(재작성 안내) + 폼 재렌더(입력값 보존)


@dataclass
class SubmitResult:
    status_code: int = 200
    result_state: str | None = None  # success | failed | None(=오류 요약만)
    form: InquiryForm | None = None
    submit_token: str = ""
    retry_after: int = 0
    extra_headers: dict = field(default_factory=dict)

    @property
    def show_form(self) -> bool:
        """성공 블록이 뜨면 폼을 교체한다(같은 화면 내 상태 전환).

        ⑦(만료)은 성공이 아니므로 폼이 그대로 남는다 — 입력값 보존 + 새 토큰으로 즉시 재제출.
        """
        return self.result_state != SUCCESS


# ---------------------------------------------------------------- 제출 단위 식별 키
def issue_token() -> str:
    """폼 렌더 시 1회용 토큰을 발급한다. 서버가 소비하며 JS 없이도 동작한다(§9.5)."""
    return signing.dumps(uuid.uuid4().hex, salt=TOKEN_SALT)


def read_token(raw: str) -> tuple[str, str]:
    """(상태, 토큰 식별자) — 상태는 valid | missing | expired | invalid.

    valid 가 아닌 셋은 모두 ⑦(재작성 안내)로 처리하지만 **판정 로그에서는 구분**한다.
    · missing : 토큰 필드 자체가 없다(폼을 거치지 않은 제출)
    · expired : 서명은 맞지만 24시간(TOKEN_MAX_AGE)이 지났다
    · invalid : 서명이 맞지 않는다(변조 · SECRET_KEY 교체)
    """
    if not raw:
        return "missing", ""
    try:
        value = signing.loads(raw, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        return "expired", ""
    except signing.BadSignature:
        return "invalid", ""
    return "valid", str(value)


# ---------------------------------------------------------------- 메일 본문
def _notify_body(inquiry: Inquiry) -> str:
    received = timezone.localtime(inquiry.created_at).strftime("%Y-%m-%d %H:%M")
    return (
        "문의가 접수되었습니다.\n\n"
        f"접수 일시: {received}\n"
        f"이름: {inquiry.name}\n"
        f"연락처: {inquiry.phone}\n"
        f"접수 번호: {inquiry.public_ref}\n\n"
        "문의 내용:\n"
        f"{inquiry.message}\n"
    )


def _maybe_usage_alert(identifier_hash: str) -> None:
    """빈도 제한 사용량 알림 — 같은 사유는 1시간에 1통으로 합산한다(§5.3)."""
    reasons = usage_alert_reasons(identifier_hash)
    if not reasons:
        return
    import datetime as dt

    recent = Outbox.objects.filter(
        kind=Outbox.Kind.RATE_LIMIT_ALERT, created_at__gte=now() - dt.timedelta(hours=1)
    ).exists()
    if recent:
        return
    enqueue(
        Outbox.Kind.RATE_LIMIT_ALERT,
        settings.OPS_ALERT_TO,
        "[점검필요] 문의 폼 빈도 제한 사용량 알림",
        "문의 폼에서 빈도 제한 차단이 임계값을 넘었습니다.\n\n" + "\n".join(reasons) + "\n",
        related_type="ratelimit",
        related_ref=identifier_hash[:16],
    )


# ---------------------------------------------------------------- 본 처리
def handle_submission(request) -> SubmitResult:
    source_hash = ip_hash(client_ip(request))

    # ④ 빈도 제한 — 검증보다 먼저 본다(차단된 요청에서 검증·저장을 하지 않기 위함)
    decision = check_form_submission(source_hash)
    if not decision.allowed:
        logger.warning("inquiry.blocked reason=rate_limit ip_hash=%s scope=form", source_hash)
        _maybe_usage_alert(source_hash)
        retry_after = decision.retry_after
        return SubmitResult(
            status_code=429,
            result_state=FAILED,
            form=InquiryForm(request.POST),
            submit_token=request.POST.get(TOKEN_FIELD, ""),
            retry_after=retry_after,
            extra_headers={"Retry-After": str(retry_after)},
        )

    # ③ honeypot — 성공 화면과 픽셀 단위로 같게 돌려준다(차단 사실 미노출, REQ-F-044)
    if (request.POST.get(HONEYPOT_FIELD) or "").strip():
        logger.warning("inquiry.blocked reason=honeypot ip_hash=%s", source_hash)
        return SubmitResult(result_state=SUCCESS)

    # ② 서버 검증 — 클라이언트 검증을 우회한 요청도 여기서 거부된다(REQ-F-042)
    form = InquiryForm(request.POST)
    if not form.is_valid():
        logger.info("inquiry.invalid fields=[%s]", ",".join(form.invalid_field_names()))
        return SubmitResult(
            result_state=None,
            form=form,
            submit_token=request.POST.get(TOKEN_FIELD, ""),  # 기존 토큰 유지 → 재제출 가능
        )

    # ⑦ 토큰 만료·부재·변조 — 저장하지 않되 **다시 작성해 달라고 안내한다**(PM 결정 2026-09-13).
    #    입력값을 보존한 폼을 **새 토큰**과 함께 재렌더하므로 그 자리에서 바로 다시 제출할 수 있다.
    state, token_id = read_token(request.POST.get(TOKEN_FIELD, ""))
    if state != "valid":
        logger.info("inquiry.expired token_state=%s ref=none", state)
        return SubmitResult(
            result_state=EXPIRED,
            form=form,  # 서버 검증을 통과한 값이 그대로 들어 있다 → 화면에 복원된다
            submit_token=issue_token(),  # 새 토큰
        )

    # ⑤ 토큰 재사용(중복 제출) — 이미 접수된 제출이므로 ①과 같은 화면을 돌려준다(저장 0건)
    existing = find_existing(token_id)
    if existing:
        logger.info("inquiry.duplicate token_state=used ref=%s", existing)
        return SubmitResult(result_state=SUCCESS)

    # ① 정상 접수 — 저장과 아웃박스 INSERT 를 **같은 트랜잭션**에서 한다(M-8)
    stamp = now()
    try:
        return _create(form, stamp, source_hash, token_id)
    except IntegrityError:
        # 같은 토큰이 **동시에** 들어와 위의 조회를 둘 다 통과한 경우다.
        # `submit_token` UNIQUE 가 두 번째를 막아 저장은 1건으로 유지된다 → ⑤와 같은 화면.
        # (이 경로가 없으면 동시 이중 제출이 500 으로 나간다 — REQ-F-046 ②)
        logger.info("inquiry.duplicate token_state=used ref=%s", find_existing(token_id) or "none")
        return SubmitResult(result_state=SUCCESS)


def find_existing(token_id: str) -> str:
    """이 토큰으로 이미 접수된 문의의 public_ref (없으면 빈 문자열)."""
    values = Inquiry.objects.filter(submit_token=token_id).values_list("public_ref", flat=True)
    return str(values[0]) if values else ""


def _create(form, stamp, source_hash: str, token_id: str) -> SubmitResult:
    with transaction.atomic():
        inquiry = Inquiry.objects.create(
            name=form.cleaned_data["name"],
            phone=form.cleaned_data["phone"],
            message=form.cleaned_data["message"],
            consent_at=stamp,
            source_ip_hash=source_hash,
            submit_token=token_id,
            created_at=stamp,
        )
        enqueue(
            Outbox.Kind.INQUIRY_NOTIFY,
            settings.INQUIRY_NOTIFY_TO,
            f"[문의 접수] {settings.SITE_NAME}",
            _notify_body(inquiry),
            related_type="inquiry",
            related_ref=str(inquiry.public_ref),
        )
    logger.info("inquiry.created ref=%s", inquiry.public_ref)
    return SubmitResult(result_state=SUCCESS)
