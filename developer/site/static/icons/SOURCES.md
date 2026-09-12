# 아이콘 출처

| 파일 | 출처 | 라이선스 |
|---|---|---|
| `phone.svg` · `message-square.svg` · `map-pin.svg` · `clock.svg` · `info.svg` · `arrow-right.svg` · `external-link.svg` | Lucide (https://lucide.dev) | ISC (상업적 사용 가능) |
| `alert-circle.svg` · `check-circle.svg` · `alert-triangle.svg` · `navigation.svg` · `copy.svg` · `chevron-down.svg` · `arrow-up.svg` · `list.svg` (구현 2단계 추가) | Lucide (https://lucide.dev) | ISC (상업적 사용 가능) |

- 형태는 Lucide 아이콘 규격(24×24 그리드, stroke-width 2, round cap/join)을 따랐고
  `design/mockups/*.html` 에서 designer 가 사용한 path 와 동일하다(목업에 없는 3종 —
  `alert-triangle`·`chevron-down`·`arrow-up`·`list` — 은 같은 규격으로 맞춰 그렸다).
- 색은 `currentColor` 를 상속하며, `{% icon "phone" %}` 템플릿 태그가 인라인 삽입한다(HTTP 요청 0건).
- 사용처: `alert-circle`(폼 오류·결과 실패) · `check-circle`(결과 성공) · `alert-triangle`(SCR-009 장식) ·
  `navigation`(길찾기) · `copy`(주소 복사) · `chevron-down`(모바일 목차) · `arrow-up`(맨 위로) · `list`(빈 상태).
