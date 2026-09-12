"""주 CTA 상태 판정 (디자인 시스템 CMP-003 H1~H3 · CMP-007 S1~S3).

판정 축은 하나다 — **현재 URL 과 목적지 URL 비교(G-7) + 대표 전화 확정 여부**.
화면 목록을 코드에 열거하지 않는다.
"""

from __future__ import annotations

CONTACT_URL = "/location#contact"
CONTACT_PATH = "/location"


def cta_state(current_path: str, has_phone: bool) -> dict:
    self_reference = current_path == CONTACT_PATH

    # ≥1280px 헤더 주 CTA
    if not self_reference:
        header = "H1"
    elif has_phone:
        header = "H2"
    else:
        header = "H3"

    # <1280px 하단 고정 바
    if not self_reference:
        bar = "S1"
    elif has_phone:
        bar = "S2"
    else:
        bar = "S3"

    return {
        "header": header,
        "bar": bar,
        "contact_url": CONTACT_URL,
        "show_bar": bar != "S3",
        # S1 에서 전화가 미확정이면 좌측 버튼을 렌더하지 않고 우측이 전폭이 된다
        "bar_two_up": bar == "S1" and has_phone,
    }
