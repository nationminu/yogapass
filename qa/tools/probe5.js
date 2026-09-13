const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8000';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu']});
 const p=await b.newPage(); await p.setViewport({width:360,height:780});
 let navs=0; p.on('framenavigated',f=>{if(f===p.mainFrame())navs++;});
 await p.goto(BASE+'/location',{waitUntil:'networkidle0'});
 navs=0;
 await p.type('#f-name','TEST-포커스2'); await p.type('#f-phone','010-1234-5678');
 await p.type('#f-message','TEST-결과블록 포커스 확인'); await p.click('#f-consent');
 await p.evaluate(()=>document.querySelector('#contact-form button[type=submit],#contact-form button').click());
 await new Promise(r=>setTimeout(r,2500));
 console.log('페이지 내비게이션 횟수 =',navs,'(0이면 JS 경로, 1이면 서버 렌더 전체 이동)');
 console.log(JSON.stringify(await p.evaluate(()=>{
  const a=document.activeElement;
  const res=document.querySelector('#contact-result,[id*="result"]');
  return {active:a?(a.id||a.tagName+'.'+(typeof a.className==='string'?a.className:'')):'none',
   resultId:res?res.id:null, resultTabindex:res?res.getAttribute('tabindex'):null,
   resultRole:res?res.getAttribute('role'):null,
   resultText:res?res.textContent.replace(/\s+/g,' ').trim().slice(0,60):null,
   activeInsideResult: res&&a?res.contains(a):false};})));
 // Tab 1회 후 위치
 await p.keyboard.press('Tab');
 console.log('Tab 1회 후:', JSON.stringify(await p.evaluate(()=>{const a=document.activeElement;const res=document.querySelector('#contact-result,[id*="result"]');
  return {active:a?(a.id||a.tagName+'.'+(typeof a.className==='string'?a.className:''))+' "'+(a.textContent||'').replace(/\s+/g,' ').trim().slice(0,20)+'"':'none', insideResult:res&&a?res.contains(a):false};})));
 await b.close();
})();
