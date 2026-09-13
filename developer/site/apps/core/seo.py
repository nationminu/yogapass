"""화면별 title·description 원본 (REQ-N-010·011 · DEF-001).

⚠ **이 표의 문자열은 기획 산출물 `planning/02_information-architecture.md` v1.1 의
§6.2 title 패턴 표 · §6.3 description 표를 그대로 옮긴 것이다.**
P5 는 렌더된 `<title>` · `<meta name="description">` 을 IA 표와 **문자열 단위로 대조**해
판정한다(REQ-N-010 수용 기준). 그러므로 여기서 문구를 새로 쓰거나 다듬지 않는다.
문구를 바꿔야 하면 IA 를 먼저 고치고(기획 소관) 그 값을 그대로 복사해 온다.

설계 의도
· 브랜드 문자열(`BRAND`)을 **DB·환경 변수와 분리**한다. 제목은 콘텐츠 적재 상태(`content/site.yml`
  미시드·DB 정지 등)와 무관하게 항상 IA 표 값이어야 하기 때문이다(DEF-001 원인 ②).
· 화면 표시용 상호(`site_name`)는 계속 `content/site.yml` → `SITE_NAME` 순서로 정해진다.
  두 값은 **같은 문자열("강남 요가패스")로 맞춰 두었고**, 정식 상호 확정(T-G) 시 함께 교체한다.
"""

from __future__ import annotations

#: IA §6.2 title 패턴의 브랜드 부분(공개 영역). 구분자는 `|` 한 글자다.
BRAND = "강남 요가패스"
SEPARATOR = " | "

#: IA §6.2 — 1차 구현 화면의 title 전문(全文). 키는 SCR ID.
TITLES: dict[str, str] = {
    "SCR-001": f"{BRAND}{SEPARATOR}강남 요가 스튜디오·수업 안내",
    "SCR-002": f"요가 강사 소개{SEPARATOR}{BRAND}",
    "SCR-003": f"오시는 길{SEPARATOR}{BRAND}",
    "SCR-006": f"개인정보 처리방침{SEPARATOR}{BRAND}",
    "SCR-008": f"페이지를 찾을 수 없습니다{SEPARATOR}{BRAND}",
    "SCR-009": f"일시적인 오류{SEPARATOR}{BRAND}",
}

#: IA §6.3 — 색인 대상 공개 화면의 description 전문. **50~90자(공백 포함)**.
#: `noindex` 화면(SCR-008·009)은 description 을 두지 않는다(IA §6.3 적용 범위).
DESCRIPTIONS: dict[str, str] = {
    "SCR-001": (
        "강남에 있는 요가 스튜디오 요가패스입니다. "
        "수업과 강사를 확인하고 궁금한 점은 온라인 문의나 전화로 남겨주세요."
    ),
    "SCR-002": (
        "강남 요가패스에서 수업을 진행하는 강사들을 소개합니다. "
        "강사별 담당 수업과 자격·경력을 확인하고 체험 수업을 신청해 보세요."
    ),
    "SCR-003": (
        "강남 요가패스 오시는 길입니다. "
        "주소와 가까운 지하철역, 운영시간을 확인하고 길찾기로 바로 이동하세요."
    ),
    "SCR-006": (
        "강남 요가패스 개인정보 처리방침입니다. "
        "수집하는 개인정보 항목과 이용 목적, 보관 기간을 안내합니다."
    ),
}

#: description 길이 규칙(REQ-N-010). 판정은 문자 단위 실측이다.
DESCRIPTION_MIN = 50
DESCRIPTION_MAX = 90


def title(screen: str) -> str:
    """SCR ID 의 title 전문. 표에 없으면 브랜드만 돌려준다(빈 title 을 만들지 않는다)."""
    return TITLES.get(screen, BRAND)


def description(screen: str) -> str:
    """SCR ID 의 description 전문. `noindex` 화면은 빈 문자열(태그 미출력)."""
    return DESCRIPTIONS.get(screen, "")


def meta(screen: str) -> dict[str, str]:
    """뷰 컨텍스트에 바로 넣는 (meta_title, meta_description) 쌍."""
    return {"meta_title": title(screen), "meta_description": description(screen)}
