---
id: DEF-009
from: qa
to: developer
phase: P5
severity: minor
status: open
related_req: [REQ-N-020, REQ-F-050]
related_tc: [TC-112]
related_scr: [SCR-006]
found_cycle: 1
created: 2026-09-13
---

# DEF-009 처리방침 수집 항목 표에 실제 저장 컬럼 2개(`consent_at`·`phone_norm`)가 빠져 양방향 대조가 어긋난다

## 환경
- 실행 방법: `docker exec -e QA_TOOLS_ENABLED=1 yogapass-app-1 python manage.py qa_pii_columns`
- 대조 대상: `developer/site/content/privacy.yml` 의 `p2 수집하는 개인정보 항목과 수집 방법` 표
- 대상 버전: 개발 보고서 v0.3

## 재현 절차
1. `docker exec -e QA_TOOLS_ENABLED=1 yogapass-app-1 python manage.py qa_pii_columns`
2. `grep -n -A12 '수집하는 개인정보 항목' developer/site/content/privacy.yml`
3. 두 목록을 양방향으로 대조한다.

## 기대 결과
근거: **REQ-N-020**(Must) 수용 기준 — *"Given **DB 스키마의 개인정보 컬럼 전량**과 처리방침 수집 항목 목록 When 대조한다 Then **양방향 누락 0건**(스키마에 있는데 방침에 없는 항목 0건, 그 반대도 0건)"*
또한 `privacy.yml` p2 본문이 스스로 *"표의 항목은 데이터베이스가 실제로 저장하는 항목과 **양방향으로 일치합니다**(REQ-N-020)."* 라고 선언한다.

## 실제 결과

**스키마 (`qa_pii_columns` 출력 — `inquiry_inquiry` 6컬럼)**

| 컬럼 | 수집 목적 | 보관 | 방침 표 기재 |
|---|---|---|---|
| `name` | 문의 답변을 위한 문의자 식별 | 365 | ○ ("이름") |
| `phone` | 문의 답변 연락 | 365 | ○ ("휴대폰 번호") |
| `phone_norm` | 표기 형식과 무관한 조회·중복 판정(생성 컬럼) | 365 | **✗ 없음** |
| `message` | 문의 내용 확인·답변 | 365 | ○ ("문의 내용") |
| `consent_at` | 수집·이용 동의 시각 증빙 | 365 | **✗ 없음** |
| `source_ip_hash` | 악용 방지 — 솔트 해시만 저장 | 365 | ○ ("출처 IP 의 해시값(원본 IP 미저장)") |

→ **스키마에 있는데 방침에 없는 항목 2건.** (`phone_norm` 은 `phone` 의 정규화 파생값, `consent_at` 은 동의 시각이라 성격은 다르지만, 둘 다 `PII_FIELDS` 로 선언된 개인정보 컬럼이므로 수용 기준의 "스키마의 개인정보 컬럼 전량"에 포함된다.)

역방향(방침에 있는데 스키마에 없는 항목)은 "접속 로그"가 애플리케이션 DB 컬럼이 아니라 컨테이너 로그라서 대조 대상이 모호하다 — 이 부분도 표기를 정리해 두면 P7 재확인이 쉬워진다.

## 증거
- `qa/evidence/cycle1/17_pii_checkrelease.txt` · `17b_recheck_direct.txt` (`qa_pii_columns` 출력)
- `developer/site/content/privacy.yml` p2 표 (34~37행)

## 비고 (판정 시점)
`/privacy` 11항목은 전부 `status: pending`(고객 확정 대기 T-F)이므로 **본문 문구의 최종 판정은 값 확정 후(P7)** 다. 그러나 **수집 항목 표는 제작이 스키마를 근거로 채운 부분**이고 "양방향 일치"를 본문에서 선언하고 있으므로, 지금 시점에 고칠 수 있는 불일치로 판단해 결함으로 발행한다. 처리 방식은 ⓐ 표에 두 항목을 추가하거나 ⓑ 파생·증빙 컬럼의 표기 규칙을 방침 머리말에 명시하는 것 중 하나면 된다.

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
| 2차 | | | `qa_pii_columns` ↔ `privacy.yml` 재대조 + TC-070(목차 11항목) 회귀 |
