/** 보충: 1280px 푸터 열 간 가로 간격 + hover/focus 시각 구분(ⓓ) 실측 */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  for (const width of [360, 768, 1280]) {
    const page = await browser.newPage();
    await page.setViewport({ width, height: 900, deviceScaleFactor: 1, isMobile: width < 768, hasTouch: width < 768 });
    await page.goto(BASE + "/", { waitUntil: "networkidle0", timeout: 30000 });
    const boxes = await page.evaluate(() => {
      const f = document.querySelector("footer");
      return [...f.querySelectorAll("a")].map((a) => {
        const r = a.getBoundingClientRect();
        return { t: a.textContent.trim().slice(0, 18), x: Math.round(r.x * 10) / 10, right: Math.round(r.right * 10) / 10, top: Math.round(r.top * 10) / 10, bottom: Math.round(r.bottom * 10) / 10 };
      });
    });
    console.log(`\n=== ${width}px — 푸터 링크 사각형 ===`);
    boxes.forEach((b) => console.log(`  "${b.t}" x=${b.x}~${b.right}  y=${b.top}~${b.bottom}`));
    // 가로로 겹치는(세로 범위가 겹치는) 쌍의 가로 간격
    console.log("  [세로 범위가 겹치는 = 가로로 나란한 쌍의 가로 간격]");
    let found = 0;
    for (let i = 0; i < boxes.length; i++)
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.top < b.bottom - 1 && b.top < a.bottom - 1) {
          const gap = Math.round((Math.max(a.x, b.x) - Math.min(a.right, b.right)) * 10) / 10;
          console.log(`    "${a.t}" ↔ "${b.t}" 가로 간격 = ${gap}px ${gap >= 8 ? "(8px 이상 충족)" : "★8px 미만"}`);
          found++;
        }
      }
    if (!found) console.log("    없음 (모든 링크가 세로로만 이어짐)");
    // ⓓ hover / focus 시각 구분
    const vis = await page.evaluate(async () => {
      const a = [...document.querySelectorAll("footer a")].find((x) => x.textContent.trim() === "홈");
      const base = getComputedStyle(a);
      const snap = (st) => ({ td: st.textDecorationLine, outline: st.outlineWidth + " " + st.outlineStyle, bg: st.backgroundColor, color: st.color });
      const before = snap(base);
      a.focus();
      const focused = snap(getComputedStyle(a));
      return { before, focused, activeIsLink: document.activeElement === a };
    });
    console.log("  [ⓓ 시각 구분] 기본:", JSON.stringify(vis.before));
    console.log("                포커스:", JSON.stringify(vis.focused), "focus 적용=", vis.activeIsLink);
    await page.close();
  }
  await browser.close();
})();
