# 강남 요가패스 홈페이지

| 항목 | 내용 |
|---|---|
| 프로젝트 ID (slug) | `yogapass` |
| 고객 | 요가패스 (강남) |
| 착수일 | 2026-09-11 |
| 틀 버전 | site-creator `f2288cc` — 이 프로젝트가 따른 규칙·템플릿의 커밋 |
| 운영 URL | (P7 배포 후 기입) |
| 현재 상태 | [pm/STATUS.md](pm/STATUS.md) 참조 |

이 저장소는 site-creator 틀로 진행한 홈페이지 제작 프로젝트의 **독립 저장소**입니다.
진행 규칙은 틀 저장소의 `CLAUDE.md`를, 문서 양식은 틀 저장소의 `templates/docs/`를 따릅니다.

## 구조

```
yogapass/
├── README.md                # 이 문서
├── pm/                      # PMO — STATUS.md(현황판), requests/(CR), gates/, 계획·보고서
├── planning/                # 기획 — 요구사항, IA, 화면정의서
├── design/                  # 디자인 — 컨셉, 디자인 시스템, 페이지 디자인, mockups/, assets/
├── developer/               # 개발 — 기술 설계, 개발 보고서
│   └── site/                #   ★ 홈페이지 소스코드
├── qa/                      # 검증 — 테스트 계획·케이스·결과, evidence/
├── devops/                  # 배포 — 배포 계획·보고서, 운영 가이드
└── shared/                  # 팀 간 소통 — tickets/, reviews/, decisions/, meetings/
```

## Git 태그

| 태그 | 의미 |
|---|---|
| `kickoff` | 프로젝트 골격 생성, 고객 요청(CR-000) 기록 |
| `G1` ~ `G8` | 단계 게이트 PM 승인 시점 |
| `G{n}-CR-{nnn}` | 변경 요청으로 회귀한 단계의 재승인 시점 |
| `release-v{x.y.z}` | 운영 배포 대상 버전 (롤백 기준점) |
