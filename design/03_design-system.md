---
doc_id: DSN-SYSTEM
title: 디자인 시스템
phase: P3
owner: designer
version: 1.1
status: in-review
reviewers: [planner, developer]
inputs: [design/03_design-concept.md, planning/02_requirements.md, planning/02_information-architecture.md, planning/02_storyboard.md, planning/02_storyboard-admin.md, interviews/2026-09-12_booking-rules.md, pm/01_project-plan.md, shared/reviews/P3_design-docs_planner_r1.md, shared/reviews/P3_design-docs_developer_r1.md]
updated: 2026-09-12
---

# 디자인 시스템 — 강남 요가패스

> **컨셉 확정**: 시안 A "정돈된 신뢰" (PM 결정 2026-09-12) + **보정 1·2 적용**
> · 보정 1 — 섹션 간격 88 → **96px**, 히어로 상하 패딩 88 → **104px** (`≥1280px` 한정)
> · 보정 2 — **1차 소개형 화면에 한해 카드 radius 8 → 12px**, 강점 카드 아이콘 프레임 **원형**. 캘린더·표·관리자는 8px 유지
>
> **v1.1 (2026-09-12) — 2차 확장.** G3a(1차 디자인) 승인본 v1.0에 **2차 컴포넌트 16종 승격 명세 + 1차 컴포넌트 확장 2종**(§3)을 더했다.
> · **§1의 1차 확정 토큰은 값이 하나도 바뀌지 않았다**(TR-10 "변경된 토큰 0건"). 추가는 §3.14의 관리자·데이터 레이아웃 토큰 7종뿐이고 **새 컬러·새 radius는 0건**이다.
> · §2(1차 컴포넌트 30종)는 손대지 않았다. 읽을 때 §1 → §2 → §3 순서 그대로 유효하다.
> · **2차 페이지 디자인(39화면)은 이 문서의 범위가 아니다** — 다음 작업(`design/03_page-design-2nd.md` 예정)에서 SCR별로 작성한다.
>
> **이 문서의 위치**
> 1. **§3.0 전역 UI 규칙(G-0~G-13)의 단일 기준은 `planning/02_requirements.md` §3.0이다.** 이 문서는 그 규칙이 요구한 **픽셀 토큰만 확정**하고 규칙 본문·값을 복제하지 않는다. 확정 결과는 §5에 모았다.
> 2. **1차에 쓰지 않는 토큰까지 지금 전부 정의한다.** 2차 39화면(캘린더·표·폼·배지·관리자 셸)에서 토큰을 다시 만들지 않기 위함이다(요구사항 §10 **TR-10** — "1차 토큰이 폐기·재정의되지 않고 확장만 된다").
> 3. **대비값은 designer가 WCAG 2.1 상대 휘도 공식으로 직접 계산**했다(sRGB → 선형화 → `0.2126R+0.7152G+0.0722B`, 대비 `(L1+0.05)/(L2+0.05)`, 소수 둘째 자리 반올림). P5에서 자동 도구로 재측정하면 같은 값이 나와야 한다.

---

## 0. 이 문서가 확정하는 것 / 확정하지 않는 것

| 구분 | 내용 |
|---|---|
| **확정한다** | 컬러·타이포·간격·radius·shadow·motion·z-index·breakpoint 토큰 전량 + **2차 레이아웃 토큰 7종(v1.1)**, 컴포넌트 **1차 30종 + 2차 승격 16종**의 구조·상태·대비(§2·§3) + 2차 예고 유지 13종의 원칙, 접근성 판정 기준(장식 이미지 목록·포커스·터치·400% 확대), 아이콘 세트 |
| **확정하지 않는다** | 화면별 배치·섹션 수치(1차 → `design/03_page-design.md` / **2차 39화면 → 다음 작업**), 실제 콘텐츠 문구(→ 화면정의서), 사실 정보(주소·전화·강사·요금 — 전부 `[TBD: 고객 확인 필요]`) |
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
| ~~캘린더 셀 배지 (`잔여 3`·`마감`)~~ | ~~11.5~12px / 700~~ | 2차 | **v1.1에서 이 예외를 쓰지 않기로 했다.** 셀 라벨은 **14px/700을 유지**하고, 폭이 모자라면 **셀 높이 72px + 라벨 2줄**로 흡수한다(§3.3 · REQ-N-006 ⑤ "14px을 줄여서 맞추지 않는다"에 더 충실하다). 예외 행은 이력으로 남긴다 |
| eyebrow(kicker) 대문자 라벨 | 12.5px / 700 | 공통 | 문장이 아닌 단일 라벨, 같은 정보가 본문에도 있을 것 |
| 데이터 표 헤더 셀 | 13px / 700 | 2차 | 관리자 영역 한정(REQ-N-A-006) |
| **상태 배지(CMP-043) 라벨 · 주 뷰 슬롯 블록(CMP-057) 안의 2줄 라벨** (v1.1 추가) | 12px / 700·400 | 2차 | **`≥1024px` 관리자 화면 한정**(REQ-N-A-006 데이터 밀도 예외). **공개·회원 화면의 배지는 14px/700을 쓴다.** 둘 다 문장이 아닌 단일 라벨(`확정`·`06:00–07:00`·`{유형} · {강사}`)이고, 같은 정보가 일 뷰·목록 모드·접근 이름에 **14px 이상으로 반드시 한 번 더** 제공된다 |

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

> **캘린더 좌우 패딩 — v1.1 정정 (C-1)**
> v1.0은 "캘린더 좌우 패딩 **12px 고정**(→ 셀 폭 46.28px)"으로 적었다. **v1.1에서 월간 캘린더(CMP-040)는 컨테이너 패딩을 그대로 따른다**(`<768px` **16px**). 360px 기준 셀 폭 = `(360 − 16×2 − 2×6) ÷ 7 = **45.14px**`.
> 바꾼 이유 2가지 — ① **REQ-N-006 ②-2의 실측 기준값이 45.1px**이고 수용 기준 문장도 "360px 실측 기준값 45.1px"로 쓰여 있다. 12px을 쓰면 P5에서 문서값과 구현값이 1.1px 갈려 불필요한 확인이 생긴다. ② 캘린더만 좌우 4px 안쪽으로 들어가면 **위아래 섹션과 좌우 정렬선이 어긋나** 화면이 흔들린다.
> **`--calendar-pad: 12px` 토큰은 값을 바꾸지 않는다**(TR-10 유지). 적용 대상만 **관리자 밀도 영역(CMP-057 주 뷰 · CMP-067 월 편성 월 뷰)의 그리드 좌우 패딩**으로 한정한다 — 그쪽은 열 폭 1px이 아쉬운 영역이라 12px이 유효하다.
> 계산식이 기준이고 45.14px은 파생값이다. 구간별 실측값은 §3.2 CMP-040 표에 있다.

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

## 3. 컴포넌트 — 2차 (v1.1 승격 명세)

### 3.0 이 절이 확정하는 것 / 지키는 원칙

v1.0 §3은 2차 27종의 **목록과 원칙**만 가진 "예고"였다. v1.1에서 그중 **16종을 실제 명세로 승격**하고, 1차 컴포넌트 2종(CMP-017·CMP-019)을 2차 요건까지 확장했다.

| 구분 | 내용 |
|---|---|
| **확정한다** | 승격 16종의 구조·수치·상태 8종·대비 측정값, 2차 레이아웃 토큰 7종, 2차 공통 상태(로딩·빈 상태·오류) 규칙, `<1024px` 표 카드 전환 규칙, 관리자 셸 3구간 |
| **확정하지 않는다** | 2차 39화면의 배치·섹션 수치(→ 다음 작업 `design/03_page-design-2nd.md`), 화면별 문구(→ 화면정의서·REQ-C-*), 레슨 유형 배지 색(§3.17 D-3 — PM 결정 대기) |
| **금지한다** | **새 컬러·새 radius·새 그림자 추가.** §1의 토큰만 조합한다. 필요해 보이면 티켓(`to-design`)으로 올리고 designer가 기존 토큰 조합으로 되돌려 준다 |

**원칙 5가지 (v1.0 §3의 "지금 고정하는 원칙"을 그대로 이행했다)**

1. **§1 토큰 값 변경 0건** — 컬러 32·타이포 10단·간격 15+3·radius 5·shadow 4·motion 7·z-index 6단·breakpoint 4구간 전부 v1.0과 같다(TR-10).
2. **색 외 구분 수단 필수** — 2차의 상태 표현은 전부 `텍스트 라벨 + (아이콘 또는 패턴)`을 함께 갖는다(REQ-N-006, §1.1 (2)).
3. **그림자는 z-index 40 이상에만** — 캘린더 셀·표 행·슬롯 카드·관리자 패널은 전부 `--shadow-none`.
4. **`--radius-lg`(12px)는 2차로 확장하지 않는다** — 2차 전 컴포넌트는 `--radius-md`(8px) 또는 `--radius-sm`(6px).
5. **키보드 경로가 없는 조작을 만들지 않는다** — 드래그·호버 전용 조작은 같은 화면 안에 키보드·클릭 대안을 병행한다.

**v1.0 대비 바뀐 값 — 정정 3건 (검토자 확인 대상)**

| # | 항목 | v1.0 | v1.1 | 근거 |
|---|---|---|---|---|
| **C-1** | 월간 캘린더 좌우 패딩 → 360px 셀 폭 | 12px → 46.28px | **컨테이너 패딩 16px → 45.14px** | REQ-N-006 ②-2 실측 기준값 45.1px과 일치시킴 + 좌우 정렬선 일치. **`--calendar-pad` 토큰 값(12px)은 그대로**이고 적용 대상만 관리자 밀도 그리드로 한정 (§1.3) |
| **C-2** | `--cell-min-h` 예정값 | 56px | **72px**(`<1024px`) / 88px / 96px | REQ-C-L-001의 셀 라벨 "잔여 9+"가 45.14px 폭에 **1줄로 들어가지 않는다**(실측 48.44px). D-4가 예고한 "셀 높이 증가 + 라벨 2줄" 흡수안을 그대로 적용 (§3.3) |
| **C-3** | `--week-col-min-w` 1024px 미달 우려 | "118px로 내리거나 패딩을 좁혀 해소" (developer R1 #11) | **하한 120/127px 유지 — 해소** | C-1로 `--calendar-pad`(12px)가 주 뷰 전용이 되면서 1024px 실측이 **118.86px → 124.57px**로 올라갔다. 하한을 내릴 필요가 없어졌다 (§3.14) |

> C-1·C-2는 **§1.6 CSS 변수 블록의 값이 아니라 "2차에서 쓸 예정값"에 대한 정정**이다. 1차 구현에 영향이 없다.

### 3.1 2차 컴포넌트 목록 (v1.0 예고 27종 → 승격 14 · 예고 유지 13 · 신규 ID 2 · 1차 확장 2)

| ID | 이름 | 대상 화면 | 상태 | 명세 위치 |
|---|---|---|---|---|
| CMP-040 | **Calendar Grid (월)** | SCR-110 · (관리자는 CMP-067) | **승격** | §3.3 |
| CMP-041 | **Slot Card · Slot List** | SCR-111 · SCR-112 · SCR-904 | **승격** | §3.4 |
| CMP-042 | **Data Table** (+ 카드 전환) | SCR-101·103·908·909·911·912·913·914·915 | **승격** | §3.5 |
| CMP-043 | **Status Badge (4군)** | 전 2차 화면 | **승격** | §3.6 |
| CMP-044 | **Select** | SCR-020·030·105·905·912·916 | **승격** | §3.7 |
| CMP-045 | **Radio / Segmented** | SCR-020·105·906 | **승격** | §3.7 |
| CMP-046 | **Date / Time Picker** | SCR-020·905·907 | **승격** | §3.7 |
| CMP-047 | **Tabs** | SCR-101·103·908·909 | **승격** | §3.8 |
| CMP-048 | **Modal / Dialog** | SCR-102·104·107·905·907·910·914 | **승격** | §3.9 |
| CMP-049 | **Dropdown Menu** | 헤더 회원 유틸 · 관리자 상단바 | **승격** | §3.10 |
| CMP-050 | **Pagination** | SCR-101·103·908·909·913·915 | **승격** | §3.11 |
| CMP-051 | Filter Chip | SCR-111 | 예고 유지 | §3.16 |
| CMP-052 | Breadcrumb | 관리자 상단바 | 예고 유지 | §3.16 |
| CMP-053 | **Admin Shell** | SCR-900~917 | **승격** | §3.13 |
| CMP-054 | Stepper | 예약 흐름 | 예고 유지 | §3.16 |
| CMP-055 | **Session Expiry Banner** | 회원·관리자 전 화면 | **승격** | §3.12 |
| CMP-056 | Popover | 주 뷰 슬롯 상세 | 예고 유지(토큰만 고정) | §3.16 |
| CMP-057 | **Schedule Week Grid (30분)** | SCR-903 | **승격** | §3.14 |
| CMP-058~066 | Progress / Tooltip / File Upload / Avatar Upload / Search Field / Accordion / Alert Banner / Split Button / Count Badge | 2차 각 화면 | 예고 유지 | §3.16 |
| **CMP-067** | **Schedule Month Composer (관리자 월 뷰)** | SCR-902 | **승격 · 신규 ID** | §3.14 |
| **CMP-068** | **Schedule Day Detail (일 뷰)** | SCR-904 | **승격 · 신규 ID** | §3.14 |
| CMP-017 | Checkbox → **다중 선택·부분 선택 확장** | SCR-908·913·916 | **1차 CMP 확장** | §3.7 |
| CMP-019 | Error Summary → **8~10항목 폼 확장** | SCR-020·030·105·905 | **1차 CMP 확장** | §3.7 |

> **신규 ID 2종을 만든 이유**: v1.0 §3.1은 관리자 월 편성을 `CMP-040`(회원 캘린더)과 `CMP-057`(주 뷰) 둘로만 잡았는데, 실제로는 **월(요약·개폐 현황) / 주(30분 편집) / 일(슬롯 상세)** 3단 뷰가 각각 다른 격자다(화면정의서 SCR-902·903·904). 회원 캘린더와 관리자 월 뷰는 **셀 안 정보가 다르고 조작이 다르므로** CMP-040을 억지로 재사용하지 않고 CMP-067로 분리했다. ID는 재사용하지 않는 규칙(CLAUDE.md §4)에 따라 058~066 다음 번호를 썼다.

### 3.2 2차 공통 상태 — §2.0 확장분

§2.0의 상태 8종(기본·hover·focus-visible·active·disabled·오류·로딩·빈 상태)은 2차에도 그대로 적용된다. **데이터를 불러오는 화면이 2차에서 처음 생기므로** 아래 4가지를 더한다.

| 상태 | 시각 규칙 | 접근성 |
|---|---|---|
| **로딩(스켈레톤)** | 실제 요소와 **같은 크기의 회색 블록**(`--color-neutral-bg` `#EEF1F5`, `--radius-md`)을 그 자리에 놓는다. 애니메이션은 `opacity 1 ↔ 0.55`, **1200ms `--ease-standard` 무한 반복**, 이동·확대 없음. **블록 크기가 실제 요소와 달라 로드 후 레이아웃이 움직이면 CLS 결함이다** | 컨테이너에 `aria-busy="true"` + 시각적으로 숨긴 텍스트 "불러오는 중". **`prefers-reduced-motion: reduce`에서는 깜빡임을 멈추고 고정 `#EEF1F5` 블록 + "불러오는 중" 텍스트를 보이게 둔다** |
| **빈 상태(empty)** | CMP-026을 그대로 쓴다. **"준비 중" 금지**(§5.0 M-5 · REQ-C-L-001). 표준 문형 = `"{대상}이 아직 없습니다. {다음 행동}"` / 미게시 월 = `"{n}월 일정은 공개되면 안내드립니다."` | `role="status"` |
| **불러오기 실패** | 표·캘린더·목록 자리에 **`error` 콜아웃(CMP-013) + "다시 시도" `secondary md` 버튼**. 화면 전체를 오류 화면으로 바꾸지 않는다(다른 영역은 살아 있다) | `role="alert"`, 포커스를 콜아웃으로 이동하지 않는다(사용자 조작 중 방해 금지) |
| **부분 실패·충돌** | 예: 마지막 한 자리를 놓친 경우 — **입력값을 유지한 채** `error` 콜아웃으로 사유를 적고 대체 행동(다른 슬롯 보기)을 버튼으로 준다. 페이지를 새로 고치게 만들지 않는다 | `role="alert"` + `aria-describedby`로 해당 조작 요소와 연결 |

> **로딩 표시를 쓰지 않아도 되는 기준**: 응답이 **300ms 안에 끝나는 조작에는 스켈레톤을 넣지 않는다**(깜빡임이 더 방해된다). 300ms를 넘길 가능성이 있는 곳만 넣는다 — 월 캘린더 조회, 표 페이지 이동, 주 뷰 로드, 제출.

### 3.3 CMP-040 Calendar Grid (월) ★

레슨 예약 캘린더(SCR-110). **하루 = 셀 1개**이고, 셀을 누르면 그 날짜의 슬롯 목록(SCR-111 · CMP-041)으로 간다.

**격자 수치 — 구간별 실측 (계산식이 기준, px는 파생값)**

| 구간 | 가용 폭 계산 | 셀 폭 | 셀 높이 `--cell-min-h` | 셀 라벨 |
|---|---|---|---|---|
| `<768px` (360px 측정) | `360 − 16×2 − 2×6 = 316` | **45.14px** | **72px** | **2줄** (날짜 / 상태) |
| `768~1023px` (768px) | `768 − 24×2 − 2×6 = 708` | **101.14px** | **72px** | 1줄 |
| `1024~1279px` (1024px) | `1024 − 32×2 − 2×6 = 948` | **135.43px** | **88px** | 1줄 |
| `≥1280px` (1200 컨테이너) | `1200 − 40×2 − 2×6 = 1108` | **158.29px** | **96px** | 1줄 |

- 열 간격 = `--space-c1` **2px** (REQ-N-006 ②-1 격자 예외 하한). 행 간격도 2px.
- 구현은 `grid-template-columns: repeat(7, 1fr)`로 **유동**이며 위 값은 측정 지점의 실측값이다. `≥1024px`에서 캘린더가 2단 레이아웃의 좌측 열에 들어가면 셀 폭은 줄어들지만 **어떤 경우에도 44px 미만이 되면 안 된다** — 44px 미만이 되는 컨테이너 폭에서는 2단을 풀고 1단으로 내린다.
- radius `--radius-md`(8px), 그림자 없음, 셀 좌우 패딩 **4px** / 상하 6px.

**셀 라벨 폭 검증 (Pretendard advance: 한글 1.0em · 숫자 0.6em · 공백 0.26em 기준)**

| 라벨 | 14px 실측 폭 | `<768px` 가용 폭(45.14 − 4×2 = **37.14px**) | 처리 |
|---|---|---|---|
| `잔여 9+` | **48.44px** | **초과** | **2줄 분할** — 1행 `잔여`(28px) / 2행 `9+`(16.8px) |
| `마감` | 28.00px | 들어감 | 1줄 |
| `휴무` | 28.00px | 들어감 | 1줄 |
| `당일` | 28.00px | 들어감 | 1줄 |
| 지난 날짜 | 라벨 없음 | — | 날짜 숫자만 |

> **셀 높이를 72px로 올린 이유가 이것이다(C-2).** REQ-C-L-001은 "14px 기준 최대 라벨 폭 약 40px"로 적고 있으나, Pretendard 실측은 **48.44px**이라 45.14px 셀에 1줄로 들어가지 않는다. **문구를 바꾸거나 글자를 14px 아래로 줄이지 않고**(REQ-N-006 ⑤ 금지), D-4가 예고한 대로 **셀을 높여 2줄로 나눴다.** 높이 계산: 상하 패딩 12 + 날짜 18 + 간격 2 + 라벨 2줄 35 = **67px → 72px 확정**.
> → 이 실측 차이는 `TKT-DSN-001`(to-planning)로 planner에 통보했다. **문구·규칙은 그대로 두고 REQ-C-L-001의 근거 수치만 정정**하면 된다.

**상태 4종 + 보조 2종**

| # | 상태 | 셀 배경 | 날짜 숫자 | 라벨 | 색 외 구분 수단 | 선택 |
|---|---|---|---|---|---|---|
| **1** | **예약 가능** | `#FFFFFF` + 1px `#DDE4EC` | `#16263A` 15px/700 | `잔여 {n}` `#1B6E3C` 14px/700 | **숫자 텍스트** + `check-circle-2` 12px | 가능 |
| **2** | **마감** | `#EEF1F5` + **45° 사선 해치**(`repeating-linear-gradient`, 선 1px `#C4CDD8`, 간격 6px) | `#4F5B6B` 15px/700 + **취소선** | `마감` `#4F5B6B` 14px/700 | 해치 패턴 + 취소선 + 텍스트 | 불가 |
| **3** | **휴무** | `#F7F9FC` | `#5A6B7D` 15px/400 | `휴무` `#5A6B7D` 14px/700 | 테두리 없음(다른 셀과 면이 다름) + 텍스트 | 불가 |
| **4** | **미게시** | `#F7F9FC` + 1px 점선 `#C4CDD8` | `#5A6B7D` 15px/400 | 라벨 없음 | **점선 테두리** + 접근 이름 "아직 공개되지 않았습니다" | 불가 |
| 보조 A | **오늘** | 상태 1~4 위에 겹침 — 셀 **2px `#0B4F9E` 테두리** | 그대로 | `당일`(당일 예약 불가 시) | 테두리 2px + 접근 이름 "오늘" | 상태에 따름 |
| 보조 B | **지난 날짜** | `#FFFFFF`, 내용 전체 `opacity: .55` | `#5A6B7D` | 없음 | 흐림 + `aria-disabled="true"` | 불가 |

> **미게시 "월 전체"는 셀 상태가 아니다.** 게시되지 않은 달은 격자를 그리지 않고 **빈 상태 블록(CMP-026)** 으로 대체한다(REQ-C-L-001 · REQ-F-L-003). 위 상태 4는 **게시된 달 안에서 편성이 없는 날**과 **관리자 월 뷰(CMP-067)** 에 쓴다. → 이것으로 `interviews/…booking-rules.md` §4의 "준비 중" 표기와 §5.0 M-5의 "준비 중 금지"가 충돌하지 않는다(designer 영향도 의견 확인 사항 #6 **해소**).

**상태(인터랙션) 8종**

| 상태 | 규칙 | 대비 |
|---|---|---|
| 기본 | 위 표 | 본문 `#16263A`/`#FFFFFF` **15.30:1** · 잔여 `#1B6E3C`/`#FFFFFF` **6.28:1** |
| hover | 선택 가능 셀만 배경 `#F0F5FB`. `@media (hover: hover)` | `#16263A`/`#F0F5FB` **13.96:1** · `#1B6E3C`/`#F0F5FB` **6.01:1** |
| focus-visible | `outline 3px #0B4F9E` + offset 2px. **간격이 2px뿐이라 링이 이웃 셀을 덮는다 → 포커스 셀에 `z-index: 1`을 준다** | 링 `#0B4F9E`/`#FFFFFF` **7.99:1** |
| active | 배경 `#E7EEF7`(= `#F0F5FB` 위 primary 6% 합성 대신 **`--color-primary-subtle` 유지 + 테두리 `#0B4F9E` 2px**로 대체 — 새 색을 만들지 않는다) | 테두리 **7.99:1** |
| **선택됨(현재 열린 날짜)** | 배경 `#0B4F9E`, 날짜·라벨 `#FFFFFF`, `aria-current="date"` | `#FFFFFF`/`#0B4F9E` **7.99:1** |
| disabled | 상태 2·3·4·보조 B. `aria-disabled="true"`, **포커스는 받는다**(건너뛰지 않는다) | `#4F5B6B`/`#EEF1F5` **6.09:1** · `#5A6B7D`/`#F7F9FC` **5.20:1** |
| 로딩 | 격자 자리에 **셀과 같은 크기의 스켈레톤 42칸**(§3.2). 월 이동 시 헤더(년월)는 즉시 바뀌고 격자만 스켈레톤 | — |
| 빈 상태 | 미게시 월 → CMP-026 (위 참조) | — |

**키보드 · 스크린리더**

| 항목 | 규칙 |
|---|---|
| 구조 | `role="grid"` + `role="row"` + `role="gridcell"`. 셀 내부 조작 요소는 **`<button>` 1개**(선택 불가 셀은 `aria-disabled="true"`인 `<button>`으로 두고 `disabled`를 쓰지 않는다 — `disabled`면 포커스를 못 받는다) |
| roving tabindex | 격자 전체에서 **`tabindex="0"`은 1개**(현재 셀), 나머지는 `-1`. ←→↑↓ 이동, `Home`/`End` = 주의 처음·끝, `PageUp`/`PageDown` = 이전·다음 달 |
| 접근 이름 | **축약 라벨을 읽지 않는다.** 전체 문장으로 준다 — `"10월 14일 수요일, 예약 가능, 잔여 12자리"` / `"10월 15일 목요일, 마감"` / `"10월 16일 금요일, 수업 없음"` / `"10월 17일 토요일, 아직 공개되지 않았습니다"` / `"10월 12일 월요일, 지난 날짜"`. **`{n}`은 상한 표기(9+)가 아니라 실제 수를 읽는다**(REQ-C-L-001) |
| 월 이동 | 이전·다음 달 버튼 44×44, `aria-label="이전 달"`. 월이 바뀌면 **격자 위 `role="status"` 영역에 "{YYYY}년 {M}월"** 을 갱신해 읽어 준다. 포커스는 이동 버튼에 남긴다 |
| 범례 | 격자 **아래**에 상시 노출(접기 금지). `잔여 n = 예약 가능한 자리 수(10 이상은 9+) · 마감 = 예약이 끝났습니다 · 휴무 = 수업 없음 · 당일 = 당일 예약은 받지 않습니다 · 흐린 날짜 = 지난 날짜`. 14px `#5A6B7D`(5.48:1) |
| 400% 확대 | **주 단위 리스트로 전환**한다 — §4.4 규칙 그대로. 데이터·접근 이름·목적지는 동일하고 표현만 바뀐다 |

### 3.4 CMP-041 Slot Card · Slot List ★

날짜별 슬롯 목록(SCR-111). 하루 최대 13슬롯이므로 **오전(~11:59) / 오후(12:00~) 2블록으로 나눈다**(`interviews/…booking-rules.md` §4).

**Slot Card**

| 항목 | 값 |
|---|---|
| 크기 | min-height **96px**(`<768px`) / **88px**(`≥768px`). 폭 100% |
| 구조 | `좌측 3px 상태 바` + `시간(h3 17~18px/700 tabular-nums)` + `유형 배지(CMP-043)` + `강사명(15px #16263A)` + `잔여(14px)` + 우측 `예약` 버튼(`primary sm`, 44px) |
| 패딩 | `16px`(좌 19px = 3px 바 + 16px) |
| radius | `--radius-md`(8px) · 테두리 1px `#DDE4EC` · **그림자 없음** |
| 카드 간격 | 12px |
| 좌측 바 | 예약 가능 `#1B6E3C` / 마감 `#4F5B6B` / 지난 `#C4CDD8`. **바는 장식이며 같은 정보가 배지·버튼 라벨에 텍스트로 있다** |

**상태 5종**

| 상태 | 시각 | 버튼 | 접근성 |
|---|---|---|---|
| 예약 가능 | 기본 | `primary sm` "예약" | — |
| 잔여 1~2 | 잔여 텍스트 `#8A5200` 700 + `alert-circle` 14px, 문구 `"잔여 2자리"` | `primary sm` "예약" | 색 외 수단 = 아이콘 + 숫자 |
| 마감 | 카드 배경 `#F7F9FC`, 시간·강사 `#5A6B7D`, 배지 `마감`(neutral) | 버튼 자리에 **텍스트 "마감"** `#4F5B6B` 15px/700 (버튼을 비활성으로 두지 않는다) | `aria-disabled` 불필요 — 조작 요소가 없다 |
| 지난 시간 | 카드 전체 `opacity: .55` | 버튼 없음 | 접근 이름에 "지난 수업" |
| 예약함(내 예약) | 좌측 바 `#0B4F9E`, 우측에 `success` 배지 `예약함` + `secondary sm` "예약 상세" | — | `aria-current` 쓰지 않음 |

**Slot List (컨테이너)**

| 항목 | 값 |
|---|---|
| 구조 | `<section>` 2개(오전·오후), 각각 `h2`(18px/700) + 개수 표기 `"오전 · 5개"` + `<ul>` |
| 빈 블록 | 오전 또는 오후에 슬롯이 없으면 **그 섹션을 렌더하지 않는다**(빈 상태 블록 2개가 겹치지 않게). 하루 전체가 비면 CMP-026 1개 |
| 마감 접기 | 마감 슬롯이 **4개 이상**이면 `<details>`로 접어 `"마감된 수업 {n}개 보기"`. **JS 없이 동작한다** |
| 필터 | 유형 필터는 CMP-051(예고 유지) — 이번 승격 범위 밖. **필터 없이도 목록이 성립**하도록 설계했다(오전·오후 분할 + 마감 접기로 최대 표시량이 9개 수준) |
| 정렬 | 시작 시각 오름차순 고정. 정렬 변경 UI를 두지 않는다 |
| 대비 | 시간 `#16263A`/`#FFFFFF` **15.30:1** · 강사 **15.30:1** · 잔여 경고 `#8A5200`/`#FFFFFF` **6.39:1** · 마감 `#4F5B6B`/`#F7F9FC` **6.54:1** |

### 3.5 CMP-042 Data Table (+ `<1024px` 카드 전환) ★

**표 (≥1024px)**

| 항목 | 값 |
|---|---|
| 행 높이 | `--table-row-h` **44px** (터치 하한과 동일) |
| 셀 패딩 | 세로 `--space-c2`(6px) / 가로 `--space-c3`(10px) |
| 헤더 | 13px/700 `#5A6B7D`, 배경 `#F7F9FC`, 하단 1px `#7E8FA3` (**관리자 한정 밀도 예외** REQ-N-A-006) |
| 본문 | 14px/400 `#16263A`. 숫자·시간·날짜는 `tabular-nums` |
| 행 구분 | 하단 1px `#DDE4EC`. **얼룩(zebra) 배경을 쓰지 않는다** — 상태 배지 틴트와 겹쳐 읽기 어려워진다 |
| sticky 헤더 | `position: sticky; top: var(--admin-topbar-h); z-index: var(--z-sticky-table)` (**공개·회원 화면에서는 `top: var(--header-h)`**). §1.4의 구현 조건 2가지(조상에 `transform`·`contain` 금지)를 그대로 적용 |
| radius | 표 컨테이너 `--radius-md`(8px) + `overflow: hidden`. 셀 radius 0 |
| 정렬 가능 헤더 | `<button>` 전체 셀, `aria-sort="ascending\|descending\|none"` + 화살표 아이콘 14px. **아이콘만으로 표시하지 않고 `aria-sort`를 함께 준다** |
| 열 폭 | 고유 식별자·상태·날짜 열은 고정 폭, 이름·메모 열이 남는 폭을 먹는다. **가로 스크롤을 만들지 않는다** — 열이 넘치면 열을 줄이거나 카드 전환 폭을 올린다 |

**카드 전환 (`<1024px`)** — 가로 스크롤 금지(REQ-N-A-001 · §4.4)

| 항목 | 값 |
|---|---|
| 구조 | 행 1개 = 카드 1개. `h3`(16px/700 — 그 행의 식별자: 예약번호·회원명 등) + 우상단 상태 배지 + 나머지 열은 **CMP-014 라벨–값 목록**(라벨 14px/700 `#5A6B7D` / 값 15px `#16263A`) |
| 카드 | 패딩 16px, radius `--radius-md`(8px), 테두리 1px `#DDE4EC`, 카드 간격 12px, **그림자 없음** |
| 숨기는 열 | **아무 열도 버리지 않는다.** 표에서 보이던 값은 카드에도 전부 있다(M-2 읽기 전용 화면의 판정 기준) |
| 조작 | 행 조작(상세·취소)은 카드 하단 `secondary sm` 버튼. **카드 전체를 링크로 만들지 않는다** |
| 관리자 M-2 | `<1024px` 관리자 화면 중 **읽기 허용 7화면**(SCR-900·901·908·909·910·913·917)만 이 카드 뷰를 그린다. 나머지는 SCR-917 안내 화면으로 보낸다 |

**상태 6종**

| 상태 | 규칙 |
|---|---|
| 기본 / hover | 행 hover 배경 `#F7F9FC` (`@media (hover: hover)`). 카드 뷰는 hover 없음 |
| focus-visible | 셀 안의 조작 요소에만 링. **행 자체를 포커스 대상으로 만들지 않는다** |
| 선택(체크박스 다중 선택) | 행 좌측 24px 체크박스(CMP-017), 선택 행 배경 `#F0F5FB` + 좌측 3px `#0B4F9E`. 헤더 체크박스는 **부분 선택(indeterminate)** 지원 |
| 로딩 | 헤더는 그대로 두고 **본문 행 높이 44px짜리 스켈레톤 10행** |
| 빈 상태 | 표 컨테이너 안에 CMP-026(높이 200px 이상). 헤더는 남긴다 |
| 오류 | 표 자리에 `error` 콜아웃 + "다시 시도" (§3.2) |

**대비**: 헤더 `#5A6B7D`/`#F7F9FC` **5.20:1** · 본문 `#16263A`/`#FFFFFF` **15.30:1** · hover 행 `#16263A`/`#F7F9FC` **14.51:1** · 선택 행 `#16263A`/`#F0F5FB` **13.96:1** · 구분선 `#DDE4EC` 1.28:1(장식) · 헤더 하단선 `#7E8FA3` **3.31:1**(UI 경계 기준 충족)

### 3.6 CMP-043 Status Badge — 4군 ★

**§1.1 (2)의 상태색만 쓴다. 새 색을 만들지 않는다.** 배지는 **테두리 없이** `배경 틴트 + 상태색 텍스트 + 12~16px 아이콘`으로 만든다(테두리를 넣으려면 색이 더 필요해진다).

| 항목 | 값 |
|---|---|
| 크기 | min-height **24px**, padding `2px 8px`, radius `--radius-sm`(6px) |
| 글자 | **14px/700** (공개·회원) / **12px/700** (관리자 데이터 표·주 뷰 블록 — §1.2 예외 표) |
| 아이콘 | 14px(공개) / 12px(관리자), `aria-hidden="true"`, `currentColor` |
| 인라인 | `display: inline-flex; gap: 4px; white-space: nowrap` |
| 조작 | **배지는 버튼이 아니다.** 누를 수 있게 만들지 않는다 |

**4군 · 16상태**

| 군 | 상태 | 배경 / 글자 | 아이콘 | 대비 |
|---|---|---|---|---|
| **예약** | 확정 | `#E7F4EC` / `#1B6E3C` | `check-circle-2` | **5.55:1** |
| | 취소 | `#EEF1F5` / `#4F5B6B` | `x-circle` | **6.09:1** |
| | 완료 | `#EEF1F5` / `#4F5B6B` | `check` | **6.09:1** |
| | 노쇼 | `#FBEAE8` / `#B3261E` | `alert-circle` | **5.61:1** |
| **상담** | 접수 | `#F0F5FB` / `#0B4F9E` | `inbox` | **7.30:1** |
| | 확정 | `#E7F4EC` / `#1B6E3C` | `check-circle-2` | **5.55:1** |
| | 완료 | `#EEF1F5` / `#4F5B6B` | `check` | **6.09:1** |
| | 취소 | `#EEF1F5` / `#4F5B6B` | `x-circle` | **6.09:1** |
| **스케줄(월)** | 작성 중 | `#FAF0E1` / `#8A5200` | `pencil` | **5.66:1** |
| | 게시됨 | `#E7F4EC` / `#1B6E3C` | `check-circle-2` | **5.55:1** |
| | 마감 | `#EEF1F5` / `#4F5B6B` | `lock` | **6.09:1** |
| | 미게시 | `#F7F9FC` / `#5A6B7D` | `circle-dashed` | **5.20:1** |
| **회원** | 정상 | `#E7F4EC` / `#1B6E3C` | `user-check` | **5.55:1** |
| | 경고 {n}건 | `#FAF0E1` / `#8A5200` | `alert-triangle` | **5.66:1** |
| | 휴면 | `#EEF1F5` / `#4F5B6B` | `moon` | **6.09:1** |
| | 탈퇴 | `#EEF1F5` / `#4F5B6B` | `user-x` | **6.09:1** |

> **"완료"와 "취소"가 같은 색(neutral)인 것은 의도다.** 둘 다 "더 이상 조작할 수 없는 종료 상태"이고, **구분은 라벨 텍스트와 아이콘(`check` vs `x-circle`)이 한다.** 색을 하나 더 만들어 구분하면 §1.1 (2)의 상태 팔레트가 깨진다(원칙 1·2).
> **슬롯 배지(v1.0 예고의 4번째 군)는 "예약" 군에 흡수했다** — 슬롯 상태(예약 가능·마감·지난)는 CMP-041 카드가 좌측 바 + 버튼 라벨로 이미 표현하며, 배지를 따로 두면 같은 화면에 상태 표시가 2벌이 된다. 대신 **회원 배지 군**을 세워 SCR-913·914를 덮었다(4군 수는 같다).

### 3.7 폼 요소 확장 — CMP-044·045·046 + CMP-017·019 확장 ★

공통: **입력 계열의 `font-size`는 어떤 구간에서도 16px**(`--fs-input`, iOS 자동 확대 방지). 높이 **52px**. radius `--radius-md`. 테두리 1px `#7E8FA3`(**3.31:1**). 상태(hover·focus·오류·disabled)는 **CMP-015와 완전히 동일**하게 맞춘다 — 폼 원자마다 다른 규칙을 만들지 않는다.

**CMP-044 Select**

| 항목 | 값 |
|---|---|
| 기본 | 네이티브 `<select>`. 높이 52px, padding `0 40px 0 14px`, 우측 `chevron-down` 16px `#5A6B7D`(절대 배치, `pointer-events: none`) |
| placeholder 옵션 | `<option value="" disabled selected>선택해 주세요</option>`. 글자 `#5A6B7D`(5.48:1) |
| 다중·검색형 | **커스텀 드롭다운은 CMP-049 규격을 따른다**(`--z-dropdown`, `--shadow-overlay`, 방향키·Esc). 옵션이 **10개 이하면 커스텀을 쓰지 않는다** |
| 상태 | 기본/hover(테두리 `#5A6B7D`)/focus-visible(테두리 2px `#0B4F9E` + 링 3px)/오류(테두리 2px `#B3261E` + `aria-invalid`)/disabled(`#EEF1F5`·`#5A6B7D` **4.83:1**)/로딩(옵션을 서버에서 받는 경우 — `disabled` + 첫 옵션 "불러오는 중…" + `aria-busy`)/빈 상태(옵션 0개 — `disabled` + "선택할 항목이 없습니다") |

**CMP-045 Radio / Segmented**

| 변형 | 규칙 |
|---|---|
| Radio(세로 목록) | 원 **24×24px** 테두리 1px `#7E8FA3`, 선택 시 테두리 **2px `#0B4F9E`** + 내부 점 10px `#0B4F9E`. **라벨 포함 행 전체가 클릭 영역, min-height 44px**, 행 간격 8px |
| Segmented(가로 2~4개) | 칩형. min-height 44px, padding `0 16px`, radius `--radius-md`, 테두리 1px `#7E8FA3`. 선택 시 **테두리 2px `#0B4F9E` + 배경 `#F0F5FB` + 글자 700 + `check` 아이콘 14px** (색·굵기·아이콘 3중) |
| 접근성 | `<fieldset>` + `<legend>`(시각적으로 숨겨도 됨), 네이티브 `<input type="radio">`. 방향키 이동은 브라우저 기본 동작을 그대로 쓴다 |
| 상태 | hover 배경 `#F7F9FC` / focus-visible 링 3px / 오류는 **fieldset 하단에 오류 문구 1개**(각 라디오에 붙이지 않는다) / disabled `#EEF1F5` |
| 대비 | 선택 테두리 `#0B4F9E`/`#FFFFFF` **7.99:1** · 라벨 `#16263A`/`#F0F5FB` **13.96:1** · 미선택 테두리 **3.31:1** |

**CMP-046 Date / Time Picker**

| 항목 | 값 |
|---|---|
| 기본 | **네이티브 `<input type="date">` · `<input type="time">`** 을 정본으로 쓴다. 높이 52px, `font-size: 16px`, `tabular-nums` |
| 제약 | 희망 일자는 `min="{내일}"`(당일 불가 — C-8). 레슨 예약도 같은 기준(B-5 ①). **`min`을 넣어도 서버 검증을 생략하지 않는다** |
| 키보드 직접 입력 | **필수.** 달력 팝업 없이 숫자만으로 입력·수정이 끝나야 한다. 라벨 아래 형식 안내 `"YYYY-MM-DD"` 14px `#5A6B7D` |
| 보조 캘린더 | 필요하면 CMP-040의 **축소 변형**(셀 44×44px, 라벨 없음, 날짜 숫자만)을 `--z-dropdown` 팝오버로 연다. 상태·접근 이름 규칙은 CMP-040과 동일 |
| 시간 선택 | 운영 시간(06:00~20:00) 밖 값은 **입력은 되지만 제출 시 오류**로 처리하고, 라벨 아래에 운영 시간을 안내한다. 시간을 30분 단위로 강제하지 않는다(상담은 캘린더와 무관 — C-2) |
| 상태 | CMP-015와 동일 6종 + **오류 문구 예시** `"내일 이후 날짜를 선택해 주세요."` |

**CMP-017 Checkbox — 확장**

| 확장 항목 | 규칙 |
|---|---|
| 다중 선택(표 행) | 박스 24×24, **클릭 영역 44×44**(패딩으로 확보). 헤더 체크박스는 `indeterminate` 지원 + `aria-label="전체 선택"` |
| 부분 선택 시각 | 체크 아이콘 대신 **가로 바 12×2px `#FFFFFF`** on `#0B4F9E` |
| 선택 개수 표시 | 표 위에 `role="status"`로 `"{n}건 선택됨"` (색만으로 알리지 않는다) |

**CMP-019 Error Summary — 8~10항목 폼 확장**

| 확장 항목 | 규칙 |
|---|---|
| 위치 | 폼 **맨 위**. 제출 실패 시 `tabindex="-1"`로 포커스 이동(1차와 동일) |
| 항목 수 | 오류가 **6개를 넘으면** 상위 6개만 링크로 나열하고 `"외 {n}건"`을 텍스트로 덧붙인다(목록이 화면을 덮지 않게) |
| 링크 동작 | 누르면 해당 필드로 **포커스 이동 + `scroll-margin-top: var(--anchor-offset)`** 적용 |
| 서버 오류 | 필드에 매핑되지 않는 오류(중복 신청 등)는 **링크가 아닌 문장**으로 목록 맨 위에 둔다 |
| 문구 | 개인정보 노출 금지 문구를 그대로 쓴다 — `"이 연락처로 접수된 신청이 있습니다. 예약 확인 또는 전화로 문의주세요."`(C-6 확정 문구, 일시·유형 미표시) |

### 3.8 CMP-047 Tabs

| 항목 | 값 |
|---|---|
| 구조 | `role="tablist"` / `role="tab"` / `role="tabpanel"`. 탭 수 2~4개 |
| 크기 | min-height **44px**, padding `0 16px`, 탭 간격 0(경계선으로 구분), 하단 1px `#DDE4EC` 전폭 |
| 기본 | 16px/400 `#5A6B7D`(5.48:1) |
| 선택 | 16px/**700** `#0B4F9E` + **하단 2px `#0B4F9E` 인셋 바** + `aria-selected="true"` (색·굵기·바 3중 — CMP-004와 같은 방식) |
| hover / focus-visible | 배경 `#F7F9FC` / 링 3px offset -2px(하단 바에 겹치지 않게) |
| 키보드 | ←→ 이동(`automatic activation`), `Home`/`End`. 탭 목록의 `tabindex`는 roving |
| 개수 표시 | 라벨 뒤 `(12)` 형태. **읽히도록 접근 이름에 "12건"으로 넣는다** |
| 빈 패널 | CMP-026. 탭 자체는 남긴다 |
| 모바일 | `<768px`에서 탭이 넘치면 **가로 스크롤이 아니라 2줄 줄바꿈**(`flex-wrap: wrap`) |

### 3.9 CMP-048 Modal / Dialog

| 항목 | `≥768px` | `<768px` |
|---|---|---|
| 형태 | 화면 중앙 다이얼로그 | **하단 시트** (위에서 아래로 고정) |
| 폭·높이 | 확인형 max-width **480px** / 폼형 **640px**, max-height `calc(100vh - 96px)` | 폭 100%, max-height **90vh**, 본문만 스크롤 |
| radius | `--radius-md` **8px** (전 모서리) | `--radius-md` **8px** (상단 2개만) |
| 배경·그림자 | `#FFFFFF` + `--shadow-modal`, backdrop `rgba(10,37,64,.48)` z-index 49 | 동일 |
| 패딩 | 24px | 20px |
| 구조 | 제목 `h2` 20~22px/700 → 본문 15~16px → 버튼 행(우측 정렬, `secondary md` + `primary md`, 간격 12px) | 버튼 **세로 스택 + 전폭**(주 버튼이 위) |
| z-index | `--z-modal`(50) | 동일 |

**동작·접근성**

- `<dialog>` 요소를 정본으로 쓰고 `showModal()`로 연다(브라우저가 **포커스 트랩·backdrop·Esc 닫기**를 제공한다).
- 열릴 때 **첫 조작 요소가 아니라 제목으로 포커스**(`tabindex="-1"`)를 보낸다 — 파괴적 동작(취소·삭제) 모달에서 실수로 확인 버튼을 누르는 것을 막는다.
- 닫히면 **열기 전 트리거 요소로 포커스 복귀**. 배경 스크롤 잠금.
- `aria-labelledby`(제목) + `aria-describedby`(본문).
- **파괴적 동작 확인 모달**: 주 버튼 라벨은 `"예"`가 아니라 **동작 이름**(`"예약 취소하기"`). `primary` 색을 그대로 쓰고 빨간 버튼을 만들지 않는다(새 색 금지 — 위험은 **문구와 본문의 `warn` 콜아웃**이 전달한다).
- 모션: `opacity` + `translateY(var(--motion-distance))`, `--motion-slow`(220ms) `--ease-out`. reduce에서 이동 0.
- 상태: 로딩(확인 버튼이 CMP-001 로딩 상태 — 폭 고정·라벨 교체) / 오류(모달 안 상단에 `error` 콜아웃, 모달을 닫지 않는다).

### 3.10 CMP-049 Dropdown Menu

| 항목 | 값 |
|---|---|
| 트리거 | 44×44 이상. `aria-haspopup="menu"` + `aria-expanded` |
| 패널 | min-width **200px**, max-height 320px(넘치면 세로 스크롤), 배경 `#FFFFFF`, 테두리 1px `#DDE4EC`, radius `--radius-md`, `--shadow-overlay`, `z-index: var(--z-dropdown)`(40) |
| 항목 | min-height **44px**, padding `0 14px`, 15px/400 `#16263A`. hover·focus 배경 `#F0F5FB` |
| 구분 | 그룹 사이 1px `#DDE4EC` + 그룹 라벨 13px/700 `#5A6B7D` |
| 위치 | 트리거 아래 4px. **뷰포트 밖으로 나가면 위로 뒤집는다**(오른쪽 정렬 우선) |
| 키보드 | ↑↓ 이동, `Home`/`End`, 문자 타이핑 점프, `Esc` 닫고 트리거로 복귀, `Tab`으로 나가면 닫힘 |
| 모바일 | `<768px`에서는 드롭다운 대신 **CMP-048 하단 시트**로 연다(44px 항목이 화면 밖으로 나가지 않게) |
| 대비 | 항목 `#16263A`/`#FFFFFF` **15.30:1** · hover `#16263A`/`#F0F5FB` **13.96:1** · 그룹 라벨 `#5A6B7D`/`#FFFFFF` **5.48:1** |

### 3.11 CMP-050 Pagination

| 항목 | 값 |
|---|---|
| 항목 | **44×44px**, 간격 `--space-2`(8px), radius `--radius-md`, 15px/400 `#16263A` |
| 현재 페이지 | 배경 `#0B4F9E` + 글자 `#FFFFFF`(**7.99:1**) + 700 + `aria-current="page"` |
| hover | 배경 `#F0F5FB` |
| 이전·다음 | 아이콘 버튼 44×44, `aria-label="이전 페이지"`. 첫·끝 페이지에서는 **`disabled`**(숨기지 않는다 — 위치가 흔들린다) |
| 생략 | 페이지가 7개를 넘으면 `1 … 4 5 6 … 20` 형태. `…`은 `aria-hidden="true"` |
| 구조 | `<nav aria-label="페이지 이동">` + `<ul>`. 각 항목은 **링크**(URL로 페이지 상태가 남는다) |
| 모바일 | `<768px`에서는 번호를 5개로 줄이고 `flex-wrap: wrap` 허용 |
| 보조 표기 | 목록 위에 `"전체 128건 중 21–40"` 14px `#5A6B7D`(5.48:1) — `role="status"` |

### 3.12 CMP-055 Session Expiry Banner

| 항목 | 값 |
|---|---|
| 형태 | **문서 흐름 안의 배너**(고정 오버레이 아님). 화면 최상단, 헤더/관리자 상단바 **바로 아래** |
| 스타일 | `warn` 콜아웃(CMP-013) — 좌측 3px `#8A5200`, 배경 `#FAF0E1`, 글자 `#8A5200`(**5.66:1**), `alert-triangle` 16px |
| 높이 | min-height 56px, 패딩 `12px 16px` |
| 구성 | 문구 `"로그인이 {m}분 {s}초 뒤 만료됩니다."` + `primary sm` "로그인 유지"(44px) + `icon` 닫기 44×44 |
| 노출 시점 | 만료 **2분 전**. 배너가 뜨면 사라지지 않는다(닫기를 눌러야 닫힌다) |
| 카운트다운 | `aria-live`를 **쓰지 않는다**(1초마다 읽히면 방해). 대신 `role="status"`인 별도 영역에서 **60초·30초 시점에만** 갱신해 읽어 준다 |
| 만료 후 | 배너를 `error` 변형으로 바꾸고 문구를 `"로그인이 만료되었습니다. 다시 로그인해 주세요."` + `primary sm` "로그인" |
| 레이아웃 영향 | 배너가 나타나면 본문이 **아래로 밀린다**. 사용자 조작 없이 발생하므로 **sticky 헤더 아래에서만** 삽입하고, 배너 등장 애니메이션은 `opacity`만 쓴다(높이 애니메이션 금지 — CLS) |

### 3.13 CMP-053 Admin Shell ★

관리자 전용 셸. **공개 헤더·GNB·하단 고정 바를 쓰지 않는다**(G-13).

| 구간 | 사이드바 | 상단바 | 본문 |
|---|---|---|---|
| `≥1280px` | `--admin-sidebar-w` **240px** 고정 펼침 | `--admin-topbar-h` **56px** | 좌측 240px 옆, 좌우 패딩 40px |
| `1024~1279px` | **아이콘 모드 64px** (`--admin-sidebar-w-compact`) | 56px | 좌측 64px 옆, 좌우 패딩 32px |
| `<1024px` | **없음** — 상단바의 햄버거로 여는 **드로어**(폭 280px, backdrop) | 56px | 전폭, 좌우 패딩 16px. **읽기 전용 7화면만 렌더**(M-2) |

**사이드바**

| 항목 | 값 |
|---|---|
| 배경 | `--color-navy` `#0A2540`, `data-surface="dark"` |
| 항목 | min-height **44px**, padding `0 16px`, 15px/400 `#FFFFFF`(**15.53:1**), 아이콘 20px + 간격 12px |
| 그룹 라벨 | 13px/700 `#B9C9DC`(**9.21:1**), 상단 여백 20px |
| hover | 배경 `#16263A` (navy 위 면 변화). `@media (hover: hover)` |
| **현재 항목** | 배경 `#0B4F9E` + 글자 `#FFFFFF`(**7.99:1**) + 700 + **좌측 3px `#FFFFFF` 바** + `aria-current="page"`<br>⚠ `#0B4F9E`와 `#0A2540`의 면 대비는 **1.94:1**로 3:1에 못 미친다 → **좌측 흰 바(15.53:1)와 굵기·`aria-current`가 실제 구분 수단**이다. 배경색만으로 현재 항목을 표시하지 않는다 |
| focus-visible | **흰색 링 3px**(`--focus-ring-color-on-dark`), offset 2px |
| 아이콘 모드(64px) | 아이콘 24px 중앙, 클릭 영역 **64×44px**. 라벨은 `aria-label`로 제공하고 hover·focus 시 우측에 툴팁(`--z-dropdown`). **툴팁만으로 라벨을 전달하므로 `aria-label`은 필수** |
| 하단 | 로그아웃 + 버전 표기 13px `#B9C9DC` |

**상단바 (56px)**

| 항목 | 값 |
|---|---|
| 배경 | `#FFFFFF` + 하단 1px `#DDE4EC`, `position: sticky; top: 0; z-index: var(--z-header)`(20) |
| 좌측 | (`<1024px`) 햄버거 44×44 / 현재 화면 제목 `h1` 17~18px/700 또는 브레드크럼(CMP-052) |
| 우측 | 알림 아이콘 버튼 44×44(개수 배지) + 계정 드롭다운(CMP-049) |
| sticky 표 헤더 | `top: var(--admin-topbar-h)` (§3.5) |

**기타**

- 본문 배경 `--color-surface-alt` `#F7F9FC`, 카드·표 컨테이너는 `#FFFFFF` — **면 구분을 배경으로 하고 그림자를 쓰지 않는다**.
- 관리자 푸터는 **개인정보 처리방침 링크 + 버전 표기만**(CMP-006 2차 규칙).
- `<1024px` 미지원 화면 접근 시 **SCR-917 안내 화면**으로 보낸다(REQ-N-A-001 · REQ-C-A-001). 안내 화면은 CMP-026 형식 + "데스크톱에서 이용해 주세요" + 지원 화면 목록 링크.
- **Skip Link(CMP-008)는 관리자에도 적용**한다. 대상은 `<main id="main" tabindex="-1">`.

### 3.14 월 편성 3단 뷰 — CMP-067(월) · CMP-057(주) · CMP-068(일) ★

`interviews/…booking-rules.md` §3의 편성 흐름을 화면 3개로 나눈 것이다. **`≥1024px` 전용**(REQ-N-A-001). 겹치는 슬롯은 존재하지 않는다(B-15 — 수업 공간 1개)는 전제를 시각 구조에 그대로 반영해 **블록 겹침 표현을 만들지 않는다.**

**CMP-067 Schedule Month Composer (월 뷰 · SCR-902)**

| 항목 | 값 |
|---|---|
| 격자 | CMP-040과 같은 7열 구조, **좌우 패딩 `--calendar-pad` 12px**(밀도 우선 — §1.3 C-1) |
| 셀 폭 | `1024~1279px`: `(1024 − 64 − 12×2 − 2×6) ÷ 7 = **132.00px**` / `≥1280px`: `(1280 − 240 − 12×2 − 2×6) ÷ 7 = **143.43px**` |
| 셀 높이 | **96px** |
| 셀 내용 | 날짜 숫자 15px/700 → `"슬롯 {n}"` 13px `#16263A` → **미배정 {n}** 배지(`warn`, 0이면 미표시) → 상태 점이 아니라 **텍스트** |
| 셀 상태 | CMP-040 상태 4종 재사용(예약 가능 = 편성됨 / 마감 / 휴무 / 미게시). **월 전체 상태(작성 중·게시됨·마감)는 헤더의 CMP-043 스케줄 배지**가 표시한다 |
| 조작 | 셀 클릭 → 일 뷰(CMP-068). 셀 위 `secondary sm` "주 뷰" 버튼은 두지 않고 **상단 뷰 전환(CMP-045 Segmented: 월·주·일)** 으로 통일 |
| 게시 전 검사 | 미배정 슬롯이 1건이라도 있으면 상단에 `warn` 콜아웃 + `"미배정 {n}건 — 게시할 수 없습니다"` + 해당 날짜로 가는 링크 목록. **게시 버튼은 `disabled`가 아니라 그대로 두고, 누르면 검사 결과 모달(CMP-048)** 을 연다(왜 못 누르는지 알 수 있게) |

**CMP-057 Schedule Week Grid (주 뷰 · 30분 · SCR-903)**

| 항목 | 값 |
|---|---|
| 시간축 | `--time-axis-w` **64px** 고정, `position: sticky; left: 0`, 배경 `#FFFFFF`, 우측 1px `#DDE4EC` |
| 행 | `--week-row-h` **28px** = 30분. 06:00~20:00 = **28행 = 784px** |
| 열 | 7일. 실측 폭 — `1024~1279px`: `(1024 − 64 − 12×2 − 64) ÷ 7 = **124.57px**`(하한 120px **충족**) / `≥1280px`: `(1280 − 240 − 12×2 − 64) ÷ 7 = **136.00px**`(하한 127px 충족) |
| 요일 헤더 | 높이 44px, `position: sticky; top: var(--admin-topbar-h)`, `z-index: var(--z-sticky-table)`. **좌상단 모서리 칸은 `z-index: calc(var(--z-sticky-table) + 1)`** (두 sticky가 만나는 칸) |
| 격자선 | 정시 1px `#DDE4EC` / 30분 1px `#EEF1F5`(더 옅게). 11:00~13:00 기본 닫힘 구간은 배경 `#F7F9FC`(**차단이 아니라 기본값** — B-1) |
| 슬롯 블록 | 60분 = `calc(var(--week-row-h) * 2)` **56px** / 90분 = **84px**. 좌우 여백 2px, radius `--radius-md`, 배경 `#F0F5FB`, 좌측 3px `#0B4F9E`, 글자 `#16263A` |
| 블록 내용 | 1행 `"06:00–07:00"` 12px/700 tabular / 2행 `"{유형} · {강사}"` 12px/400. **2줄까지만** — 정원·예약 수는 넣지 않는다(56px 안에 3줄은 들어가지 않는다) |
| 정원·예약 수 | **일 뷰(CMP-068)와 슬롯 상세 모달**에서 본다. (v1.0 §3 예고의 "팝오버"는 CMP-056으로 남아 있고, **팝오버 없이도 정보에 도달**한다) |
| 미배정 블록 | 배경 `#FAF0E1`, 좌측 3px `#8A5200`, 2행에 `"강사 미배정"` 12px/700 `#8A5200`(**5.66:1**) + `alert-triangle` 12px |
| 조작 | **드래그를 도입하지 않는다.** 빈 칸 클릭 → "슬롯 추가"(SCR-905), 블록 클릭 → "슬롯 수정". 키보드는 격자 roving tabindex(←→ 요일, ↑↓ 30분, `Enter` 열기) |
| 세로 스크롤 | 784px + 헤더 44px이 뷰포트를 넘으므로 **그리드 컨테이너가 세로 스크롤**한다. 시간축 sticky로 항상 보인다 |
| 대비 | 블록 본문 `#16263A`/`#F0F5FB` **13.96:1** · 시간축 라벨 `#5A6B7D`/`#FFFFFF` **5.48:1** · 정시 격자선 `#DDE4EC` 1.28:1(장식 — 구조는 시간축 텍스트가 전달한다) |

**CMP-068 Schedule Day Detail (일 뷰 · SCR-904)**

| 항목 | 값 |
|---|---|
| 구조 | 좌측 시간축 64px + 우측 **1열 전폭** 타임라인. 행 높이는 주 뷰와 동일(28px/30분) |
| 블록 | 폭이 넓으므로 **3줄** — `시간` / `{유형} · {강사}` / `예약 {n}/{정원}` 13px |
| 목록 모드 | 타임라인 위에 **"목록으로 보기" 토글**(CMP-045 Segmented). 목록 모드는 CMP-042 표(시간·유형·강사·정원·예약·상태·조작)를 쓴다. **격자를 읽기 어려운 사용자를 위한 동등 경로이며 선택이 아니라 필수다** |
| 조작 | 슬롯 클릭 → 수정 모달. 예약자 있는 슬롯 닫기는 **확인 모달 + 사유 입력 필수**(B-8 경고 기록) |

### 3.15 2차 토큰 — 확정값과 CSS 추가분

**v1.0 §3.2에서 "이름만 예약"했던 토큰 5종 → 확정**

| 토큰 | v1.0 예정값 | **v1.1 확정값** | 변경 |
|---|---|---|---|
| `--admin-sidebar-w` | 240px | **240px** | 없음 |
| `--admin-sidebar-w-compact` | 64px | **64px** | 없음 |
| `--admin-topbar-h` | 56px | **56px** | 없음 |
| `--table-row-h` | 44px | **44px** | 없음 |
| `--cell-min-h` | 56px | **72px** (≥1024px 88px / ≥1280px 96px) | **변경(C-2)** — 라벨 2줄 흡수 |
| `--week-col-min-w` | 127px / 120px | **127px / 120px** | 없음 — **C-3으로 우려 해소** |

**v1.1 신규 토큰 2종** (레이아웃 파생값이라 값을 화면 CSS에 흩어 놓으면 3개 뷰가 어긋난다)

| 토큰 | 값 | 이유 |
|---|---|---|
| `--week-row-h` | **28px** | 30분 1행. 슬롯 블록 높이가 이 값의 배수(`60분 = ×2`, `90분 = ×3`)라 단일 출처가 필요하다 |
| `--time-axis-w` | **64px** | 주 뷰·일 뷰가 같은 시간축을 쓴다. 열 폭 계산식에도 들어간다 |

> **신규 컬러 0건 · 신규 radius 0건 · 신규 shadow 0건 · 신규 motion 0건 · 신규 breakpoint 0건.** 추가된 것은 위 **레이아웃 치수 2종**과 §3.16의 예약 토큰뿐이다. **§1.6 CSS 변수 블록의 기존 값은 하나도 바뀌지 않았다** (TR-10 "변경된 토큰 0건" 충족).

```css
/* ============================================================
   강남 요가패스 2차 토큰 v1.1 (2026-09-12)
   §1.6 :root 블록 뒤에 이어 붙인다. 기존 값을 덮어쓰지 않는다.
   ============================================================ */
:root {
  /* ---- admin shell (CMP-053) ---- */
  --admin-sidebar-w:         240px;
  --admin-sidebar-w-compact:  64px;
  --admin-topbar-h:           56px;

  /* ---- data table (CMP-042) ---- */
  --table-row-h: 44px;

  /* ---- calendar (CMP-040 / CMP-067) ---- */
  --cell-min-h: 72px;          /* <1024px — 라벨 2줄 수용 */

  /* ---- schedule grid (CMP-057 / CMP-068) ---- */
  --week-row-h:      28px;     /* 30분 1행 */
  --time-axis-w:     64px;
  --week-col-min-w: 120px;     /* 1024~1279px 하한 */
  --slot-block-60:  calc(var(--week-row-h) * 2);  /* 56px */
  --slot-block-90:  calc(var(--week-row-h) * 3);  /* 84px */
  /* --calendar-pad(12px)는 §1.6에 이미 있다. v1.1부터 관리자 밀도 그리드
     (CMP-057 · CMP-067) 전용이며 회원 월 캘린더는 --container-pad를 따른다. */
}

@media (min-width: 1024px) {
  :root { --cell-min-h: 88px; }
}

@media (min-width: 1280px) {
  :root {
    --cell-min-h: 96px;
    --week-col-min-w: 127px;
  }
}
```

**개발 주의 2가지 (2차)**

> ① **sticky 2축이 만나는 칸**(주 뷰 좌상단)은 `z-index`를 `calc(var(--z-sticky-table) + 1)`로 올린다. 올리지 않으면 요일 헤더와 시간축이 서로를 덮는다.
> ② **관리자 표의 sticky 헤더 `top`은 `var(--admin-topbar-h)`** 다. 공개·회원 화면의 `var(--header-h)`를 그대로 복사하면 56px ≠ 64/68/72px이라 헤더가 겹치거나 떠 보인다.

### 3.16 예고 유지 컴포넌트 (13종 — 다음 작업에서 승격)

2차 페이지 디자인(39화면)과 함께 명세한다. **아래 원칙은 지금 고정되어 있고 바뀌지 않는다.**

| ID | 이름 | 고정된 원칙 |
|---|---|---|
| CMP-051 | Filter Chip | CMP-023(Anchor Chip) 확장 — pill, min-height 44px, 선택 시 배경 `#F0F5FB` + 테두리 `#0B4F9E` + `aria-pressed="true"` + 해제 `x` 16px |
| CMP-052 | Breadcrumb | 마지막 항목 `aria-current="page"`, 구분자 `/` `aria-hidden`, 14px `#5A6B7D` |
| CMP-054 | Stepper | 현재 단계 `aria-current="step"` + 번호 + 라벨(색만 금지). 단계 3개 이하 |
| CMP-056 | Popover | **CMP-049의 패널 토큰을 그대로 쓴다**(`--z-dropdown`·`--shadow-overlay`·radius 8px). 포커스 트랩 없음, Esc 닫기 있음 |
| CMP-058 | Progress | 높이 6px, radius pill, 트랙 `#EEF1F5` / 바 `#0B4F9E`. `role="progressbar"` + 숫자 텍스트 병기 |
| CMP-059 | Tooltip | **정보 전달 유일 수단으로 쓰지 않는다.** 아이콘 모드 사이드바 라벨은 `aria-label`이 정본 |
| CMP-060 | File Upload | 드래그 영역 + **버튼 경로 필수**. 용량·형식 제한을 라벨에 텍스트로 |
| CMP-061 | Avatar Upload | 1:1 크롭, `object-position: 50% 28%`(§6.2). 인물 스톡 대체 금지 |
| CMP-062 | Search Field | 높이 52px, `type="search"`, 지우기 버튼 44×44, 결과 개수 `role="status"` |
| CMP-063 | Accordion | `<details>/<summary>` 정본(JS 없이 동작 · CMP-005와 같은 규칙) |
| CMP-064 | Alert Banner | CMP-013 콜아웃 + 닫기 버튼. `role="status"`/`"alert"` |
| CMP-065 | Split Button | 주 동작 + 드롭다운(CMP-049). 두 영역 각각 44px |
| CMP-066 | Count Badge | radius pill, 12px/700, 배경 `#B3261E` + `#FFFFFF`(**6.54:1** 반전 조합은 4.5:1 이상). **숫자만으로 의미를 전달하지 않고 접근 이름에 "읽지 않은 알림 3건"** |

### 3.17 레슨 유형 배지 색 — D-3 (v1.0에서 이어짐 · PM 결정 대기)

레슨 유형은 2차에서 **관리자 관리 대상**(REQ-F-A-025 · B-16-a)이라 designer가 고정 팔레트를 줄 수 없다. 선택지는 v1.0과 같다.

- **ⓐ 중립 1색 + 텍스트 구분** (권고) — 배지 색을 쓰지 않고 유형명 텍스트로만 구분. 색 관리 비용 0, 접근성 위험 0.
- **ⓑ 검증된 6~8색 팔레트를 designer가 제공하고 관리자가 그중 선택** — 시각 구분은 좋아지지만 팔레트 밖의 색이 들어올 경로를 막아야 한다.

**v1.1에서 더한 것 — 무회신이어도 막히지 않게 기본값을 실행했다.**

| 항목 | v1.1 처리 |
|---|---|
| 현재 명세 | **ⓐ로 그려 두었다.** 유형 배지는 `#EEF1F5` / `#4F5B6B`(**6.09:1**) 중립 1색 + **유형명 텍스트**다(CMP-041 슬롯 카드 · CMP-057 주 뷰 블록). |
| ⓑ 채택 시 영향 | **CMP-043 배지 정의 1곳과 관리자 유형 관리 화면(SCR-912)의 색 선택 UI만** 추가된다. 슬롯 카드·주 뷰 블록·표는 배지의 배경·글자 색만 바뀌므로 **레이아웃 재작업 0건**이다. |
| ⓑ 채택 시 조건 | designer가 **흰 배경 4.5:1 이상 + 서로 구별되는 6색**을 제공하고, 관리자 화면은 **그 6색 중에서만** 고를 수 있게 한다(자유 색 입력 금지). 색과 별개로 **유형명 텍스트는 항상 함께 노출**한다. |

→ **2차 페이지 디자인 착수 전 PM 결정 항목**이다. 무회신이면 ⓐ로 확정한다.

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

**2차 추가 조합 (v1.1 · #28~#37)** — 새 색을 쓰지 않았으므로 **기존 색끼리의 새 조합**뿐이다.

| # | 전경 | 배경 | 대비 | 기준 | 판정 | 쓰이는 곳 |
|---|---|---|---|---|---|---|
| 28 | `#16263A` 본문 | `#F7F9FC` surface-alt | **14.51:1** | 4.5:1 | 통과 | 표 행 hover, 관리자 본문 배경 |
| 29 | `#5A6B7D` 표 헤더·보조 | `#F7F9FC` | **5.20:1** | 4.5:1 | 통과 | CMP-042 헤더, 휴무·미게시 셀 |
| 30 | `#0B4F9E` 링크 | `#F7F9FC` | **7.58:1** | 4.5:1 | 통과 | 관리자 본문 위 링크 |
| 31 | `#4F5B6B` 마감 | `#F7F9FC` | **6.54:1** | 4.5:1 | 통과 | CMP-041 마감 카드 |
| 32 | `#16263A` 본문 | `#EEF1F5` neutral-bg | **13.50:1** | 4.5:1 | 통과 | 스켈레톤 위 텍스트, 마감 셀 날짜 |
| 33 | `#0B4F9E` | `#EEF1F5` | **7.05:1** | 4.5:1 | 통과 | 비활성 면 위 링크 |
| 34 | `#16263A` | `#E7F4EC` success-bg | **13.52:1** | 4.5:1 | 통과 | 성공 배지 옆 본문 |
| 35 | `#16263A` | `#FAF0E1` warning-bg | **13.55:1** | 4.5:1 | 통과 | 미배정 블록 본문 |
| 36 | `#16263A` | `#FBEAE8` error-bg | **13.12:1** | 4.5:1 | 통과 | 오류 콜아웃 본문 |
| 37 | `#1B6E3C` 잔여 | `#F0F5FB` 틴트 | **6.01:1** | 4.5:1 | 통과 | 캘린더 셀 hover 상태의 잔여 라벨 |
| 38 | `#0B4F9E` 사이드바 현재 항목 면 | `#0A2540` 사이드바 | **1.94:1** | 3:1 | **미달 — 면 대비로 쓰지 않는다** | CMP-053. 구분은 **좌측 3px `#FFFFFF` 바(15.53:1) + 700 + `aria-current`** 가 한다 |

> **대비 미달 색은 팔레트에 하나도 없다.** 밝은 파랑(`#3B82F6`·`#4DA3FF` 계열, 흰 배경 2.6~3.1:1)은 이 시스템에 존재하지 않으며 **추가를 금지**한다.

### 4.2 터치 타깃

| 대상 | 규칙 |
|---|---|
| 모든 버튼·링크 버튼·입력·체크박스 행 | **44×44px 이상** |
| 인접 조작 요소 간격 | **8px 이상** (`--touch-gap`) |
| **격자형 컴포넌트 예외(2차)** | 캘린더 날짜 셀은 **셀 44×44px 이상 + 경계 간격 2px 이상**이면 된다(REQ-N-006 ②-1). **360px 실측 셀 폭 45.14px · 높이 72px** (v1.1 C-1·C-2 — §1.3 · §3.3) |
| **주 뷰 격자(2차 · 관리자)** | `≥1024px` 데스크톱 전용 화면이라 REQ-N-A-003 완화 기준을 적용한다. 30분 행 28px은 44px 미만이지만 **조작 대상은 행이 아니라 슬롯 블록(56px 이상)과 빈 칸 클릭 영역(정시 단위 56px)** 이다 |
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
| G-13 관리자 셸(2차) | 사이드바 240 / 64px, 상단바 56px. **v1.1에서 3구간 구조·현재 항목 표시·M-2 처리까지 확정** | CMP-053 (§3.13) |
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
| `favicon.svg` (48 viewBox) | **제작 완료 (v1.1 · 2026-09-12)** | 다크 모드 대응(심볼 `#FFFFFF` 전환). **그대로 배포 가능** |
| `icon-master-512.svg` · `apple-touch-icon-master-180.svg` | **제작 완료 (v1.1)** | `icon-512.png`·`icon-192.png`·`apple-touch-icon.png` 내보내기 마스터. 흰 배경 불투명 |
| `og-image.svg` (1200×630) | **제작 완료 (v1.1)** | 로고 + 헤드라인 + 틴트 배경, **사진 없이 성립**. `og:image:alt` 문안 확정 |
| PNG·ICO 래스터 5종 | **미생성 — P4 빌드로 이관(D-9)** | 변환 명령·규격·HTML 삽입 코드는 `design/assets/SOURCES.md` §4.1에 있다. 준비 안 되면 **해당 태그를 빼고 빌드**(아래 ②), 단 `favicon.svg`는 항상 넣는다 |

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

**2차 추가 (v1.1)**

14. **격자·표에 가로 스크롤을 만들지 않는다.** 넘치면 ① 열 줄이기 ② `<1024px` 카드 전환(CMP-042) ③ 400% 확대 시 주 단위 리스트(§4.4) 순으로 푼다.
15. **상태는 언제나 `텍스트 + (아이콘 또는 패턴)`** 이다. 좌측 컬러 바·배경 틴트·점은 **보조**이며 그것만으로 상태를 전달하면 디자인 QA 지적 대상이다.
16. **비활성 셀·행도 포커스를 받는다.** `disabled` 대신 `aria-disabled="true"`를 쓴다(캘린더·표에서 건너뛰면 무슨 날짜인지 알 수 없다).
17. **관리자 sticky 헤더의 `top`은 `--admin-topbar-h`**(56px), 공개·회원은 `--header-h`. 값을 복사하지 말고 변수를 쓴다.
18. **드래그·hover 전용 조작을 만들지 않는다.** 만들면 **같은 화면 안에** 클릭·키보드 대안을 병행한다(주 뷰는 드래그를 아예 도입하지 않는 것으로 확정했다).
19. **300ms 안에 끝나는 조작에는 로딩 표시를 넣지 않는다**(§3.2).

---

## 8. 미해결 · 확인 필요 사항

| # | 항목 | 영향 | designer 기준(무회신 시) |
|---|---|---|---|
| D-1 | **고객 로고 원본·브랜드 컬러**(V-2, 기한 09-17) | `--color-primary` 계열 4개 + 전 화면 대비 재검증 0.5작업일 | `#0B4F9E` 확정값 유지, 수령분은 CR |
| ~~D-2~~ | ~~z-index 쌓임 순서~~ | — | **해소(2026-09-12)** — planner R1 §3.1 A · developer R1 #10 **둘 다 승인**. 구현 조건 2가지를 §1.4에 추가했다 |
| D-3 | **레슨 유형 배지 색**(§3.17) | 2차 CMP-043 | **ⓐ 중립 1색 + 텍스트 구분으로 v1.1 명세를 작성했다.** 무회신이면 ⓐ 확정. ⓑ 채택 시에도 레이아웃 재작업 0건 |
| ~~D-4~~ | ~~캘린더 셀 `잔여 {n}`의 `{n}` 정의~~ | — | **해소(2026-09-12)** — REQ-C-L-001 v0.7이 `{n}` = **잔여 자리 합계**, 2자리 이상은 **"잔여 9+"** 로 확정했다. v1.1은 그 문구를 그대로 쓰되 **폭 실측(48.44px)이 셀 폭(45.14px)을 넘어** D-4가 예고한 흡수안(셀 높이 증가 + 라벨 2줄)을 **셀 72px · 2줄**로 적용했다 (§3.3) |
| **D-8** | **REQ-C-L-001의 근거 수치 "14px 최대 라벨 폭 약 40px"** | 문구·규칙은 영향 없음. 기획 문서의 괄호 안 근거 수치만 사실과 다름 | **`TKT-DSN-001`(to-planning) 발행.** designer 기준: **문구를 바꾸지 않고 2줄 배치로 흡수**하고, planner는 근거 수치만 48.44px·2줄 전제로 정정한다 |
| **D-9** | **파비콘·OG 래스터(PNG·ICO) 미생성** | P4 빌드 산출물 | **SVG 원본 4종은 제작 완료**(`design/assets/`). 래스터 변환 도구가 designer 환경에 없어 **변환 명령·규격을 `assets/SOURCES.md` §4.1에 넘겼다.** `favicon.svg`는 그대로 배포 가능하므로 **최소한 SVG 파비콘은 항상 넣는다** |
| D-5 | 사진 조달 방침(Q11) | 히어로·카드 이미지 자리 | **사진 0장 전제**로 1차 완주. 수령 시 레이아웃 변경 없이 교체 |
| D-6 | 임시 로고를 1차 오픈에 사용해도 되는가(Q-D5) | 파비콘·OG 제작 시점 | 임시 로고로 제작하고 수령 시 재제작. **제작 납기·미제작 시 처리는 §6.3에서 확정**(v0.2) |
| D-7 | **폴백 `@font-face` 메트릭 오버라이드 수치**(`size-adjust`·`ascent-override`·`descent-override`) | 글꼴 교체 시 CLS | **P4 기술 설계에서 실측 → designer 1회 확인.** 수용 기준은 §1.2 ⑤에서 P3가 확정했다(블록 높이 차 ±2px 이내 · CLS 0.01 이하) |

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 | 관련 리뷰/CR |
|---|---|---|---|---|
| **1.1** | 2026-09-12 | designer | **2차 디자인 시스템 확장 (G3a 승인 후속 · 2차 선착수).** ① **§3 전면 개편** — v1.0의 "2차 확장 예고 27종"을 **승격 명세 16종**(CMP-040 월 캘린더 / 041 슬롯 카드·목록 / 042 데이터 표 + `<1024px` 카드 전환 / 043 상태 배지 4군 16상태 / 044 Select / 045 Radio·Segmented / 046 DateTime / 047 Tabs / 048 Modal·하단 시트 / 049 Dropdown / 050 Pagination / 053 Admin Shell / 055 세션 만료 배너 / 057 주 뷰 30분 그리드 / **067 관리자 월 뷰**(신규 ID) / **068 일 뷰**(신규 ID))로 승격하고, **1차 CMP 2종 확장**(017 다중·부분 선택 / 019 8~10항목 폼). 각 컴포넌트에 상태(기본·hover·focus-visible·active·disabled·오류·로딩·빈 상태)와 **대비 측정값** 기재 ② **§3.2 2차 공통 상태 4종 신설**(스켈레톤·빈 상태·불러오기 실패·부분 실패, 300ms 기준) ③ **§3.15 2차 토큰 확정** — 예약 5종 확정 + 신규 2종(`--week-row-h` 28px · `--time-axis-w` 64px) + CSS 추가 블록. **신규 컬러·radius·shadow·motion·breakpoint 0건, §1.6 기존 토큰 값 변경 0건(TR-10 충족)** ④ **정정 3건** — C-1 월 캘린더 좌우 패딩 12px → 컨테이너 16px(셀 폭 **45.14px**, REQ-N-006 ②-2 실측값과 일치. `--calendar-pad` 값은 유지하고 적용 대상을 관리자 밀도 그리드로 한정) / C-2 `--cell-min-h` 56 → **72px**(라벨 "잔여 9+" 실측 48.44px > 45.14px → 2줄 배치, D-4 흡수안) / C-3 `--week-col-min-w` 하한 우려 **해소**(1024px 실측 118.86 → **124.57px**, developer R1 #11 닫힘) ⑤ §1.2 최소 크기 예외에 **상태 배지 12px(관리자 한정)** 행 추가 ⑥ §4.1 **대비 조합 11건 추가**(#28~#38), §4.2 격자 예외 값 갱신 + 주 뷰 행 신설 ⑦ §7 사용 원칙 **2차 6조항 추가** ⑧ §8 D-4 해소 · D-3 기본값 실행 · **D-8·D-9 신설** ⑨ 미게시 월을 **셀 상태가 아닌 빈 상태 블록**으로 규정해 "준비 중" 문구 충돌 해소 | 2차 범위 확정(PM 2026-09-12) · `planning/02_storyboard-admin.md` v1.0 · `interviews/2026-09-12_booking-rules.md` v1.2 · REQ-C-L-001 v0.7 · developer R1 #11 · `shared/tickets/TKT-DSN-001_to-planning_calendar-cell-label-width.md` |
| **1.0** | 2026-09-12 | designer / PMO | **G3a 게이트 승인 기준선** (내용은 v0.2와 동일, status `approved` · version 1.0 전환) | `pm/gates/` G3a |
| 0.2 | 2026-09-12 | designer | **R1 교차 검토 반영(planner 수정 요청 · developer 조건부 승인).** ① **Must** — CMP-003에 `≥1280px` **헤더 주 CTA 상태 3종(H1·H2·H3)** 신설: 고정 바와 동일한 판단 축(G-6 ①·②)을 적용해 자기 참조 시 "전화 문의" 대체 / 대표 전화 `[TBD]`면 미노출, 선택 근거·`aria-current` 처리 명문화 ② CMP-007에 **S1 보조 규칙(대표 전화 미확정 → 좌측 버튼 미렌더·우측 전폭)** 을 전 화면 공통으로 1회만 정의 ③ G-11 조건식 `and (max-width: 400px)` 병기(§1.6·§4.4) + 해당 구간 `--anchor-offset` 해제 ④ `:focus-visible`의 `border-radius` 삭제 + 선택자 풀어쓰기 + 스타일시트 말미 배치 규칙 ⑤ `ResizeObserver` 갱신 대상에 **헤더** 추가 + 비노출 구간 `removeProperty` ⑥ **폰트 파일 구성 확정**(static 400/700 + `unicode-range` 분할 subset · 500 미사용 · 폴백 메트릭 보정 필수 + 수용 기준) 및 "Variable은 weight를 덜 써도 작아지지 않는다" 전제 정정 ⑦ 행간·자간 변수 5개 추가 ⑧ CMP-005 `<details>` 정본 확정(`aria-expanded` 수동 금지, JS 역할 3가지 한정) ⑨ CMP-008 `<main id="main" tabindex="-1">` 확정 ⑩ **파비콘 4종·OG 1종 납기·미제작 시 처리 확정** ⑪ z-index 구현 조건 2줄 · D-2 해소 ⑫ CMP-004/005 weight 500 → 400 ⑬ 이동값 `--motion-distance` 참조 통일 · reduce 스피너 주석 ⑭ `--week-col-min-w` 2차 재확인 메모 ⑮ D-7 신설 | `shared/reviews/P3_design-docs_planner_r1.md` #1~#3·#8 · `shared/reviews/P3_design-docs_developer_r1.md` #1~#13 |
| 0.1 | 2026-09-12 | designer | 최초 작성 — 시안 A + 보정 1·2 기준 토큰 전량(컬러 32·타이포 10단·간격 15+3·radius 5·shadow 4·motion 7·z-index 6단·breakpoint 4구간), 개발 전달용 CSS 변수 블록, 1차 컴포넌트 30종 + 2차 확장 예고 27종, 대비 측정 27조합, 장식 이미지 판정 목록, 400% 확대·G-11 규칙, 아이콘 세트 Lucide 확정 | ADR(컨셉 선택 2026-09-12), 요구사항 §3.0·§10 TR-10, designer R1 #1·R2 #N1·#N2 |
