/* CMP-005 모바일 메뉴 — 마크업 정본은 <details>/<summary> 다.
   JS 역할은 딱 3가지: ① 열 때 첫 항목 포커스 ② Esc 닫기 + 트리거 복귀 ③ 배경 스크롤 잠금.
   상태 속성(aria-expanded)은 브라우저가 관리하므로 건드리지 않는다. */
(function () {
  "use strict";
  var details = document.querySelector(".mnav");
  if (!details) return;
  var summary = details.querySelector("summary");
  var panel = details.querySelector(".mpanel");

  details.addEventListener("toggle", function () {
    if (details.open) {
      document.body.style.overflow = "hidden";
      var first = panel && panel.querySelector("a");
      if (first) first.focus();
    } else {
      document.body.style.overflow = "";
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && details.open) {
      details.open = false;
      if (summary) summary.focus();
    }
  });

  document.addEventListener("click", function (event) {
    if (details.open && !details.contains(event.target)) details.open = false;
  });
})();
