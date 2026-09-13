# static/img 자산 출처·상태 (developer 관리본)

> 원본은 전부 `design/assets/` 에 있다. 여기 있는 것은 **빌드용 사본·래스터 내보내기 결과**다.
> 디자인 원본의 출처·라이선스 정본은 `design/assets/SOURCES.md` 다(designer 소관).

| 파일 | 원본 | 생성 방법 | 상태 |
|---|---|---|---|
| `favicon.svg` | `design/assets/favicon.svg` | 복사 + **XML 주석 오류 수정**(연속 하이픈 — TKT-DSN-002 회신 ④) | 임시 로고 기반 |
| `favicon.ico` | 같음 | `rsvg-convert` 32·48 → `magick` 멀티사이즈 ICO | 임시 로고 기반 |
| `icon-192.png` · `icon-512.png` | `design/assets/icon-master-512.svg` | `rsvg-convert` | 임시 로고 기반 |
| `apple-touch-icon.png` | `design/assets/apple-touch-icon-master-180.svg` | `rsvg-convert` | 임시 로고 기반 |
| `og-image.png` | `design/assets/og-image.svg` | **⚠ 임시본** — 아래 참조 | **임시(TEMPORARY)** |
| `logo-horizontal.svg` · `logo-mark.svg` · `apple-touch-icon.svg` · `og-image.svg` | `design/assets/` | 복사 | 임시 로고 기반 |

---

## ⚠ `og-image.png` — 임시본이다 (PM 결정 2026-09-13 · TKT-DSN-002)

**무엇이 임시인가**: 조판에 쓰인 **폰트**다. 레이아웃·색·문구·좌표는 designer 원본(`design/assets/og-image.svg`) 그대로다.
원본은 `font-family` 첫 항목이 Pretendard 인데, 저장소의 Pretendard 는 `unicode-range` 로 분할된 **woff2 서브셋 184개**뿐이라
래스터 변환기(fontconfig/freetype)가 로드하지 못한다. 그래서 변환 환경에서 쓸 수 있는 **Noto Sans CJK KR** 로 렌더했다.
→ **자간·글자 폭이 Pretendard 조판과 다르다.** 그 외는 동일하다.

**임시본 표시 3곳**: ① 작업 사본 파일명 `assets-work/og-image.TEMP-source.svg` ② 그 파일 머리 주석 ③ `og-image.png` 안의 PNG `tEXt Comment` 청크
(`Comment = TEMPORARY placeholder OG image. TKT-DSN-002 …`).

> **⚠ 작업 사본의 위치 (DEF-010)**: 변환용 작업 사본은 `developer/site/assets-work/` 에 둔다.
> `static/` 아래에 두면 ① 운영 이미지의 `/app/static/img/` 에 들어가고(자산 목록 대조에서 초과 1건)
> ② `collectstatic` 이 배포 산출물로 굽고 ③ 정적 경로로 직접 접근할 수 있게 된다.
> `.dockerignore` 가 `assets-work/` 와 `*.TEMP-*` 를 이중으로 제외한다.

**생성·검증 명령** (일회용 컨테이너 — 틀·프로젝트에 변환 도구를 설치하지 않는다):

```bash
# developer/site 에서 (작업 사본은 assets-work/, 결과물은 static/img/)
docker run --rm -v "$(pwd -W)/assets-work:/work" -v "$(pwd -W)/static/img:/out" alpine:3.20 sh -c '
  apk add --no-cache rsvg-convert imagemagick font-noto-cjk optipng
  cd /tmp && cp /work/og-image.TEMP-source.svg src.svg
  rsvg-convert -w 1200 -h 630 src.svg -o og-raw.png
  optipng -quiet -o5 og-raw.png && cp og-raw.png /out/og-image.png'
# PNG tEXt Comment 삽입은 apps 컨테이너의 python 으로 수행(IHDR 뒤 tEXt 청크 1개)
```

**검증 결과 (2026-09-13)**

| 확인 | 결과 |
|---|---|
| 규격 | PNG **1200×630** · 8-bit sRGB |
| 용량 | **30,916 B (≈30KB)** — 상한 300KB 대비 10% |
| **텍스트·로고가 좌우 96px 여백 안에 들어가는가** | **들어간다.** 텍스트+로고만 렌더해 `magick -trim` 으로 실측한 경계 = **516×323 at (97, 136)** → 좌 97 ≥ 96, 우 613 ≤ 1104 (티켓이 경고한 여백 초과 없음. 눈이 아니라 실측으로 확인했다) |
| HTTP | `GET /static/img/og-image.png` → 200 |
| 메타 태그 | `og:image` · `:width` · `:height` · `:alt` · `twitter:card` 5줄이 자동으로 붙는다 |

**정식본 교체 절차 (코드 변경 0)**

1. Pretendard 가 설치된 환경 또는 텍스트를 아웃라인(path)으로 바꾼 SVG 로 `design/assets/og-image.svg` 를 1200×630 PNG(≤300KB)로 내보낸다.
2. 그 파일을 **`developer/site/static/img/og-image.png` 에 덮어쓴다.** 파일명·경로가 같으므로 템플릿·뷰·설정은 고치지 않는다
   (`apps/core/context_processors._og_image` 가 파일 존재 여부만 본다).
3. `assets-work/og-image.TEMP-source.svg` 를 삭제하고 이 문서의 임시 표기 행을 갱신한다.
4. 운영 배포 시 `collectstatic` 이 해시 파일명으로 다시 굽는다 — 별도 작업 없다.
