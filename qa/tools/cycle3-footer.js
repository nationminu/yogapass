/** cycle3-footer.js — REQ-N-006 ②-3 세로 목록형 인접 타깃 예외 실측 (v1.2 재판정)
 *  확인 항목 ① 각 타깃 실측 크기 ② 타깃 사이에 어느 타깃에도 속하지 않는 간극 ③ 목록 블록 ↔ 바깥 조작 요소 8px
 *  조건 ⓐ 세로 1방향 ⓑ 컨테이너 가로 폭 전체 ⓒ 44px 빈틈없이 ⓓ 구분선·hover·focus 구분
 */
"use strict";
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.BASE || "http://localhost:8001";
const VIEWPORTS = [360, 768, 1280];

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  for (const width of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport({ width, height: 900, deviceScaleFactor: 1, isMobile: width < 768, hasTouch: width < 768 });
    await page.goto(BASE + "/", { waitUntil: "networkidle0", timeout: 30000 });
    const r = await page.evaluate(() => {
      const out = { groups: [], outside: [] };
      const footer = document.querySelector("footer");
      // 푸터 안의 링크를 "직계 부모(목록 블록)" 단위로 묶는다
      const links = [...footer.querySelectorAll("a")];
      const byParent = new Map();
      for (const a of links) {
        const p = a.parentElement;
        if (!byParent.has(p)) byParent.set(p, []);
        byParent.get(p).push(a);
      }
      for (const [parent, items] of byParent) {
        const pr = parent.getBoundingClientRect();
        const rows = items.map((a) => {
          const rc = a.getBoundingClientRect();
          const st = getComputedStyle(a);
          return {
            text: a.textContent.trim().slice(0, 20),
            x: Math.round(rc.x), y: Math.round(rc.y),
            w: Math.round(rc.width * 10) / 10, h: Math.round(rc.height * 10) / 10,
            top: Math.round(rc.top * 10) / 10, bottom: Math.round(rc.bottom * 10) / 10,
            display: st.display,
            borderBottom: st.borderBottomWidth + " " + st.borderBottomStyle,
            textDecoration: st.textDecorationLine,
          };
        });
        rows.sort((a, b) => a.top - b.top);
        // 세로 인접 간극 (앞 요소 bottom ↔ 다음 요소 top)
        const gaps = [];
        for (let i = 1; i < rows.length; i++) gaps.push(Math.round((rows[i].top - rows[i - 1].bottom) * 10) / 10);
        // 가로로 나란한 쌍이 있는가 (세로 1방향 조건 ⓐ)
        let sideBySide = 0;
        for (let i = 0; i < rows.length; i++)
          for (let j = i + 1; j < rows.length; j++)
            if (rows[i].top < rows[j].bottom - 1 && rows[j].top < rows[i].bottom - 1) sideBySide += 1;
        out.groups.push({
          parent: parent.tagName.toLowerCase() + (parent.className ? "." + String(parent.className).trim().split(/\s+/)[0] : ""),
          parentWidth: Math.round(pr.width * 10) / 10,
          parentTop: Math.round(pr.top * 10) / 10,
          parentBottom: Math.round(pr.bottom * 10) / 10,
          rows, gaps, sideBySide,
        });
      }
      // 목록 블록 바깥의 조작 요소 (푸터 안 다른 링크/버튼 그룹 + 푸터 바로 앞뒤 조작 요소)
      const fr = footer.getBoundingClientRect();
      const all = [...document.querySelectorAll("a,button,input,select,textarea")].filter((el) => {
        const rc = el.getBoundingClientRect();
        return rc.height > 0 && rc.bottom > fr.top - 300;
      });
      out.outside = all.map((el) => {
        const rc = el.getBoundingClientRect();
        return { tag: el.tagName.toLowerCase(), text: (el.textContent || "").trim().slice(0, 18), top: Math.round(rc.top), bottom: Math.round(rc.bottom), h: Math.round(rc.height), inFooter: footer.contains(el) };
      });
      return out;
    });
    console.log("\n================ 뷰포트 " + width + "px ================");
    for (const g of r.groups) {
      console.log(`[목록 블록] ${g.parent}  폭=${g.parentWidth}px  범위 top=${g.parentTop}~${g.parentBottom}`);
      for (const row of g.rows)
        console.log(`   · "${row.text}" ${row.w}x${row.h}  top=${row.top} bottom=${row.bottom}  display=${row.display}  border-bottom=${row.borderBottom}  text-decoration=${row.textDecoration}`);
      console.log(`   세로 인접 간극: [${g.gaps.join(", ")}]   가로로 나란한 쌍: ${g.sideBySide}건   블록 폭 대비 타깃 폭: ${g.rows.map((x) => (x.w === g.parentWidth ? "전체" : x.w + "/" + g.parentWidth)).join(", ")}`);
      const minH = Math.min(...g.rows.map((x) => x.h));
      console.log(`   최소 타깃 높이 = ${minH}px  → 44px 기준 ${minH >= 44 ? "충족" : "★미달"} / 간극 0px(맞닿음) ${g.gaps.every((x) => x === 0) ? "예" : "아니오"}`);
    }
    console.log("[푸터 주변 조작 요소 목록] (블록↔바깥 간격 8px 확인용)");
    for (const o of r.outside) console.log(`   ${o.inFooter ? "푸터내" : "푸터밖"} <${o.tag}> "${o.text}" top=${o.top} bottom=${o.bottom} h=${o.h}`);
    await page.close();
  }
  await browser.close();
})();
