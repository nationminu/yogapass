---
doc_id: DSN-SYSTEM
title: 디자인 시스템
phase: P3
owner: designer
version: 0.2
status: in-review
reviewers: [planner, developer]
inputs: [design/03_design-concept.md, planning/02_requirements.md, planning/02_information-architecture.md, planning/02_storyboard.md, pm/01_project-plan.md, shared/reviews/P3_design-docs_planner_r1.md, shared/reviews/P3_design-docs_developer_r1.md]
updated: 2026-09-12
---

# 디자인 시스템 — 강남 요가패스

> **컨셉 확정**: 시안 A "정돈된 신뢰" (PM 결정 2026-09-12) + **보정 1·2 적용**
> · 보정 1 — 섹션 간격 88 → **96px**, 히어로 상하 패딩 88 → **104px** (`≥1280px` 한정)
> · 보정 2 — **1차 소개형 화면에 한해 카드 radius 8 → 12px**, 강점 카드 아이콘 프레임 **원형**. 캘린더·표·관리자는 8px 유지
>
> **이 문서의 위치**
> 1. **§3.0 전역 UI 규칙(G-0~G-13)의 단일 기준은 `planning/02_requirements.md` §3.0이다.** 이 문서는 그 규칙이 요구한 **픽셀 토큰만 확정**하고 규칙 본문·값을 복제하지 않는다. 확정 결과는 §5에 모았다.
> 2. **1차에 쓰지 않는 토큰까지 지금 전부 정의한다.** 2차 39화면(캘린더·표·폼·배지·관리자 셸)에서 토큰을 다시 만들지 않기 위함이다(요구사항 §10 **TR-10** — "1차 토큰이 폐기·재정의되지 않고 확장만 된다").
> 3. **대비값은 designer가 WCAG 2.1 상대 휘도 공식으로 직접 계산**했다(sRGB → 선형화 → `0.2126R+0.7152G+0.0722B`, 대비 `(L1+0.05)/(L2+0.05)`, 소수 둘째 자리 반올림). P5에서 자동 도구로 재측정하면 같은 값이 나와야 한다.

---

## 0. 이 문서가 확정하는 것 / 확정하지 않는 것

| 구분 | 내용 |
|---|---|
| **확정한다** | 컬러·타이포·간격·radius·shadow·motion·z-index·breakpoint 토큰 전량, 컴포넌트 40종(1차 30 + 2차 예고 27)의 구조·상태, 접근성 판정 기준(장식 이미지 목록·포커스·터치·400% 확대), 아이콘 세트 |
| **확정하지 않는다** | 화면별 배치·섹션 수치(→ `design/03_page-design.md`), 실제 콘텐츠 문구(→ 화면정의서), 사실 정보(주소·전화·강사·요금 — 전부 `[TBD: 고객 확인 필요]`) |
| **조건부 값** | Primary `#0B4F9E`는 **고객 로고·브랜드 컬러 미수령(계획서 V-2, 기한 09-17) 상태의 확정값**이다. 수령 시 CR로 처리하며 **바뀌는 토큰은 `--color-primary` 계열 4개뿐**이고 전 화면 대비 재검증 0.5작업일이 붙는다 |

---

## 1. 디자인 토큰

### 1.1 컬러

#### (1) 브랜드 · 중립 (스케일 10단)

| 토큰 | 값 | 용도 | 흰 배경 대비 | 기준 | 판정 |
|---|---|---|---|---|---|
| `--color-primary` | `#0B4F9E` | 주 CTA 배경, 링크, 포커스 링, `aria-current` 표시 | **7.99:1** | 4.5:1 | 통과 |
| `--color-primary-hover` | `#08407F` | 버튼 hover | **10.24:1** | 4.5:1 | 통과 |
| `--color-primary-active` | `#06336A` | 버튼 active(눌림) | **12.43:1** | 4.5:1 | 통과 |
| `--color-primary-subtle` | `#F0F5FB` | 틴트 배경(히어로·콜아웃·아이콘 프레임) | 1.10:1 (배경 전용) | — | 배경 전용 |
| `--color-navy` | `#0A2540` | 푸터 배경, 강조 면 | **15.53:1** | 4.5:1 | 통과 |
| `--color-ink` | `#16263A` | 제목·본문 기본 | **15.30:1** | 4.5:1 | 통과 |
| `--color-muted` | `#5A6B7D` | 보조 텍스트, placeholder, 캡션 | **5.48:1** | 4.5:1 | 통과 |
| `--color-border-strong` | `#7E8FA3` | 입력 테두리, 보조 버튼 테두리, UI 경계 | **3.31:1** | 3:1 (WCAG 1.4.11) | 통과 |
| `--color-border` | `#DDE4EC` | 카드·섹션 구분선 | 1.28:1 | — | **장식 전용 — 정보 전달 금지** |
| `--color-surface` | `#FFFFFF` | 기본 배경 | — | — | — |
| `--color-surface-alt` | `#F7F9FC` | 교차 섹션 배경(선택적) | 1.05:1 | — | 배경 전용 |

**어두운 면(네이비 `#0A2540`) 위 전용**

| 토큰 | 값 | 용도 | `#0A2540` 대비 | 판정 |
|---|---|---|---|---|
| `--color-on-navy` | `#FFFFFF` | 푸터 제목·로고·링크 | **15.53:1** | 통과 |
| `--color-on-navy-muted` | `#B9C9DC` | 푸터 보조 텍스트·저작권 | **9.21:1** | 통과 |
| `--color-on-navy-line` | `#24405F` | 푸터 내부 구분선 | 1.4:1 | 장식 전용 |
| `--focus-ring-on-dark` | `#FFFFFF` | 어두운 면 위 포커스 링 | **15.53:1** | 통과 |

#### (2) 상태색 (컨셉 §2.0 ② 공통값 그대로 승계 — 시안 선택과 무관하게 고정)

| 토큰 | 값 | 배경 | 대비 | 용도 | **색 외 구분 수단(필수)** |
|---|---|---|---|---|---|
| `--color-success` | `#1B6E3C` | `#FFFFFF` | **6.28:1** | 접수 완료, 잔여 n(2차) | 체크 아이콘 + "완료"/"잔여 n" 텍스트 |
| `--color-success-bg` | `#E7F4EC` | — | `#1B6E3C` 올릴 때 **5.55:1** | 성공 결과 블록 | 테두리 `#9FCBB1` + 아이콘 |
| `--color-warning` | `#8A5200` | `#FFFFFF` | **6.39:1** | 주의·안내 | 삼각 경고 아이콘 + 텍스트 |
| `--color-warning-bg` | `#FAF0E1` | — | `#8A5200` 올릴 때 **5.66:1** | 경고 콜아웃 | 좌측 3px 바 + 아이콘 |
| `--color-error` | `#B3261E` | `#FFFFFF` | **6.54:1** | 폼 오류, 전송 실패 | 오류 아이콘 + `role="alert"` + 오류 요약 블록 |
| `--color-error-bg` | `#FBEAE8` | — | `#B3261E` 올릴 때 **5.61:1** | 오류 요약 블록 | 테두리 `#E8B3AE` + 아이콘 |
| `--color-neutral` | `#4F5B6B` | `#FFFFFF` | **6.90:1** | 마감·비활성·지난 날짜(2차) | 라벨 "마감" + **사선 해치 + 취소선** |
| `--color-neutral-bg` | `#EEF1F5` | — | `#4F5B6B` 올릴 때 **6.09:1** | 마감 셀, disabled 배경 | 사선 해치 패턴 |
| `--color-info-bg` | `#F0F5FB` | — | `#0B4F9E` 올릴 때 **7.30:1** | 정보 콜아웃 | 좌측 3px 바 + 아이콘 |

> **색상만으로 정보를 전달하지 않는다**(REQ-N-006). 위 표의 "색 외 구분 수단" 열은 **선택 사항이 아니라 구현 필수 조건**이다. 이 열이 비어 있는 상태색 사용은 P4 디자인 QA에서 결함으로 잡는다.

#### (3) 비활성(disabled)

| 토큰 | 값 | 대비 | 비고 |
|---|---|---|---|
| `--color-disabled-bg` | `#EEF1F5` | — | |
| `--color-disabled-fg` | `#5A6B7D` | `#EEF1F5` 위 **4.83:1** | WCAG 1.4.3은 비활성 요소를 면제하지만 **읽히도록 4.5:1을 넘겨 두었다** |
| `--color-disabled-border` | `#C4CDD8` | 1.61:1 | 장식 |

> 비활성 상태는 **색만으로 표시하지 않는다** — `disabled`/`aria-disabled="true"` + `cursor: not-allowed` + 버튼 라벨 변경(예: "보내는 중…")을 함께 쓴다.

#### (4) 사진 오버레이 (사진 수령 시 적용 · 현재는 미사용)

| 토큰 | 값 | 규칙 |
|---|---|---|
| `--overlay-hero-mobile` | `rgba(10,37,64,0.78)` | 균일 오버레이 |
| `--overlay-hero-desktop` | `linear-gradient(90deg, rgba(10,37,64,.86) 0%, rgba(10,37,64,.68) 55%, rgba(10,37,64,.38) 100%)` | **불투명도 0.68 미만 구간에는 텍스트를 놓지 않는다** |

**오버레이 최악 조건 대비 검증** (사진이 순백 `#FFFFFF`일 때 = 최악)

| 오버레이 | 합성색 | 흰 텍스트 대비 | 판정 |
|---|---|---|---|
| `rgba(10,37,64,.78)` | ≈ `#405569` | **7.72:1** | 통과 |
| `rgba(10,37,64,.68)` | ≈ `#586B7D` | **5.50:1** | 통과 (텍스트 허용 하한) |
| `rgba(10,37,64,.62)` | ≈ `#677889` | 4.54:1 | 경계 — **사용 금지** |
| `rgba(10,37,64,.38)` | — | 약 2.6:1 | **텍스트 금지 구간**(그래픽 전용) |

### 1.2 타이포그래피

**폰트**: **Pretendard / Pretendard Variable** 단일 (SIL Open Font License 1.1 · https://github.com/orioncactus/pretendard). 라이선스 근거는 `design/assets/SOURCES.md` §2.

- **로딩 방식**: P4에서 **self-host**(로컬 번들). 외부 CDN·Google Fonts를 쓰지 않는다(초기 로드 외부 도메인 요청 0건 — REQ-F-032·REQ-N-004 성능 목표와 같은 원칙).
- **폴백 스택**: `-apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif` (OS 동봉 폰트 — 저장소에 포함하지 않는다)
- **숫자**: 전역 `font-variant-numeric: tabular-nums` (시간·잔여·날짜·전화번호 정렬 — 2차 캘린더·표에서 필수)

**폰트 파일 구성 — 확정 (v0.2 · developer R1 #5 처리)**

| # | 항목 | 확정값 | 근거 |
|---|---|---|---|
| ① | 파일 형태 | **static 2종(400 · 700)** × **`unicode-range` 분할 subset woff2**(Pretendard 배포본의 dynamic subset 세트). **Variable 단일 파일을 쓰지 않는다** | Variable 단일 파일은 한글 전체를 포함해 1MB를 넘고, **weight를 덜 쓴다고 파일이 작아지지 않는다**(v0.1의 "Variable 단일 파일 사용 시 weight 400/500/700만 사용한다"는 전제를 **정정**한다). `unicode-range` 분할은 첫 화면에 실제로 쓰인 글자 chunk만 내려받아 모바일 LCP 위험을 없앤다 |
| ② | 1차 사용 weight | **400 · 700 두 종뿐. `--fw-medium: 500`은 1차에서 사용하지 않는다** (토큰 이름은 2차용으로 남긴다) | 500을 쓰면 static 파일이 1세트 더 늘어난다. 500을 쓰던 곳은 **CMP-004 GNB 항목**과 **CMP-005 패널 항목** 둘뿐이며, 둘 다 기본 **400 / 현재 항목 700**으로 내린다. 굵기 대비가 500↔700에서 400↔700으로 커져 현재 메뉴 표시가 오히려 뚜렷해진다 |
| ③ | 로딩 | `font-display: swap`. **preload는 Latin + 한글 기본 chunk(400)만 2개**로 제한한다(분할 subset 전량 preload 금지 — 오히려 느려진다) | LCP 요소가 h1(700)이지만 첫 화면 문자 수가 적어 swap 노출 시간이 짧다 |
| ④ | 폴백 메트릭 보정 | **필수.** 폴백용 `@font-face`(`local("Malgun Gothic")` / `local("Apple SD Gothic Neo")`)에 **`size-adjust` · `ascent-override` · `descent-override`를 지정**해 교체 시 CLS를 0으로 만든다 | `swap` + 메트릭 미보정은 글꼴 교체 시점에 줄 높이가 바뀌어 CLS가 생긴다 |
| ⑤ | ④의 수치 | **P4 기술 설계에서 실측해 확정**하고 designer가 1회 확인한다. **수용 기준은 designer가 지금 확정한다 — 폴백 렌더와 Pretendard 렌더에서 `h1 2줄 + 서브카피 3줄` 블록의 높이 차이가 ±2px 이내, 측정 CLS 0.01 이하** | 오버라이드 값은 두 폰트의 실제 메트릭에서 나오는 값이라 문서에서 지어낼 수 없다. **판정 기준을 P3에서 닫아 두면 P5 판정이 열리지 않는다** |

> ②로 인해 §1.2 타이포 표의 weight 열에는 **400과 700만** 나타난다. 1차 구현에서 `font-weight: 500`을 쓰면 디자인 QA 지적 대상이다.

| 토큰 | 역할 | `≥1280px` | `768~1279px` | `<768px` | weight | line-height | letter-spacing |
|---|---|---|---|---|---|---|---|
| `--font-h1` | 페이지 제목 (화면당 1개) | 46px | 36px | 27px | 700 | 1.25 / 1.3 / 1.3 | -0.015em |
| `--font-h2` | 섹션 제목 | 32px | 26px | 22px | 700 | 1.3 | -0.015em |
| `--font-h3` | 카드 제목 | 18px | 18px | 17px | 700 | 1.45 | -0.01em |
| `--font-h4` | 소제목·라벨 제목 | 16px | 16px | 15px | 700 | 1.5 | 0 |
| `--font-lead` | 리드·히어로 서브카피 | 18px | 17px | 15px | 400 | 1.7 | 0 |
| `--font-body` | 본문 | 16px | 16px | 15px | 400 | 1.7 | 0 |
| `--font-body-sm` | 보조 본문·카드 설명 | 15px | 15px | 14px | 400 | 1.7 | 0 |
| `--font-caption` | 캡션·오류 문구·고지 | 14px | 14px | 14px | 400 | 1.6 | 0 |
| `--font-label` | 폼 라벨·버튼 | 16px | 16px | 15px | 700 | 1.4 | 0 |
| `--font-eyebrow` | 상단 라벨(kicker) | 13px | 13px | 12.5px | 700 | 1.4 | 0.1em |

**최소 크기 규칙 (REQ-N-006 ⑤)**

- **문장(본문·설명·오류·안내)의 하한은 14px이다.** 어떤 뷰포트에서도 14px 미만으로 내리지 않는다.
- 14px 미만이 허용되는 자리는 **아래 3가지뿐**이며, 전부 "문장이 아닌 라벨"이다.

| 예외 | 허용 크기 | 차수 | 조건 |
|---|---|---|---|
| 캘린더 셀 배지 (`잔여 3`·`마감`) | 11.5~12px / 700 | 2차 | 셀 44×56px 이상 + 축약 문구 규칙(REQ-C-L-001) + 색 외 구분 수단 병기 |
| eyebrow(kicker) 대문자 라벨 | 12.5px / 700 | 공통 | 문장이 아닌 단일 라벨, 같은 정보가 본문에도 있을 것 |
| 데이터 표 헤더 셀 | 13px / 700 | 2차 | 관리자 영역 한정(REQ-N-A-006) |

> **셀 라벨을 14px 아래로 줄여서 폭을 맞추지 않는다.** 폭이 모자라면 **문구를 축약하거나 셀 높이를 64px로 올려 2줄 배치**한다(designer R2 #N1 흡수 경로).
> **입력 필드(`input`·`textarea`·`select`)의 font-size는 어떤 뷰포트에서도 16px 미만으로 두지 않는다** — iOS Safari가 16px 미만 입력에 포커스하면 뷰포트를 자동 확대해 §3.0 G-9(가상 키보드 중 고정 바 유지) 검증이 깨진다.

**텍스트 200% 확대 대응 (IA §2.1이 P3로 넘긴 항목)**

| 대상 | 규칙 |
|---|---|
| GNB(`768~1279px`) | 200% 확대 시 인라인 GNB가 가용 폭을 넘으면 **햄버거 패널로 전환**한다(`@container` 미사용, `@media (max-width: 1279px) and (min-resolution: …)` 대신 **JS 없이 되는 폴백**: GNB에 `flex-wrap: nowrap` + `min-width: 0` + 항목 `text-overflow` 금지 → 넘치면 `@media` 전환 대신 **헤더 높이 자동 증가(2줄 허용)**) |
| 버튼·칩 | `min-height`만 고정하고 **높이를 px로 잠그지 않는다**(`height` 금지, `min-height` + `padding` 사용). 라벨은 줄바꿈을 허용한다 |
| 고정 바 | 라벨이 2줄이 되면 바 높이가 자동으로 늘어난다. **본문 하단 여백은 고정 바 실제 높이를 CSS 변수로 반영**(§5 참조)해 계산식이 함께 커지게 한다 |
| 표·캘린더(2차) | 가로 스크롤 대신 **셀 높이 증가 → 그래도 넘치면 §4.4의 리스트 전환** |

### 1.3 간격 · 레이아웃

**간격 스케일** (4px 기준)

| 토큰 | 값 | 주 용도 |
|---|---|---|
| `--space-1` | 4px | 아이콘-텍스트 |
| `--space-2` | 8px | 요소 간 최소 간격, **터치 타깃 인접 간격 하한** |
| `--space-3` | 12px | 폼 라벨-입력, 버튼 내부 |
| `--space-4` | 16px | 카드 내부, 모바일 컨테이너 패딩 |
| `--space-5` | 20px | |
| `--space-6` | 24px | 카드 패딩(모바일), 태블릿 컨테이너 패딩 |
| `--space-7` | 32px | 카드 패딩(데스크톱), 블록 간 |
| `--space-8` | 40px | 데스크톱 컨테이너 좌우 패딩 |
| `--space-9` | 48px | |
| `--space-10` | 56px | 섹션 간격(모바일) |
| `--space-11` | 64px | 히어로 패딩(모바일) |
| `--space-12` | 72px | 섹션 간격(태블릿) |
| `--space-13` | 80px | 히어로 패딩(태블릿) |
| `--space-14` | **96px** | **섹션 간격(데스크톱) — 보정 1** |
| `--space-15` | **104px** | **히어로 상하 패딩(데스크톱) — 보정 1** |

**compact 스케일 (2차 데이터 영역 전용 — 관리자 표·캘린더·주 뷰)**

| 토큰 | 값 | 용도 |
|---|---|---|
| `--space-c1` | 2px | 캘린더 셀 경계 간격(REQ-N-006 ②-1 하한) |
| `--space-c2` | 6px | 표 셀 세로 패딩, 배지 좌우 패딩 |
| `--space-c3` | 10px | 표 셀 가로 패딩 |

**컨테이너 · 그리드**

| 항목 | `<768px` | `768~1023px` | `1024~1279px` | `≥1280px` |
|---|---|---|---|---|
| `--container-max` | 100% | 100% | 100% | **1200px** |
| 좌우 패딩 | **16px** | 24px | 32px | **40px** |
| 열(column) | 4 | 8 | 12 | **12** |
| gutter | 16px | 20px | 24px | **24px** |
| 본문 최대 폭(읽기 영역) | 100% | 100% | 720px | **720px** |
| 폼 영역 최대 폭 | 100% | 100% | 640px | **640px** |

> **캘린더 전용 예외(2차)**: 캘린더 컴포넌트의 좌우 패딩은 컨테이너 패딩을 따르지 않고 **12px 고정**이다. 360px 기준 셀 폭 = `(360 − 12×2 − 2×6) ÷ 7 = 46.28px` → **셀 폭 46.28px · 높이 56px**. 계산식이 기준이고 46.28px은 파생값이다(REQ-N-006 ②-2와 같은 방식).

### 1.4 Radius · Shadow · Motion · Z-index

**Radius**

| 토큰 | 값 | 적용 |
|---|---|---|
| `--radius-sm` | 6px | 배지, 칩, 작은 아이콘 프레임, 입력 보조 요소 |
| `--radius-md` | **8px** | **기본값** — 버튼, 입력, 데이터 표 셀, 캘린더 셀, 관리자 전 요소 |
| `--radius-lg` | **12px** | **1차 소개형 화면의 카드·패널 한정(보정 2)** — 강점 카드, 수업 유형 카드, 강사 카드, 히어로 그래픽 패널, 지도 대체 영역, 결과 블록 |
| `--radius-pill` | 999px | eyebrow 라벨, 페이지 내 이동 칩, 원형 아이콘 프레임(보정 2) |
| `--radius-none` | 0 | 전폭 섹션, 푸터 |

> **`--radius-lg`(12px)는 2차 데이터 화면으로 확장하지 않는다.** 캘린더 셀·표 행·슬롯 카드·관리자 패널은 `--radius-md`(8px)를 쓴다. 밀도가 높은 영역에서 12px는 셀 내부 가용 폭을 줄인다.

**Shadow** — 시안 A의 원칙은 **"면은 테두리로 구분하고 그림자는 쓰지 않는다"** 이다.

| 토큰 | 값 | 허용 범위 |
|---|---|---|
| `--shadow-none` | `none` | **기본값.** 카드·버튼·입력·표·캘린더·섹션 — 전부 그림자 없음 |
| `--shadow-overlay` | `0 6px 20px rgba(10,37,64,.16)` | **z-index 40 이상(드롭다운·팝오버)에만** |
| `--shadow-modal` | `0 16px 48px rgba(10,37,64,.24)` | **모달·다이얼로그(z-index 50)에만** |
| `--shadow-bar` | `0 -1px 0 #DDE4EC` | 하단 고정 바 상단 경계(그림자가 아니라 1px 라인) |

> 규칙: **문서 흐름 안에 있는 요소에는 그림자를 쓰지 않는다.** 실제로 떠 있는(레이어가 분리된) 요소만 그림자를 갖는다. 이 규칙을 지켜야 2차에서 표·캘린더의 시각 소음이 누적되지 않는다.

**Motion**

| 토큰 | 값 | 용도 |
|---|---|---|
| `--motion-fast` | 120ms | 색 변화(hover·active), 포커스 링 |
| `--motion-base` | 160ms | 표시/숨김, 아코디언, 칩 선택 |
| `--motion-slow` | 220ms | 패널·드로어 슬라이드, 모달 등장 |
| `--ease-standard` | `cubic-bezier(.2, 0, 0, 1)` | 기본 |
| `--ease-out` | `cubic-bezier(0, 0, .2, 1)` | 등장 |
| `--motion-distance` | **최대 8px** | 이동 애니메이션의 이동 거리 상한 |

규칙: ① **페이지 전환 애니메이션을 만들지 않는다** ② 애니메이션 대상은 `opacity`·`transform`만 (레이아웃 속성 금지 — CLS 0) ③ **`prefers-reduced-motion: reduce`에서 모든 duration을 0.01ms로 낮추고 `transform` 이동을 제거**한다(상태 전환 자체는 유지).

**Z-index 6단** (요구사항 §10 "z-index 레이어 6단" 대응 — **쌓임 순서를 시각 논리대로 재정렬했다**)

| 토큰 | 값 | 레이어 | 비고 |
|---|---|---|---|
| `--z-sticky-table` | 10 | sticky 표 헤더·시간축 (2차) | 페이지 헤더보다 **아래** — 표 헤더가 사이트 헤더를 덮으면 안 된다 |
| `--z-header` | 20 | sticky 사이트 헤더 / 관리자 상단바 | |
| `--z-fixed-bar` | 30 | 하단 고정 바 | |
| `--z-dropdown` | 40 | 드롭다운, 팝오버, 툴팁 | `--shadow-overlay` 허용 시작 |
| `--z-modal` | 50 | 모달·다이얼로그 (backdrop 49) | `--shadow-modal` |
| `--z-toast` | 60 | 토스트·스낵바 | 모달 위에서도 보여야 한다 |

> 기획 문서(§10·화면정의서 §2차 예고)의 나열 순서와 2번째·1번째가 바뀌었다. **나열 순서는 열거였고 쌓임 순서가 아니었다**고 보아 시각 논리를 따랐다. → **planner·developer R1에서 둘 다 승인**(planner R1 §3.1 A · developer R1 #10). D-2는 해소로 닫는다.
>
> **구현 조건 2가지 (developer R1 #10 · 숫자만으로는 보장되지 않는다)**
> ① z-index는 **같은 쌓임 맥락 안에서만** 비교된다. **표 컨테이너와 그 조상에 `transform`·`filter`·`opacity<1`·`will-change`·`contain: paint`·`isolation: isolate`를 쓰지 않는다**(새 쌓임 맥락이 생기면 10 < 20 비교가 무의미해져 표 헤더가 사이트 헤더를 덮는다).
> ② sticky 표 헤더의 `top`은 **`var(--header-h)`** 로 잡는다(`0`으로 두면 z-index와 무관하게 사이트 헤더 뒤에 가려 읽을 수 없다).

### 1.5 Breakpoint (4구간)

| 이름 | 범위 | 측정 지점 | 이 구간에서 달라지는 것 |
|---|---|---|---|
| `mobile` | ~ 767px | **360px** | 햄버거 헤더, 1열, 하단 고정 바 노출, 컨테이너 패딩 16px |
| `tablet` | 768 ~ 1023px | **768px** | 인라인 GNB(헤더 CTA 없음 — G-8), 2열, 고정 바 노출, 패딩 24px |
| `tablet-wide` | 1024 ~ 1279px | **1024px** | tablet 규칙 승계 + 패딩 32px. **2차 관리자 사이드바가 고정 펼침으로 바뀌는 경계** |
| `desktop` | 1280px ~ | **1280px** | 헤더 주 CTA 노출, 고정 바 미노출, 컨테이너 1200px, 보정 1 여백 |

- **뷰포트는 점값이 아니라 구간으로 규정한다**(요구사항 §3.0 G-1). 360·768·1024·1280px는 **측정 지점**이다.
- `1024px`는 공개·회원 영역에서는 `tablet`과 같은 규칙을 쓰고, **2차 관리자 영역에서만 별도 경계**로 동작한다(REQ-N-A-001).
- CSS 작성 방향은 **모바일 우선**(`min-width` 미디어 쿼리)이다.

### 1.6 CSS 변수 (개발 전달용 — 그대로 복사해 쓴다)

```css
/* ============================================================
   강남 요가패스 디자인 토큰 v0.1 (2026-09-12)
   컨셉: 시안 A "정돈된 신뢰" + 보정 1·2
   ⚠ 값을 화면 CSS에 직접 쓰지 말고 반드시 변수를 참조한다.
   ============================================================ */
:root {
  /* ---- color: brand / neutral ---- */
  --color-primary:        #0B4F9E;   /* 7.99:1  on #fff */
  --color-primary-hover:  #08407F;   /* 10.24:1 */
  --color-primary-active: #06336A;   /* 12.43:1 */
  --color-primary-subtle: #F0F5FB;
  --color-navy:           #0A2540;   /* 15.53:1 */
  --color-ink:            #16263A;   /* 15.30:1 */
  --color-muted:          #5A6B7D;   /* 5.48:1  */
  --color-border-strong:  #7E8FA3;   /* 3.31:1  UI 경계 */
  --color-border:         #DDE4EC;   /* 장식 전용 */
  --color-surface:        #FFFFFF;
  --color-surface-alt:    #F7F9FC;

  /* ---- color: on dark ---- */
  --color-on-navy:        #FFFFFF;   /* 15.53:1 on navy */
  --color-on-navy-muted:  #B9C9DC;   /*  9.21:1 on navy */
  --color-on-navy-line:   #24405F;

  /* ---- color: status (색 외 구분 수단 병기 필수) ---- */
  --color-success:        #1B6E3C;   /* 6.28:1 */
  --color-success-bg:     #E7F4EC;   /* 5.55:1 with success */
  --color-success-border: #9FCBB1;
  --color-warning:        #8A5200;   /* 6.39:1 */
  --color-warning-bg:     #FAF0E1;   /* 5.66:1 with warning */
  --color-error:          #B3261E;   /* 6.54:1 */
  --color-error-bg:       #FBEAE8;   /* 5.61:1 with error */
  --color-error-border:   #E8B3AE;
  --color-neutral:        #4F5B6B;   /* 6.90:1 */
  --color-neutral-bg:     #EEF1F5;   /* 6.09:1 with neutral */
  --color-info-bg:        #F0F5FB;   /* 7.30:1 with primary */

  /* ---- color: disabled ---- */
  --color-disabled-bg:     #EEF1F5;
  --color-disabled-fg:     #5A6B7D;  /* 4.83:1 on disabled-bg */
  --color-disabled-border: #C4CDD8;

  /* ---- typography ---- */
  --font-family: Pretendard, "Pretendard Fallback", -apple-system,
                 "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
  /* static 400/700 + unicode-range 분할 subset (§1.2 폰트 파일 구성).
     "Pretendard Fallback" = 메트릭 오버라이드를 건 폴백 @font-face 이름. */
  --fw-regular: 400;  --fw-bold: 700;
  --fw-medium: 500;            /* 2차 예약 — 1차에서 사용하지 않는다 */

  --fs-h1: 27px;   --lh-h1: 1.3;
  --fs-h2: 22px;   --lh-h2: 1.3;
  --fs-h3: 17px;   --lh-h3: 1.45;
  --fs-h4: 15px;   --lh-h4: 1.5;
  --fs-lead: 15px;
  --fs-body: 15px;
  --fs-body-sm: 14px;
  --fs-caption: 14px;          /* 문장 하한 — 더 내리지 않는다 */
  --fs-label: 15px;
  --fs-eyebrow: 12.5px;
  --fs-input: 16px;            /* iOS 자동 확대 방지 — 어떤 구간에서도 16px 유지 */
  --lh-body: 1.7;  --lh-caption: 1.6;  --lh-label: 1.4;
  --ls-heading: -0.015em;      /* h1·h2 */
  --ls-h3: -0.01em;  --ls-h4: 0;  --ls-eyebrow: 0.1em;

  /* ---- spacing ---- */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;  --space-4: 16px;
  --space-5: 20px;  --space-6: 24px;  --space-7: 32px;  --space-8: 40px;
  --space-9: 48px;  --space-10: 56px; --space-11: 64px; --space-12: 72px;
  --space-13: 80px; --space-14: 96px; --space-15: 104px;
  /* compact (2차 데이터 영역 전용) */
  --space-c1: 2px;  --space-c2: 6px;  --space-c3: 10px;

  /* ---- layout ---- */
  --container-max: 1200px;
  --container-pad: 16px;       /* 구간별로 아래 미디어 쿼리에서 덮는다 */
  --content-max: 100%;
  --form-max: 100%;
  --grid-gutter: 16px;
  --calendar-pad: 12px;        /* 2차 캘린더 전용 고정값 */
  --gnb-item-pad-x: 12px;      /* 768~1279px GNB 폭 계산 전제(IA §2.1) — 고정 */
  --logo-max-w: 140px;         /* 로고 폭 상한(IA §2.1 전제 ①) */

  /* ---- radius ---- */
  --radius-sm: 6px;  --radius-md: 8px;  --radius-lg: 12px;  --radius-pill: 999px;

  /* ---- shadow ---- */
  --shadow-none: none;
  --shadow-overlay: 0 6px 20px rgba(10,37,64,.16);
  --shadow-modal:   0 16px 48px rgba(10,37,64,.24);

  /* ---- motion ---- */
  --motion-fast: 120ms;  --motion-base: 160ms;  --motion-slow: 220ms;
  --ease-standard: cubic-bezier(.2, 0, 0, 1);
  --ease-out: cubic-bezier(0, 0, .2, 1);
  --motion-distance: 8px;

  /* ---- z-index ---- */
  --z-sticky-table: 10;  --z-header: 20;  --z-fixed-bar: 30;
  --z-dropdown: 40;      --z-modal: 50;   --z-toast: 60;

  /* ---- interaction ---- */
  --touch-min: 44px;             /* 터치 타깃 하한 (REQ-N-006 ②) */
  --touch-gap: 8px;              /* 인접 간격 하한 (격자 예외는 --space-c1) */
  --focus-ring-width: 3px;
  --focus-ring-offset: 2px;
  --focus-ring-color: var(--color-primary);
  --focus-ring-color-on-dark: #FFFFFF;

  /* ---- 전역 UI 규칙 파생 토큰 (요구사항 §3.0) ---- */
  --header-h: 64px;              /* <768px */
  --fixed-bar-h: 60px;           /* G-2 하한 56px 이상 — 44px 버튼 + 상하 8px */
  --safe-b: env(safe-area-inset-bottom, 0px);
  /* G-3: 본문 하단 여백 = 고정 바 높이 + safe-area + 16px */
  --body-pad-bottom: calc(var(--fixed-bar-h) + var(--safe-b) + var(--space-4));
  /* G-10: 앵커 진입 오프셋 = 헤더 높이 + 16px */
  --anchor-offset: calc(var(--header-h) + var(--space-4));
  /* G-9: 포커스 필드가 고정 바에 가리지 않게 */
  --scroll-pad-bottom: var(--body-pad-bottom);
}

/* ---- tablet: 768~1023px ---- */
@media (min-width: 768px) {
  :root {
    --fs-h1: 36px; --lh-h1: 1.3;
    --fs-h2: 26px; --fs-h3: 18px; --fs-h4: 16px;
    --fs-lead: 17px; --fs-body: 16px; --fs-body-sm: 15px;
    --fs-label: 16px; --fs-eyebrow: 13px;
    --container-pad: 24px; --grid-gutter: 20px;
    --header-h: 68px;
  }
}

/* ---- tablet-wide: 1024~1279px ---- */
@media (min-width: 1024px) {
  :root {
    --container-pad: 32px; --grid-gutter: 24px;
    --content-max: 720px; --form-max: 640px;
  }
}

/* ---- desktop: 1280px+ ---- */
@media (min-width: 1280px) {
  :root {
    --fs-h1: 46px; --lh-h1: 1.25;
    --fs-h2: 32px;
    --fs-lead: 18px;
    --container-pad: 40px;
    --header-h: 72px;
    /* 고정 바 미노출 구간 — 본문 하단 여백 해제 */
    --fixed-bar-h: 0px;
    --body-pad-bottom: 0px;
    --scroll-pad-bottom: var(--anchor-offset);
  }
}

/* ---- G-11: 400% 확대 상황(1280px 400% 확대 ≈ 가로 320px · 세로 400px 상당) ----
   ⚠ max-height 단독으로 쓰지 않는다. 360×640 단말을 가로로 돌리면 640×360이 되어
   조건에 걸리고, 고정 바가 정적 배치로 내려가 화면에서 사라진다(G-1 취지와 충돌).
   and (max-width: 400px)로 400% 확대 상황만 잡는다. (planner R1 #2) */
@media (max-height: 420px) and (max-width: 400px) {
  :root {
    --body-pad-bottom: 0px;
    --anchor-offset: var(--space-4);   /* 헤더가 떠 있지 않으므로 오프셋 불필요 (developer R1 #4) */
  }
  /* 헤더 sticky 해제 · 고정 바 정적 배치 — §4.4 참조 */
}

/* ---- 모션 민감 사용자 ---- */
@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0.01ms; --motion-base: 0.01ms; --motion-slow: 0.01ms;
          --motion-distance: 0px; }
  *, *::before, *::after {
    animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; scroll-behavior: auto !important;
  }
}

/* ---- 전역 기본 ---- */
html { scroll-padding-bottom: var(--scroll-pad-bottom); scroll-padding-top: var(--anchor-offset); }
body { font-family: var(--font-family); font-size: var(--fs-body); line-height: var(--lh-body);
       color: var(--color-ink); background: var(--color-surface);
       font-variant-numeric: tabular-nums;
       padding-bottom: var(--body-pad-bottom); }
:target { scroll-margin-top: var(--anchor-offset); }

/* ---- 포커스 표시 : 스타일시트 맨 뒤에 둔다 (developer R1 #1) ----
   · border-radius를 선언하지 않는다 — outline이 아니라 요소 자체의 모서리를 바꾸므로
     포커스 순간 pill 칩(999px)·카드(12px)가 6px로 변형된다.
     브라우저 outline은 이미 요소의 border-radius를 따라 그려진다.
   · :where()는 특이성 0이라 뒤에 오는 .btn류 규칙이 outline을 덮을 수 있어
     선택자를 풀어 쓴다(각 (0,1,1) — .btn (0,1,0)보다 강하다). */
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
summary:focus-visible,
[tabindex]:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}
[data-surface="dark"] a:focus-visible,
[data-surface="dark"] button:focus-visible {
  outline-color: var(--focus-ring-color-on-dark);
}
```

> **개발 주의 3가지** (v0.2에서 ②를 확장하고 ③을 신설했다 — developer R1 #2·#3)
> ① `--fixed-bar-h`를 `≥1280px`에서 `0px`로 덮었기 때문에 `--body-pad-bottom` 계산이 자동으로 0이 된다. **고정 바 실제 높이가 바뀌면 이 변수 하나만 고치면 전 화면이 따라온다.**
> ② **`ResizeObserver` 실측 갱신 대상은 고정 바와 헤더 둘 다다.** 텍스트 200% 확대로 고정 바 라벨이 2줄이 되면 바 높이가 60px를 넘고, 같은 조건에서 GNB가 2줄이 되거나 로고 폭 폴백 ③이 걸리면 **헤더도 64/68/72px을 넘는다**. 헤더는 `min-height`로 선언돼 실제 높이가 자동으로 늘어나는데 `--header-h`는 고정값이므로, 갱신하지 않으면 `--anchor-offset`(= `--header-h + 16px`)과 `scroll-padding-top`이 실제 높이를 따라가지 못해 **앵커 진입 시 대상 제목이 sticky 헤더 뒤로 숨는다**(G-10 미충족 — SCR-003 이동 칩, SCR-006 목차 13항목이 직접 영향). → **`--fixed-bar-h`와 `--header-h`를 같은 스크립트 하나에서 실측값으로 갱신**한다(G-9 WebKit 폴백 스크립트에 함께 넣는다). `--header-h`만 갱신하면 `--anchor-offset`은 `calc()`라 자동으로 따라온다.
> ③ `documentElement.style.setProperty()`는 **인라인 스타일**이라 `@media (min-width: 1280px)`의 `--fixed-bar-h: 0px`와 `@media (max-height: 420px) and (max-width: 400px)` 블록을 **이긴다**. 따라서 **바를 렌더하지 않는 구간(`≥1280px`, 400% 확대 조건)에서는 `removeProperty('--fixed-bar-h')`로 인라인 속성을 되돌린다.** 되돌리지 않으면 데스크톱으로 넓혔을 때 바는 사라졌는데 본문 하단에 76px 빈 공간이 남는다. (헤더는 전 구간에서 렌더되므로 `--header-h`는 되돌릴 필요가 없다.)

---

## 2. 컴포넌트 — 1차 (SCR-001·002·003·006·008·009)

### 2.0 전 컴포넌트 공통 상태 정의

| 상태 | 시각 규칙 | 접근성 |
|---|---|---|
| **기본(default)** | 토큰 기본값 | — |
| **hover** | 색 1단계 진하게(`--motion-fast` 색 전환). **이동·확대 없음** | 마우스 전용 — 터치에서 stuck hover가 남지 않도록 `@media (hover: hover)`로 감싼다 |
| **focus-visible** | `outline: 3px solid #0B4F9E` + `offset: 2px`. **`outline: none` 금지** | 키보드 탐색 시 항상 보인다. 어두운 면 위에서는 흰색 링 |
| **active(눌림)** | 배경 `--color-primary-active`, `transform: translateY(1px)` | — |
| **disabled** | `--color-disabled-*` + `cursor: not-allowed` | `disabled` 또는 `aria-disabled="true"`. **포커스 순서에서 제거되는 버튼은 대체 안내를 함께 둔다** |
| **오류(error)** | 테두리 2px `--color-error` + 오류 아이콘 + 14px 오류 문구 | `aria-invalid="true"` + `aria-describedby`로 오류 문구 연결, `role="alert"` |
| **로딩(loading)** | 라벨을 진행 문구로 교체("보내는 중…") + 24px 스피너. **버튼 폭을 바꾸지 않는다**(CLS 0).<br>**모션 축소 환경(`prefers-reduced-motion: reduce`)에서는 스피너 회전이 멈추므로 라벨 교체가 주 진행 표시다** — 스피너를 유일한 진행 표시로 만들지 않는다 (developer R1 #12) | `aria-busy="true"`, `aria-live="polite"` |
| **빈 상태(empty)** | 아이콘 + 안내 문장 + 다음 행동 버튼 | **"준비 중" 표현 금지**(§5.0 M-5). "공개되면 안내드립니다" 계열 사용 |

### 2.1 컴포넌트 목록 (1차)

| ID | 이름 | 사용 화면 | 비고 |
|---|---|---|---|
| CMP-001 | Button | 전 화면 | |
| CMP-002 | Link (인라인 / 단독 / 새 창) | 전 화면 | |
| CMP-003 | Header (3구간 변형) | 전 화면 | |
| CMP-004 | GNB Item | 전 화면 | |
| CMP-005 | Mobile Menu Panel | `<768px` 전 화면 | |
| CMP-006 | Footer | 전 화면 | |
| CMP-007 | **Bottom Fixed Bar** | `<1280px` 공개·회원 전 화면 | 상태 5종 |
| CMP-008 | Skip Link | 전 화면 | |
| CMP-009 | Container / Section | 전 화면 | |
| CMP-010 | Card (강점 / 수업 유형 / 강사) | SCR-001·002 | 3변형 |
| CMP-011 | Icon Frame | SCR-001 | 원형(보정 2) |
| CMP-012 | Eyebrow Label | SCR-001 | |
| CMP-013 | Callout (info / warn / error) | SCR-001·003·006 | |
| CMP-014 | Definition List (라벨–값) | SCR-003 | |
| CMP-015 | Text Input | SCR-003 | |
| CMP-016 | Textarea + 글자 수 카운터 | SCR-003 | |
| CMP-017 | Checkbox (동의) | SCR-003 | |
| CMP-018 | Form Field (라벨·설명·오류 래퍼) | SCR-003 | |
| CMP-019 | Error Summary Block | SCR-003 | REQ-N-008 |
| CMP-020 | Result Block (성공 / 실패) | SCR-003 | |
| CMP-021 | Toast | SCR-003 (주소 복사) | |
| CMP-022 | Map Placeholder (클릭 투 로드) | SCR-003 | |
| CMP-023 | Anchor Chip | SCR-003 | |
| CMP-024 | Page Header (h1 + 리드) | SCR-002·003·006·008 | |
| CMP-025 | CTA Band (하단 전환 블록) | SCR-001·002 | |
| CMP-026 | Empty State | SCR-001·002 | |
| CMP-027 | Initial Avatar | SCR-001·002 | 인물 스톡 금지 |
| CMP-028 | TOC (앵커 목차) | SCR-006 | |
| CMP-029 | Back To Top | SCR-006 | Could |
| CMP-030 | Divider | 전 화면 | |

---

### CMP-001 Button

| 항목 | 내용 |
|---|---|
| 변형 | `primary`(채운 파랑) / `secondary`(흰 배경 + `#7E8FA3` 1px 테두리 + 파랑 글자) / `text`(텍스트 링크형) / `icon`(아이콘 단독) |
| 크기 | `lg` **min-height 52px** / padding 0 24px / 16px·700 — 주 CTA<br>`md` **min-height 48px** / padding 0 20px / 16px·700 — 일반<br>`sm` **min-height 44px** / padding 0 14px / 15px·700 — 고정 바·인라인<br>`icon` **44×44px**, 내부 아이콘 22px |
| radius | `--radius-md` (8px) — **버튼은 보정 2의 12px 대상이 아니다** |
| 기본 | `primary` 배경 `#0B4F9E` / 글자 `#FFFFFF` (**7.99:1**)<br>`secondary` 배경 `#FFFFFF` / 테두리 `#7E8FA3`(**3.31:1**) / 글자 `#0B4F9E`(**7.99:1**)<br>`text` 글자 `#0B4F9E` + 밑줄(hover 시 두께 2px) |
| hover | `primary` → `#08407F` / `secondary` → 배경 `#F0F5FB`, 테두리 `#0B4F9E` / `text` → `#08407F` |
| focus-visible | `outline 3px #0B4F9E`, offset 2px. 푸터(네이비) 안에서는 흰색 링 |
| active | 배경 `#06336A`, `translateY(min(1px, var(--motion-distance)))` — reduce에서 이동 0 |
| disabled | 배경 `#EEF1F5` / 글자 `#5A6B7D`(4.83:1) / 테두리 `#C4CDD8` / `cursor: not-allowed` |
| 로딩 | 라벨 교체 + 18px 스피너(회전 800ms linear). `aria-busy="true"`. **폭 고정**.<br>**reduce 환경에서는 스피너가 정지하므로 라벨 교체("보내는 중…")가 주 표시다** |
| 접근성 | 모든 크기가 44px 이상. 인접 버튼 간 간격 **8px 이상**. 아이콘 단독은 `aria-label` 필수. 아이콘 + 텍스트 병기 시 아이콘은 `aria-hidden="true"` |
| 사용 화면 | SCR-001·002·003·006·008·009 |

### CMP-002 Link

| 항목 | 내용 |
|---|---|
| 인라인 링크 | `#0B4F9E` + **항상 밑줄**(색만으로 구분하지 않는다). hover 시 `#08407F` + 밑줄 두께 2px |
| 단독 링크 | 밑줄 없음 + 우측 화살표 아이콘 16px. hover 시 화살표가 `translateX(min(4px, var(--motion-distance)))` 이동 — reduce에서 자동으로 0이 된다 |
| 새 창 링크 | 라벨 뒤 외부 링크 아이콘 14px + **접근 이름에 "(새 창 열림)" 포함**(REQ-F-005). `target="_blank" rel="noopener noreferrer"` |
| `tel:` 링크 | 전화 아이콘 + 번호. **번호가 `[TBD]`면 링크 자체를 렌더하지 않는다**(REQ-N-023 — `[TBD]` 문자열을 화면에 노출하지 않는다) |
| 터치 | 인라인 링크가 본문 중간에 있어 44px을 만들 수 없는 경우, **줄 높이 1.7 확보 + 링크 전후 여백**으로 오조작을 줄인다(WCAG 2.5.5 "인라인 예외") |

### CMP-003 Header

**고정 방식**: `position: sticky; top: 0; z-index: var(--z-header)` (G-10). 하단 1px `--color-border`. 배경 `#FFFFFF` 불투명(반투명 금지 — 스크롤 시 대비 흔들림 방지).

| 구간 | 높이 | 구성 (1차) | 2차 확장 |
|---|---|---|---|
| `<768px` | **64px** | 로고(높이 32px, 폭 ≤140px) + `우측` 전화 아이콘 버튼 44×44 + 햄버거 44×44. 두 버튼 간격 8px | 패널 안에 회원 메뉴 섹션 추가 |
| `768~1279px` | **68px** | 로고 + 인라인 GNB 4개(**항목 좌우 패딩 12px 고정** — `--gnb-item-pad-x`) + 전화 아이콘 44×44. **헤더 주 CTA 없음**(G-8) | GNB 5개 + 유틸 슬롯(비로그인 "로그인" 텍스트 버튼 56px / 로그인 사람 아이콘 44px + 드롭다운) |
| `≥1280px` | **72px** | 로고 + 인라인 GNB 4개 + 전화번호 텍스트(15px, `#16263A`) + **주 CTA `primary md`("문의하기")** — **자기 참조 화면에서는 아래 H1~H3 상태를 따른다** | 주 CTA가 상담 예약/레슨 예약으로 분기 + 회원 유틸 텍스트 |

**`≥1280px` 헤더 주 CTA 상태 3종 ★ (v0.2 신설 — planner R1 #1 Must)**

`≥1280px`는 **고정 바 미노출 구간**이라 헤더 주 CTA가 그 화면의 **유일한 상시 주 CTA**다. 따라서 자기 참조 처리를 정의하지 않으면 `/location`에서 `/location#contact`로 가는 강조 버튼이 남아 IA §2.1 마지막 줄·요구사항 §3.0 G-6 ①과 충돌한다.

> **채택 원칙: 헤더 주 CTA는 하단 고정 바(CMP-007)와 동일한 판단 축을 쓴다.** 규칙을 두 벌 만들지 않고 G-6 ①·②를 그대로 한 번 더 적용한다. 판정은 **현재 URL과 목적지 URL 비교**(G-7)이며 화면 목록을 하드코딩하지 않는다.

| # | 상태 | 시각 | 조건 | 대응하는 고정 바 상태 |
|---|---|---|---|---|
| **H1** | **기본** | `primary md` "문의하기" → `/location#contact` | 목적지 URL ≠ 현재 화면 URL | S1 |
| **H2** | **전화 문의로 대체** | `primary md` "전화 문의"(`phone` 아이콘 + 라벨) → `tel:` 대표 전화 | **자기 참조**(G-6 ①) + 대표 전화 **확정** | S2 |
| **H3** | **미노출** | 버튼을 렌더하지 않는다. 헤더 우측에는 GNB와 (확정된 경우) 전화번호 텍스트만 남는다 | **자기 참조 + 대표 전화 `[TBD]`**(G-6 ②) — **현재 SCR-003이 이 상태다** | S3 |

**선택 근거 (다른 안을 버린 이유)**

| 검토안 | 판정 | 이유 |
|---|---|---|
| ⓐ 버튼을 비활성(disabled)으로 둔다 | **기각** | 비활성 강조 버튼은 "지금 누를 수 없는 주 CTA"로 읽혀 전환 화면에서 오히려 방해가 된다. 스크린리더에도 의미 없는 요소가 남는다 |
| ⓑ 페이지 내 앵커 이동("문의 폼으로")으로 의미를 바꾼다 | **기각** | 같은 역할을 **페이지 헤더의 이동 칩(CMP-023 "문의하기")**이 이미 하고 있어 같은 화면에 같은 목적지 버튼이 2개가 된다(G-8이 막으려던 상황과 같다) |
| ⓒ **자기 참조면 "전화 문의"로 대체, 전화 미확정이면 미노출** | **채택** | 고정 바 S2/S3와 **판단 축·조건·데이터 의존이 완전히 동일**해 구현이 분기 하나를 공유한다. 대표 전화가 확정되면 H2가 자동으로 살아나 `≥1280px`에서도 대체 연락 수단이 상시 노출된다 |

**H3에서 `≥1280px` 주 CTA가 사라지는 것에 대한 보완** — 이 상태는 **전환 목적지 화면(SCR-003) 자신**에서만 발생하며, 같은 화면 안에 ⓐ 페이지 헤더 이동 칩 "문의하기" ⓑ 문의 폼 `#contact` 본체 ⓒ 폼 하단 대체 연락 안내가 있어 전환 경로가 끊기지 않는다. 다른 화면(SCR-001·002·006·008·009)은 전부 H1이다.

**`aria-current` 처리 (명확화)**

- **헤더 주 CTA 버튼에는 어떤 상태에서도 `aria-current`를 부여하지 않는다.** H1·H2는 목적지가 현재 화면이 아니고, H3은 요소 자체가 없다.
- 현재 화면 표시는 **GNB 항목의 `aria-current="page"` 1개로만** 한다(`/location`에서는 "오시는 길").
- **GNB "문의하기"(`/location#contact`)는 `/location`에서 페이지 내 앵커 이동으로 계속 동작**하며 `aria-current`를 받지 않는다(경로는 같지만 프래그먼트가 다른 위치 이동이고, 이동 링크로 **강조**하지 않는다는 규칙의 대상은 강조 버튼이다).

- **로고 폭 상한 140px**(`--logo-max-w`). 고객 로고가 가로형 워드마크로 와서 140px을 넘으면 **IA §2.1 폴백 순서**를 적용한다: ① `768~1279px`에서 심볼 전용(44px)으로 전환 → ② GNB 항목 패딩 8px → ③ 메뉴 1개를 유틸 드롭다운으로 이동. **③까지 가면 designer가 티켓으로 알린다.**
- **현재 메뉴 표시**: `aria-current="page"` + 글자 700 + **하단 2px `#0B4F9E` 인셋 라인**(색 + 굵기 + 라인 3중 표시 — 색만으로 구분하지 않는다).
- 텍스트 200% 확대 시 헤더 높이는 자동 증가한다(`min-height`로 선언, `height` 금지).

### CMP-004 GNB Item

| 상태 | 규칙 |
|---|---|
| 기본 | 15px/**400**, `#16263A`, padding `10px 12px`, radius 6px, **min-height 44px** (v0.2: 500 → 400 — §1.2 폰트 파일 구성 ②) |
| hover | 배경 `#F0F5FB` |
| focus-visible | 포커스 링 3px |
| current | `#0B4F9E` / 700 / `box-shadow: inset 0 -2px 0 #0B4F9E` + `aria-current="page"` |

### CMP-005 Mobile Menu Panel

| 항목 | 내용 |
|---|---|
| 형태 | 헤더 아래에서 내려오는 **전폭 패널**(드로어 아님). 배경 `#FFFFFF`, 하단 1px 라인 |
| 항목 | **min-height 52px**, 좌우 패딩 16px, 16px/**400**, 항목 간 1px `--color-border` (v0.2: 500 → 400 — §1.2 ②). 현재 항목만 700 |
| 열림/닫힘 | `--motion-base` `--ease-out`, `opacity` + `translateY(calc(-1 * var(--motion-distance)))` — reduce에서 이동 0 |
| 포커스 | 열면 첫 항목으로 포커스 이동, `Esc`로 닫고 햄버거 버튼으로 포커스 복귀. **패널이 열린 동안 배경 스크롤 잠금** |
| **마크업 정본** | **`<details>/<summary>` 기반이 정본이다** (developer R1 #8 확인 요청 → 확정). `<summary>`는 브라우저가 펼침 상태를 접근성 트리에 **자체 노출**하므로 **`aria-expanded`를 수동으로 붙이지 않는다**(수동 값이 어긋나면 스크린리더에 모순된 상태가 읽힌다) |
| JS 비활성 | `<details>` 기반이라 **JS 없이도 펼쳐진다**(REQ-N-028). **JS의 역할은 ① 열 때 첫 항목 포커스 이동 ② `Esc` 닫기 + 트리거 복귀 ③ 배경 스크롤 잠금 세 가지로 한정**한다. 상태 속성 갱신은 JS가 하지 않는다 |
| 하단 | 전화 링크 + 개인정보 처리방침 링크 (푸터까지 가지 않아도 도달 가능) |

### CMP-006 Footer

| 항목 | 내용 |
|---|---|
| 배경 | `--color-navy` `#0A2540`, `data-surface="dark"` |
| 텍스트 | 제목·링크 `#FFFFFF`(15.53:1) / 보조·저작권 `#B9C9DC`(9.21:1) / 구분선 `#24405F` |
| 패딩 | `<768px` 40px 0 32px / `768~1279px` 48px 0 / `≥1280px` 56px 0 |
| 레이아웃 | `<768px` 1열 · `768~1279px` 2열 · `≥1280px` 4열(사업장 정보 / 메뉴 / 안내 / SNS) |
| 구성(1차) | 로고(소형, 흰색) · 상호·주소 `[TBD]` · 대표 전화 `tel:` `[TBD]` · 운영시간·휴무일 `[TBD]` · 홈/강사 소개/오시는 길/문의하기 링크 · **개인정보 처리방침(굵게 700)** · 사업자 정보 `[TBD]` · SNS(계정 없으면 섹션 미노출) · 저작권 |
| 값 미확정 처리 | **해당 행을 렌더하지 않는다.** `[TBD]` 문자열을 화면에 출력하지 않는다(REQ-N-023) |
| 2차 | 상담 예약·상담 신청 조회·레슨 예약·이용약관·로그인/마이페이지 링크 추가. **관리자 영역 푸터는 처리방침 링크 + 버전 표기만** |

### CMP-007 Bottom Fixed Bar ★

> 규칙 본문은 `planning/02_requirements.md` §3.0 G-1~G-9다. 여기서는 **픽셀 토큰과 상태 5종의 시각 명세만** 정의한다.

| 항목 | 확정값 |
|---|---|
| 높이 | **`--fixed-bar-h: 60px`** (G-2 하한 56px 이상) = 버튼 44px + 상하 패딩 8px |
| 배경 · 경계 | `#FFFFFF` + 상단 1px `#DDE4EC` (`--shadow-bar`) |
| 안전 영역 | `padding-bottom: env(safe-area-inset-bottom)` |
| 본문 겹침 | `body { padding-bottom: var(--body-pad-bottom) }` = `60px + safe-area + 16px` = **76px + safe-area** (G-3 계산식의 파생값) |
| 버튼 간격 | **8px** (G-5) |
| 좌우 패딩 | 12px |
| z-index | `--z-fixed-bar` (30) |
| 노출 구간 | `<1280px` (= mobile + tablet + tablet-wide) |

**상태 5종**

| # | 상태 | 시각 | 조건 |
|---|---|---|---|
| S1 | **2분할(기본)** | 좌 `secondary sm` "전화 문의"(전화 아이콘) 40% / 우 `primary sm` "문의하기"(말풍선 아이콘) 60%, 간격 8px | 자기 참조가 아닌 공개·회원 화면 |
| S2 | **전폭 1버튼** | `primary sm` "전화 문의" 100% | 자기 참조 화면(G-6 ①) — 1차에서는 **SCR-003** |
| S3 | **미노출** | 바를 렌더하지 않고 `--body-pad-bottom: 0` | 자기 참조 + 대표 전화 `[TBD]`(G-6 ②) — **현재 SCR-003이 이 상태다** |
| S4 | **가상 키보드 활성** | 바를 계속 표시. WebKit은 `visualViewport` 보정으로 위치 유지 | G-9 |
| S5 | **정적 배치** | `position: static`으로 전환, 문서 끝에 배치, 본문 하단 여백 해제, 헤더 sticky 해제, 앵커 오프셋 해제 | `@media (max-height: 420px) and (max-width: 400px)` (G-11 — §4.4. v0.2에서 `max-width` 조건 추가) |

**S1 보조 규칙 — 대표 전화 미확정 (v0.2 신설 · 전 화면 공통 · planner R1 #3)**

> **S1에서 대표 전화가 확정되지 않았으면 좌측 "전화 문의" 버튼을 렌더하지 않고, 우측 "문의하기" 버튼이 전폭(100%)이 된다.** 바 자체는 유지한다 — **G-6 ②의 미노출 단서는 자기 참조 화면(S3)에만 적용**되므로, 자기 참조가 아닌 화면은 주 CTA가 살아 있어 바를 없앨 이유가 없다.
> 같은 조건에서 **헤더 전화 아이콘 버튼(`<768px`·`768~1279px`)·헤더 전화번호 텍스트(`≥1280px`)·푸터 전화 행·모바일 패널 전화 링크도 함께 렌더하지 않는다**(CMP-002 `tel:` 규칙 · REQ-N-023: `[TBD]` 문자열을 화면에 출력하지 않는다).
> **이 규칙은 여기 한 곳에만 둔다.** 페이지 디자인의 화면별 절(SCR-001·002·006·008·009)은 "S1 유지 + 이 규칙 적용"으로만 적고 조건을 복제하지 않는다.

| 조건 | 좌측 "전화 문의" | 우측 "문의하기" | 바 노출 |
|---|---|---|---|
| 대표 전화 확정 | 40% 노출 | 60% | 노출 |
| 대표 전화 `[TBD]` | **미렌더** | **100% 전폭** | 노출 |

**대비 검증**: 좌 `secondary` 테두리 `#7E8FA3` = 3.31:1(≥3:1 ✓), 글자 `#0B4F9E` = 7.99:1 ✓ / 우 `primary` 흰 글자 = 7.99:1 ✓ / 상단 경계선은 장식이며 바와 본문의 구분은 배경 흰색 + 1px 라인 + 그림자 아닌 실선으로 전달한다.

### CMP-008 Skip Link

포커스 전에는 화면 밖(`position:absolute; left:-9999px`)에 두고, `:focus`에서 **좌상단 16px 지점에 `primary md` 버튼**으로 나타난다. 라벨 "본문 바로가기", 대상 `#main`. `z-index`는 `--z-toast`(헤더 위에 떠야 한다).

> **구현 확정 (developer R1 #7)**: 대상 요소는 **`<main id="main" tabindex="-1">`** 으로 만든다. Safari 등 일부 브라우저는 `tabindex="-1"`이 없으면 skip link를 눌러도 포커스가 실제로 이동하지 않는다. 목업에는 `.skip` CSS만 있고 마크업이 빠져 있었으므로 v0.2에서 **`mockups/scr-003.html`·`mockups/scr-001.html`의 대표 프레임과 신규 `mockups/scr-006.html`에 마크업을 넣었다.** `scr-002.html`·`scr-008.html`은 `.skip` 스타일 자체가 없어 v0.2 반영 범위에서 제외했다(같은 구조 반복 — **구현 정본은 이 절이며 전 화면에 적용한다**).

### CMP-009 Container / Section

- `.container`: `max-width: var(--container-max); margin-inline:auto; padding-inline: var(--container-pad)`
- `.section`: 상하 패딩 = `<768px` 56px / `768~1279px` 72px / `≥1280px` **96px**(보정 1). 섹션 사이 구분은 1px `--color-border` 또는 `--color-surface-alt` 교차 배경 **둘 중 하나만** 쓴다(중복 금지).
- `.section--hero`: 상하 패딩 = 64 / 80 / **104px**(보정 1)

### CMP-010 Card (3변형)

| 변형 | 구조 | 수치 |
|---|---|---|
| `card--feature` (강점) | 원형 아이콘 프레임 → h3 → 설명 2줄 | 패딩 24px(`<768`) / 32px(`≥1280`), radius **12px**, 테두리 1px `#DDE4EC`, 배경 `#FFFFFF` |
| `card--lesson` (수업 유형) | 태그 → h3 → 설명 1~2문장 | 동일. 상단에 **1:1 사진 자리**(현재 미사용) |
| `card--instructor` (강사) | 1:1 이미지 영역 → 이름 h3 → 담당 수업 → 경력(최대 3줄, 초과 시 "더 보기") | 동일. 이미지 영역은 `aspect-ratio: 1/1`, radius 상단 12px |

공통: **그림자 없음**. hover 시 테두리만 `#7E8FA3`로 진해진다(`--motion-fast`). **카드 전체를 링크로 만들지 않는다**(강사 카드는 상세 화면이 없다 — 화면정의서 SCR-002 §2).

### CMP-011 Icon Frame (보정 2)

원형 `56×56px`, 배경 `--color-primary-subtle`, 테두리 1px `--color-border`, 내부 아이콘 24px `--color-primary`. **장식이므로 `aria-hidden="true"`** (같은 의미가 카드 제목에 텍스트로 있다).

### CMP-012 Eyebrow Label

`--radius-pill`, 배경 `#FFFFFF`, 테두리 1px `#7E8FA3`, 글자 `#0B4F9E` 12.5~13px/700, letter-spacing 0.1em, padding `6px 14px`. **장식이 아니라 텍스트**이므로 스크린리더에 읽힌다.

### CMP-013 Callout

| 변형 | 좌측 바 3px | 배경 | 글자 | 아이콘 |
|---|---|---|---|---|
| `info` | `#0B4F9E` | `#F0F5FB` | `#16263A` (13.96:1) | info 16px `#0B4F9E` |
| `warn` | `#8A5200` | `#FAF0E1` | `#8A5200` (5.66:1) | alert-triangle |
| `error` | `#B3261E` | `#FBEAE8` | `#B3261E` (5.61:1) | alert-circle |

패딩 16px 18px, radius `--radius-md`(좌측 바 쪽은 0), 폰트 14~15px.

### CMP-014 Definition List (라벨–값)

`<dl>` 기반. `<768px` 1열(라벨 위 14px `#5A6B7D`/700 → 값 15px `#16263A`), `≥768px` 좌 라벨 96px 고정 + 우 값. 행 간 1px `#DDE4EC`, 행 세로 패딩 14px. **값이 미확정이면 행 자체를 렌더하지 않는다.** 행 우측에 `sm` 버튼(주소 복사·전화 걸기)을 둘 수 있고 그 버튼은 44×44 이상.

### CMP-015 Text Input

| 상태 | 규칙 |
|---|---|
| 기본 | 높이 **52px**, padding `0 14px`, 테두리 1px `#7E8FA3`(3.31:1), radius 8px, 배경 `#FFFFFF`, **font-size 16px**, 글자 `#16263A` |
| placeholder | `#5A6B7D` (5.48:1). **placeholder를 라벨 대용으로 쓰지 않는다** |
| hover | 테두리 `#5A6B7D` |
| focus-visible | 테두리 `#0B4F9E` 2px + 포커스 링 3px offset 2px |
| 오류 | 테두리 **2px `#B3261E`** + 좌측 아이콘 없음(아이콘은 오류 문구에) + `aria-invalid="true"` |
| disabled | 배경 `#EEF1F5`, 테두리 `#C4CDD8`, 글자 `#5A6B7D` |
| 자동완성 | `autocomplete="name"`·`"tel"` 지정 |

### CMP-016 Textarea + 글자 수 카운터

높이 min 140px(`<768px`) / 160px, padding `12px 14px`, `resize: vertical`. 카운터는 우측 하단 14px `#5A6B7D`, **`aria-live="polite"`로 100자 단위에서만 읽어 준다**(매 글자 읽기 금지). 한도 초과 시 카운터가 `#B3261E`/700으로 바뀌고 **동시에 "최대 500자까지 입력할 수 있습니다." 문구를 띄운다**(색만으로 전달 금지).

### CMP-017 Checkbox (동의)

박스 **24×24px**, 테두리 1px `#7E8FA3`, radius 6px. 체크 시 배경 `#0B4F9E` + 흰 체크 아이콘 16px. **라벨을 포함한 행 전체가 클릭 영역이고 min-height 44px**. 필수 표시는 라벨 끝 `*`(색 `#B3261E`) + **`required` 속성 + "(필수)" 텍스트**(색만으로 전달 금지). 동의 문구 안의 "개인정보 처리방침 보기"는 새 창 링크(CMP-002).

### CMP-018 Form Field (래퍼)

구조: `라벨(15~16px/700) → 설명(14px #5A6B7D, 선택) → 입력 → 오류 문구(14px #B3261E + 16px 아이콘)`.
- 라벨과 입력은 `<label for>`로 연결한다. 설명·오류는 `aria-describedby`로 연결한다.
- 필드 간 세로 간격 **20px**, 라벨–입력 8px, 입력–오류 6px.
- **검증 시점은 blur 이후**(REQ-F-041). 입력 중 실시간 오류 표시 금지.
- 오류 발생 시 레이아웃이 밀리지 않도록 **오류 문구 자리를 미리 비워 두지 않는다** — 대신 폼 컨테이너에 `contain: layout` 없이 자연 증가를 허용하고, 제출 버튼 위치 변화는 CLS 판정 대상 밖(사용자 조작 후 변화)이다.

### CMP-019 Error Summary Block

폼 상단에 삽입. `role="alert"` + `tabindex="-1"` + 제출 실패 시 **포커스 이동**. 배경 `#FBEAE8`, 테두리 1px `#E8B3AE`, 좌측 바 3px `#B3261E`, radius 8px, 패딩 16px.
구성: 제목("입력 내용을 확인해 주세요") + 오류 항목 **링크 목록**(누르면 해당 필드로 포커스 이동). REQ-N-008의 "입력 5개 이상 폼" 기준을 문의 폼(4항목)에도 적용한다 — **비용이 거의 없고 2차 폼 8~10항목에 그대로 재사용**된다.

### CMP-020 Result Block (성공 / 실패)

폼을 **교체**하는 블록(같은 화면 내 상태 전환). `tabindex="-1"` + 포커스 이동.

| 변형 | 배경 | 테두리 | 아이콘 | role |
|---|---|---|---|---|
| 성공 | `#E7F4EC` | 1px `#9FCBB1` | check-circle 28px `#1B6E3C` | `role="status"` |
| 실패 | `#FBEAE8` | 1px `#E8B3AE` | alert-circle 28px `#B3261E` | `role="alert"` |

패딩 24px, radius **12px**(1차 소개형). 성공은 제목 + 안내 2줄 + "다시 문의하기" `secondary md`. 실패는 제목 + 안내 + **전화 링크**(대체 연락 수단) + "다시 시도" `primary md`, **입력값 유지**.

### CMP-021 Toast

화면 하단 중앙, **고정 바 위 12px**(`bottom: calc(var(--fixed-bar-h) + var(--safe-b) + 12px)`), `z-index: var(--z-toast)`. 배경 `#16263A`, 글자 `#FFFFFF`(15.30:1), radius 8px, 패딩 `12px 16px`, 14~15px. 3초 후 자동 사라짐, `role="status"`. 등장은 `opacity` + `translateY(var(--motion-distance))` `--motion-base` — reduce에서 이동 0.

### CMP-022 Map Placeholder (클릭 투 로드)

| 항목 | 내용 |
|---|---|
| 높이(로드 전후 **동일**) | `<768px` **272px** / `768~1279px` **320px** / `≥1280px` **400px** |
| 배경 | 브랜드 라인 격자 그래픽(CSS `repeating-linear-gradient`, 40px 간격, `rgba(11,79,158,.10)`) + `#FFFFFF` |
| 테두리 | 1px `#7E8FA3`, radius **12px**, `overflow: hidden` |
| 중앙 | `primary md` "지도 불러오기"(min 48px) |
| 하단 고지 | 12px 아래 14px `#5A6B7D` "지도를 불러오면 `[지도 서비스명]`으로 연결됩니다" |
| 로드 후 | 같은 박스 안에 `iframe` 100%×100%, `title="요가패스 위치 지도"`. **버튼 제거, 포커스는 지도 섹션 제목으로 이동** |
| CLS | 로드 전후 높이가 동일하므로 레이아웃 이동 0 |
| JS 비활성 | `<noscript>` 안에 주소 텍스트 + 외부 지도 길찾기 링크 + 전화 링크(REQ-N-029) |
| 지도 캡처 | **사용 금지**(REQ-N-024). 대체 영역은 CSS 그래픽이며 이미지 파일이 아니다 |

### CMP-023 Anchor Chip

`--radius-pill`, min-height **44px**, padding `0 16px`, 테두리 1px `#7E8FA3`, 글자 `#0B4F9E` 15px/700. 칩 간격 8px, **`flex-wrap: wrap`으로 줄바꿈 허용**(200% 확대 시 가로 스크롤 방지). 활성(현재 섹션) 상태는 배경 `#F0F5FB` + 테두리 `#0B4F9E` + `aria-current="true"`.

### CMP-024 Page Header

h1 + 리드(`--font-lead`, `#5A6B7D`) + (선택) 앵커 칩. 상하 패딩 = `<768px` 32/24px, `≥1280px` 56/32px. 하단 1px `#DDE4EC`. **h1은 화면당 1개**(REQ-N-009).

### CMP-025 CTA Band (하단 전환 블록)

배경 `--color-primary-subtle` `#F0F5FB`, 상하 1px `#DDE4EC`, 상하 패딩 = 섹션 값과 동일. 중앙 정렬: h2(22/26/32px) → 보조 문구(`#5A6B7D`) → 버튼 2개(`primary lg` + `secondary lg`), 버튼 간격 12px, `<768px`에서는 **세로 스택 + 전폭**.
틴트 위 대비: 제목 `#16263A` **13.96:1** ✓ / 보조 `#5A6B7D` **5.00:1** ✓ / `secondary` 버튼 배경을 `#FFFFFF`로 유지해 틴트와 구분.

### CMP-026 Empty State

중앙 정렬. 아이콘 40px `#7E8FA3` → 안내 문장(15~16px `#16263A`) → 보조 문장(14px `#5A6B7D`) → 다음 행동 버튼(`secondary md`). 패딩 40px 24px, 배경 `#F7F9FC`, 테두리 1px `#DDE4EC`, radius 12px.
**문구 규칙: "준비 중"을 쓰지 않는다.** 표준 문형 = `"{대상}은 공개되면 안내드립니다. 자세한 내용은 전화로 문의해 주세요."`

### CMP-027 Initial Avatar

`aspect-ratio: 1/1`, 배경 `#F0F5FB`, 테두리 1px `#DDE4EC`, 중앙에 이름 첫 글자 (`#0B4F9E`, 카드 폭의 34% 크기, 700). **`aria-hidden="true"` — 대체 텍스트를 주지 않는다**(카드 안에 이름이 이미 텍스트로 있다 — 화면정의서 SCR-002 §3).
**인물 스톡 사진으로 대체하지 않는다.** 사진이 실제로 있을 때만 `alt="{이름} 강사"`.

### CMP-028 TOC (앵커 목차)

`≥1024px`: 좌측 240px `position: sticky; top: calc(var(--header-h) + 24px)`. 항목 min-height 44px, 현재 항목 `aria-current="true"` + 좌측 2px `#0B4F9E` 바.
`<1024px`: `<details>` 접이식("목차" 요약, 기본 접힘). **JS 없이 동작한다.**

### CMP-029 Back To Top

`icon` 버튼 48×48, 우측 하단 `bottom: calc(var(--fixed-bar-h) + var(--safe-b) + 16px)`, `z-index: var(--z-fixed-bar)` − 1. 스크롤 600px 이상에서 노출. `aria-label="맨 위로"`. **Could 항목**이며 미구현해도 게이트를 막지 않는다.

### CMP-030 Divider

1px `--color-border`. **정보 구분(섹션 경계)에는 여백을 우선 쓰고 라인은 보조**로만 쓴다. 1.28:1이므로 라인만으로 의미를 전달하지 않는다.

---

## 3. 2차 확장 예고 (요구사항 §10 TR-10 대응)

> **1차 토큰은 폐기·재정의하지 않고 확장만 한다.** 아래는 2차 P3에서 **추가로 정의할 컴포넌트 목록과 지금 고정해 두는 원칙**이다. 원칙을 미리 박아 두면 2차에서 토큰을 다시 만들지 않는다.

### 3.1 확장 컴포넌트 목록 (27종)

| ID | 이름 | 대상 화면 | 지금 고정하는 원칙 |
|---|---|---|---|
| CMP-040 | **Calendar Grid (월)** | SCR-110, SCR-902 | `role="grid"` + roving tabindex, **비활성 날짜도 포커스 허용**. 셀 44×56px 이상, 경계 간격 `--space-c1`(2px), 캘린더 좌우 패딩 12px 고정. radius 8px |
| CMP-041 | Slot Card (슬롯) | SCR-111 | 좌측 3px 상태 컬러 바 + 배지 + 시간(tabular-nums). 카드 min-height 96px |
| CMP-042 | **Data Table** (+모바일 카드 변형) | SCR-908·909·913 등 | `≥1024px` 표 / `<1024px` **카드 리스트로 전환**(가로 스크롤 금지). sticky 표 헤더 `--z-sticky-table`. 셀 패딩 `--space-c2 --space-c3`, 표 헤더 13px/700 |
| CMP-043 | **Status Badge (4군)** | 전 2차 화면 | 예약 / 상담 / 스케줄 / 슬롯 4군. **§1.1 (2) 상태색만 사용**하고 새 색을 만들지 않는다. **반드시 텍스트 라벨 + 아이콘 또는 패턴 병기**. radius `--radius-sm`, 11.5~12px/700, padding `1px 7px` |
| CMP-044 | Select | 폼 화면 | 높이 52px, 네이티브 `<select>` 우선. 커스텀 드롭다운은 `--z-dropdown` |
| CMP-045 | Radio / Segmented | SCR-020·105 | 터치 44px, 선택 상태는 **테두리 2px + 체크 아이콘** 병기 |
| CMP-046 | Date / Time Picker | SCR-020·905 | 네이티브 입력 우선 + 캘린더 보조. **키보드 직접 입력 경로 필수** |
| CMP-047 | Tabs | SCR-101 (예정/지난) | `role="tablist"`, 선택 탭은 하단 2px 바 + 700 + `aria-selected` |
| CMP-048 | Modal / Dialog | 취소 확인 등 | `--z-modal`, `--shadow-modal`, **포커스 트랩 + Esc 닫기 + 열기 전 요소로 포커스 복귀**. `<768px`는 하단 시트 |
| CMP-049 | Dropdown Menu | 헤더 회원 유틸 | `--z-dropdown`, `aria-expanded`·`aria-haspopup="menu"`, 방향키 이동, Esc 닫기 |
| CMP-050 | Pagination | 목록 화면 | 항목 44×44, 현재 페이지 `aria-current="page"` |
| CMP-051 | Filter Chip | SCR-111 | CMP-023 확장(선택 상태 + 해제 버튼) |
| CMP-052 | Breadcrumb | 관리자 상단바 | 마지막 항목 `aria-current="page"` |
| CMP-053 | **Admin Shell** | SCR-900~916 | 사이드바 `≥1280px` 240px 고정 / **`1024~1279px` 아이콘 모드 64px** / `<1024px` 상단 드로어. 상단바 56px. **공개 헤더·GNB·고정 바 미적용**(G-13) |
| CMP-054 | Stepper | 예약 흐름 | 현재 단계 `aria-current="step"` |
| CMP-055 | Session Expiry Banner | 회원·관리자 | 만료 2분 전 `warn` 콜아웃 + "로그인 유지" 버튼, `role="status"` |
| CMP-056 | Popover | 주 뷰 슬롯 상세 | `--z-dropdown` |
| CMP-057 | Week Grid (30분) | SCR-903 | 시간축 64px, **`≥1280px` 열 폭 하한 127px · `1024~1279px` 하한 120px**, 행 28px. **드래그를 도입하면 키보드 대안을 같은 화면에 병행**한다 |
| CMP-058~066 | Progress / Tooltip / File Upload / Avatar Upload / Search Field / Accordion / Alert Banner / Split Button / Count Badge | 2차 각 화면 | 전부 기존 토큰 조합으로 만들고 **새 컬러·새 radius를 만들지 않는다** |

### 3.2 2차에서 추가될 토큰 (지금 이름만 예약)

| 예약 토큰 | 예정 값 | 이유 |
|---|---|---|
| `--admin-sidebar-w` / `--admin-sidebar-w-compact` | 240px / 64px | CMP-053 |
| `--admin-topbar-h` | 56px | CMP-053 |
| `--table-row-h` | 44px | CMP-042 (터치 하한과 동일) |
| `--cell-min-h` | 56px | CMP-040 |
| `--week-col-min-w` | 127px (`≥1280`) / 120px (`1024~1279`) | CMP-057. **2차 착수 시 재확인**(developer R1 #11): 1024px 실측 = `1024 − 사이드바 64 − 컨테이너 패딩 32×2 − 시간축 64 = 832`, `÷ 7 = 118.86px`로 120px 하한에 **1.1px 모자라 가로 스크롤이 생긴다.** 하한을 118px로 내리거나 이 화면의 컨테이너 패딩을 24px로 좁혀 해소한다. **1차 토큰에는 영향이 없어 지금 고치지 않는다** |

> **새로 추가되는 것은 위 5종 계열뿐이며 §1의 컬러·타이포·간격·radius·shadow·motion·z-index·breakpoint 토큰은 값이 바뀌지 않는다.** 이것이 TR-10의 "변경된 토큰 0건" 목표다.

### 3.3 레슨 유형 배지 색 — 미해결 사항

레슨 유형은 2차에서 **관리자 관리 대상**(REQ-F-A-025)이라 designer가 고정 팔레트를 줄 수 없다. 두 선택지를 남긴다.
- **ⓐ 중립 1색 + 텍스트 구분** (권고) — 배지 색을 쓰지 않고 유형명 텍스트로만 구분. 색 관리 비용 0, 접근성 위험 0.
- **ⓑ 검증된 6~8색 팔레트를 designer가 제공하고 관리자가 그중 선택** — 시각 구분은 좋아지지만 팔레트 밖의 색이 들어올 경로를 막아야 한다.
→ **2차 착수 시 PM 결정 항목**이다. 1차 디자인에는 영향이 없다.

---

## 4. 접근성 규칙 (판정 기준)

### 4.1 대비 — 전 조합 측정표

| # | 전경 | 배경 | 대비 | 기준 | 판정 |
|---|---|---|---|---|---|
| 1 | `#16263A` 본문 | `#FFFFFF` | **15.30:1** | 4.5:1 | 통과 |
| 2 | `#16263A` 본문 | `#F0F5FB` 틴트 | **13.96:1** | 4.5:1 | 통과 |
| 3 | `#5A6B7D` 보조 | `#FFFFFF` | **5.48:1** | 4.5:1 | 통과 |
| 4 | `#5A6B7D` 보조 | `#F0F5FB` 틴트 | **5.00:1** | 4.5:1 | 통과 |
| 5 | `#5A6B7D` 비활성 | `#EEF1F5` | **4.83:1** | (면제) | 통과 |
| 6 | `#0B4F9E` 링크·버튼 글자 | `#FFFFFF` | **7.99:1** | 4.5:1 | 통과 |
| 7 | `#0B4F9E` | `#F0F5FB` 틴트 | **7.30:1** | 4.5:1 | 통과 |
| 8 | `#FFFFFF` | `#0B4F9E` primary 버튼 | **7.99:1** | 4.5:1 | 통과 |
| 9 | `#FFFFFF` | `#08407F` hover | **10.24:1** | 4.5:1 | 통과 |
| 10 | `#FFFFFF` | `#06336A` active | **12.43:1** | 4.5:1 | 통과 |
| 11 | `#FFFFFF` | `#0A2540` 푸터 | **15.53:1** | 4.5:1 | 통과 |
| 12 | `#B9C9DC` 푸터 보조 | `#0A2540` | **9.21:1** | 4.5:1 | 통과 |
| 13 | `#1B6E3C` 성공 | `#FFFFFF` | **6.28:1** | 4.5:1 | 통과 |
| 14 | `#1B6E3C` | `#E7F4EC` | **5.55:1** | 4.5:1 | 통과 |
| 15 | `#8A5200` 경고 | `#FFFFFF` | **6.39:1** | 4.5:1 | 통과 |
| 16 | `#8A5200` | `#FAF0E1` | **5.66:1** | 4.5:1 | 통과 |
| 17 | `#B3261E` 오류 | `#FFFFFF` | **6.54:1** | 4.5:1 | 통과 |
| 18 | `#B3261E` | `#FBEAE8` | **5.61:1** | 4.5:1 | 통과 |
| 19 | `#4F5B6B` 마감 | `#FFFFFF` | **6.90:1** | 4.5:1 | 통과 |
| 20 | `#4F5B6B` | `#EEF1F5` | **6.09:1** | 4.5:1 | 통과 |
| 21 | `#7E8FA3` 입력 테두리·UI 경계 | `#FFFFFF` | **3.31:1** | 3:1 (1.4.11) | 통과 |
| 22 | `#0B4F9E` 포커스 링 | `#FFFFFF` | **7.99:1** | 3:1 | 통과 |
| 23 | `#0B4F9E` 포커스 링 | `#F0F5FB` | **7.30:1** | 3:1 | 통과 |
| 24 | `#FFFFFF` 포커스 링 | `#0A2540` | **15.53:1** | 3:1 | 통과 |
| 25 | `#DDE4EC` 장식 구분선 | `#FFFFFF` | 1.28:1 | — | **장식 전용 — 정보 전달 금지** |
| 26 | `#FFFFFF` 히어로 텍스트 | 사진 + `rgba(10,37,64,.68)` (최악=백색 사진) | **5.50:1** | 4.5:1 | 통과 |
| 27 | `#FFFFFF` 히어로 텍스트 | 사진 + `rgba(10,37,64,.78)` | **7.72:1** | 4.5:1 | 통과 |

> **대비 미달 색은 팔레트에 하나도 없다.** 밝은 파랑(`#3B82F6`·`#4DA3FF` 계열, 흰 배경 2.6~3.1:1)은 이 시스템에 존재하지 않으며 **추가를 금지**한다.

### 4.2 터치 타깃

| 대상 | 규칙 |
|---|---|
| 모든 버튼·링크 버튼·입력·체크박스 행 | **44×44px 이상** |
| 인접 조작 요소 간격 | **8px 이상** (`--touch-gap`) |
| **격자형 컴포넌트 예외(2차)** | 캘린더 날짜 셀은 **셀 44×44px 이상 + 경계 간격 2px 이상**이면 된다(REQ-N-006 ②-1). 360px 실측 셀 폭 46.28px · 높이 56px |
| 본문 중간 인라인 링크 | WCAG 2.5.5 인라인 예외 적용. 줄 높이 1.7 확보 |

### 4.3 장식 이미지 판정 목록 (REQ-N-006 ④ — 이 문서가 단일 기준)

| 분류 | 대상 | 처리 |
|---|---|---|
| **장식** (`alt=""` 또는 `aria-hidden="true"`) | 히어로 라인 격자 패널 / 강점 카드 아이콘(CMP-011) / 수업 유형 카드 태그 아이콘 / 위치 요약 브랜드 그래픽 / 섹션 구분선 / 이니셜 아바타(CMP-027) / **텍스트 라벨과 함께 쓰인 모든 버튼·링크 내부 아이콘** / 콜아웃 아이콘 / 지도 대체 영역의 격자 배경 / 마감 사선 해치(2차) / 가로형 로고 안의 심볼 부분 |
| **의미 있음** (대체 텍스트 필수) | 헤더·푸터 로고 — `alt="요가패스 홈"`(링크일 때) / 강사 실제 사진 — `alt="{이름} 강사"` / OG 이미지 — `og:image:alt` / 지도 `iframe` — `title="요가패스 위치 지도"` / **아이콘 단독 버튼** — `aria-label`(전화 문의·메뉴 열기·닫기·맨 위로·복사) |
| **판정 원칙** | **같은 정보가 인접 텍스트에 이미 있으면 장식이다.** 그 정보가 이미지에만 있으면 의미 있는 이미지다 |

### 4.4 400% 확대 · reflow (G-11 · REQ-N-006 ⑤ — 이 문서가 규칙을 정의한다)

1280px를 400% 확대하면 **가로 320px · 세로 약 400px 상당**이 된다. 이 조건에서:

| 대상 | 규칙 | 조건 |
|---|---|---|
| 하단 고정 바 | `position: static`으로 전환해 **문서 마지막에 정적 배치**, `--body-pad-bottom: 0` | `@media (max-height: 420px) and (max-width: 400px)` |
| sticky 헤더 | `position: static`으로 전환 | `@media (max-height: 420px) and (max-width: 400px)` |
| **앵커 오프셋** | `--anchor-offset: var(--space-4)`(16px)로 낮춘다. 헤더가 떠 있지 않은데 80~88px 오프셋을 유지하면 **세로 420px 뷰포트의 약 20%가 빈 여백**이 되어 G-11의 목적(콘텐츠 손실 방지)과 반대로 움직인다 (developer R1 #4) | `@media (max-height: 420px) and (max-width: 400px)` |
| 전 레이아웃 | 1열 전환, **가로 스크롤 0** | `@media (max-width: 400px)` |
| 칩·버튼 그룹 | `flex-wrap: wrap`으로 줄바꿈(가로 스크롤 금지) | 항상 |
| **캘린더(2차)** | 7열 `role="grid"`를 **주 단위 리스트(`<ul>`)로 전환**한다. 각 주가 제목(`{n}월 {d}일 ~ {d}일`), 각 날짜가 리스트 항목(min-height 44px, 날짜 + 상태 라벨 + 잔여). **데이터·접근 이름·링크 목적지는 그리드와 동일**하고 표현만 바뀐다 | `@media (max-width: 359.98px), (max-height: 420px)` |
| 데이터 표(2차) | CMP-042의 모바일 카드 변형을 그대로 쓴다 | `@media (max-width: 1023.98px)` |

**근거**: 세로 420px에서 헤더 64px + 고정 바 60px = 124px이 뷰포트의 29.5%를 차지해 본문 가용 높이가 300px 아래로 떨어진다. 콘텐츠 손실(WCAG 1.4.10) 판정을 피하려면 이 지점에서 고정 요소를 풀어야 한다.

> **조건식에 `and (max-width: 400px)`를 병기하는 이유 (v0.2 · planner R1 #2)**: `max-height: 420px` 단독이면 **가로 모드 휴대폰(360×640 → 640×360)** 에서도 발동해 **1차의 유일한 상시 전환 수단인 고정 바가 화면에서 사라진다**(G-1 "스크롤 위치·상태로 숨기지 않는다"의 취지와 충돌). 판정 뷰포트(360/768/1280 세로)에는 걸리지 않아 P5에서 잡히지 않는 종류의 문제다. 1280px 400% 확대는 **가로 320px · 세로 약 400px**이라 `max-width: 400px`에 그대로 걸리고, 가로 모드 휴대폰(가로 640px 이상)은 제외된다. §1.6 CSS 블록과 이 표를 함께 고쳤다.

### 4.5 키보드 · 스크린리더

- **포커스 순서 = DOM 순서.** `tabindex` 양수 금지.
- `outline: none`을 어디에도 쓰지 않는다. 커스텀 포커스 스타일을 쓰더라도 `:focus-visible`에서 3:1 이상 대비의 링이 보여야 한다.
- 랜드마크: `header` / `nav` / `main#main` / `footer`. **h1은 화면당 1개**, 제목 단계 건너뜀 0.
- 열림/닫힘 요소는 `aria-expanded`, 현재 위치는 `aria-current`, 상태 알림은 `role="status"`(성공) / `role="alert"`(오류).
- **패널·모달은 포커스 트랩 + Esc 닫기 + 트리거로 포커스 복귀**.
- `<html lang="ko">`.

### 4.6 접근성 체크리스트

- [x] 본문 텍스트 대비 4.5:1, 큰 텍스트 3:1 이상 — §4.1 측정표 27조합 전부 통과
- [x] UI 컴포넌트·그래픽 경계 3:1 이상 — `#7E8FA3` 3.31:1
- [x] 포커스 표시가 모든 인터랙티브 요소에 명확함 — §2.0 · §4.5
- [x] 터치 영역 44×44px 이상, 인접 간격 8px 이상 — §4.2 (격자 예외 명시)
- [x] 색상만으로 정보를 전달하지 않음 — §1.1 (2) "색 외 구분 수단" 열
- [x] 모션은 `prefers-reduced-motion` 대응 — §1.4 · §1.6
- [x] 장식 이미지 판정 목록 정의 — §4.3
- [x] 400% 확대 reflow 규칙 정의 — §4.4
- [x] 본문 최소 14px / 입력 16px — §1.2

---

## 5. 전역 UI 규칙(§3.0 G-0~G-13)에 대한 P3 확정값

> **규칙 본문은 `planning/02_requirements.md` §3.0이 단일 기준이다.** 아래는 그 규칙이 "P3가 확정한다"고 넘긴 값만 모은 것이며, 규칙 문장을 복제하지 않는다.

| 규칙 | P3가 확정한 값 | 토큰 |
|---|---|---|
| G-2 고정 바 높이 | **60px** (하한 56px 이상) | `--fixed-bar-h` |
| G-3 본문 하단 여백 | `calc(60px + env(safe-area-inset-bottom) + 16px)` = **76px + safe-area** | `--body-pad-bottom` |
| G-4 제출 버튼 간격 | 폼 마지막 요소 하단 마진 **16px** + G-3 여백 | `--space-4` |
| G-5 고정 바 구성 | 버튼 `sm`(44px) × 2, 간격 8px, 좌 40% / 우 60%, 좌우 패딩 12px | CMP-007 |
| G-8 헤더 CTA | `≥1280px`에서만 `primary md`. **자기 참조 처리는 CMP-003 H1~H3**(고정 바 S1~S3와 동일한 판단 축 — v0.2 신설) | CMP-003 |
| G-6 ① 헤더 적용 | 자기 참조 → 헤더 주 CTA를 **"전화 문의"(`tel:`)로 대체**(H2) | CMP-003 |
| G-6 ② 헤더 적용 | 자기 참조 + 대표 전화 `[TBD]` → 헤더 주 CTA **미노출**(H3) | CMP-003 |
| G-6 ② 비적용 화면 | 자기 참조가 아닌 화면에서 대표 전화가 `[TBD]`면 **바는 유지하고 좌측 전화 버튼만 미렌더**(S1 보조 규칙) | CMP-007 |
| G-9 `scroll-padding-bottom` | `--scroll-pad-bottom` = `--body-pad-bottom` | `html` 선언 |
| G-10 헤더 높이 · 앵커 오프셋 | 64 / 68 / 72px, 앵커 오프셋 = `헤더 높이 + 16px` | `--header-h` · `--anchor-offset` |
| G-11 400% 확대 | `@media (max-height: 420px) and (max-width: 400px)` → 헤더·고정 바 정적 배치 + 앵커 오프셋 16px (v0.2: 가로 모드 휴대폰 오발동 방지) | §4.4 |
| G-12 회원 헤더(2차) | 공개 헤더 + 회원 메뉴. 구간별 구성은 **IA §2.1 표를 따른다**(값 복제 안 함) | CMP-003 |
| G-13 관리자 셸(2차) | 사이드바 240 / 64px, 상단바 56px | CMP-053 |
| IA §2.1 GNB 전제 | 항목 좌우 패딩 **12px 고정**, 로고 폭 상한 **140px** | `--gnb-item-pad-x` · `--logo-max-w` |

> ⚠ **개발·기획 확인 필요**: G-3의 파생값이 기획 문서에 예시로 적혀 있던 **72px이 아니라 76px**이 된다(고정 바를 56px이 아닌 60px로 확정했기 때문). 기획 3문서는 "계산식이 기준이고 72px은 파생값"이라고 명시해 두었으므로 **문서 수정은 필요 없다.** P5 판정은 계산식으로 한다.

---

## 6. 아이콘 · 이미지 가이드

### 6.1 아이콘 세트 — **Lucide 채택 (확정 · 번복하지 않는다)**

| 항목 | 내용 |
|---|---|
| 세트 | **Lucide** — https://lucide.dev |
| 라이선스 | **ISC License** (상업적 사용·수정·재배포 가능). 고지문을 `design/assets/SOURCES.md`와 저장소 `LICENSES/` 에 동봉한다 |
| 채택 이유 | 2px stroke·24px 그리드·각 없는 라운드 캡이 시안 A의 1px 라인 구조와 결이 같다. 아이콘 수가 충분해 2차 40~60종을 한 세트로 덮는다 |
| 사용 규격 | 기본 24px / 작게 16~18px / 아이콘 프레임 안 24px / 히어로·빈 상태 40px. **stroke-width 2px 고정**(크기가 작아져도 1.5px로 바꾸지 않는다 — 대비 유지) |
| 색 | `currentColor` 사용. 단독으로 색을 지정하지 않는다 |
| 구현 | **인라인 SVG 또는 SVG 스프라이트**. 아이콘 폰트를 쓰지 않는다(폰트 로드 실패 시 의미 없는 글리프가 남는다) |
| 접근성 | 텍스트와 병기 → `aria-hidden="true"` / 단독 → `role="img"` + `aria-label` |

**1차 필요 아이콘 16종**: `phone` · `menu` · `x` · `map-pin` · `navigation`(길찾기) · `copy` · `clock` · `train-front`(지하철) · `bus` · `car`(주차) · `arrow-right` · `arrow-up` · `external-link` · `check-circle-2` · `alert-circle` · `info`
**2차 추가 예상 30~45종**: 캘린더·사용자·잠금·필터·정렬·편집·삭제·저장·검색·체크·경고·벨 등

### 6.2 이미지 규칙

| 항목 | 규칙 |
|---|---|
| 형식 | **AVIF → WebP → JPEG/PNG 순 폴백**(`<picture>`). 로고·아이콘·그래픽은 **SVG** |
| 용량 상한 | 히어로 배경 **200KB 이하**(1920px 기준) / 카드·강사 사진 **80KB 이하**(800px 기준) / OG 이미지 **300KB 이하** |
| 반응형 | `srcset` + `sizes` 필수. `width`·`height` 속성 또는 `aspect-ratio` 필수(**CLS 0**) |
| 지연 로딩 | 히어로 이미지는 `loading="eager"` + `fetchpriority="high"`, 나머지는 `loading="lazy"` |
| 비율 | 히어로 배경 **16:9** / 수업 유형 카드 **1:1** / 강사 카드 **1:1 (표시 규격 단일 확정)** / OG **1200×630** |
| 강사 사진 크롭 | 원본이 4:5여도 **1:1로 상단 기준 중앙 크롭**(`object-fit: cover; object-position: 50% 28%`). 얼굴이 상단 1/3에 오는 것을 전제로 하며, 고객 제출 규격에 이 기준을 명시한다 |
| 톤 | 밝고 채도 낮은 자연광. 강한 필터·비네팅 금지. **인물이 화면을 가득 덮는 구성 지양**(PM 지시 2026-09-12) |
| 금지 | **지도 서비스 화면 캡처**(REQ-N-024) / **인물 스톡 사진을 특정 강사 사진으로 사용**(REQ-F-022) / 라이선스 미확인 자산 |
| 출처 기록 | 모든 자산은 **파일을 넣기 전에** `design/assets/SOURCES.md`에 행을 추가한다(REQ-N-024, 누락 0건) |

### 6.3 브랜드 자산

| 자산 | 상태 | 비고 |
|---|---|---|
| `logo-yogapass-mark.svg` (48×48) | **임시(Placeholder)** | `currentColor` 기반. 헤더·푸터·파비콘 공용 |
| `logo-yogapass-horizontal.svg` (236×48) | **임시(Placeholder)** | 헤더 로고. 워드마크가 `<text>`라 **확정본은 아웃라인(path) 변환 필요** |
| 파비콘 세트 (`favicon.ico` 32/48, `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` 180) | **미제작 — 납기 확정** | **G3 승인 직후 2작업일 이내에 임시 로고(심볼 SVG) 기반으로 제작해 `design/assets/`에 넣고 developer에게 티켓으로 알린다** |
| OG 이미지 (1200×630) | **미제작 — 납기 확정** | 동일 납기. 로고 + 헤드라인 + 틴트 배경, **사진 없이 성립**하게 제작 |

> **파비콘·OG 처리 방침 확정 (developer R1 #9 — 제안대로 승인)**
> ① designer가 **G3 승인 직후 2작업일 이내**에 임시 로고 기반으로 4종 + 1종을 제작해 전달한다(고객 로고 수령 시 CR로 재제작 — D-1과 같은 경로).
> ② 그때까지 제작이 늦어지면 **placeholder 파일을 만들지 않고 `<link rel="icon">`·`og:image` 태그 자체를 뺀 채 빌드**하고, 수령 시 교체한다. 깨진 아이콘·빈 이미지가 남는 것보다 낫고 Lighthouse 권장사항 감점 폭도 작다.
> ③ OG 이미지에는 `og:image:alt`를 함께 넣는다(§4.3 "의미 있음" 분류).
| 고객 로고 원본 | **[TBD: 고객 제공 필요]** | 계획서 V-2 · 기한 09-17. AI/SVG 또는 고해상도 PNG + 브랜드 컬러 HEX + 최소 사용 크기·보호 여백 |
| 스튜디오 사진 · 강사 사진 | **[TBD: 고객 제공 필요]** | 조달 방침 미회신(Q11). **사진 0장 전제로 1차 디자인이 성립**하며, 수령 시 레이아웃 변경 없이 교체 가능 |

---

## 7. 사용 원칙 (개발 전달 노트)

1. **값을 직접 쓰지 않는다.** 모든 색·크기·간격은 §1.6의 CSS 변수를 참조한다. 하드코딩된 HEX·px는 디자인 QA에서 지적 대상이다.
2. **그림자는 z-index 40 이상에만.** 카드·버튼·입력·표에는 쓰지 않는다.
3. **`--radius-lg`(12px)는 1차 소개형 카드·패널 전용.** 버튼·입력·데이터 요소는 8px.
4. **상태색을 쓸 때는 색 외 구분 수단을 반드시 함께 넣는다**(§1.1 (2)).
5. **모바일 우선**(`min-width` 미디어 쿼리)으로 작성한다.
6. **`height` 대신 `min-height`** — 텍스트 200% 확대 대응.
7. **입력 `font-size`는 16px 미만으로 내리지 않는다** — iOS 자동 확대 방지.
8. 애니메이션은 `opacity`·`transform`만, 이동 거리 8px 이하.
9. **`[TBD]` 값은 화면에 문자열로 출력하지 않는다** — 해당 행·링크 자체를 렌더하지 않는다(REQ-N-023).
10. 신규 색·radius·간격이 필요하면 **토큰을 추가하지 말고 designer에게 티켓**(`to-design`)을 보낸다.
11. **포커스 표시 규칙 블록은 스타일시트의 맨 뒤에 둔다.** 컴포넌트 클래스 규칙보다 뒤에 와야 `outline` 선언이 덮이지 않는다(§1.6 주석 참조).
12. **행간·자간은 §1.6의 변수를 쓴다** — `--lh-h1~h4` · `--lh-body` · `--lh-caption` · `--lh-label` · `--ls-heading`(h1·h2) · `--ls-h3` · `--ls-h4` · `--ls-eyebrow`. §1.2 표의 값 중 변수로 존재하지 않는 것은 없다(v0.2에서 5개 추가 — developer R1 #6).
13. **1차에서 `font-weight: 500`(`--fw-medium`)을 사용하지 않는다** — 폰트 파일이 1세트 늘어난다(§1.2 폰트 파일 구성 ②).

---

## 8. 미해결 · 확인 필요 사항

| # | 항목 | 영향 | designer 기준(무회신 시) |
|---|---|---|---|
| D-1 | **고객 로고 원본·브랜드 컬러**(V-2, 기한 09-17) | `--color-primary` 계열 4개 + 전 화면 대비 재검증 0.5작업일 | `#0B4F9E` 확정값 유지, 수령분은 CR |
| ~~D-2~~ | ~~z-index 쌓임 순서~~ | — | **해소(2026-09-12)** — planner R1 §3.1 A · developer R1 #10 **둘 다 승인**. 구현 조건 2가지를 §1.4에 추가했다 |
| D-3 | **레슨 유형 배지 색**(§3.3) | 2차 CMP-043 | ⓐ 중립 1색 + 텍스트 구분. 2차 착수 시 PM 결정 |
| D-4 | **캘린더 셀 `잔여 {n}`의 `{n}` 정의**(잔여 자리 합계 vs 슬롯 수 — designer R2 #N1) | 2차 셀 폭 46.28px 초과 여부 | 2자리(최대 "잔여 12")를 전제로 **셀 높이 64px + 라벨 2줄** 흡수안 적용 |
| D-5 | 사진 조달 방침(Q11) | 히어로·카드 이미지 자리 | **사진 0장 전제**로 1차 완주. 수령 시 레이아웃 변경 없이 교체 |
| D-6 | 임시 로고를 1차 오픈에 사용해도 되는가(Q-D5) | 파비콘·OG 제작 시점 | 임시 로고로 제작하고 수령 시 재제작. **제작 납기·미제작 시 처리는 §6.3에서 확정**(v0.2) |
| D-7 | **폴백 `@font-face` 메트릭 오버라이드 수치**(`size-adjust`·`ascent-override`·`descent-override`) | 글꼴 교체 시 CLS | **P4 기술 설계에서 실측 → designer 1회 확인.** 수용 기준은 §1.2 ⑤에서 P3가 확정했다(블록 높이 차 ±2px 이내 · CLS 0.01 이하) |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| 0.2 | 2026-09-12 | designer | **R1 교차 검토 반영(planner 수정 요청 · developer 조건부 승인).** ① **Must** — CMP-003에 `≥1280px` **헤더 주 CTA 상태 3종(H1·H2·H3)** 신설: 고정 바와 동일한 판단 축(G-6 ①·②)을 적용해 자기 참조 시 "전화 문의" 대체 / 대표 전화 `[TBD]`면 미노출, 선택 근거·`aria-current` 처리 명문화 ② CMP-007에 **S1 보조 규칙(대표 전화 미확정 → 좌측 버튼 미렌더·우측 전폭)** 을 전 화면 공통으로 1회만 정의 ③ G-11 조건식 `and (max-width: 400px)` 병기(§1.6·§4.4) + 해당 구간 `--anchor-offset` 해제 ④ `:focus-visible`의 `border-radius` 삭제 + 선택자 풀어쓰기 + 스타일시트 말미 배치 규칙 ⑤ `ResizeObserver` 갱신 대상에 **헤더** 추가 + 비노출 구간 `removeProperty` ⑥ **폰트 파일 구성 확정**(static 400/700 + `unicode-range` 분할 subset · 500 미사용 · 폴백 메트릭 보정 필수 + 수용 기준) 및 "Variable은 weight를 덜 써도 작아지지 않는다" 전제 정정 ⑦ 행간·자간 변수 5개 추가 ⑧ CMP-005 `<details>` 정본 확정(`aria-expanded` 수동 금지, JS 역할 3가지 한정) ⑨ CMP-008 `<main id="main" tabindex="-1">` 확정 ⑩ **파비콘 4종·OG 1종 납기·미제작 시 처리 확정** ⑪ z-index 구현 조건 2줄 · D-2 해소 ⑫ CMP-004/005 weight 500 → 400 ⑬ 이동값 `--motion-distance` 참조 통일 · reduce 스피너 주석 ⑭ `--week-col-min-w` 2차 재확인 메모 ⑮ D-7 신설 | `shared/reviews/P3_design-docs_planner_r1.md` #1~#3·#8 · `shared/reviews/P3_design-docs_developer_r1.md` #1~#13 |
| 0.1 | 2026-09-12 | designer | 최초 작성 — 시안 A + 보정 1·2 기준 토큰 전량(컬러 32·타이포 10단·간격 15+3·radius 5·shadow 4·motion 7·z-index 6단·breakpoint 4구간), 개발 전달용 CSS 변수 블록, 1차 컴포넌트 30종 + 2차 확장 예고 27종, 대비 측정 27조합, 장식 이미지 판정 목록, 400% 확대·G-11 규칙, 아이콘 세트 Lucide 확정 | ADR(컨셉 선택 2026-09-12), 요구사항 §3.0·§10 TR-10, designer R1 #1·R2 #N1·#N2 |
