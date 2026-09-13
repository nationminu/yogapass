/* 전 화면 공통 뷰포트 보정 (페이지 디자인 §2.5 · 디자인 시스템 §1.6 개발 주의 ②③)
   ① --fixed-bar-h · --header-h 를 ResizeObserver 로 실측 갱신한다.
      (텍스트 200% 확대로 고정 바 라벨·GNB 가 2줄이 되면 G-4 간격과 G-10 앵커 오프셋이 함께 깨진다)
   ② 바를 렌더하지 않는 구간(≥1280px, 400% 확대 조건)에서는 removeProperty 로 인라인 값을 되돌린다.
      인라인 스타일은 미디어 쿼리를 이기기 때문이다.
   ③ WebKit 가상 키보드 폴백(G-9 ②): visualViewport 변화 시 고정 바 위치를 보정한다.
      G-9 는 3단 구현이고 이 파일은 그중 ②만 담당한다 — ① 은 templates/base.html 의
      viewport 메타 `interactive-widget=resizes-content`(Chromium 경로), ③ 은 tokens.css 의
      scroll-padding-bottom 이다. 아래 `isWebKit` 가드는 ①이 있는 전제에서만 옳다(DEF-011). */
(function () {
  "use strict";
  var root = document.documentElement;
  var bar = document.querySelector(".barwrap");
  var header = document.querySelector(".hdr");
  var noBarQuery = window.matchMedia(
    "(min-width: 1280px), (max-height: 420px) and (max-width: 400px)"
  );

  function syncBar() {
    if (!bar) return;
    if (noBarQuery.matches) {
      root.style.removeProperty("--fixed-bar-h");
      return;
    }
    var height = Math.round(bar.getBoundingClientRect().height);
    if (height > 0) root.style.setProperty("--fixed-bar-h", height + "px");
  }

  /* --header-h 는 **앵커 오프셋(G-10)용 실측값**이다.
     헤더 행의 min-height 는 별도 토큰 --header-min-h 를 쓴다 — 같은 변수를 쓰면
     "실측 높이 → 변수 → min-height → 더 큰 높이" 되먹임으로 헤더가 계속 자란다. */
  function syncHeader() {
    if (!header) return;
    var height = Math.round(header.getBoundingClientRect().height);
    if (height > 0) root.style.setProperty("--header-h", height + "px");
  }

  function syncAll() { syncBar(); syncHeader(); }

  if (window.ResizeObserver) {
    var observer = new ResizeObserver(syncAll);
    if (bar) observer.observe(bar);
    if (header) observer.observe(header);
  }
  if (noBarQuery.addEventListener) noBarQuery.addEventListener("change", syncAll);
  window.addEventListener("resize", syncAll);
  syncAll();

  /* G-9 WebKit 폴백 — 가상 키보드가 뜨면 고정 바가 화면 밖으로 밀린다.
     관측 신호: <html data-vk-fallback="1"> (기술 설계 §10.5 ① 규격 — 검증 도구 ⑥ 가 이 값을 본다) */
  var vv = window.visualViewport;
  if (!vv || !bar) return;
  var isWebKit = /AppleWebKit/.test(navigator.userAgent) && !/Chrome|Chromium|Edg/.test(navigator.userAgent);
  if (!isWebKit) return;
  root.setAttribute("data-vk-fallback", "1");
  function follow() {
    if (noBarQuery.matches) { bar.style.transform = ""; return; }
    var offset = window.innerHeight - vv.height - vv.offsetTop;
    bar.style.transform = offset > 0 ? "translateY(-" + offset + "px)" : "";
  }
  vv.addEventListener("resize", follow);
  vv.addEventListener("scroll", follow);
})();
