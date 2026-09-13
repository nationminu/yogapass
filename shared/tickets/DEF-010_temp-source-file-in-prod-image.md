---
id: DEF-010
from: qa
to: developer
phase: P5
severity: trivial
status: open
related_req: [REQ-N-024]
related_tc: [TC-116]
related_scr: []
found_cycle: 1
created: 2026-09-13
---

# DEF-010 운영 이미지의 정적 자산에 작업 중간 파일 `og-image.TEMP-source.svg` 가 포함돼 자산 목록 대조에서 초과 1건이 난다

## 환경
- 실행 방법: `docker run --rm --entrypoint sh yogapass-app:0.1.0-qa1 -c 'ls -la /app/static/img/'`
- 대상 버전: 개발 보고서 v0.3, qa가 직접 빌드한 운영 이미지 `yogapass-app:0.1.0-qa1`

## 재현 절차
1. `APP_VERSION=0.1.0-qa1 docker compose -f compose.yaml -f compose.prod.yaml build app`
2. `docker run --rm --entrypoint sh yogapass-app:0.1.0-qa1 -c 'ls /app/static/img/'`
3. 출력 목록을 `design/assets/SOURCES.md` 기재 항목과 대조한다.

## 기대 결과
근거: **REQ-N-024**(Must) 수용 기준 — *"Given **사용된 모든 이미지** When 라이선스 목록(`design/assets/SOURCES.md`)을 대조한다 Then **누락 0건**이고 모두 상업적 사용 가능 라이선스이며 지도 서비스 화면 캡처 0건"*

## 실제 결과
운영 이미지의 `/app/static/img/` 12개 중 아래 1건이 **산출물이 아니라 변환 작업용 중간 파일**이다.

```
og-image.TEMP-source.svg   2,998 B   2026-09-13 01:25
```

- 개발 보고서 v0.3 §7이 *"임시본 표시 4곳: 작업 사본 파일명 `og-image.TEMP-source.svg` …"* 로 설명한 파일이며, 화면·메타 태그에서 참조되지 않는다.
- `design/assets/SOURCES.md` 의 자산 표에는 이 파일명이 없다 → 대조 시 **"이미지에 있는데 목록에 없는 항목" 1건**.
- 부수 영향: 배포 산출물에 내부 작업 파일이 노출된다(정적 경로로 직접 접근 가능).

**함께 확인한 정상 항목(참고)**: 지도 서비스 화면 캡처 **0건**(지도 대체 영역은 CSS `repeating-linear-gradient`), 인물 스톡 사진 **0장**(`<img>` 태그 자체가 0건), 나머지 11개 자산은 `design/assets/SOURCES.md` 에 기재돼 있다.

## 증거
- `qa/evidence/cycle1/51_assets_sources.txt` (이미지 내 `/app/static/img/` 목록 + `SOURCES.md` 기재 항목)
- `qa/evidence/cycle1/33_prod_image_safety.txt` (운영 이미지 파일 구성)

## 비고
같은 성격으로 운영 이미지 루트에 `compose.yaml`·`compose.local.yaml`·`compose.prod.yaml`·`Dockerfile`·`requirements-dev.txt` 가 함께 들어 있다. 비밀 값은 없고(REQ-N-018 검색 0건) 보안 문제로 보지는 않으나, `.dockerignore` 정리 시 함께 검토하면 좋겠다.

---

## 조치 (developer 작성)
- 원인:
- 조치 내용:
- 수정 파일:
- 영향 범위 (회귀 테스트 필요 영역):
- 일자:

## 재검증 (qa 작성)
| 사이클 | 결과 (closed / reopened) | 일자 | 비고 |
|---|---|---|---|
| 2차 | | | 운영 이미지 재빌드 후 자산 목록 재대조 + `og:image` 200 응답 회귀 |
