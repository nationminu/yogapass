const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu','--hide-scrollbars']});
 for(const w of [320,360,768,1280]){
  const p=await b.newPage(); await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
  await p.goto('http://localhost:8001/location',{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const vis=e=>{if(!e)return false;const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getBoundingClientRect().height>0;};
   const wrap=document.querySelector('.barwrap');
   const btns=wrap?[...wrap.querySelectorAll('a,button')].filter(vis).map(e=>e.textContent.trim().replace(/\s+/g,' ')+'['+e.getAttribute('href')+'] '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height)):[];
   const hcta=[...document.querySelectorAll('.hdr .hdr-cta')].filter(vis).map(e=>e.textContent.trim()+'['+e.getAttribute('href')+'] aria-current='+e.getAttribute('aria-current'));
   return {dfb:document.documentElement.getAttribute('data-fixed-bar'), wrapDom:!!wrap, barVis:vis(wrap), btns, hcta,
     pb:getComputedStyle(document.body).paddingBottom, sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth,
     gnbCur:[...document.querySelectorAll('nav a[aria-current="page"]')].map(e=>e.textContent.trim())};
  });
  console.log(`  ${String(w).padStart(4)}px  data-fixed-bar=${r.dfb}  .barwrap=${r.wrapDom?'있음':'없음'}/${r.barVis?'표시':'미표시'}  body pb=${r.pb}  가로스크롤=${r.sw>r.cw?'있음 '+r.sw+'/'+r.cw:'없음'}`);
  console.log(`         고정 바 버튼: ${r.btns.join(' | ')||'-'}`);
  console.log(`         헤더 주 CTA : ${r.hcta.join(' | ')||'없음'}   GNB aria-current: ${JSON.stringify(r.gnbCur)}`);
  await p.close();
 }
 await b.close();
})();
