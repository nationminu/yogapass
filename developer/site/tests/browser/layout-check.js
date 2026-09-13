/**
 * 레이아웃 회귀 점검 (DEF-003 · DEF-004 · DEF-005)
 *
 * Django 테스트로는 잡을 수 없는 것 — **실제 렌더 결과**를 잰다.
 *   ① 가로 스크롤 0건 (320 / 360 / 768 / 1280px)   REQ-N-006 ⑤ · REQ-N-001
 *   ② 조작 요소 터치 타깃 44×44px 이상              REQ-N-006 ②
 *   ③ 문장 글꼴 14px 이상                           REQ-N-006 ⑤ · 디자인 시스템 §타이포
 *   ④ 콘솔 오류 0건 (CSP 차단 포함)                  REQ-N-015
 *   ⑤ 헤더 높이가 재측정으로 커지지 않는지            (viewport.js 되먹임 회귀)
 *
 * 실행 (developer/site 에서):
 *   BASE=http://localhost:8000 \
 *   NODE_PATH=../../qa/tools/node_modules \
 *   CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe" \
 *   node tests/browser/layout-check.js
 *
 * puppeteer-core·Chrome 은 저장소에 두지 않는다(검증 도구는 qa 소관). 없으면 안내하고 종료한다.
 * 종료 코드: 위반 0건이면 0, 1건 이상이면 1.
 */
"use strict";

let puppeteer;
try {
  puppeteer = require("puppeteer-core");
} catch (error) {
  console.error(
    "puppeteer-core 를 찾을 수 없습니다. NODE_PATH 로 위치를 알려주십시오.\n" +
      "  예) NODE_PATH=../../qa/tools/node_modules node tests/browser/layout-check.js"
  );
  process.exit(2);
}

const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8000";
const PAGES = ["/", "/instructors", "/location", "/privacy", "/nope"];
const VIEWPORTS = [320, 360, 768, 1280];
/**
 * 크기 판정에서 빼는 것 (qa 1차 판정과 같은 기준 — DEF-005 티켓의 제외 목록)
 *   · 문단 안 인라인 링크          WCAG 2.5.5 인라인 예외
 *   · 화면 밖에 둔 요소            skip link(포커스 시 48px) · honeypot 필드
 *   · 체크박스 input               클릭 영역은 감싸는 label(행 전체 44px 이상)이다
 */
function measure() {
  const de = document.documentElement;
  const clientWidth = de.clientWidth;
  const visible = (el) => {
    const st = getComputedStyle(el);
    if (st.display === "none" || st.visibility === "hidden") return false;
    const rc = el.getBoundingClientRect();
    return rc.width > 0 || rc.height > 0;
  };
  const name = (el) =>
    el.tagName.toLowerCase() +
    (typeof el.className === "string" && el.className
      ? "." + el.className.trim().split(/\s+/)[0]
      : "");

  const offscreen = (rc) => rc.right < 0 || rc.bottom < 0;
  /** 시각적으로 감춘 영역(.visually-hidden · clip 한 thead) 안의 요소는 레이아웃 판정 대상이 아니다. */
  const clipped = (el) => {
    for (let node = el; node && node !== document.body; node = node.parentElement) {
      const st = getComputedStyle(node);
      if (st.clip && st.clip !== "auto") return true;
      const rc = node.getBoundingClientRect();
      if (rc.width <= 1 && rc.height <= 1) return true;
    }
    return false;
  };

  const overflow = [];
  document.querySelectorAll("body *").forEach((el) => {
    if (!visible(el)) return;
    const rc = el.getBoundingClientRect();
    if (offscreen(rc) || clipped(el)) return;
    if (rc.right > clientWidth + 1) {
      overflow.push(name(el) + " [" + Math.round(rc.left) + "," + Math.round(rc.right) + "]");
    }
  });

  const inline = new Set(document.querySelectorAll("p a, li a, dd a"));
  const small = [];
  document.querySelectorAll("a,button,input,select,textarea,summary").forEach((el) => {
    if (!visible(el) || inline.has(el)) return;
    if (el.type === "checkbox" && [...(el.labels || [])].some((l) => l.getBoundingClientRect().height >= 44)) return;
    const rc = el.getBoundingClientRect();
    if (offscreen(rc) || clipped(el)) return;
    if (rc.width < 44 || rc.height < 44) {
      small.push(name(el) + " " + Math.round(rc.width) + "x" + Math.round(rc.height));
    }
  });

  const tinyText = [];
  document.querySelectorAll("body *").forEach((el) => {
    if (!visible(el) || el.children.length || !el.textContent.trim()) return;
    const size = parseFloat(getComputedStyle(el).fontSize);
    // eyebrow(12.5px)는 디자인 시스템이 명시한 예외, SVG 안의 텍스트는 그래픽이다.
    if (size < 14 && !el.classList.contains("eyebrow") && !el.closest("svg")) {
      tinyText.push(name(el) + " " + size + "px");
    }
  });

  const header = document.querySelector(".hdr");
  return {
    scrollWidth: de.scrollWidth,
    clientWidth,
    overflow: [...new Set(overflow)],
    small: [...new Set(small)],
    tinyText: [...new Set(tinyText)],
    // 서버가 내려준 인라인 style 속성만 센다. viewport.js 가 <html>·.barwrap 에 거는 것은
    // CSSOM 조작이라 CSP 대상이 아니다(요소 자체가 JS 관리 대상임을 알 수 있게 따로 표시한다).
    inlineStyle: [...document.querySelectorAll("body [style]")].filter(
      (el) => !el.classList.contains("barwrap")
    ).length,
    headerHeight: header ? Math.round(header.getBoundingClientRect().height) : 0,
    bodyPaddingBottom: getComputedStyle(document.body).paddingBottom,
    hasFixedBar: !!document.querySelector(".barwrap"),
  };
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
  });
  let violations = 0;
  console.log("화면 | 뷰포트 | 가로스크롤 | 넘침 | 작은타깃 | 작은글꼴 | 인라인style | 콘솔 | 헤더h | body-pb(고정바)");
  for (const path of PAGES) {
    for (const width of VIEWPORTS) {
      const page = await browser.newPage();
      const errors = [];
      page.on("console", (m) => m.type() === "error" && errors.push(m.text().slice(0, 100)));
      page.on("pageerror", (e) => errors.push("pageerror: " + e.message.slice(0, 100)));
      await page.setViewport({
        width,
        height: 780,
        deviceScaleFactor: 1,
        isMobile: width < 768,
        hasTouch: width < 768,
      });
      await page.goto(BASE + path, { waitUntil: "networkidle0", timeout: 30000 });
      const first = await page.evaluate(measure);
      // ⑤ 재측정 — viewport.js 의 ResizeObserver 가 헤더를 계속 키우지 않는지 본다
      await page.setViewport({ width, height: 781, deviceScaleFactor: 1 });
      await new Promise((r) => setTimeout(r, 250));
      const again = await page.evaluate(measure);

      const problems = [];
      if (first.scrollWidth > first.clientWidth + 1) problems.push("가로스크롤");
      if (first.small.length) problems.push("작은타깃");
      if (first.tinyText.length) problems.push("작은글꼴");
      if (first.inlineStyle) problems.push("인라인style");
      if (errors.length) problems.push("콘솔오류");
      if (again.headerHeight > first.headerHeight) problems.push("헤더높이증가");
      if (!first.hasFixedBar && first.bodyPaddingBottom !== "0px") problems.push("고정바없는데하단여백");
      if (problems.length) violations += 1;

      console.log(
        [
          path,
          width + "px",
          first.scrollWidth > first.clientWidth + 1
            ? "있음 " + first.scrollWidth + "/" + first.clientWidth
            : "없음",
          first.overflow.join(" ; ") || "0건",
          first.small.join(" ; ") || "0건",
          first.tinyText.join(" ; ") || "0건",
          first.inlineStyle + "건",
          errors.length ? errors.length + "건: " + errors[0] : "0건",
          first.headerHeight + "→" + again.headerHeight,
          first.bodyPaddingBottom + (first.hasFixedBar ? "(바 있음)" : "(바 없음)"),
        ].join(" | ") + (problems.length ? "   ← " + problems.join(",") : "")
      );
      await page.close();
    }
  }
  await browser.close();
  console.log(violations ? `\n✗ 위반 ${violations}건` : "\n✓ 위반 0건");
  process.exit(violations ? 1 : 0);
})();
