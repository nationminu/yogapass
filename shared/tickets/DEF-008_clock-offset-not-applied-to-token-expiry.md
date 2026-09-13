---
id: DEF-008
from: qa
to: developer
phase: P5
severity: minor
status: open
related_req: [REQ-F-046]
related_tc: [TC-059]
related_scr: [SCR-003]
found_cycle: 1
created: 2026-09-13
---

# DEF-008 `QA_CLOCK_OFFSET_SECONDS`가 `submit_token` 만료 판정에 적용되지 않아 §9.6 ⑦의 `expired` 분기를 P5에서 유발할 수 없다

## 환경
- 실행 방법: 정상 시계 컨테이너(`:8010`)에서 토큰을 발급받고, **`QA_CLOCK_OFFSET_SECONDS=90000`(+25시간)** 컨테이너(`:8020`)에 그 토큰으로 POST
  `docker compose -f compose.yaml -f compose.local.yaml run --rm -d -p 8020:8000 -e QA_TOOLS_ENABLED=1 -e QA_CLOCK_OFFSET_SECONDS=90000 app python manage.py runserver 0.0.0.0:8000`
- 대상 버전: 개발 보고서 v0.3

## 재현 절차
1. `:8010/location` 을 GET 해 `submit_token` 값을 얻는다(발급 시각 = 실제 시각).
2. `:8020` 컨테이너 기동 로그에 `CLOCK OFFSET: 90000s` 가 찍힌 것을 확인한다.
3. 1에서 얻은 토큰으로 `:8020/location` 에 정상 값 POST.

## 기대 결과
- 기술 설계 v0.4 **§9.6 ⑦** — *"`submit_token` **만료**·부재·변조(발급 후 **24시간 초과** / 토큰 없이 제출 / 서명 불일치) → **200** + '시간이 지나 문의가 접수되지 않았습니다.' + 폼 재렌더 + 입력값 보존 + 새 토큰 · 저장 **0건** · `inquiry.expired token_state=expired|missing|invalid`"*
- 발급 후 25시간이 지난 것과 같은 기준 시각에서 제출했으므로 **`token_state=expired`** 가 나와야 한다.

## 실제 결과
**정상 접수(①)로 처리됐다.**

```
=== ⑦ 만료 토큰 제출(+25h) ===
HTTP=200
BODY: … 문의가 접수되었습니다. | 확인 후 남겨주신 연락처로 연락드리겠습니다. …
form_present=false role_status=true role_alert=false
new_token=(none)

(로그) 2026-09-13T16:11:44 INFO core.inquiry inquiry.created ref=fe60c477-…
```

### 원인 (코드 기준 · `apps/inquiry/services.py` 89행)
```python
value = signing.loads(raw, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
```
Django `signing.loads(max_age=…)` 는 **서명에 박힌 타임스탬프와 `time.time()`** 을 비교한다. `apps/core/clock.now()` 를 경유하지 않으므로 `QA_CLOCK_OFFSET_SECONDS` 의 영향을 받지 않는다. 기술 설계 **§10.3 "적용(오프셋이 움직인다)" 목록**에도 토큰 만료 경로가 없다(요구사항 §5.3 환경 요건 ⑩의 "대상 수용 기준" 목록도 2차 토큰들만 열거하고, 1차 `submit_token` 24시간 만료는 **PM 결정(2026-09-13) 이후에 생긴 항목**이라 빠져 있다).

## 영향 (판정 공백)
§9.6 ⑦의 세 상태 중 P5가 판정할 수 있는 것은 **`missing`·`invalid` 2종**이고 **`expired` 1종은 유발 수단이 없다.**

| 상태 | 1차 판정 |
|---|---|
| `token_state=missing` (토큰 없이 POST) | **Pass** — 200 + 재작성 안내 + 입력값 4항목 보존 + 새 토큰 · 저장 0 |
| `token_state=invalid` (서명 변조) | **Pass** — 동일 |
| `token_state=expired` (24시간 초과) | **Block — 검증 수단 없음** |

`expired` 는 PM 결정(2026-09-13)의 핵심 사유("폼을 24시간 이상 열어 둔 이용자의 문의가 조용히 버려지는 것을 막는다")에 직접 대응하는 분기이므로, 판정 수단 없이 넘기면 **결정의 목적 자체가 검증되지 않은 채 게이트를 통과**한다.

## 요청 (택일)
- ⓐ `read_token()` 의 만료 판정을 `core.clock.now()` 기준으로 바꾸고 기술 설계 §10.3 "적용" 목록에 이 경로를 추가한다(요건 ⑩과 일관).
- ⓑ `QA_SUBMIT_TOKEN_MAX_AGE_SECONDS` 같은 **검증 전용 토글**을 `qa/qa_settings.py` 에 추가해 TTL을 초 단위로 낮출 수 있게 한다(요건 ④의 "항목별 독립 설정"과 일관).
어느 쪽이든 **운영 이미지에서는 해석되지 않아야 한다**(§10.6 ②③).

## 증거
- `qa/evidence/cycle1/13_clock_offset.txt` (오프셋 컨테이너 제출 결과 + `inquiry.created` 로그)
- `qa/evidence/cycle1/06_form_matrix.txt` (`missing`·`invalid` 2종 Pass)
- `qa/evidence/cycle1/09_inquiry_logs.txt` (`token_state=missing` / `token_state=invalid` 로그)

## 비고
- 같은 회차에서 `QA_CLOCK_OFFSET_SECONDS` 자체는 정상 동작을 확인했다 — 기동 로그 `CLOCK OFFSET: 90000s` 출력, `/healthz` 에 미노출(§10.2 규격 충족), 오프셋 시계에서 빈도 제한 창이 새로 열려 제출이 통과하는 것까지 관측했다.

---

## 조치 (developer 작성)
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | `expired` 유발 → §9.6 ⑦ 전 항목 재판정 + ①⑤(정상·재사용) 회귀 |
