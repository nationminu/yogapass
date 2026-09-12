/* SCR-003 지도 — 클릭 투 로드 (REQ-F-030·031·032) + 주소 복사 토스트(CMP-021, REQ-F-034)
   · 버튼을 누르기 전에는 지도 서비스 도메인으로 요청이 0건이다.
   · 대체 영역과 iframe 의 높이가 같아서(.map 의 --map-h) 로드 전후 레이아웃 이동이 없다.
   · 로드 후 포커스는 iframe 이 아니라 지도 섹션 제목으로 옮긴다(페이지 디자인 §4.1).
   · JS 가 없으면 이 파일이 하는 일은 전부 일어나지 않는다 — 주소·교통 정보는 서버 렌더 HTML 에 이미 있다. */
(function () {
  "use strict";

  // ---------------------------------------------------------------- 클릭 투 로드
  var frame = document.getElementById("map-frame");
  var button = frame && frame.querySelector("[data-map-load]");
  if (frame && button) {
    button.addEventListener("click", function () {
      var src = frame.getAttribute("data-map-src");
      if (!src) return;
      var iframe = document.createElement("iframe");
      iframe.src = src;
      iframe.title = frame.getAttribute("data-map-title") || "위치 지도";
      iframe.loading = "lazy";
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      frame.innerHTML = "";
      frame.appendChild(iframe);
      var heading = document.getElementById("map-title");
      if (heading) heading.focus();
    });
  }

  // ---------------------------------------------------------------- 주소 복사 + 토스트
  var copyButtons = document.querySelectorAll("[data-copy]");
  if (!copyButtons.length) return;

  var toast = null;
  var timer = null;

  function showToast(message) {
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "toast";
      toast.setAttribute("role", "status");
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    // 강제 리플로우 후 클래스 추가 — 등장 전환이 첫 호출에서도 동작하게 한다
    void toast.offsetWidth;
    toast.classList.add("on");
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      toast.classList.remove("on");
    }, 3000);
  }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // 보안 컨텍스트가 아니면(예: http 로 연 스테이징) 폴백
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "absolute";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (error) {
      ok = false;
    }
    document.body.removeChild(area);
    return ok ? Promise.resolve() : Promise.reject(new Error("copy failed"));
  }

  Array.prototype.forEach.call(copyButtons, function (element) {
    element.addEventListener("click", function () {
      copy(element.getAttribute("data-copy") || "").then(
        function () {
          showToast("주소를 복사했습니다");
        },
        function () {
          showToast("주소를 복사하지 못했습니다. 직접 선택해 복사해 주세요");
        }
      );
    });
  });
})();
