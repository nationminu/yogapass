"""요건 ⑧ — 표준 시드 (기술 설계 §10.1 ⑧ · §10.2).

**고정 시드다 — 재실행해도 같은 결과가 된다**
(문의는 `submit_token` 이 결정적이라 중복 생성되지 않는다).
1차분 범위

    ① 문의 데이터 N건 (기본 20건). 이름·문의 내용에 `TEST-` 접두어가 붙어
       `qa_purge_test_data` 로 한 번에 지워진다(§10.4).
    ② **표시 번호 1,000건 생성 검사** — `--refs` 로 실행하면 `core.refs.new_display_no()` 를
       1,000건 만들어 **중복 건수**와 **인접 증가(연번처럼 보이는) 비율**을 출력한다
       (REQ-N-R-010 ④ "연번 증가 0건" 판정의 근거 자료. 2차 예약번호 판정에 그대로 쓴다).

2차에는 슬롯 400 · 예약 200 · 상담 100 시드가 여기에 추가된다.
"""

from __future__ import annotations

import datetime as dt

from apps.core.clock import now
from apps.core.refs import new_display_no
from apps.inquiry.models import Inquiry
from qa.base import QaCommand

TEST_PREFIX = "TEST-"
NAMES = ["김검증", "이표본", "박시드", "최확인", "정판정"]


class Command(QaCommand):
    help = "검증용 표준 시드를 만든다 (고정 시드 · 재실행 안전)"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--count", type=int, default=20, help="문의 시드 건수")
        parser.add_argument(
            "--refs", type=int, default=0, help="표시 번호 생성 검사 건수(예: 1000)"
        )

    def handle(self, *args, **options) -> None:
        created = 0
        moment = now()
        for index in range(options["count"]):
            token = "qa-seed-%04d" % index
            _, made = Inquiry.objects.get_or_create(
                submit_token=token,
                defaults={
                    "name": TEST_PREFIX + NAMES[index % len(NAMES)],
                    "phone": "010-0000-%04d" % (index % 10000),
                    "message": TEST_PREFIX + "표준 시드 문의 %d번입니다." % index,
                    "consent_at": moment - dt.timedelta(minutes=index),
                    "created_at": moment - dt.timedelta(minutes=index),
                    "source_ip_hash": "seed",
                },
            )
            created += 1 if made else 0
        self.stdout.write(
            "inquiry 시드 %d건 요청 → 신규 %d건 / 기존 %d건"
            % (options["count"], created, options["count"] - created)
        )

        if options["refs"]:
            total = options["refs"]
            values = [new_display_no() for _ in range(total)]
            duplicates = total - len(set(values))
            ascending = sum(1 for a, b in zip(values, values[1:], strict=False) if b > a)
            self.stdout.write(
                "표시 번호 %d건 생성: 중복 %d건 · 인접 증가 %d건(%.1f%%, 난수라면 약 50%%)"
                % (total, duplicates, ascending, ascending / max(total - 1, 1) * 100)
            )
            self.stdout.write("예시 3건: " + ", ".join(values[:3]))
