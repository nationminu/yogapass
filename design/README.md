# design/ — 디자인팀

기획 산출물을 시각 언어와 구현 가능한 디자인 명세로 바꿉니다. 에이전트 정의: 틀 저장소 `.claude/agents/designer.md` · 문서 템플릿: 틀 저장소 `templates/docs/design/`

## 산출물 (P3)
| 파일 | 내용 | 검토자 |
|---|---|---|
| `03_design-concept.md` | 컨셉 시안 2~3안, 비교, 권고 → **PM 선택** | planner, developer |
| `03_design-system.md` | 디자인 토큰(CSS 변수), 컴포넌트(CMP) | planner, developer |
| `03_page-design.md` | SCR별 레이아웃·반응형·인터랙션 명세 | planner, developer |
| `mockups/` | `concept-{a,b,c}.html`, `scr-{nnn}.html` 정적 목업 | — |
| `assets/` | 로고·아이콘·이미지, `SOURCES.md`(출처·라이선스) | — |
| `WORKLOG.md` | 작업 과정 로그 | — |

## 입력 → 출력
- **입력**: `planning/02_*.md`, `pm/01_project-plan.md`, `pm/requests/`
- **출력 사용처**: developer(P4 구현), qa(P5 디자인 일치 검증)

## 검토 참여
P2 기획, P4 구현(디자인 QA), P6·P8 보고서
