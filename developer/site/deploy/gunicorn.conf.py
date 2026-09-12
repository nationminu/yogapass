"""gunicorn 설정 (기술 설계 §2.0 — sync worker)."""

import os

bind = f"0.0.0.0:{os.environ.get('GUNICORN_PORT', '8000')}"
workers = int(os.environ.get("GUNICORN_WORKERS", "3"))
worker_class = "sync"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(M)sms'
forwarded_allow_ips = "*"  # nginx 만 앞에 둔다. 실제 IP 판정은 TRUSTED_PROXY_COUNT 로 한다
