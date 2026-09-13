# P5 1차 사이클 실행 증거 — 2026-09-13

대상: `developer/site/` (개발 보고서 v0.3) · 판정 문서: `qa/05_test-cases.md` · `qa/05_test-report.md`
모든 명령은 `developer/site/` 또는 `qa/tools/` 에서 실행했고 **소스는 수정하지 않았다**.

| 파일 | 내용 | 관련 TC / DEF |
|---|---|---|
| `00_compose_ps.txt` · `01_req-n-034_down_up.txt` | `down` → `up -d`(플래그 없이) 5서비스 healthy + `backup` 1회성 | TC-126 (REQ-N-034) |
| `02_http_status.txt` | 앱 직접·nginx 경유 10경로 상태 코드 | TC-012·080 |
| `03_meta_landmarks.txt` | title·description·canonical·OG·랜드마크·h1 | TC-001·102·105·106 |
| `04_tbd_scan.txt` | M-5 `[TBD]` 패턴 스캔 | TC-070·115 |
| `05_qa_tools_gate.txt` · `17b_recheck_direct.txt` | 검증 도구 마스터 스위치(종료 코드 2) · `check_release` · `qa_pii_columns` | TC-131·115·112 |
| `06_form_matrix.txt` · `07_form_token_reuse.txt` | 폼 응답 ①②③⑤⑦ curl 재현 | TC-052·054·057·058·059 |
| `08_db_counts.txt` · `09_inquiry_logs.txt` | `qa_show`·`qa_mail_log` 건수 · `key=value` 로그 | TC-052·054·057·058 |
| `10~11`, `14_rate_limit*` | 빈도 제한 429 + `Retry-After` + 창 경과 복귀 | TC-055 |
| `12b_error500_post.txt` | ⑥ 서버 오류 500 + `errors/500.html` | TC-060·085 |
| `13_clock_offset.txt` | `QA_CLOCK_OFFSET_SECONDS` 동작 · 토큰 만료 미적용 | TC-059 / **DEF-008** |
| `15_concurrency.txt` | 동시 이중 제출 200×5 · 저장 1건 | TC-058 |
| `16*_usage_alert*` | 사용량 알림 `rate_limit_alert` 1건 | TC-056 |
| `18_a11y_markup.txt` · `38_contrast.txt` · `43_a11y_detail.txt` · `45_focus_tab.txt` | 접근성 마크업·대비 18조합·터치 타깃·Tab 순회 | TC-095~101 / **DEF-005** |
| `19_links_*` · `20_jsonld*` | 링크 25/25 200 · 앵커 id · JSON-LD | TC-012·104 |
| `21_secret_scan.txt` · `34_prod_image_safety2.txt` | M-4 비밀 정보 패턴(저장소·이미지 레이어) | TC-110 |
| `22~28` | 백업·실패 주입·**복구 리허설**·파기·일일 요약·헬스 폴링 | TC-123·124·127·128 |
| `29_deploy.txt` · `30_rollback_defect.txt` | 배포 0단계 차단 · 롤백 가드 | TC-125 / **DEF-007** |
| `31~36` | 운영 이미지 빌드·안전장치 5중·운영 미리보기 기동·정적 파이프라인 | TC-131·126 |
| `37_req_1st_list.tsv` | 요구사항 `차수` 열 기계 집계 = 96건(Must 60) | RTM 커버리지 |
| `39_lighthouse_mobile_summary.txt` + `lighthouse-mobile/` | **M-1 판정용** 모바일 3회 중앙값 | TC-093·099·107 |
| `32_lighthouse_desktop_summary.txt` | (참고) desktop 프리셋 — M-1 불일치라 판정에 쓰지 않음 | — |
| `40_console_errors.txt` · `41_inline_style.txt` | CSP 인라인 스타일 차단 · 콘솔 오류 2건 | **DEF-003** |
| `42_viewport.txt` + `screenshots/` | 320/360/768/1280 실제 렌더 · 가로 스크롤 · 넘침 | TC-090·098 / **DEF-004** |
| `44_fixedbar_focus_nojs.txt` · `48_fixedbar_phone_confirmed.txt` | 고정 바·헤더 CTA 분기(전화 미확정/확정) · JS 비활성 | TC-003~007·120 / **DEF-006** |
| `46_content_change.txt` · `47_instructors.txt` | 데이터 파일 변경 → 3곳 반영 · 강사 경계값 | TC-084·030~033 |
| `49_meta_vs_ia.txt` | title·description ↔ IA §6.2·§6.3 대조 | TC-102·103 / **DEF-001** |
| `50_html_validate.txt` + `html/` | Nu Html Checker(vnu) 검사 — 오류 5건 | TC-108 / **DEF-002** |
| `51_assets_sources.txt` | 이미지 자산 ↔ `SOURCES.md` · WebKit 체크리스트 | TC-116 / **DEF-010** |
| `52_unit_tests.txt` | 개발팀 자동 테스트 53건 qa 재실행 | 전반 |
| `53_nginx_502.txt` | nginx 502 정적 점검 화면 | TC-085 |
| `54_purge_testdata.txt` · `55_teardown.txt` | 테스트 데이터 전량 삭제(최종 0건) · 임시 자원 정리 | 종료 기준 |
| `56_form_js.txt` · `57_result_focus.txt` | blur 검증·제출 포커스 이동·결과 블록 포커스 | TC-051·061 |
| `pages/` | 판정에 사용한 렌더 HTML 원본 | — |

`qa/tools/` 에 설치한 도구: `puppeteer-core`(기존 Chrome 사용) · `vnu-jar`(Nu Html Checker). 스크립트 5개(`viewport-check.js` · `a11y-detail.js` · `probe2~5.js`).
