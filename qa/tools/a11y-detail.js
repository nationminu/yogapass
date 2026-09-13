const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu']});
 for(const [name,path] of [['home','/'],['location','/location'],['privacy','/privacy']]){
  const p=await b.newPage();
  await p.setViewport({width:360,height:780,isMobile:true,hasTouch:true});
  await p.goto(BASE+path,{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const small=[],tiny=[];
   document.querySelectorAll('body *').forEach(el=>{
    const st=getComputedStyle(el); if(st.display==='none'||st.visibility==='hidden')return;
    const rc=el.getBoundingClientRect();
    if(el.children.length===0&&el.textContent.trim()){
      const f=parseFloat(st.fontSize);
      if(f<14&&rc.left>-1000) small.push({sel:el.tagName.toLowerCase()+'.'+(el.className||''),fs:f,txt:el.textContent.trim().slice(0,30)});
    }
   });
   document.querySelectorAll('a,button,input,select,textarea,summary').forEach(el=>{
    const st=getComputedStyle(el); if(st.display==='none'||st.visibility==='hidden')return;
    const rc=el.getBoundingClientRect(); if(rc.width===0&&rc.height===0)return;
    if(rc.left< -1000) return;
    if(rc.width<44||rc.height<44){
      const inPara=!!el.closest('p,li,dd,td,th');
      tiny.push({sel:el.tagName.toLowerCase()+'.'+(el.className||''),w:Math.round(rc.width),h:Math.round(rc.height),inline:inPara,txt:(el.textContent||el.type||'').trim().slice(0,25)});
    }
   });
   return {small,tiny};
  });
  console.log('### '+name+' (360px)');
  console.log(' -- 14px 미만 텍스트 --');
  [...new Map(r.small.map(x=>[x.sel+x.fs,x])).values()].forEach(x=>console.log('   '+x.fs+'px  '+x.sel+'  "'+x.txt+'"'));
  console.log(' -- 44x44 미만 조작 요소 --');
  [...new Map(r.tiny.map(x=>[x.sel+x.w+x.h,x])).values()].forEach(x=>console.log('   '+x.w+'x'+x.h+'  '+x.sel+'  inline='+x.inline+'  "'+x.txt+'"'));
  await p.close();
 }
 await b.close();
})();
