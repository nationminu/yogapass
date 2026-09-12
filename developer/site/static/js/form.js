/* 문의 폼 — **점진적 향상 전용** (REQ-F-041·046 / REQ-N-030)
   JS 가 하는 일은 4가지뿐이고, 없어도 폼은 서버 렌더 경로로 그대로 동작한다.
     ① 글자 수 카운터(100자 단위로만 읽어 준다 — CMP-016)
     ② blur 이후 검증(입력 중 실시간 오류 금지 — REQ-F-041)
     ③ 제출 중 버튼 비활성 + "보내는 중…"(폭 고정, aria-busy)
     ④ 결과·오류 요약 블록으로 포커스 이동(autofocus 폴백을 보강)
   검증 문구는 서버(apps/inquiry/forms.py)와 같은 문자열을 쓴다. 판정의 정본은 서버다. */
(function () {
  "use strict";

  var MESSAGES = {
    name: { required: "이름을 입력해 주세요." },
    phone: {
      required: "휴대폰 번호를 입력해 주세요.",
      pattern: "휴대폰 번호 형식이 올바르지 않습니다. 예: 010-1234-5678"
    },
    message: { required: "문의 내용을 입력해 주세요." },
    consent: { required: "개인정보 수집·이용에 동의해 주세요." }
  };
  var PHONE_RE = /^01[016789]-?\d{3,4}-?\d{4}$/;
  // static/icons/alert-circle.svg 와 같은 도형 (Lucide, ISC)
  var ICON_ALERT =
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ' +
    'focusable="false"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>';

  // ---------------------------------------------------------------- ④ 포커스 이동
  var focusTarget = document.getElementById("contact-result") || document.getElementById("contact-errors");
  if (focusTarget && document.activeElement !== focusTarget) focusTarget.focus();

  var form = document.getElementById("contact-form");
  if (!form) return;

  // ---------------------------------------------------------------- ① 글자 수 카운터
  Array.prototype.forEach.call(form.querySelectorAll("[data-counter]"), function (field) {
    var counter = document.getElementById(field.getAttribute("data-counter"));
    if (!counter) return;
    var output = counter.querySelector("[data-count]");
    var max = parseInt(counter.getAttribute("data-max"), 10) || 0;
    var announced = -1;

    function sync() {
      var length = field.value.length;
      if (output) output.textContent = String(length);
      counter.classList.toggle("over", max > 0 && length > max);
      // 매 글자를 읽지 않도록 100자 단위에서만 라이브 영역을 갱신한다
      var bucket = Math.floor(length / 100);
      if (bucket === announced) {
        counter.setAttribute("aria-live", "off");
      } else {
        announced = bucket;
        counter.setAttribute("aria-live", "polite");
      }
    }
    field.addEventListener("input", sync);
    sync();
  });

  // ---------------------------------------------------------------- ② blur 이후 검증
  function messageFor(name, field) {
    var value = (field.type === "checkbox" ? (field.checked ? "on" : "") : field.value).trim();
    if (!value) return MESSAGES[name] ? MESSAGES[name].required : "필수 항목입니다.";
    if (name === "phone" && !PHONE_RE.test(value.replace(/\s/g, ""))) return MESSAGES.phone.pattern;
    return "";
  }

  function setError(field, text) {
    var name = field.name;
    var wrapper = field.closest(".field") || field.closest(".agree");
    var existing = document.getElementById("err-" + name);
    if (!text) {
      field.classList.remove("err");
      field.removeAttribute("aria-invalid");
      if (existing && existing.getAttribute("data-js") === "1") existing.remove();
      return;
    }
    field.classList.add("err");
    field.setAttribute("aria-invalid", "true");
    if (existing) {
      existing.lastChild.textContent = text;
      return;
    }
    var paragraph = document.createElement("p");
    paragraph.className = "errmsg";
    paragraph.id = "err-" + name;
    paragraph.setAttribute("data-js", "1");
    // 오류는 색만이 아니라 아이콘 + 문구로 전달한다(서버 렌더 오류와 같은 구성)
    paragraph.innerHTML = ICON_ALERT;
    paragraph.appendChild(document.createTextNode(text));
    if (!wrapper) return;
    if (wrapper.classList.contains("field")) {
      wrapper.appendChild(paragraph);
    } else if (wrapper.parentNode) {
      wrapper.parentNode.insertBefore(paragraph, wrapper.nextSibling);
    }
    var described = (field.getAttribute("aria-describedby") || "").split(" ").filter(Boolean);
    if (described.indexOf(paragraph.id) === -1) {
      described.push(paragraph.id);
      field.setAttribute("aria-describedby", described.join(" "));
    }
  }

  var touched = {};
  Array.prototype.forEach.call(form.querySelectorAll("[name]"), function (field) {
    if (!MESSAGES[field.name]) return;
    field.addEventListener("blur", function () {
      touched[field.name] = true;
      setError(field, messageFor(field.name, field));
    });
    field.addEventListener("input", function () {
      if (touched[field.name]) setError(field, messageFor(field.name, field));
    });
    field.addEventListener("change", function () {
      if (field.type === "checkbox") setError(field, messageFor(field.name, field));
    });
  });

  // ---------------------------------------------------------------- ③ 제출 중 상태
  form.addEventListener("submit", function (event) {
    var first = null;
    Array.prototype.forEach.call(form.querySelectorAll("[name]"), function (field) {
      if (!MESSAGES[field.name]) return;
      var text = messageFor(field.name, field);
      setError(field, text);
      if (text && !first) first = field;
    });
    if (first) {
      event.preventDefault();
      first.focus();
      return;
    }
    var button = form.querySelector("[data-submit]");
    if (!button || button.getAttribute("aria-busy") === "true") return;
    // 폭을 고정해 라벨이 바뀌어도 레이아웃이 움직이지 않게 한다
    button.style.minWidth = button.getBoundingClientRect().width + "px";
    button.setAttribute("aria-busy", "true");
    button.setAttribute("aria-disabled", "true");
    button.innerHTML = '<span class="spin" aria-hidden="true"></span>보내는 중…';
  });
})();
