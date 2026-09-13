---
id: DEF-006
from: qa
to: developer
phase: P5
severity: minor
status: open
related_req: [REQ-F-003, REQ-N-002]
related_tc: [TC-004]
related_scr: [SCR-003]
found_cycle: 1
created: 2026-09-13
---

# DEF-006 대표 전화 미확정 + 자기 참조 화면에서 고정 바가 없는데 본문 하단 여백 76px이 남는다

## 환경
- 실행 방법 / URL: 운영 미리보기 `http://localhost:8001/location` (대표 전화 `[TBD]` 상태 = 현재 기본 시드)
- 브라우저 · 뷰포트: Chrome headless(puppeteer-core) 360×780 · 768×1024 (1280px은 정상)
- 대상 버전: 개발 보고서 v0.3, 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `content/site.yml`의 `settings.phone`이 `value: null / is_published: false`(현재 기본값)인 상태에서 `seed_content`를 실행한다.
2. `cd qa/tools && BASE=http://localhost:8001 node probe2.js`
3. `/location` 행의 `고정바` 와 `body.padding-bottom` 값을 본다.

## 기대 결과
근거: **REQ-F-003 ②**(Must) 수용 기준 — *"Given 대표 전화 미확정 Then 고정 바가 노출되지 않고 **본문 하단 여백도 적용되지 않으며** 폼 하단 대체 연락 안내는 그대로 보인다"*
(§3.0 G-6 ② 단서 · G-3 "고정 바가 **노출되는 뷰포트에서** 본문 하단 여백을 둔다")

## 실제 결과

| 화면 | 뷰포트 | 고정 바 | `body` padding-bottom | 판정 |
|---|---|---|---|---|
| `/location` | 360px | **없음**(기대대로) | **76px** | **여백이 남는다 — 위반** |
| `/location` | 768px | **없음**(기대대로) | **76px** | **위반** |
| `/location` | 1280px | 없음 | 0px | 정상 |
| `/` (비자기참조) | 360px | 있음 h=61 | 77px | 정상 |

- 고정 바가 사라지는 조건(자기 참조 + 전화 `[TBD]`)에서 **여백 제거 조건만 함께 적용되지 않았다.**
- 영향: 1차 유일 폼 화면인 `/location` 하단에 빈 여백 76px이 남아 페이지 디자인의 하단 간격과 달라진다. 기능 영향은 없다.
- 참고: 전화번호를 확정 값으로 시드하면 `/location`에 "전화 문의" 전폭 1버튼 고정 바가 정상 노출되고 여백 77px이 맞는 상태가 된다(증거 `48_…`). 즉 **`[TBD]` 경로에서만 나타난다**.

## 증거
- `qa/evidence/cycle1/44_fixedbar_focus_nojs.txt` (전화 `[TBD]` 상태 측정표 — `/location` 360·768px `body.padding-bottom=76px`, 고정바 없음)
- `qa/evidence/cycle1/48_fixedbar_phone_confirmed.txt` (전화 확정 상태 — 고정 바 1버튼 + 여백 77px, 정상)

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
| 2차 | | | TC-004 재수행 + TC-003·005·007(전화 확정/미확정 양쪽) 회귀 |
