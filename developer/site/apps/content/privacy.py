"""개인정보 처리방침 본문 로더 (기술 설계 §6.2 — pages/privacy.html 이 이 파일을 직접 읽는다).

DB 테이블을 만들지 않는 이유: 1차 테이블 목록(§5.1)에 없고, 본문은 고객이 확정하는
**문서 한 벌**이라 파일이 단일 원본이면 충분하다. 2차 목차 재작성(TR-07)도 파일 교체다.
파일 변경 시각을 캐시 키로 써서 재기동 없이 반영된다.

표 블록은 여기서 (라벨, 값) 쌍으로 펼친다 — <768px 카드 전환(페이지 디자인 §5.2)에 쓰는
`data-label` 을 템플릿에서 인덱스 비교로 만들지 않기 위함이다.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import yaml
from django.conf import settings

logger = logging.getLogger("content")

PRIVACY_PATH = Path(settings.BASE_DIR) / "content" / "privacy.yml"


@lru_cache(maxsize=4)
def _load(_cache_key: float) -> dict:
    if not PRIVACY_PATH.is_file():
        logger.warning("content.privacy_missing path=%s", PRIVACY_PATH)
        return {}
    return yaml.safe_load(PRIVACY_PATH.read_text(encoding="utf-8")) or {}


def _expand(sections: list) -> list:
    for section in sections:
        for block in section.get("body") or []:
            if block.get("type") != "table":
                continue
            columns = block.get("columns") or []
            block["labeled_rows"] = [
                [
                    {"label": columns[index] if index < len(columns) else "", "value": cell}
                    for index, cell in enumerate(row)
                ]
                for row in (block.get("rows") or [])
            ]
    return sections


def privacy_document() -> dict:
    try:
        key = PRIVACY_PATH.stat().st_mtime
    except OSError:
        key = 0.0
    data = _load(key)
    sections = _expand(data.get("sections") or [])
    return {
        "effective_date": data.get("effective_date"),
        "version": data.get("version"),
        "sections": sections,
        "toc": [{"id": s.get("id"), "title": s.get("title")} for s in sections],
        "pending_ids": [s.get("id") for s in sections if s.get("status") != "confirmed"],
    }
