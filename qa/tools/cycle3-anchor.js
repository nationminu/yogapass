/** cycle3-anchor.js — 앵커 이동 회귀 (#contact · #map) · viewport 메타 변경 영향 확인 */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
const CASES = [["/location#contact", "contact"], ["/location#map", "map"]];
const VIEWPORTS = [320, 360, 768, 1280];

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  console.log("URL | 뷰 | 헤더(pos,h) | 대상 top | 헤더 아래 여유 | 스크롤Y | 고정바 | 판정");
  let bad = 0;
  for (const [url, id] of CASES) {
    for (const width of VIEWPORTS) {
      const page = await browser.newPage();
      await page.setViewport({ width, height: 780, deviceScaleFactor: 1, isMobile: width < 768, hasTouch: width < 768 });
      await page.goto(BASE + url, { waitUntil: "networkidle0", timeout: 30000 });
      await new Promise((r) => setTimeout(r, 400));
      const r = await page.evaluate((id) => {
        const el = document.getElementById(id);
        const header = document.querySelector("header");
        const bar = document.querySelector(".barwrap");
        const hr = header ? header.getBoundingClientRect() : null;
        const er = el ? el.getBoundingClientRect() : null;
        const bar_r = bar ? bar.getBoundingClientRect() : null;
        return {
          found: !!el,
          headerPos: header ? getComputedStyle(header).position : null,
          headerBottom: hr ? Math.round(hr.bottom) : 0,
          top: er ? Math.round(er.top) : null,
          scrollY: Math.round(window.scrollY),
          scrollMarginTop: el ? getComputedStyle(el).scrollMarginTop : null,
          barTop: bar_r && bar_r.height > 0 ? Math.round(bar_r.top) : null,
          innerHeight: window.innerHeight,
        };
      }, id);
      const clearance = r.top === null ? null : r.top - r.headerBottom;
      const ok = r.found && clearance !== null && clearance >= 0;
      if (!ok) bad += 1;
      console.log([url, width + "px", r.headerPos + "," + r.headerBottom, r.top, clearance, r.scrollY, r.barTop === null ? "없음/숨김" : "top=" + r.barTop + "/" + r.innerHeight, ok ? "OK(헤더에 가리지 않음)" : "★가림"].join(" | ") + "  scroll-margin-top=" + r.scrollMarginTop);
      await page.close();
    }
  }
  console.log(bad === 0 ? "\n✓ 앵커 이동 위반 0건" : "\n★ 위반 " + bad + "건");
  await browser.close();
})();
