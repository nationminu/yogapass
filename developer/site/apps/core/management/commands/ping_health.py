"""`/healthz` 5분 폴링 — 일일 운영 요약 메일 ⓐ 의 원천 (기술 설계 §3.3 · §3.4).

⚠ **호출 대상은 항상 앱에 직접**이다 — nginx 를 경유하지 않고 `SITE_BASE_URL` 도 쓰지 않는다
   (devops R2 #3). 스테이징의 `auth_basic` 예외를 만들지 않기 위한 규칙이며,
   기본값은 `HEALTHCHECK_URL=http://app:8000/healthz` 다.

`unless-stopped` 는 "종료"만 잡고 "살아 있지만 응답 실패"는 잡지 못한다(devops R1 #15).
그 상태를 기록으로 남기는 것이 이 명령의 목적이다.
"""

from __future__ import annotations

import urllib.error
import urllib.request

from django.core.management.base import BaseCommand

from apps.core.jobs import run_job
from config.env import env, env_int

JOB = "ping_health"


class Command(BaseCommand):
    help = "앱 /healthz 를 직접 호출해 결과를 core_jobrunlog 에 남긴다"

    def handle(self, *args, **options) -> None:
        url = env("HEALTHCHECK_URL", "http://app:8000/healthz")
        timeout = env_int("HEALTHCHECK_TIMEOUT_SECONDS", 5)
        with run_job(JOB) as job:
            if job.skipped:
                return
            try:
                with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310
                    code = response.getcode()
                    body = response.read(16).decode("utf-8", "replace").strip()
            except (urllib.error.URLError, OSError) as exc:
                job.note(f"url={url} result=error detail={str(exc)[:200]}")
                self.stderr.write(f"ping_health error: {exc}")
                raise
            ok = code == 200 and body == "ok"
            job.note(f"url={url} status={code} ok={ok}")
            if not ok:
                self.stderr.write(f"ping_health unexpected: status={code} body={body!r}")
                raise RuntimeError(f"healthz 응답이 정상이 아닙니다: status={code}")
            self.stdout.write("ping_health ok")
