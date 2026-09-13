---
id: TKT-DSN-002
type: request                # request | question | asset | issue
from: design
to: developer
phase: P3 → P4
priority: medium
status: open
related: [design/assets/SOURCES.md §4.1, design/03_design-system.md §6.3, design/03_design-system.md §8 D-9, shared/reviews/P3_design-docs_developer_r1.md #9]
created: 2026-09-12
due: P4 빌드 구성 시
---

# TKT-DSN-002 파비콘·OG SVG 원본 전달 — PNG·ICO 래스터 내보내기 요청

## 요청 내용

디자인 시스템 §6.3이 "G3 승인 직후 2작업일 이내"로 약속한 파비콘·OG를 **SVG 원본 4종으로 제작해 전달**한다.

| 전달한 파일 | 규격 | 배경 |
|---|---|---|
| `design/assets/favicon.svg` | 48 viewBox (크기 무제한) | 투명 · 다크 모드 대응 |
| `design/assets/icon-master-512.svg` | 512×512 | `#FFFFFF` |
| `design/assets/apple-touch-icon-master-180.svg` | 180×180 | `#FFFFFF` |
| `design/assets/og-image.svg` | 1200×630 | `#F0F5FB` |

**요청**: 위 원본에서 아래 래스터 5종을 P4 빌드에서 내보내 주기 바란다. designer 작업 환경에 래스터 변환 도구(sharp·ImageMagick 등)가 없어 **SVG 원본까지만** 제작했다.

| 산출물 | 크기 | 원본 |
|---|---|---|
| `favicon.ico` | 32 + 48 멀티사이즈 | `favicon.svg` |
| `icon-192.png` | 192×192 | `icon-master-512.svg` |
| `icon-512.png` | 512×512 | `icon-master-512.svg` |
| `apple-touch-icon.png` | 180×180 | `apple-touch-icon-master-180.svg` |
| `og-image.png` | 1200×630 · **300KB 이하** | `og-image.svg` |

변환 명령 예시, HTML 삽입 규격(`<link rel="icon">` · `og:image` · **`og:image:alt` 필수**), 대비 확인값은 **`design/assets/SOURCES.md` §4.1**에 전부 적어 두었다.

## 배경·이유

- developer R1 #9에서 합의한 처리 방침 ①(designer가 임시 로고 기반으로 제작해 전달) 이행분이다.
- **`favicon.svg`는 그대로 배포 가능**하다. 최신 Chrome·Edge·Firefox·Safari 17+가 SVG 파비콘을 지원하므로, 래스터가 늦어져도 **SVG 파비콘 `<link>`는 항상 넣는다**.
- 래스터가 준비되지 않은 시점에는 방침 ②대로 **placeholder 파일을 만들지 말고 해당 `<link>`·`og:image` 태그를 빼고 빌드**한다(깨진 아이콘·빈 이미지가 남는 것보다 낫다).
- `og-image.png` 래스터화는 **Pretendard가 설치·지정된 환경**에서 해야 조판이 일치한다. 폴백 폰트로 구우면 글자 폭이 달라져 좌우 96px 여백을 넘을 수 있다 — 변환 후 1회 눈으로 확인해 주기 바란다.
- 전부 **임시 로고(Placeholder) 기반**이다. 고객 로고 원본(V-2, 기한 09-17) 수령 시 designer가 재제작하고 CR로 처리한다(교체 절차는 SOURCES.md §4.1 마지막 줄).

## 완료 조건

- [ ] 래스터 5종이 빌드 산출물에 포함된다(또는 미포함 시 해당 태그가 빠진 채 빌드된다).
- [ ] `og:image:alt`가 들어간다 — `"강남 요가패스 로고와 '강남 요가 스튜디오' 문구가 있는 대표 이미지"`.
- [ ] `og-image.png`가 300KB 이하다.
- [ ] 실행한 변환 명령과 결과 파일 크기를 `design/assets/SOURCES.md` §4.1 표에 기록한다(designer가 이 문서를 갱신해도 된다 — 결과만 알려 주기 바란다).

---

## 처리 결과 (수신 팀 작성)

> **2026-09-13 갱신 (2차 회신)** — PM 결정에 따라 **`og-image.png` 보류를 해제하고 임시본을 넣었다.**
> 아래 ①~④는 1차 회신 원문이고, **⑤가 2차 회신**이다. 표의 `og-image.png` 행도 갱신했다.

- 처리 내용: **처리 완료(임시본 포함)** — 래스터 **5종 전부 산출**(`og-image.png` 은 **임시본**). 더불어 **`favicon.svg` 의 XML 파싱 오류 1건**을 발견해 회신한다.

**① 래스터 내보내기 결과**

| 산출물 | 결과 | 크기 | 규격 확인 |
|---|---|---|---|
| `favicon.ico` | ✅ | 13.9KB | `identify` = ICO 32×32 + 48×48 (멀티사이즈) |
| `icon-192.png` | ✅ | 3.1KB | PNG 192×192 |
| `icon-512.png` | ✅ | 8.8KB | PNG 512×512 |
| `apple-touch-icon.png` | ✅ | 3.0KB | PNG 180×180 |
| `og-image.png` | ⚠ **임시본** (2026-09-13) | 30.9KB (상한 300KB) | PNG 1200×630 · 텍스트+로고 실측 경계 516×323 at (97,136) → 좌우 96px 여백 안. 아래 ⑤ |

실행한 변환 명령(**일회용 컨테이너** — 틀·프로젝트에 변환 도구를 설치하지 않았다):

```bash
docker run --rm -v ".../design/assets:/in" -v ".../developer/site/static/img:/out" alpine:3.20 sh -c '
apk add --no-cache rsvg-convert imagemagick
rsvg-convert -w 192 -h 192 /in/icon-master-512.svg            -o /out/icon-192.png
rsvg-convert -w 512 -h 512 /in/icon-master-512.svg            -o /out/icon-512.png
rsvg-convert -w 180 -h 180 /in/apple-touch-icon-master-180.svg -o /out/apple-touch-icon.png
rsvg-convert -w 48 -h 48 -b none /out/favicon.svg -o /tmp/f48.png
rsvg-convert -w 32 -h 32 -b none /out/favicon.svg -o /tmp/f32.png
magick /tmp/f32.png /tmp/f48.png /out/favicon.ico'
```

**② HTML 삽입** — `templates/base.html` 에 SVG 파비콘 + `.ico` 폴백 + `apple-touch-icon` 3줄을 넣었다(SOURCES.md §4.1 규격). 운영 빌드에서 해시 파일명·brotli·`immutable` 적용까지 확인했다.

**③ `og-image.png` 보류 사유** — 원본이 `font-family: Pretendard` 로 조판돼 있는데, 저장소에 있는 Pretendard 는 **`unicode-range` 로 분할된 woff2 서브셋 184개**뿐이라 fontconfig/freetype 이 로드하지 못한다(woff2 미지원). 폴백 폰트로 구우면 **글자 폭이 달라져 좌우 96px 여백을 넘을 수 있고**(티켓이 경고한 바로 그 상황), 이 작업 환경에는 결과를 눈으로 확인할 브라우저가 없다. 따라서 티켓의 방침 ②대로 **placeholder 를 만들지 않고 `og:image` 계열 태그(`og:image`·width·height·alt·`twitter:card`)를 빼고 빌드**했다.
- **파일만 `developer/site/static/img/og-image.png` 에 놓이면 코드 변경 없이 태그 5줄이 자동으로 붙는다**(`apps/core/context_processors._og_image` 가 파일 존재 여부만 본다). `og:image:alt` 문구는 티켓의 문자열을 그대로 넣어 두었다.
- 처리 방법 제안(택1): ⓐ Pretendard **정적 TTF/OTF** 1벌을 `design/assets/` 에 함께 전달해 주면 우리가 굽는다 ⓑ designer 환경에서 브라우저로 SVG 를 열어 PNG 로 내보낸다 ⓒ **텍스트를 아웃라인(path)으로 변환한 `og-image-outlined.svg`** 를 주면 폰트 없이도 조판이 정확히 재현된다 — **ⓒ를 권한다**(고객 로고 수령 시 재제작에도 그대로 쓸 수 있다).

**④ ⚠ 회신: `design/assets/favicon.svg` 가 XML 로 파싱되지 않는다 (designer 조치 필요)**
- 증상: `rsvg-convert` · XML 파서에서 `XML parse error: Comment must not contain '--' (double-hyphen) (line 6)`.
- 원인: 6행 주석 안의 `--color-primary` — **XML 주석에는 연속 하이픈을 넣을 수 없다.**
- 영향: 브라우저는 `image/svg+xml` 을 **XML 로 엄격 파싱**하므로 이 파일을 그대로 배포하면 **파비콘이 표시되지 않는다.** (`icon-master-512.svg` · `apple-touch-icon-master-180.svg` · `og-image.svg` 는 이상 없음)
- 우리 조치: 사본 `developer/site/static/img/favicon.svg` 의 해당 문구를 `` `color-primary` 토큰 `` 으로 바꿔 해소하고, 그 사본으로 `.ico` 를 만들었다. **원본 수정은 designer 소관**이라 고치지 않았다.

**⑤ `og-image.png` — 임시본 생성 (2026-09-13 · PM 결정 반영)**

PM 결정: **"임시본을 넣고 나중에 교체한다. 임시본임을 파일명·주석·인계 메모에 분명히 남기고, 정식본 교체 시 코드 변경이 없게 하라."**

- **무엇이 임시인가**: **폰트뿐이다.** 레이아웃·색·문구·좌표는 `design/assets/og-image.svg` 원본 그대로이며, **조판만 Noto Sans CJK KR 로 렌더**했다(저장소의 Pretendard 는 `unicode-range` 분할 woff2 서브셋뿐이라 래스터 변환기가 로드하지 못한다 — ③ 참조). 따라서 **자간·글자 폭이 Pretendard 조판과 다르다.**
- **티켓이 경고한 "좌우 96px 여백 초과"는 눈이 아니라 실측으로 확인했다**: 배경·격자·브랜드 바를 제거한 **텍스트+로고만** 렌더해 `magick -trim` 으로 경계를 쟀다 → **516×323 at (97, 136)** → 좌 97 ≥ 96 · 우 613 ≤ 1104 → **여백 안에 들어간다.**
- **임시본 표시 4곳**: ⓐ 작업 사본 파일명 `developer/site/static/img/og-image.TEMP-source.svg` ⓑ 그 파일의 머리 주석 ⓒ `og-image.png` 안의 PNG `tEXt Comment`(`TEMPORARY placeholder OG image. TKT-DSN-002 / PM decision 2026-09-13 …`) ⓓ **인계 메모 `developer/site/static/img/SOURCES.md`**(생성 명령·검증값·교체 절차 포함).
- **검증 결과**: PNG 1200×630 · 8-bit sRGB · **30,916 B**(상한 300KB의 10%) · `GET /static/img/og-image.png` → 200 · `og:image`·`:width`·`:height`·**`og:image:alt`(티켓 문자열 그대로)**·`twitter:card` **5줄이 자동으로 붙는 것**을 실행 응답에서 확인했다.

**정식본 교체 절차 (코드 변경 0)**

1. Pretendard 가 설치된 환경, 또는 **텍스트를 아웃라인(path)으로 바꾼 SVG**(우리가 권했던 ⓒ안)로 `design/assets/og-image.svg` 를 1200×630 PNG(≤300KB)로 내보낸다.
2. 그 파일을 **`developer/site/static/img/og-image.png` 에 덮어쓴다.** 경로·파일명이 같으므로 템플릿·뷰·설정은 고치지 않는다(`apps/core/context_processors._og_image` 가 파일 존재만 본다).
3. `og-image.TEMP-source.svg` 를 삭제하고 `static/img/SOURCES.md` 의 임시 표기 행을 갱신한다. 운영 배포 시 `collectstatic` 이 해시 파일명으로 다시 굽는다.
4. 고객 로고 원본(V-2) 수령 시에는 위 1~3을 designer 재제작본으로 한 번 더 수행하면 된다 — **CR 처리 범위가 파일 1개로 끝난다.**

- 변경 파일·버전:
  - `developer/site/static/img/` — `favicon.ico` · `icon-192.png` · `icon-512.png` · `apple-touch-icon.png` (신규) · `favicon.svg` (XML 오류 수정) · **`og-image.png`(임시본, 2026-09-13)** · **`og-image.TEMP-source.svg`(신규)** · **`SOURCES.md`(신규 — 인계 메모)**
  - `developer/site/templates/base.html` · `templates/partials/meta.html` · `apps/core/context_processors.py`
  - `developer/04_dev-report.md` v0.2 §7 → **v0.3 §7**
- 처리 일자: 2026-09-13 (1차 회신) · **2026-09-13 2차 회신 — `og-image.png` 임시본 반영**

## 확인 (발행 팀 작성)
- [ ] 처리 결과 확인 → `status: closed`
- 코멘트:
