# shared/ — 팀 간 소통 공간

서브에이전트는 서로를 직접 호출할 수 없으므로, 모든 팀 간 소통은 이 디렉토리의 **파일**로 이루어집니다.
오케스트레이터가 이 파일들을 근거로 다음 에이전트를 호출합니다.

## 구성
| 디렉토리 | 용도 | 파일명 규칙 | 템플릿 | 작성 |
|---|---|---|---|---|
| `reviews/` | 교차 검토 기록 | `{단계}_{대상}_{검토자}_r{n}.md`<br>CR 영향 의견: `CR-{nnn}_impact_{팀}.md` | `templates/docs/shared/review.md` | 검토자 (처리 결과 열은 Owner) |
| `tickets/` | 팀 간 요청·질의·자료 요청 | `TKT-{발행팀}-{nnn}_to-{수신팀}_{slug}.md` | `templates/docs/shared/ticket.md` | 발행 팀 (처리 결과는 수신 팀) |
| `tickets/` | 결함 | `DEF-{nnn}_{slug}.md` | `templates/docs/shared/defect.md` | qa (조치 절은 developer) |
| `decisions/` | 결정 기록 | `ADR-{nnn}_{slug}.md` | `templates/docs/shared/decision.md` | pmo |
| `meetings/` | 회의록 (킥오프·조율·회고) | `MTG-{YYYYMMDD}_{slug}.md` | `templates/docs/shared/meeting.md` | pmo |

팀 코드(파일명용): `pm` · `planning` · `design` · `developer` · `qa` · `devops`

## 언제 무엇을 쓰나
| 상황 | 수단 |
|---|---|
| 단계 산출물을 검토하고 수정 요청 | **리뷰** |
| 작업 중 다른 팀에 질문·자료·수정을 요청 (리뷰 주기 밖) | **티켓** |
| 테스트에서 요구사항·명세와 다른 동작 발견 | **결함(DEF)** |
| 선택지 중 하나를 골라야 하고 되돌리기 어려움, PM 결정, 팀 간 합의 | **결정 기록(ADR)** |

## 상태 흐름
**티켓(TKT)**
```
open → in-progress → resolved (수신 팀 처리) → closed (발행 팀 확인)
                  └→ rejected (사유 기재)
```
**결함(DEF)**
```
open → in-progress → resolved (developer) → closed (qa 재검증)
                                          └→ reopened
                  └→ rejected (qa·planner 합의)
```
**결정(ADR)**: `proposed → accepted | rejected`, 이후 번복 시 새 ADR을 만들고 기존 ADR은 `superseded`

## 원칙
- 타 팀 산출물을 직접 수정하지 않는다 — 리뷰나 티켓으로 요청한다.
- 하나의 티켓·결함에는 하나의 주제만 담는다.
- 결론이 난 논의는 반드시 파일 상태(status)에 반영한다. 상태가 실제와 다르면 게이트를 통과할 수 없다.
