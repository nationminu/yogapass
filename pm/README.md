# pm/ — 총괄 PM · PMO

총괄 PM(사용자)의 요청·결정과 PMO 에이전트(틀 저장소 `.claude/agents/pmo.md`)의 관리 문서를 모아 둡니다.

## 구성
| 경로 | 내용 | 작성 |
|---|---|---|
| `STATUS.md` | ★ 프로젝트 현황판 (상태 기준 문서) | pmo / 오케스트레이터 |
| `WORKLOG.md` | PMO 작업 과정 로그 | pmo |
| `requests/CR-000_initial-request.md` | 고객 최초 요청 (원문 보존) | 오케스트레이터(원문), pmo(정리) |
| `requests/CR-{nnn}_*.md` | 변경 요청 + 영향도 분석 + PM 결정 | 오케스트레이터(원문), pmo(분석) |
| `01_project-plan.md` | P1 프로젝트 계획서 | pmo |
| `gates/G{n}_{slug}.md` | 단계별 게이트 문서 | pmo (PM 결정 절은 PM 응답으로 기입) |
| `06_interim-report.md` | P6 중간보고서 | pmo |
| `08_final-report.md` | P8 최종 보고서 | pmo |
| (틀 저장소) `templates/docs/pm/` | change-request, project-plan, gate, interim-report, final-report 템플릿 | — |

## 게이트 파일
`G1_plan` · `G2_planning` · `G3_design` · `G4_development` · `G5_verification` · `G6_interim-report` · `G7_deployment` · `G8_closing`
