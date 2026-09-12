from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "apps.content"
    label = "content"
    verbose_name = "콘텐츠"

    def ready(self) -> None:
        from apps.content import checks  # noqa: F401 - 시스템 점검 등록 (REQ-N-023 ①)
