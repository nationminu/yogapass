/** cycle3-fixedbar.js — /location 고정 바 렌더 상태에서의 회귀 (G-3·G-4·앵커) */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
const VIEWPORTS = [320, 360, 768, 1280];
(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  for (const width of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport({ width, height: 780, deviceScaleFactor: 1, isMobile: width < 768, hasTouch: width < 768 });
    await page.goto(BASE + "/location#contact", { waitUntil: "networkidle0", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 400));
    const r = await page.evaluate(() => {
      const de = document.documentElement;
      const bar = document.querySelector(".barwrap");
      const br = bar ? bar.getBoundingClientRect() : null;
      const header = document.querySelector("header");
      const hb = header ? Math.round(header.getBoundingClientRect().bottom) : 0;
      const contact = document.getElementById("contact");
      const cr = contact ? contact.getBoundingClientRect() : null;
      const submit = document.querySelector('form button[type="submit"], form input[type="submit"]');
      return {
        meta: (document.querySelector('meta[name="viewport"]') || {}).content || "",
        fixedAttr: document.body.getAttribute("data-fixed-bar") || de.getAttribute("data-fixed-bar"),
        barExists: !!bar,
        barVisible: br ? br.height > 0 : false,
        barPos: bar ? getComputedStyle(bar).position : null,
        barRect: br ? { top: Math.round(br.top), bottom: Math.round(br.bottom), h: Math.round(br.height) } : null,
        innerHeight: window.innerHeight,
        bodyPB: getComputedStyle(document.body).paddingBottom,
        barBtns: [...document.querySelectorAll(".barwrap a, .barwrap button")].map((a) => {
          const q = a.getBoundingClientRect();
          return a.textContent.trim() + "[" + (a.getAttribute("href") || "") + "] " + Math.round(q.width) + "x" + Math.round(q.height);
        }),
        headerBottom: hb,
        contactTop: cr ? Math.round(cr.top) : null,
        scrollWidth: de.scrollWidth,
        clientWidth: de.clientWidth,
        submitText: submit ? submit.textContent.trim() : null,
      };
    });
    // 문서 끝까지 스크롤 후 제출 버튼과 고정 바 간격 (G-4 16px 이상)
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await new Promise((r) => setTimeout(r, 400));
    const g4 = await page.evaluate(() => {
      const submit = document.querySelector('form button[type="submit"], form input[type="submit"]');
      const bar = document.querySelector(".barwrap");
      if (!submit) return { gap: null, note: "제출 버튼 없음" };
      const sr = submit.getBoundingClientRect();
      const br = bar ? bar.getBoundingClientRect() : null;
      return {
        submitBottom: Math.round(sr.bottom),
        barTop: br && br.height > 0 ? Math.round(br.top) : null,
        gap: br && br.height > 0 ? Math.round(br.top - sr.bottom) : Math.round(window.innerHeight - sr.bottom),
        innerHeight: window.innerHeight,
      };
    });
    console.log(
      `${String(width).padStart(4)}px  meta토큰=${r.meta.includes("interactive-widget=resizes-content") ? "있음" : "★없음"}  data-fixed-bar=${r.fixedAttr}  barwrap=${r.barExists ? (r.barVisible ? "있음/표시" : "있음/미표시") : "없음"}  pos=${r.barPos}  rect=${JSON.stringify(r.barRect)} vs innerH=${r.innerHeight}  body-pb=${r.bodyPB}  가로스크롤=${r.scrollWidth > r.clientWidth + 1 ? "★있음 " + r.scrollWidth + "/" + r.clientWidth : "없음"}`
    );
    console.log(`        고정 바 버튼: ${r.barBtns.join(" ; ") || "-"}`);
    console.log(`        #contact top=${r.contactTop} (헤더 bottom=${r.headerBottom}, 여유=${r.contactTop - r.headerBottom})`);
    console.log(`        G-4 문서 끝 스크롤: 제출버튼 bottom=${g4.submitBottom} 고정바 top=${g4.barTop} 간격=${g4.gap}px (기준 16px 이상)`);
    await page.close();
  }
  await browser.close();
})();
