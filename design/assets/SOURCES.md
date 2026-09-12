# 디자인 에셋 출처 · 라이선스

> 이 문서는 `design/assets/`와 `design/mockups/`에 쓰인 **모든** 폰트·이미지·아이콘·그래픽의 출처와 라이선스를 기록한다.
> 상업적 사용이 허용되지 않는 자산은 어떤 경우에도 쓰지 않는다 (`CLAUDE.md` §8).
> **updated: 2026-09-12 · 단계: P3 (G3a 승인 후속 — 파비콘·OG 제작) (version 0.3)**

---

## 1. 현재 저장소에 실제로 포함된 자산

| 파일 | 종류 | 제작·출처 | 라이선스 | 상태 |
|---|---|---|---|---|
| `logo-yogapass-mark.svg` | 로고 심볼 (48×48) | **designer 자체 제작** (2026-09-12, 원본 도형: 원 + 호 + 직선) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder)** |
| `logo-yogapass-horizontal.svg` | 로고 가로형 (236×48) | **designer 자체 제작** (2026-09-12) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder)** |
| `favicon.svg` | 파비콘 (48 viewBox · 크기 무제한) | **designer 자체 제작** (2026-09-12, 심볼 파생) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder) · 그대로 배포 가능** |
| `icon-master-512.svg` | PNG 파비콘 마스터 (512×512, 흰 배경) | **designer 자체 제작** (2026-09-12, 심볼 파생) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder) · 래스터 내보내기 필요** |
| `apple-touch-icon-master-180.svg` | iOS 홈 화면 아이콘 마스터 (180×180, 흰 배경) | **designer 자체 제작** (2026-09-12, 심볼 파생) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder) · 래스터 내보내기 필요** |
| `og-image.svg` | OG·트위터 카드 대표 이미지 (1200×630) | **designer 자체 제작** (2026-09-12, 심볼 + 텍스트 + CSS 격자 그래픽) | 본 프로젝트 산출물 — 고객 귀속 | **임시(Placeholder) · 래스터 내보내기 필요** |
| `../mockups/concept-a.html` 내 인라인 SVG | 심볼·아이콘 3종(위치·말풍선·사람) | **designer 자체 제작** (24×24 그리드, stroke 2px 직접 작도) | 본 프로젝트 산출물 | 임시 |
| `../mockups/concept-b.html` 내 인라인 SVG | 동일 3종(stroke 1.8px 변형) | **designer 자체 제작** | 본 프로젝트 산출물 | 임시 |
| `../mockups/concept-c.html` 내 인라인 SVG | 심볼 | **designer 자체 제작** | 본 프로젝트 산출물 | 임시 |
| `../mockups/scr-001.html` 내 인라인 SVG | 심볼 + 아이콘 6종(전화·말풍선·위치·시계·화살표·정보) | **designer 자체 제작** (24px 그리드, stroke 2px 직접 작도 — **Lucide 파일을 복사하지 않았다**) | 본 프로젝트 산출물 | 임시(P4에서 Lucide 공식 SVG로 교체) |
| `../mockups/scr-002.html` 내 인라인 SVG | 심볼 + 아이콘 3종 | **designer 자체 제작** | 본 프로젝트 산출물 | 임시 |
| `../mockups/scr-003.html` 내 인라인 SVG | 심볼 + 아이콘 6종(위치·길찾기·복사·전화·정보·오류) | **designer 자체 제작** | 본 프로젝트 산출물 | 임시 |
| `../mockups/scr-008.html` 내 인라인 SVG | 심볼 + 아이콘 2종(전화·경고) | **designer 자체 제작** | 본 프로젝트 산출물 | 임시 |
| `../mockups/scr-006.html` 내 인라인 SVG **(v0.3 신규 등록 — G3a 지적 반영)** | 심볼 4개소 + 아이콘 7종 8개소(정보·메뉴×2·목차 chevron-down·chevron-up·맨 위로 arrow-up·말풍선·전화×2) = **`<svg>` 요소 13개소** | **designer 자체 제작** (24px 그리드, stroke 2px 직접 작도 — Lucide 파일을 복사하지 않았다) | 본 프로젝트 산출물 | 임시(P4에서 Lucide 공식 SVG로 교체) |

**목업별 인라인 SVG 실측 개수 (2026-09-12 측정 · 등록 누락 0건 확인)**

| 파일 | `<svg>` 요소 수 | 등록 |
|---|---|---|
| `concept-a.html` | 9 | v0.1 |
| `concept-b.html` | 9 | v0.1 |
| `concept-c.html` | 6 | v0.1 |
| `scr-001.html` | 45 | v0.2 |
| `scr-002.html` | 5 | v0.2 |
| `scr-003.html` | **18** | v0.2 |
| `scr-006.html` | **13** | **v0.3 (신규)** |
| `scr-008.html` | 8 | v0.2 |
| **합계** | **113** | — |

> **G3a 게이트 지적 "`scr-006.html` 인라인 SVG 18개소 미등록"에 대한 확인 결과**: 미등록 파일이 `scr-006.html`이라는 지적은 맞다(v0.2 표에 행이 없었다). 다만 **18개소는 이미 등록된 `scr-003.html`의 개수**이고, `scr-006.html`의 실측치는 **13개소**다. 위 실측표로 두 값을 함께 남겨 재확인이 필요 없게 했다. 이 표의 8개 파일이 `design/mockups/`의 전체이며, **이제 미등록 파일은 0건**이다.

- **외부에서 가져온 파일은 현재 0건이다.** 목업은 웹폰트·외부 이미지·외부 스크립트를 일절 로드하지 않는다(브라우저에서 바로 열리고, 오프라인에서도 동일하게 보인다).
- **사진 0장.** 사진이 들어갈 자리는 목업에 점선 라벨("사진 예정 자리")로 표시했다.

### 1.1 임시 로고에 대한 고지
- 고객 로고 원본(`pm/01_project-plan.md` V-2, 기한 09-17)과 브랜드 색상 코드가 **미확보**다. CR-000 원문에는 "로고 있음"으로 적혀 있으나 파일을 받지 못했다.
- 따라서 위 2개 SVG는 **컨셉 시안 비교와 레이아웃 검토를 위한 임시 자산**이며, 고객 로고 수령 즉시 교체한다.
- 워드마크는 SVG `<text>`로 조판되어 있어 뷰어 폰트에 따라 자간이 달라진다. **확정본은 아웃라인(path)으로 변환**한다.
- **[TBD: 고객 제공 필요]** 로고 원본(AI/SVG 또는 고해상도 PNG), 브랜드 컬러 HEX, 로고 최소 사용 크기·보호 여백 규정(있다면).

---

## 2. 폰트 — **Pretendard 단일 채택 (2026-09-12 확정)**

> **현재 목업은 웹폰트를 로드하지 않는다.** 아래 채택본은 P4에서 **self-host**(로컬 번들)한다.
> 폰트 파일은 `design/assets/fonts/`에 넣고 이 표의 "포함 여부"를 갱신한다.

| 폰트 | 용도 | 배포처 | 라이선스 | 상업적 사용 | 웹 임베딩 | 포함 여부 |
|---|---|---|---|---|---|---|
| **Pretendard / Pretendard Variable** | **채택 — 제목·본문·UI·숫자 전부** | https://github.com/orioncactus/pretendard | SIL Open Font License 1.1 | 가능 | 가능 | 미포함(P4 self-host 예정) |
| ~~Nanum Myeongjo~~ | ~~시안 B 제목 전용~~ | https://hangeul.naver.com/font | SIL OFL 1.1 | 가능 | 가능 | **미채택**(시안 A 선택으로 불필요) |
| **IBM Plex Sans KR** | Pretendard 대체 후보(예비) | https://github.com/IBM/plex | SIL Open Font License 1.1 | 가능 | 가능 | 미포함 |
| **Noto Sans KR** | 폴백 후보 | https://github.com/notofonts/noto-cjk | SIL Open Font License 1.1 | 가능 | 가능 | 미포함 |

**self-host 요건 (P4 전달)**
- weight **400 / 500 / 700**만 사용한다(Variable 단일 파일도 가능). `font-display: swap`.
- **Korean subset + Latin 우선 로드**, 나머지는 unicode-range 분할.
- 외부 CDN·Google Fonts를 쓰지 않는다 — 초기 로드의 외부 도메인 요청을 0건으로 유지한다.
- `OFL.txt`를 폰트 파일과 같은 디렉터리에 함께 배치한다.

- **OFL 1.1 준수 사항**: ① 폰트 자체를 유료로 재판매하지 않는다 ② 라이선스 원문(`OFL.txt`)을 폰트 파일과 함께 배포한다 ③ 예약 폰트 이름(Reserved Font Name)이 있는 경우 수정본에 같은 이름을 쓰지 않는다. → self-host 시 `OFL.txt`를 함께 배치한다.
- **시스템 폴백 스택**(웹폰트 로드 실패 시): `-apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif`. 폴백 폰트는 OS 동봉 폰트이므로 저장소에 포함하지 않는다.

---

## 3. 아이콘 — **Lucide 채택 (2026-09-12 확정 · 번복하지 않는다)**

| 세트 | 배포처 | 라이선스 | 상업적 사용 | 판정 |
|---|---|---|---|---|
| **Lucide** | https://lucide.dev | **ISC License** | 가능 | **채택** — 2px stroke·24px 그리드가 시안 A의 1px 라인 구조와 결이 같고, 2차 40~60종을 한 세트로 덮는다 |
| Phosphor Icons | https://phosphoricons.com | MIT License | 가능 | 미채택 |
| Material Symbols | https://fonts.google.com/icons | Apache License 2.0 | 가능 | 미채택 |

- **현재 목업의 아이콘은 Lucide 파일을 복사한 것이 아니라 designer가 같은 규격(24px 그리드 · stroke 2px · round cap)으로 직접 작도한 SVG다.** P4에서 Lucide 공식 SVG로 교체한다.
- **1차 필요 아이콘 16종**: `phone` · `menu` · `x` · `map-pin` · `navigation` · `copy` · `clock` · `train-front` · `bus` · `car` · `arrow-right` · `arrow-up` · `external-link` · `check-circle-2` · `alert-circle` · `info`
- **2차 추가 예상 30~45종** (캘린더·사용자·잠금·필터·정렬·편집·삭제·저장·검색·벨 등).
- **라이선스 고지 방식**: ISC 원문(`LICENSE`)을 저장소 `LICENSES/lucide-ISC.txt`로 동봉하고 이 문서에 경로를 기록한다. 아이콘 폰트가 아니라 **인라인 SVG 또는 SVG 스프라이트**로 번들한다.

---

## 4. 이미지 · 사진

| 항목 | 현재 상태 |
|---|---|
| 스튜디오 사진 | **[TBD: 고객 제공 필요]** — 조달 방침(고객 촬영 / 전문 촬영 / 스톡) 미회신(계획서 Q11). 수령 전까지 그래픽 패널로 대체한다 |
| 강사 인물 사진 | **[TBD: 고객 제공 필요]** — 미제공 시 **이니셜 플레이스홀더**를 쓴다. **인물 스톡 사진 대체는 금지**(화면정의서 SCR-002 §3) |
| 지도 이미지 | **사용하지 않는다.** 메인에는 지도를 넣지 않고(REQ-F-030 ⓑ), **지도 서비스 화면 캡처는 금지**(REQ-N-024) |
| OG 이미지 · 파비콘 | **v0.3에서 SVG 원본 4종 제작 완료** (§4.1). PNG·ICO 래스터는 P4 빌드에서 내보낸다. 고객 로고 수령 시 재제작 |

- 스톡 이미지를 쓰게 될 경우의 준수 사항(미리 고정): **상업적 사용 + 웹 배포 허용 라이선스만** 사용하고, 라이선스 유형·출처 URL·다운로드 일자·사용 화면을 이 문서 §4에 행으로 추가한다. 인물이 식별되는 사진은 모델 릴리스 확인 전까지 쓰지 않는다.

---

## 4.1 파비콘 · OG 이미지 (v0.3 신규 · G3a 승인 후속)

디자인 시스템 §6.3이 "G3 승인 직후 2작업일 이내"로 확정한 납기 항목이다. **임시 로고(심볼)에서 파생**했고 외부 자산을 쓰지 않았다.

**제작한 원본 (SVG · `design/assets/`)**

| 파일 | 규격 | 배경 | 용도 |
|---|---|---|---|
| `favicon.svg` | 48 viewBox (크기 무제한) | 투명 | 브라우저 탭 아이콘. `prefers-color-scheme: dark`에서 심볼이 `#FFFFFF`로 전환된다 |
| `icon-master-512.svg` | 512×512 | `#FFFFFF` | `icon-512.png` · `icon-192.png` 내보내기 마스터 |
| `apple-touch-icon-master-180.svg` | 180×180 | `#FFFFFF` | `apple-touch-icon.png` 내보내기 마스터 |
| `og-image.svg` | 1200×630 | `#F0F5FB` 틴트 | `og-image.png` 내보내기 마스터 |

**내보내야 할 래스터 산출물 (P4 빌드 — designer 환경에 래스터 변환 도구가 없어 SVG 원본까지만 제작했다)**

| 산출물 | 크기 | 원본 | 비고 |
|---|---|---|---|
| `favicon.ico` | 32 + 48 멀티사이즈 | `favicon.svg` | 구형 브라우저·북마크용. **최신 Chrome·Edge·Firefox·Safari 17+는 `favicon.svg`만으로 동작**하므로 `.ico`는 폴백이다 |
| `icon-192.png` | 192×192 | `icon-master-512.svg` | 웹 매니페스트 `purpose: "any"` |
| `icon-512.png` | 512×512 | `icon-master-512.svg` | 웹 매니페스트 `purpose: "any"` |
| `apple-touch-icon.png` | 180×180 | `apple-touch-icon-master-180.svg` | iOS 홈 화면. 모서리 둥글리기를 넣지 않는다(iOS가 마스킹) |
| `og-image.png` | 1200×630 · **300KB 이하** | `og-image.svg` | 디자인 시스템 §6.2 용량 상한 |

**변환 명령 예 (둘 중 하나 · P4에서 실행하고 결과를 이 표에 기록한다)**

```bash
# sharp-cli (Node)
npx sharp-cli -i design/assets/icon-master-512.svg            -o icon-512.png        resize 512 512
npx sharp-cli -i design/assets/icon-master-512.svg            -o icon-192.png        resize 192 192
npx sharp-cli -i design/assets/apple-touch-icon-master-180.svg -o apple-touch-icon.png resize 180 180
npx sharp-cli -i design/assets/og-image.svg                   -o og-image.png        resize 1200 630
npx png-to-ico icon-32.png icon-48.png > favicon.ico          # 32·48 PNG를 먼저 내보낸 뒤 묶는다

# ImageMagick
magick -background none design/assets/favicon.svg -define icon:auto-resize=48,32 favicon.ico
```

> ⚠ `og-image.png` 래스터화 시 **Pretendard(SIL OFL 1.1)가 설치·지정된 환경**에서 실행한다. 폴백 폰트로 굽히면 조판(자간·글자 폭)이 디자인과 달라진다. 변환 후 **실제 글자 폭이 좌측 96px / 우측 96px 여백 안에 들어가는지 1회 눈으로 확인**한다.

**HTML 삽입 규격 (developer 전달)**

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">      <!-- 폴백 -->
<link rel="apple-touch-icon" href="/apple-touch-icon.png"><!-- 180×180 -->
<meta property="og:image" content="https://{도메인}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="강남 요가패스 로고와 '강남 요가 스튜디오' 문구가 있는 대표 이미지">
```

- **`og:image:alt`는 필수**다(디자인 시스템 §4.3 "의미 있음" 분류).
- 래스터 산출물이 P4 빌드 시점까지 준비되지 않으면 **placeholder 파일을 만들지 말고 해당 `<link>`·`og:image` 태그를 빼고 빌드**한다(디자인 시스템 §6.3 ②). 단 `favicon.svg`는 지금 상태로 배포 가능하므로 **최소한 SVG 파비콘은 항상 넣는다.**

**대비·접근성 확인값**

| 대상 | 전경 | 배경 | 대비 | 판정 |
|---|---|---|---|---|
| OG 헤드라인 "강남 요가패스" | `#16263A` | `#F0F5FB` | **13.96:1** | 통과 |
| OG 워드마크 "YOGAPASS" | `#0A2540` | `#F0F5FB` | **14.17:1** | 통과 |
| OG 서브카피 "강남 요가 스튜디오" | `#5A6B7D` | `#F0F5FB` | **5.00:1** | 통과 |
| OG 심볼·좌측 바 | `#0B4F9E` | `#F0F5FB` | **7.30:1** | 통과 |
| 파비콘 심볼 (라이트) | `#0B4F9E` | 흰 탭 배경 | **7.99:1** | 통과 |
| 파비콘 심볼 (다크) | `#FFFFFF` | `#202124` 계열 탭 배경 | **15.0:1 이상** | 통과 |

- OG 이미지에는 **주소·전화·강사·요금·`[TBD]` 값을 넣지 않았다**(REQ-N-023). 문안은 확정된 브랜드 표기 2개(`YOGAPASS`, `강남 요가패스`)와 일반 서술 1개(`강남 요가 스튜디오`)뿐이다.

### 고객 로고 수령 시 교체 절차 (1줄 요약)

> **`logo-yogapass-mark.svg`의 도형만 고객 원본(아웃라인 path)으로 갈아끼우고 위 4개 SVG의 `<g>` 심볼 블록을 같은 path로 교체 → 래스터 5종 재내보내기 → 이 문서 §1·§4.1 표의 "상태"를 `확정`으로 갱신 → `--color-primary` 계열 4개가 바뀌면 디자인 시스템 §4.1 대비표 재계산(0.5작업일, D-1)** — 이 순서를 CR로 처리한다.

---

## 5. 색상 · 그래픽

- 3개 시안의 컬러 팔레트는 **designer가 직접 지정하고 흰 배경 대비를 계산해 검증**한 값이다(WCAG 2.1 상대 휘도 공식). 외부 팔레트를 복제하지 않았다. 측정값은 `design/03_design-concept.md` §2 각 시안의 대비 표에 있다.
- **확정 팔레트(시안 A)의 전 조합 대비 측정값 27건은 `design/03_design-system.md` §4.1에 있다.** 이 표가 P5 대비 판정의 기준이다.
- 목업의 그래픽(라인 격자, 아치, 색면, 사선 해치)은 전부 **CSS로 생성**한 것이며 외부 이미지 파일이 아니다.

---

## 6. 갱신 규칙

1. 외부 자산을 새로 넣을 때마다 **파일을 커밋하기 전에** 이 문서에 행을 추가한다(파일명·출처 URL·라이선스·취득일·사용 위치).
2. 라이선스를 확인할 수 없는 자산은 **사용하지 않는다.**
3. 임시 자산은 "상태" 열에 **임시(Placeholder)** 로 표시하고, 교체되면 그 행을 갱신한다(행을 지우지 않는다).

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
|---|---|---|---|
| 0.1 | 2026-09-12 | designer | 최초 작성 — 임시 로고 2종 등록, 폰트·아이콘 후보와 라이선스 정리, 사진 미확보 [TBD] 목록화 |
| 0.3 | 2026-09-12 | designer | **G3a 승인 후속** — ① **파비콘·OG SVG 원본 4종 제작·등록**(`favicon.svg`·`icon-master-512.svg`·`apple-touch-icon-master-180.svg`·`og-image.svg`) + §4.1 신설(래스터 내보내기 규격·변환 명령·HTML 삽입 규격·대비 6건·`og:image:alt`) ② **G3a 지적 처리 — `scr-006.html` 인라인 SVG 등록**(실측 13개소) + **목업 8파일 전량 `<svg>` 실측표(합계 113)** 추가로 미등록 0건 확인, 지적문의 "18개소"는 `scr-003.html` 값임을 병기 ③ **고객 로고 수령 시 교체 절차 1줄 확정** ④ §4 파비콘·OG 행 갱신 (근거: G3a 게이트 지적 · 디자인 시스템 §6.3) |
| 0.2 | 2026-09-12 | designer | P3 상세 디자인 반영 — **폰트 Pretendard 단일 채택**(SIL OFL 1.1, self-host 요건 명시) · **아이콘 Lucide 채택**(ISC, 1차 16종 목록 + 고지 방식) · 1차 목업 4종(scr-001·002·003·008)의 인라인 SVG 등록 · 파비콘·OG 규격 확정 · 확정 팔레트 대비 측정표 위치 참조 추가 |
