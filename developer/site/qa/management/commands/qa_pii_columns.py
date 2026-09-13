"""요건 ⑪ — 개인정보 컬럼 목록 출력 (기술 설계 §10.1 · §10.2).

    manage.py qa_pii_columns [--format table|json]

REQ-N-020(처리방침 수집 항목 ↔ 스키마 양방향 대조)과 REQ-N-038(항목별 보관 기간) 판정 증거다.

선언 위치: **모델 클래스의 `PII_FIELDS` 딕셔너리**(필드명 → (수집 목적, 마스킹 대상 여부)) +
`RETENTION_KEY`. 설계 원안은 필드 인자 `pii=True` 였으나, Django 에서 필드에 사용자 인자를 주려면
필드 클래스를 상속해야 하고 **마이그레이션 상태가 바뀐다.** 선언을 읽는 쪽(이 명령)의 동작은
같으므로 마이그레이션에 영향이 없는 모델 속성 선언으로 구현했다(기술 설계 v0.4 §10.1 ⑪ 반영).
"""

from __future__ import annotations

from django.apps import apps
from django.conf import settings

from qa.base import QaCommand

COLUMNS = [
    "app",
    "model",
    "table",
    "column",
    "type",
    "purpose",
    "retention_days",
    "masked",
]


class Command(QaCommand):
    help = "개인정보 컬럼 목록(테이블·컬럼·목적·보관 기간)을 출력한다"

    def handle(self, *args, **options) -> None:
        rows = []
        for model in apps.get_models():
            declared = getattr(model, "PII_FIELDS", None)
            if not declared:
                continue
            key = getattr(model, "RETENTION_KEY", "")
            days = settings.RETENTION_DAYS.get(key, "") if key else ""
            for field_name, (purpose, masked) in declared.items():
                field = model._meta.get_field(field_name)
                rows.append(
                    {
                        "app": model._meta.app_label,
                        "model": model.__name__,
                        "table": model._meta.db_table,
                        "column": field.column,
                        "type": field.get_internal_type(),
                        "purpose": purpose,
                        "retention_days": days,
                        "masked": "Y" if masked else "N",
                    }
                )
        self.emit(rows, COLUMNS, options["format"])
