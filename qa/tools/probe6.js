// QA cycle2 종합 프로브 — DEF-004/005/006 + G-8 회귀 + 헤더 높이 안정성 + 앵커
const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
const PAGES=[['home','/'],['instructors','/instructors'],['location','/location'],['privacy','/privacy'],['e404','/nope']];
const VPS=[320,360,768,1280];
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu','--hide-scrollbars']});
 console.log('=== A. 화면×뷰포트: 헤더 주CTA(G-8) · 고정 바 · body 하단 여백 · aria-current · 헤더 높이 ===');
 console.log('화면\t뷰포트\t헤더CTA\t헤더CTA문구\t고정바\t고정바버튼\tbody padding-bottom\t--fixed-bar-h\theaderH\taria-current(GNB/CTA)');
 for(const [name,path] of PAGES){
  for(const w of VPS){
   const p=await b.newPage();
   await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
   await p.goto(BASE+path,{waitUntil:'networkidle0'});
   const r=await p.evaluate(()=>{
    const vis=el=>{if(!el)return false;const s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return false;const rc=el.getBoundingClientRect();return rc.width>0&&rc.height>0;};
    const hdr=document.querySelector('header');
    // 헤더 안의 강조 버튼(주 CTA)
    const hcta=[...document.querySelectorAll('header a.btn, header a[class*="btn-p"], header .hdr-cta')].filter(vis);
    const bar=document.querySelector('.fixedbar, .fixed-bar, [class*="fixedbar"], [data-fixed-bar], footer ~ div[class*="bar"]');
    const barEl=[...document.querySelectorAll('*')].find(e=>e.className&&typeof e.className==='string'&&/fixedbar|fixed-bar/.test(e.className)&&vis(e));
    const barBtns=barEl?[...barEl.querySelectorAll('a,button')].filter(vis).map(e=>e.textContent.trim().replace(/\s+/g,' ').slice(0,20)+'['+e.getAttribute('href')+']'):[];
    const cs=getComputedStyle(document.body);
    const cur=[...document.querySelectorAll('[aria-current="page"]')].map(e=>e.tagName.toLowerCase()+'.'+(typeof e.className==='string'?e.className.split(' ')[0]:'')+':'+e.textContent.trim().slice(0,10));
    const gnbCur=[...document.querySelectorAll('header nav a[aria-current="page"], nav[class*="gnb"] a[aria-current="page"]')].length;
    const ctaCur=hcta.filter(e=>e.getAttribute('aria-current')).length;
    return {
     hcta:hcta.length, hctaTxt:hcta.map(e=>e.textContent.trim().replace(/\s+/g,' ')+'['+e.getAttribute('href')+']').join(' ; '),
     bar: !!barEl, barBtns,
     pb: cs.paddingBottom,
     fbh: getComputedStyle(document.documentElement).getPropertyValue('--fixed-bar-h').trim(),
     hdrH: hdr?Math.round(hdr.getBoundingClientRect().height):null,
     dataFb: document.documentElement.getAttribute('data-fixed-bar'),
     cur, gnbCur, ctaCur,
    };
   });
   console.log([name,w+'px',r.hcta,(r.hctaTxt||'-'),r.bar?'있음':'없음',(r.barBtns.join(' | ')||'-'),r.pb,(r.fbh||'-'),r.hdrH,r.gnbCur+'/'+r.ctaCur].join('\t'));
   await p.close();
  }
 }
 console.log('\n=== B. 헤더 높이 되먹임 회귀 — 같은 페이지 5회 연속 로드 ===');
 for(const w of [360,768,1280]){
  const p=await b.newPage();
  await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
  const hs=[];
  for(let i=0;i<5;i++){
   await p.goto(BASE+'/',{waitUntil:'networkidle0'});
   await new Promise(r=>setTimeout(r,300));
   hs.push(await p.evaluate(()=>{const h=document.querySelector('header');return [Math.round(h.getBoundingClientRect().height), getComputedStyle(document.documentElement).getPropertyValue('--header-h').trim(), getComputedStyle(document.documentElement).getPropertyValue('--header-min-h').trim()];}));
  }
  console.log(w+'px  높이(5회): '+hs.map(x=>x[0]).join(' → ')+'  | --header-h: '+hs.map(x=>x[1]).join(',')+'  | --header-min-h: '+hs[0][2]);
  await p.close();
 }
 console.log('\n=== C. 조작 요소 크기·인접 간격 (헤더 로고 · GNB · 푸터 링크) ===');
 for(const w of [360,768,1280]){
  const p=await b.newPage();
  await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
  await p.goto(BASE+'/',{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const vis=el=>{const s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return false;const rc=el.getBoundingClientRect();return (rc.width>0||rc.height>0)&&rc.right>0;};
   const box=el=>{const rc=el.getBoundingClientRect();return {w:Math.round(rc.width),h:Math.round(rc.height),t:Math.round(rc.top),b:Math.round(rc.bottom),l:Math.round(rc.left),r:Math.round(rc.right)};};
   const g=sel=>[...document.querySelectorAll(sel)].filter(vis).map(e=>({txt:e.textContent.trim().replace(/\s+/g,' ').slice(0,16),...box(e)}));
   const logo=g('header a.logo, header a[class*="logo"]');
   const gnb=g('header nav a');
   const foot=g('footer a');
   const svg=[...document.querySelectorAll('header a.logo svg, header a[class*="logo"] svg')].filter(vis).map(box);
   const copy=[...document.querySelectorAll('footer p')].filter(vis).map(e=>({txt:e.textContent.trim().slice(0,30),fs:getComputedStyle(e).fontSize}));
   return {logo,logoSvg:svg,gnb,foot,copy};
  });
  console.log('--- '+w+'px');
  console.log('  로고 링크: '+JSON.stringify(r.logo.map(x=>x.w+'x'+x.h)) + '  그래픽(svg): '+JSON.stringify(r.logoSvg.map(x=>x.w+'x'+x.h)));
  console.log('  GNB: '+r.gnb.map(x=>`"${x.txt}" ${x.w}x${x.h}`).join(' , '));
  const gaps=[];for(let i=1;i<r.gnb.length;i++)gaps.push(r.gnb[i].l-r.gnb[i-1].r);
  console.log('  GNB 인접 간격(px): '+JSON.stringify(gaps)+'  | GNB 전체 폭: '+(r.gnb.length?(r.gnb[r.gnb.length-1].r-r.gnb[0].l):0));
  console.log('  푸터 링크: '+r.foot.map(x=>`"${x.txt}" ${x.w}x${x.h}`).join(' , '));
  const fg=[];for(let i=1;i<r.foot.length;i++)fg.push(r.foot[i].t-r.foot[i-1].b);
  console.log('  푸터 링크 인접 간격(px): '+JSON.stringify(fg));
  console.log('  푸터 문단 글꼴: '+JSON.stringify(r.copy));
  await p.close();
 }
 console.log('\n=== D. 앵커 이동 위치 (#contact · #map, 헤더에 가리지 않는지) ===');
 for(const w of [360,1280]){
  for(const a of ['#map','#contact']){
   const p=await b.newPage();
   await p.setViewport({width:w,height:800,isMobile:w<768,hasTouch:w<768});
   await p.goto(BASE+'/location'+a,{waitUntil:'networkidle0'});
   await new Promise(r=>setTimeout(r,500));
   const r=await p.evaluate((id)=>{
    const t=document.querySelector(id);
    if(!t)return {err:'대상 없음'};
    const rc=t.getBoundingClientRect();
    const hdr=document.querySelector('header').getBoundingClientRect();
    return {top:Math.round(rc.top), headerBottom:Math.round(hdr.bottom), sm:getComputedStyle(t).scrollMarginTop, hidden: rc.top < hdr.bottom};
   },a);
   console.log(`  ${w}px ${a} → 대상 top=${r.top}px, 헤더 bottom=${r.headerBottom}px, scroll-margin-top=${r.sm}, 헤더에 가림=${r.hidden?'예(NG)':'아니오(OK)'}`);
   await p.close();
  }
 }
 await b.close();
})();
