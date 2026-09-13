const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu','--hide-scrollbars']});
 for(const w of [320,360,768,1280]){
  const p=await b.newPage(); await p.setViewport({width:w,height:900,isMobile:w<768,hasTouch:w<768});
  await p.goto(BASE+'/privacy',{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const out=[];
   document.querySelectorAll('table').forEach((t,i)=>{
    const st=getComputedStyle(t);
    const rc=t.getBoundingClientRect();
    const par=t.parentElement; const ps=getComputedStyle(par);
    const prc=par.getBoundingClientRect();
    out.push({i:i+1, rows:t.querySelectorAll('tr').length, display:st.display,
      tableW:Math.round(rc.width), tableRight:Math.round(rc.right),
      parent:par.tagName.toLowerCase()+'.'+(typeof par.className==='string'?par.className.split(' ')[0]:''),
      parentOverflowX:ps.overflowX, parentW:Math.round(prc.width), parentScrollW:par.scrollWidth,
      theadDisplay:t.querySelector('thead')?getComputedStyle(t.querySelector('thead')).display:'-',
    });
   });
   return {out, sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth};
  });
  console.log('--- '+w+'px  문서 scrollW/clientW = '+r.sw+'/'+r.cw+(r.sw>r.cw?'  ← 가로 스크롤 발생':'  가로 스크롤 없음'));
  r.out.forEach(t=>console.log(`   표${t.i} 행${t.rows} display=${t.display} thead=${t.theadDisplay} 표폭=${t.tableW}(right ${t.tableRight}) 부모=${t.parent} overflowX=${t.parentOverflowX} 부모폭=${t.parentW} 부모scrollW=${t.parentScrollW}`));
  await p.close();
 }
 await b.close();
})();
