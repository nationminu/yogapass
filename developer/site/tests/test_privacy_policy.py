"""처리방침 수집 항목 ↔ DB 스키마 양방향 대조 (REQ-N-020 · DEF-009).

`manage.py qa_pii_columns` 가 출력하는 목록의 원본은 모델의 `PII_FIELDS` 다.
방침 본문(`content/privacy.yml`)의 수집 항목 표에 그 컬럼들이 **전부** 적혀 있어야 한다.
컬럼을 추가·삭제하면 이 테스트가 먼저 깨진다.
"""

from __future__ import annotations

from django.test import TestCase

from apps.content.privacy import privacy_document
from apps.inquiry.models import Inquiry

COLLECTED_SECTION = "p2"


def collected_items_text() -> str:
    """처리방침 '수집하는 개인정보 항목' 절의 본문 전체를 한 문자열로 펼친다."""
    section = next(s for s in privacy_document()["sections"] if s.get("id") == COLLECTED_SECTION)
    parts: list[str] = [str(section.get("title") or "")]
    for block in section.get("body") or []:
        if block.get("type") == "table":
            for row in block.get("rows") or []:
                parts.extend(str(cell) for cell in row)
        elif block.get("type") == "ul":
            parts.extend(str(item) for item in block.get("items") or [])
        else:
            parts.append(str(block.get("text") or ""))
    return "\n".join(parts)


class CollectedItemsMatchSchemaTests(TestCase):
    def test_every_pii_column_has_a_policy_term(self):
        """선언한 개인정보 컬럼마다 방침 표기 문자열이 지정돼 있다."""
        self.assertEqual(set(Inquiry.PII_FIELDS), set(Inquiry.PII_POLICY_TERMS))

    def test_every_pii_column_appears_in_the_policy_table(self):
        """스키마에 있는데 방침에 없는 항목 0건 (REQ-N-020 수용 기준의 한쪽 방향)."""
        text = collected_items_text()
        missing = [
            f"{column}({term})"
            for column, term in Inquiry.PII_POLICY_TERMS.items()
            if term not in text
        ]
        self.assertEqual(missing, [], f"처리방침 수집 항목 표에 없는 컬럼: {missing}")

    def test_derived_and_consent_columns_are_explained(self):
        """파생 컬럼·동의 시각은 '이용자 직접 입력'이 아니므로 수집 방법을 따로 적는다."""
        text = collected_items_text()
        self.assertIn("자동 생성", text)
        self.assertIn("동의 처리 시 자동 기록", text)
