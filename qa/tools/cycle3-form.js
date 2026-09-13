/** 핵심 전환 동선 스모크: /location#contact 문의 폼 1건 정상 접수 (viewport 메타 변경 후 회귀) */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8000";
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  const pg = await b.newPage();
  await pg.setViewport({ width: 360, height: 780, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  await pg.goto(BASE + "/location#contact", { waitUntil: "networkidle0", timeout: 30000 });
  console.log("meta:", await pg.evaluate(() => document.querySelector('meta[name="viewport"]').content));
  const fields = await pg.evaluate(() => [...document.querySelectorAll("form input, form textarea, form select")].map((e) => e.name + "(" + e.type + ")"));
  console.log("폼 필드:", fields.join(", "));
  await pg.type('input[name="name"]', "TEST-cycle3");
  await pg.type('input[name="phone"]', "010-1234-5678");
  await pg.type('textarea[name="message"]', "TEST-cycle3 문의 본문입니다. 회귀 확인용.");
  await pg.evaluate(() => { const c = document.querySelector('input[type="checkbox"][name="consent"]'); if (c) c.click(); });
  await Promise.all([
    pg.waitForNavigation({ waitUntil: "networkidle0", timeout: 30000 }),
    pg.evaluate(() => document.querySelector('form button[type="submit"], form input[type="submit"]').click()),
  ]);
  const r = await pg.evaluate(() => {
    const status = document.querySelector('[role="status"]');
    const alert = document.querySelector('[role="alert"]');
    return {
      url: location.href,
      status: status ? status.textContent.replace(/\s+/g, " ").trim().slice(0, 120) : null,
      alert: alert ? alert.textContent.replace(/\s+/g, " ").trim().slice(0, 120) : null,
      meta: document.querySelector('meta[name="viewport"]').content,
    };
  });
  console.log("결과 URL:", r.url);
  console.log("role=status:", r.status);
  console.log("role=alert :", r.alert);
  console.log("제출 후 meta:", r.meta);
  await b.close();
})();
