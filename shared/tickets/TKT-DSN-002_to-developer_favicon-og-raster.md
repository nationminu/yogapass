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
- 처리 내용:
- 변경 파일·버전:
- 처리 일자:

## 확인 (발행 팀 작성)
- [ ] 처리 결과 확인 → `status: closed`
- 코멘트:
