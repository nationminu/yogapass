"""배포 차단 점검 — REQ-N-023 ① "운영 배포 시점 [TBD] 표시 0건".

개인정보 처리방침 본문이 고객 확정 전(status: pending)인 채로 운영에 올라가는 경로를 막는다.

· 시스템 점검(`manage.py check`)에서는 **Warning** 으로만 낸다 — migrate·collectstatic 같은
  일반 명령을 깨뜨리지 않기 위함이다.
· 실제 차단은 **`manage.py check_release`** 가 한다(미확정이 남아 있으면 종료 코드 1).
  배포 스크립트의 사전 점검 단계에서 이 명령을 부른다(기술 설계 §12.2 0단계).
"""

from __future__ import annotations

from django.conf import settings
from django.core.checks import Warning, register


def pending_privacy_sections() -> list[str]:
    from apps.content.privacy import privacy_document

    return [str(item) for item in privacy_document()["pending_ids"]]


HINT = (
    "content/privacy.yml 의 각 항목 본문을 고객 확정값으로 채우고 status 를 confirmed 로 "
    "바꾼 뒤 다시 배포하십시오 (REQ-N-023 ① · REQ-F-050 · T-F)."
)


def message(pending: list[str]) -> str:
    return "개인정보 처리방침 본문이 확정되지 않았습니다(미확정 항목: " + ", ".join(pending) + ")."


@register("content")
def privacy_content_confirmed(app_configs, **kwargs):
    if getattr(settings, "DJANGO_ENV", "local") not in ("production", "staging"):
        return []
    pending = pending_privacy_sections()
    if not pending:
        return []
    return [Warning(message(pending), hint=HINT, id="content.W001")]
