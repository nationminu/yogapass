"""content/*.yml → DB upsert (기술 설계 §5.1.1).

⚠ 파일을 고치는 것만으로는 화면에 반영되지 않는다. 이 명령을 1회 실행해야 한다.
   (P8 운영 가이드 "콘텐츠 수정 절차"에 같은 문장을 적는다.)
"""

from __future__ import annotations

from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import Instructor, LessonType, SiteSetting

CONTENT_DIR = Path(settings.BASE_DIR) / "content"


class Command(BaseCommand):
    help = "content/*.yml 의 내용을 DB에 upsert 한다 (키: slug / setting key)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", help="변경 없이 계획만 출력")

    def handle(self, *args, **options) -> None:
        dry = options["dry_run"]
        created = updated = 0
        with transaction.atomic():
            for seed in (self._seed_instructors, self._seed_lesson_types, self._seed_site):
                c, u = seed()
                created, updated = created + c, updated + u
            if dry:
                transaction.set_rollback(True)
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_content 완료 created={created} updated={updated} dry_run={dry}"
            )
        )

    def _load(self, name: str):
        path = CONTENT_DIR / name
        if not path.is_file():
            self.stderr.write(f"시드 파일 없음: {path}")
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _seed_instructors(self) -> tuple[int, int]:
        data = self._load("instructors.yml")
        if data is None:
            return 0, 0
        created = updated = 0
        for order, row in enumerate(data.get("instructors") or [], start=1):
            defaults = {
                "name": row.get("name", ""),
                "headline": row.get("headline") or "",
                "bio": row.get("bio") or "",
                "credentials": row.get("credentials") or [],
                "classes": row.get("classes") or [],
                "display_order": row.get("display_order", order),
                "is_active": bool(row.get("is_active", True)),
            }
            _, is_new = Instructor.objects.update_or_create(slug=row["slug"], defaults=defaults)
            created, updated = (created + 1, updated) if is_new else (created, updated + 1)
        return created, updated

    def _seed_lesson_types(self) -> tuple[int, int]:
        data = self._load("lesson_types.yml")
        if data is None:
            return 0, 0
        created = updated = 0
        for order, row in enumerate(data.get("lesson_types") or [], start=1):
            defaults = {
                "name": row.get("name", ""),
                "tag": row.get("tag") or "",
                "description": row.get("description") or "",
                "default_duration_min": row.get("default_duration_min"),
                "default_capacity": row.get("default_capacity"),
                "display_order": row.get("display_order", order),
                "is_active": bool(row.get("is_active", True)),
            }
            _, is_new = LessonType.objects.update_or_create(slug=row["slug"], defaults=defaults)
            created, updated = (created + 1, updated) if is_new else (created, updated + 1)
        return created, updated

    def _seed_site(self) -> tuple[int, int]:
        data = self._load("site.yml")
        if data is None:
            return 0, 0
        created = updated = 0
        for key, raw in (data.get("settings") or {}).items():
            raw = raw or {}
            value = raw.get("value")
            defaults = {
                "value": value,
                "is_published": bool(raw.get("is_published", False)) and value not in (None, ""),
                "note": raw.get("note") or "",
            }
            _, is_new = SiteSetting.objects.update_or_create(key=key, defaults=defaults)
            created, updated = (created + 1, updated) if is_new else (created, updated + 1)
        return created, updated
