"""스테이징 설정 — 운영과 같은 파이프라인 + 색인 차단(기술 설계 §3.5.1)."""

from .production import *  # noqa: F401,F403

# 전 응답 noindex 강제 (nginx 와 2중 — 기술 설계 §12.3 #9)
FORCE_NOINDEX = True
