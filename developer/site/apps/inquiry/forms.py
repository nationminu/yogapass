"""문의 폼 — **서버 검증이 정본**이다 (REQ-F-040·041·042·043).

필드·오류 문구는 페이지 디자인 §4.3 의 표를 그대로 옮긴 것이다. 문구를 바꾸지 않는다.
honeypot 은 폼 필드로 두되 화면 밖에 배치하고(REQ-N-019) 값이 차 있으면 봇으로 판정한다.
"""

from __future__ import annotations

import re

from django import forms

NAME_MAX = 20
MESSAGE_MAX = 500
PHONE_RE = re.compile(r"^01[016789]-?\d{3,4}-?\d{4}$")

ERRORS = {
    "name_required": "이름을 입력해 주세요.",
    "name_max": f"이름은 최대 {NAME_MAX}자까지 입력할 수 있습니다.",
    "phone_required": "휴대폰 번호를 입력해 주세요.",
    "phone_invalid": "휴대폰 번호 형식이 올바르지 않습니다. 예: 010-1234-5678",
    "message_required": "문의 내용을 입력해 주세요.",
    "message_max": f"최대 {MESSAGE_MAX}자까지 입력할 수 있습니다.",
    "consent_required": "개인정보 수집·이용에 동의해 주세요.",
}

#: honeypot 필드 이름 — 자동완성이 인식하기 쉬운 이름(email·url 등)을 피한다.
HONEYPOT_FIELD = "company_ref"


class InquiryForm(forms.Form):
    name = forms.CharField(
        label="이름",
        max_length=NAME_MAX,
        error_messages={"required": ERRORS["name_required"], "max_length": ERRORS["name_max"]},
    )
    phone = forms.CharField(
        label="휴대폰 번호",
        max_length=20,
        error_messages={
            "required": ERRORS["phone_required"],
            "max_length": ERRORS["phone_invalid"],
        },
    )
    message = forms.CharField(
        label="문의 내용",
        max_length=MESSAGE_MAX,
        widget=forms.Textarea,
        error_messages={
            "required": ERRORS["message_required"],
            "max_length": ERRORS["message_max"],
        },
    )
    consent = forms.BooleanField(
        label="개인정보 수집·이용 동의",
        error_messages={"required": ERRORS["consent_required"]},
    )

    #: 화면 순서 = 오류 요약 블록의 항목 순서 (CMP-019)
    field_order = ["name", "phone", "message", "consent"]

    def clean_name(self) -> str:
        value = (self.cleaned_data.get("name") or "").strip()
        if not value:
            raise forms.ValidationError(ERRORS["name_required"])
        return value

    def clean_phone(self) -> str:
        value = (self.cleaned_data.get("phone") or "").strip()
        if not value:
            raise forms.ValidationError(ERRORS["phone_required"])
        if not PHONE_RE.match(value.replace(" ", "")):
            raise forms.ValidationError(ERRORS["phone_invalid"])
        return value

    def clean_message(self) -> str:
        value = (self.cleaned_data.get("message") or "").strip()
        if not value:
            raise forms.ValidationError(ERRORS["message_required"])
        return value

    def error_items(self) -> list[dict]:
        """CMP-019 오류 요약 블록용 (필드 순서 유지 · 첫 오류 문구 1건씩)."""
        items = []
        for name in self.field_order:
            messages = self.errors.get(name)
            if messages:
                items.append({"anchor": f"f-{name}", "message": messages[0]})
        for message in self.errors.get("__all__", []):
            items.append({"anchor": "contact-form", "message": message})
        return items

    def invalid_field_names(self) -> list[str]:
        """판정 로그 `inquiry.invalid fields=[…]` 용 — **필드 이름만**, 값은 기록하지 않는다."""
        return [name for name in self.field_order if name in self.errors]
