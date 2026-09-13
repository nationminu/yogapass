"""요건 ⑧ — 동시 요청 스크립트 (기술 설계 §10.1 ⑧).

문의 폼에 **동시에 N건**을 제출해 ① 빈도 제한이 동시 요청에서도 성립하는지
② 같은 토큰을 동시에 쓰면 저장이 1건으로 막히는지(REQ-F-046 ②)를 확인한다.

    # 서로 다른 토큰으로 20건 동시 제출 (빈도 제한 재현)
    python qa/concurrency.py --url http://localhost:8000/location --count 20

    # **같은 토큰**으로 5건 동시 제출 (중복 제출 방지 재현)
    python qa/concurrency.py --url http://localhost:8000/location --count 5 --same-token

출력: 상태 코드별 집계 + 소요 시간.
저장 건수는 `manage.py qa_show inquiry --count-only` 로 확인한다.
Django 를 import 하지 않으므로 **컨테이너 밖에서도** 표준 라이브러리만으로 돌아간다.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

TOKEN_RE = re.compile(r'name="submit_token" value="([^"]+)"')
CSRF_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')
FIELDS = {
    "name": "TEST-동시제출",
    "phone": "010-1234-5678",
    "message": "TEST-동시 제출 검증입니다.",
    "consent": "on",
}


def _opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def fetch_form(url: str):
    opener, jar = _opener()
    with opener.open(url, timeout=10) as response:
        body = response.read().decode("utf-8", "replace")
    token = TOKEN_RE.search(body)
    csrf = CSRF_RE.search(body)
    return opener, jar, (token.group(1) if token else ""), (csrf.group(1) if csrf else "")


def submit(url: str, shared=None):
    opener, jar, token, csrf = fetch_form(url)
    if shared:
        token = shared
    data = dict(FIELDS)
    data["submit_token"] = token
    data["csrfmiddlewaretoken"] = csrf
    request = urllib.request.Request(  # noqa: S310 - http 고정 URL 만 쓴다(검증 스크립트)
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Referer": url, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with opener.open(request, timeout=15) as response:
            return response.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:  # noqa: BLE001 - 집계 목적
        return f"error:{type(exc).__name__}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000/location")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--workers", type=int, default=0, help="기본값 = --count (전부 동시)")
    parser.add_argument("--same-token", action="store_true", help="같은 토큰으로 동시 제출")
    args = parser.parse_args()

    shared = None
    if args.same_token:
        _, _, shared, _ = fetch_form(args.url)
        print(f"공유 토큰으로 제출합니다: {shared[:16]}…")

    workers = args.workers or args.count
    started = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: submit(args.url, shared), range(args.count)))
    elapsed = time.time() - started

    print("요청 %d건 · 동시 %d · 소요 %.2fs" % (args.count, workers, elapsed))
    for code, count in sorted(Counter(results).items(), key=lambda item: str(item[0])):
        print("  %-10s %d건" % (code, count))
    print("저장 건수는 `manage.py qa_show inquiry --count-only` 로 확인하십시오.")


if __name__ == "__main__":
    main()
