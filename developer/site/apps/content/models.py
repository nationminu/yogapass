"""1차 콘텐츠 모델 — 강사 · 수업 유형 · 사이트 설정 (기술 설계 §5.1).

1차에는 content/*.yml 이 단일 원본이고 seed_content 명령이 DB로 upsert 한다.
2차에 관리자 CRUD 가 생기면 seed_content 는 초기 적재 전용으로 역할이 바뀐다.
"""

from __future__ import annotations

import uuid

from django.db import models


class Instructor(models.Model):
    public_ref = models.UUIDField("외부 식별자", default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField("시드 키", max_length=60, unique=True)
    name = models.CharField("이름", max_length=60)
    headline = models.CharField("한 줄 소개", max_length=120, blank=True, default="")
    bio = models.TextField("소개", blank=True, default="")
    credentials = models.JSONField("경력·자격", default=list, blank=True)
    classes = models.JSONField("담당 수업", default=list, blank=True)
    display_order = models.PositiveSmallIntegerField("표시 순서", default=0)
    is_active = models.BooleanField("공개", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_instructor"
        ordering = ["display_order", "id"]
        verbose_name = "강사"

    def __str__(self) -> str:
        return self.name

    @property
    def initial(self) -> str:
        return (self.name or "?")[:1]


class LessonType(models.Model):
    slug = models.SlugField("시드 키", max_length=60, unique=True)
    name = models.CharField("유형명", max_length=60)
    tag = models.CharField("분류 태그", max_length=20, blank=True, default="")
    description = models.TextField("설명", blank=True, default="")
    default_duration_min = models.PositiveSmallIntegerField("기본 소요(분)", null=True, blank=True)
    default_capacity = models.PositiveSmallIntegerField("기본 정원", null=True, blank=True)
    display_order = models.PositiveSmallIntegerField("표시 순서", default=0)
    is_active = models.BooleanField("공개", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_lessontype"
        ordering = ["display_order", "id"]
        verbose_name = "수업 유형"

    def __str__(self) -> str:
        return self.name


class SiteSetting(models.Model):
    """상호·주소·전화·운영시간 등 표시 값.

    값이 [TBD] 인 항목은 is_published=False 로 두고 **화면에 렌더하지 않는다**
    (REQ-N-023 — [TBD] 문자열을 화면에 출력하지 않는다).
    """

    key = models.CharField("키", max_length=60, unique=True)
    value = models.JSONField("값", null=True, blank=True)
    is_published = models.BooleanField("확정·노출", default=False)
    note = models.CharField("비고", max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_sitesetting"
        ordering = ["key"]
        verbose_name = "사이트 설정"

    def __str__(self) -> str:
        return self.key
