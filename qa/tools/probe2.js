const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu']});
 console.log('=== A. 하단 고정 바 / 헤더 주 CTA (REQ-F-003 · REQ-N-002 · §3.0) ===');
 for(const [name,path] of [['home','/'],['instructors','/instructors'],['location','/location'],['privacy','/privacy'],['e404','/nope']]){
  for(const w of [360,768,1280]){
   const p=await b.newPage(); await p.setViewport({width:w,height:780,isMobile:w<768,hasTouch:w<768});
   await p.goto(BASE+path,{waitUntil:'networkidle0'});
   await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
   await new Promise(r=>setTimeout(r,300));
   const r=await p.evaluate(()=>{
    const bar=document.querySelector('.fixed-bar,.barwrap,[data-fixed-bar],footer ~ div');
    const cand=[...document.querySelectorAll('div,nav')].find(e=>{const s=getComputedStyle(e);return s.position==='fixed'&&e.getBoundingClientRect().bottom>=window.innerHeight-2&&e.getBoundingClientRect().height>20;});
    const hdr=document.querySelector('header');
    const hs=hdr?getComputedStyle(hdr):null;
    const hdrCta=hdr?[...hdr.querySelectorAll('a.btn,button.btn,a.strong')].map(e=>e.textContent.trim().replace(/\s+/g,' ').slice(0,20)):[];
    const padB=getComputedStyle(document.body).paddingBottom;
    return {bar:cand?{h:Math.round(cand.getBoundingClientRect().height),txt:cand.textContent.replace(/\s+/g,' ').trim().slice(0,40),btns:cand.querySelectorAll('a,button').length}:null,
      headerPos:hs?hs.position:null, headerBottom:hdr?Math.round(hdr.getBoundingClientRect().bottom):null, hdrCta, padB,
      ariaCurrent:document.querySelectorAll('[aria-current="page"]').length};
   });
   console.log(name+' '+w+'px | 고정바='+(r.bar?('있음 h='+r.bar.h+' 버튼'+r.bar.btns+'개 "'+r.bar.txt+'"'):'없음')+' | header.position='+r.headerPos+' bottom='+r.headerBottom+' | 헤더CTA='+(r.hdrCta.length?r.hdrCta.join(','):'없음')+' | body.padding-bottom='+r.padB+' | aria-current='+r.ariaCurrent);
   await p.close();
  }
 }
 console.log('\n=== B. 포커스 표시 · 체크박스 라벨 행 · 푸터 링크 (360px /location) ===');
 {const p=await b.newPage(); await p.setViewport({width:360,height:780,isMobile:true,hasTouch:true});
  await p.goto(BASE+'/location',{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const lab=[...document.querySelectorAll('label')].find(l=>l.querySelector('input[type=checkbox]'));
   const lr=lab?lab.getBoundingClientRect():null;
   const foot=[...document.querySelectorAll('footer a')].slice(0,4).map(a=>{const c=a.getBoundingClientRect();return a.textContent.trim().slice(0,12)+' '+Math.round(c.width)+'x'+Math.round(c.height);});
   return {label:lr?Math.round(lr.width)+'x'+Math.round(lr.height):'없음', foot};
  });
  console.log('동의 체크박스 라벨 행 = '+r.label);
  console.log('푸터 링크 = '+r.foot.join(' ; '));
  // focus outline
  const fo=await p.evaluate(async()=>{
   const els=[...document.querySelectorAll('a[href],button,input,textarea,summary')].filter(e=>e.getBoundingClientRect().width>0).slice(0,6);
   const out=[];
   for(const e of els){e.focus();const s=getComputedStyle(e);out.push((e.tagName.toLowerCase())+' outline='+s.outlineStyle+' '+s.outlineWidth+' '+s.outlineColor+' boxShadow='+(s.boxShadow||'none').slice(0,30));}
   return out;});
  console.log('포커스 표시:'); fo.forEach(x=>console.log('  '+x));
  await p.close();}
 console.log('\n=== C. JavaScript 비활성 (REQ-N-028 · 029) ===');
 for(const [name,path] of [['home','/'],['instructors','/instructors'],['location','/location'],['privacy','/privacy'],['e404','/nope']]){
  const p=await b.newPage(); await p.setJavaScriptEnabled(false); await p.setViewport({width:360,height:780});
  await p.goto(BASE+path,{waitUntil:'domcontentloaded'});
  const r=await p.evaluate(()=>0).catch(()=>null);
  const html=await p.content();
  const txt=html.replace(/<script[\s\S]*?<\/script>/g,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
  console.log(name+' | 본문 글자수='+txt.length+' | 링크='+(html.match(/<a /g)||[]).length+'개 | noscript='+(html.match(/<noscript/g)||[]).length+' | 메뉴details='+(html.match(/<details/g)||[]).length+' | tel링크='+(html.match(/href="tel:/g)||[]).length);
  await p.close();
 }
 await b.close();
})();
