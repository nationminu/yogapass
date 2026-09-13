// QA cycle2 — 고정 바(.barwrap/.bar) · GNB/모바일 패널 구분 실측
const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
const PAGES=[['home','/'],['instructors','/instructors'],['location','/location'],['privacy','/privacy'],['e404','/nope']];
const VPS=[320,360,768,1280];
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu','--hide-scrollbars']});
 console.log('=== A. 고정 바 실측 (CMP-007 .barwrap/.bar) + 하단 여백 + 겹침 ===');
 console.log('화면\t뷰포트\tdata-fixed-bar\t.barwrap DOM\t.bar 표시\t바 높이\t바 버튼\tbody pb\t문서끝 제출버튼과 바 간격');
 for(const [name,path] of PAGES){
  for(const w of VPS){
   const p=await b.newPage();
   await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
   await p.goto(BASE+path,{waitUntil:'networkidle0'});
   const r=await p.evaluate(()=>{
    const vis=el=>{if(!el)return false;const s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return false;const rc=el.getBoundingClientRect();return rc.width>0&&rc.height>0;};
    const wrap=document.querySelector('.barwrap');
    const bar=document.querySelector('.barwrap .bar');
    const btns=bar?[...bar.querySelectorAll('a,button')].filter(vis).map(e=>e.textContent.trim().replace(/\s+/g,' ')+'['+e.getAttribute('href')+'] '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height)):[];
    let gap=null;
    const submit=document.querySelector('form button[type="submit"], form input[type="submit"]');
    if(submit&&wrap&&vis(wrap)){window.scrollTo(0,document.body.scrollHeight);}
    return {dfb:document.documentElement.getAttribute('data-fixed-bar'), wrapDom:!!wrap, barVis:vis(wrap), barH:wrap&&vis(wrap)?Math.round(wrap.getBoundingClientRect().height):0, btns, pb:getComputedStyle(document.body).paddingBottom, hasSubmit:!!submit};
   });
   let gap='-';
   if(r.hasSubmit&&r.barVis){
    await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
    await new Promise(x=>setTimeout(x,300));
    gap=await p.evaluate(()=>{const s=document.querySelector('form button[type="submit"]');const wr=document.querySelector('.barwrap');return Math.round(wr.getBoundingClientRect().top - s.getBoundingClientRect().bottom);});
   }
   console.log([name,w+'px',r.dfb,r.wrapDom?'있음':'없음',r.barVis?'표시':'미표시',r.barH+'px',(r.btns.join(' | ')||'-'),r.pb,gap].join('\t'));
   await p.close();
  }
 }
 console.log('\n=== B. GNB(nav.gnb) vs 모바일 패널(.mpanel) 구분 — display·크기·간격 ===');
 for(const w of [320,360,768,1280]){
  const p=await b.newPage();
  await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
  await p.goto(BASE+'/',{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const info=sel=>{const el=document.querySelector(sel);if(!el)return null;const s=getComputedStyle(el);const rc=el.getBoundingClientRect();
    const links=[...el.querySelectorAll('a')].map(a=>{const r2=a.getBoundingClientRect();const s2=getComputedStyle(a);return {t:a.textContent.trim(),w:Math.round(r2.width),h:Math.round(r2.height),l:Math.round(r2.left),r:Math.round(r2.right),top:Math.round(r2.top),bot:Math.round(r2.bottom),disp:s2.display};});
    return {display:s.display, visibility:s.visibility, w:Math.round(rc.width), h:Math.round(rc.height), links};};
   const det=document.querySelector('details.mnav');
   const sum=document.querySelector('summary.mnav-btn');
   return {gnb:info('nav.gnb'), mpanel:info('nav.mpanel'), detailsOpen:det?det.open:null,
     mnavBtn: sum?{disp:getComputedStyle(sum).display, w:Math.round(sum.getBoundingClientRect().width), h:Math.round(sum.getBoundingClientRect().height)}:null};
  });
  console.log('--- '+w+'px  details.open='+r.detailsOpen+'  햄버거 버튼='+JSON.stringify(r.mnavBtn));
  for(const k of ['gnb','mpanel']){
   const o=r[k]; if(!o){console.log('  '+k+': 없음');continue;}
   console.log(`  ${k}: display=${o.display} 크기=${o.w}x${o.h}`);
   console.log('    링크: '+o.links.map(x=>`"${x.t}" ${x.w}x${x.h}(disp=${x.disp})`).join(' , '));
   const gaps=[];for(let i=1;i<o.links.length;i++)gaps.push(o.display==='none'?null:(o.links[i].l-o.links[i-1].r));
   const vg=[];for(let i=1;i<o.links.length;i++)vg.push(o.links[i].top-o.links[i-1].bot);
   console.log('    가로 간격: '+JSON.stringify(gaps)+'  세로 간격: '+JSON.stringify(vg));
  }
  // 모바일 패널 열었을 때
  if(w<768){
   await p.evaluate(()=>{const d=document.querySelector('details.mnav'); if(d) d.open=true;});
   await new Promise(x=>setTimeout(x,300));
   const o=await p.evaluate(()=>{const el=document.querySelector('nav.mpanel');const links=[...el.querySelectorAll('a')].map(a=>{const r2=a.getBoundingClientRect();return {t:a.textContent.trim(),w:Math.round(r2.width),h:Math.round(r2.height),top:Math.round(r2.top),bot:Math.round(r2.bottom)};});return {links, de:document.documentElement.scrollWidth+'/'+document.documentElement.clientWidth};});
   console.log('  [패널 열림] 링크: '+o.links.map(x=>`"${x.t}" ${x.w}x${x.h}`).join(' , '));
   const vg=[];for(let i=1;i<o.links.length;i++)vg.push(o.links[i].top-o.links[i-1].bot);
   console.log('    세로 간격: '+JSON.stringify(vg)+'  | 열린 상태 scrollW/clientW: '+o.de);
  }
  await p.close();
 }
 await b.close();
})();
