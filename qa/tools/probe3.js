const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu']});
 const p=await b.newPage(); await p.setViewport({width:360,height:780,isMobile:true,hasTouch:true});
 await p.goto(BASE+'/location',{waitUntil:'networkidle0'});
 console.log('=== 키보드 Tab 순회 · 포커스 표시 (360px /location, 앞 20개) ===');
 for(let i=0;i<20;i++){
  await p.keyboard.press('Tab');
  const r=await p.evaluate(()=>{const e=document.activeElement;if(!e||e===document.body)return null;
   const s=getComputedStyle(e);const rc=e.getBoundingClientRect();
   return {tag:e.tagName.toLowerCase(),cls:(typeof e.className==='string'?e.className:'').slice(0,24),txt:(e.textContent||e.type||'').replace(/\s+/g,' ').trim().slice(0,22),
    outline:s.outlineStyle+' '+s.outlineWidth+' '+s.outlineColor, shadow:(s.boxShadow||'none').slice(0,40), w:Math.round(rc.width),h:Math.round(rc.height), vis:rc.width>0&&rc.height>0};});
  if(!r){console.log((i+1)+') (body)');continue;}
  const visible=r.outline.startsWith('none')===false||r.shadow!=='none';
  console.log((i+1)+') '+r.tag+'.'+r.cls+' "'+r.txt+'" '+r.w+'x'+r.h+' | outline='+r.outline+' shadow='+r.shadow+' | 포커스표시='+(visible?'있음':'**없음**'));
 }
 console.log('\n=== 동의 체크박스 영역 ===');
 console.log(JSON.stringify(await p.evaluate(()=>{
  const inp=document.getElementById('f-consent');
  const lab=document.querySelector('label[for="f-consent"]');
  const row=inp?inp.closest('div,fieldset,p'):null;
  const g=e=>e?{tag:e.tagName.toLowerCase(),cls:(typeof e.className==='string'?e.className:''),w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height)}:null;
  return {input:g(inp),label:g(lab),row:g(row)};
 })));
 console.log('\n=== 제출 버튼 ↔ 고정 바 간격 (G-4) — 고정 바가 있는 화면 home 으로 확인 ===');
 await p.goto(BASE+'/',{waitUntil:'networkidle0'});
 console.log(JSON.stringify(await p.evaluate(()=>{
  window.scrollTo(0,document.body.scrollHeight);
  const bar=[...document.querySelectorAll('div,nav')].find(e=>{const s=getComputedStyle(e);return s.position==='fixed'&&e.getBoundingClientRect().bottom>=window.innerHeight-2&&e.getBoundingClientRect().height>20;});
  const last=[...document.querySelectorAll('main a,main button')].pop();
  return {barTop:bar?Math.round(bar.getBoundingClientRect().top):null,lastBottom:last?Math.round(last.getBoundingClientRect().bottom):null,gap:bar&&last?Math.round(bar.getBoundingClientRect().top-last.getBoundingClientRect().bottom):null};
 })));
 await b.close();
})();
