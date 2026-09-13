/**
 * cycle3-probe.js — qa 자체 계측 (developer 도구와 독립)
 *  ① 런타임 DOM viewport 메타 토큰
 *  ② 가로 스크롤 (320/360/768/1280)
 *  ③ 고정 바 위치 — position/fixed 여부, 하단 밀착, 본문 하단 여백, 뷰포트 안 가시성
 *  ④ 콘솔 오류 — 출처 URL·문서 상태까지 함께 기록(자기404 분류를 qa가 직접 한다)
 * 사용: BASE=http://localhost:8001 NODE_PATH=./node_modules node cycle3-probe.js
 */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
const PAGES = ["/", "/instructors", "/location", "/privacy", "/nope"];
const VIEWPORTS = [320, 360, 768, 1280];

function measure() {
  const de = document.documentElement;
  const bar = document.querySelector(".barwrap");
  const br = bar ? bar.getBoundingClientRect() : null;
  const header = document.querySelector("header");
  return {
    viewport: (document.querySelector('meta[name="viewport"]') || {}).content || "",
    metaCount: document.querySelectorAll('meta[name="viewport"]').length,
    scrollWidth: de.scrollWidth,
    clientWidth: de.clientWidth,
    innerHeight: window.innerHeight,
    bodyPB: getComputedStyle(document.body).paddingBottom,
    scrollPadBottom: getComputedStyle(de).scrollPaddingBottom,
    bar: bar
      ? {
          pos: getComputedStyle(bar).position,
          top: Math.round(br.top),
          bottom: Math.round(br.bottom),
          height: Math.round(br.height),
          width: Math.round(br.width),
          zIndex: getComputedStyle(bar).zIndex,
        }
      : null,
    headerPos: header ? getComputedStyle(header).position : null,
    headerH: header ? Math.round(header.getBoundingClientRect().height) : 0,
  };
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
  });
  console.log("화면 | 뷰 | 메타토큰(개수) | scrollW/clientW | 고정바(pos,높이,bottom vs innerH) | body-pb | scroll-pad-b | 콘솔오류(자기404/기타)");
  let violations = 0;
  for (const path of PAGES) {
    for (const width of VIEWPORTS) {
      const page = await browser.newPage();
      const errs = [];
      page.on("console", (m) => {
        if (m.type() !== "error") return;
        errs.push({ text: m.text(), url: (m.location() && m.location().url) || "" });
      });
      page.on("pageerror", (e) => errs.push({ text: "pageerror: " + e.message, url: "(pageerror)" }));
      await page.setViewport({ width, height: 780, deviceScaleFactor: 1, isMobile: width < 768, hasTouch: width < 768 });
      const res = await page.goto(BASE + path, { waitUntil: "networkidle0", timeout: 30000 });
      const docUrl = res.url();
      const docStatus = res.status();
      const m = await page.evaluate(measure);
      // 문서 자신의 404 와 그 밖의 오류를 qa 가 직접 분류한다
      const self404 = errs.filter((e) => docStatus === 404 && e.url === docUrl && /404/.test(e.text));
      const other = errs.filter((e) => !(docStatus === 404 && e.url === docUrl && /404/.test(e.text)));
      const problems = [];
      if (!m.viewport.includes("interactive-widget=resizes-content")) problems.push("메타누락");
      if (m.metaCount !== 1) problems.push("메타" + m.metaCount + "개");
      if (m.scrollWidth > m.clientWidth + 1) problems.push("가로스크롤");
      if (m.bar) {
        if (m.bar.pos !== "fixed" && width < 1280) problems.push("바position=" + m.bar.pos);
        if (width < 1280 && Math.abs(m.bar.bottom - m.innerHeight) > 1) problems.push("바하단이탈");
      }
      if (other.length) problems.push("콘솔오류");
      if (problems.length) violations += 1;
      console.log(
        [
          path,
          width + "px",
          (m.viewport.includes("interactive-widget=resizes-content") ? "있음" : "★없음") + "(" + m.metaCount + ")",
          m.scrollWidth + "/" + m.clientWidth,
          m.bar ? m.bar.pos + "," + m.bar.height + "px,bottom=" + m.bar.bottom + " vs " + m.innerHeight : "바없음",
          m.bodyPB,
          m.scrollPadBottom,
          self404.length + "/" + other.length + (other.length ? " :: " + other[0].text.slice(0, 90) : ""),
        ].join(" | ") + (problems.length ? "   ← " + problems.join(",") : "")
      );
      await page.close();
    }
  }
  console.log(violations === 0 ? "\n✓ qa 자체 계측 위반 0건" : "\n★ 위반 " + violations + "건");
  await browser.close();
  process.exit(violations === 0 ? 0 : 1);
})();
