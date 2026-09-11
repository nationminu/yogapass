# developer/ — 개발팀

승인된 기획·디자인을 실제 홈페이지로 구현합니다. 에이전트 정의: 틀 저장소 `.claude/agents/developer.md` · 문서 템플릿: 틀 저장소 `templates/docs/developer/`

## 산출물 (P4, P5)
| 파일 | 내용 | 검토자 |
|---|---|---|
| `04_tech-design.md` | 기술 설계서 — 스택·구조·로컬 실행 방법 (**구현 전 승인 필수**) | devops, qa |
| `site/` | ★ 홈페이지 소스코드 (`site/README.md`에 실행 방법) | designer, planner |
| `04_dev-report.md` | 개발 보고서 — REQ/SCR별 구현 현황, 로컬 빌드 확인 결과 | designer, planner |
| `WORKLOG.md` | 작업 과정 로그 | — |

P5에서는 `shared/tickets/DEF-*` 결함을 수정하고 티켓의 조치 절을 기입합니다.

## 입력 → 출력
- **입력**: `planning/02_*.md`, `design/03_*.md`, `design/mockups/`, `design/assets/`
- **출력 사용처**: qa(P5 검증), devops(P7 배포), P8 운영 가이드

## 검토 참여
P1 계획서, P2 기획, P3 디자인, P5 결함 판정, P7 배포 계획, P6·P8 보고서
