"""검증 도구 공통 골격 (기술 설계 §10.2 공통 행).

· 모든 `qa_*` 명령은 **`QA_TOOLS_ENABLED=1` 이 아니면 종료 코드 2** 로 끝난다.
  (운영 이미지에는 이 디렉토리 자체가 없어 명령이 등록되지도 않는다 — §10.6 ②④)
· 출력 형식은 `--format table|json` 공통이며, json 은 **증거 파일로 그대로 첨부**할 수 있는
  단일 JSON 배열이다.
· **결과 0건도 종료 코드 0** 이다(오류 = 1 과 구분한다).
"""

from __future__ import annotations

import datetime as dt
import json
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

EXIT_DISABLED = 2


class QaCommand(BaseCommand):
    """QA_TOOLS_ENABLED 가드 + 공통 출력 옵션."""

    def add_arguments(self, parser) -> None:
        parser.add_argument("--format", choices=["table", "json"], default="table")

    def execute(self, *args, **options):
        if not getattr(settings, "QA_TOOLS_ENABLED", False):
            self.stderr.write("이 환경에서는 사용할 수 없습니다 (QA_TOOLS_ENABLED 미설정).")
            sys.exit(EXIT_DISABLED)
        return super().execute(*args, **options)

    # ------------------------------------------------------------------ 출력
    def emit(self, rows: list[dict], columns: list[str], fmt: str) -> None:
        if fmt == "json":
            self.stdout.write(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
            return
        if not rows:
            self.stdout.write("(0건)")
            return
        widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
        self.stdout.write(" | ".join(c.ljust(widths[c]) for c in columns))
        self.stdout.write("-+-".join("-" * widths[c] for c in columns))
        for row in rows:
            self.stdout.write(" | ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))
        self.stdout.write("(%d건)" % len(rows))


# ---------------------------------------------------------------- 공통 헬퍼
def parse_since(raw: str | None):
    """--since <ISO8601> 해석. 시간대가 없으면 Asia/Seoul 로 본다."""
    if not raw:
        return None
    value = dt.datetime.fromisoformat(raw)
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    return value


def stamp(value) -> str:
    """ISO8601(UTC) + KST 병기 (§10.2)."""
    if value is None:
        return ""
    return "{} (KST {})".format(
        value.isoformat(),
        timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S"),
    )


def mask_name(value: str) -> str:
    if not value:
        return ""
    if len(value) == 1:
        return "*"
    if len(value) == 2:
        return value[0] + "*"
    return value[0] + "*" * (len(value) - 2) + value[-1]


def mask_phone(value: str) -> str:
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) < 7:
        return "***"
    return f"{digits[:3]}-****-{digits[-4:]}"


def mask_email(value: str) -> str:
    if "@" not in (value or ""):
        return mask_name(value or "")
    local, domain = value.split("@", 1)
    return f"{mask_name(local)}@{domain}"
