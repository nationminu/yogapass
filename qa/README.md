# qa/ — 품질검증팀

사이트가 요구사항과 품질 기준을 충족하는지 실제로 실행해서 검증합니다. 에이전트 정의: 틀 저장소 `.claude/agents/qa.md` · 문서 템플릿: 틀 저장소 `templates/docs/qa/`

## 산출물
| 단계 | 파일 | 내용 | 검토자 |
|---|---|---|---|
| P5 | `05_test-plan.md` | 테스트 계획서 — 범위·유형·환경·진입/종료 기준 | developer, planner |
| P5 | `05_test-cases.md` | 테스트 케이스 + 요구사항 추적 매트릭스(RTM) | developer, planner |
| P5 | `05_test-report.md` | 테스트 결과 보고서 — 통계·결함·품질 지표·권고 | developer, planner |
| P7 | `07_smoke-test-report.md` | 운영 환경 스모크 테스트 결과 | devops |
| — | `evidence/` | 테스트 증거(출력 로그, 스크린샷, Lighthouse 리포트) | — |
| — | `WORKLOG.md` | 작업 과정 로그 | — |

결함은 `shared/tickets/DEF-{nnn}_*.md`로 발행합니다. **qa는 소스코드를 수정하지 않습니다.**

## 결함 흐름
```
open → in-progress → resolved (developer) → closed (qa 재검증 통과)
                                          └→ reopened → in-progress …
                  └→ rejected (결함 아님 — qa·planner 합의)
```

## 검토 참여
P2 기획(테스트 가능성), P4 기술 설계, P7 배포 계획, P6·P8 보고서
