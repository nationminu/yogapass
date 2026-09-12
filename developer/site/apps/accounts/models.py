"""커스텀 사용자 모델 (기술 설계 §5.0).

⚠ 1차에는 운영자 계정만 존재하고 회원 가입 경로를 열지 않는다.
   그래도 AUTH_USER_MODEL 을 1차 첫 마이그레이션에 넣는다 —
   나중에 바꾸면 전 외래키·마이그레이션을 재작성해야 한다.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("role", User.Role.STAFF)
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("role", User.Role.STAFF)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("슈퍼유저는 is_staff·is_superuser 가 참이어야 합니다.")
        return self._create(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        MEMBER = "member", "회원"
        STAFF = "staff", "운영자"

    email = models.EmailField("이메일", unique=True)
    name = models.CharField("이름", max_length=60, blank=True, default="")
    role = models.CharField("역할", max_length=16, choices=Role.choices, default=Role.STAFF)
    is_active = models.BooleanField("활성", default=True)
    is_staff = models.BooleanField("관리자 화면 접근", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "accounts_user"
        verbose_name = "사용자"

    def __str__(self) -> str:
        return self.email
