"""운영 배포 사전 점검 (REQ-N-023 ① — 오픈 판정 기준).

배포 스크립트의 0단계에서 부른다. 확정되지 않은 공개 콘텐츠가 남아 있으면 **종료 코드 1** 로 끝나
배포가 진행되지 않는다. 검증 환경(staging)에서는 미확정 본문 그대로 판정해야 하므로 `--warn-only`
를 쓴다.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.content.checks import pending_privacy_sections


class Command(BaseCommand):
    help = "운영 배포 전 [TBD] 잔존 여부를 점검한다 (REQ-N-023 ①)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--warn-only", action="store_true", help="발견해도 종료 코드 0 (스테이징용)"
        )

    def handle(self, *args, **options) -> None:
        pending = pending_privacy_sections()
        if not pending:
            self.stdout.write(self.style.SUCCESS("check_release OK pending=0"))
            return
        detail = ",".join(pending)
        line = f"check_release FAILED pending={len(pending)} sections=[{detail}]"
        if options["warn_only"]:
            self.stdout.write(self.style.WARNING(line + " (warn-only)"))
            return
        self.stderr.write(self.style.ERROR(line))
        self.stderr.write(
            "개인정보 처리방침 본문(content/privacy.yml)을 고객 확정값으로 채우고 "
            "status 를 confirmed 로 바꾼 뒤 다시 배포하십시오 (REQ-F-050 · T-F)."
        )
        raise SystemExit(1)
