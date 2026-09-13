"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
const OUT = "../evidence/cycle3/screenshots/";
const PAGES = [["/", "home"], ["/instructors", "instructors"], ["/location", "location"], ["/privacy", "privacy"], ["/nope", "nope"]];
(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  for (const [p, n] of PAGES)
    for (const w of [360, 1280]) {
      const pg = await b.newPage();
      await pg.setViewport({ width: w, height: 780, deviceScaleFactor: 1, isMobile: w < 768, hasTouch: w < 768 });
      await pg.goto(BASE + p, { waitUntil: "networkidle0", timeout: 30000 });
      await pg.screenshot({ path: OUT + n + "_" + w + ".png" });
      console.log("saved", n + "_" + w + ".png");
      await pg.close();
    }
  await b.close();
})();
