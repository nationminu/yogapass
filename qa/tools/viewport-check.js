const puppeteer=require('puppeteer-core');
const fs=require('fs');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
const BASE=process.env.BASE||'http://localhost:8001';
const OUT=process.env.OUT||'../evidence/cycle1/screenshots';
const PAGES=[['home','/'],['instructors','/instructors'],['location','/location'],['privacy','/privacy'],['e404','/nope']];
const VIEWPORTS=[[360,780],[768,1024],[1280,900],[320,780]];
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu','--hide-scrollbars']});
 console.log('화면 | 뷰포트 | 가로스크롤(scrollW/clientW) | 넘치는 요소 | 콘솔에러 | 최소글꼴(px) | 작은터치타깃 | 스크린샷');
 for(const [name,path] of PAGES){
  for(const [w,h] of VIEWPORTS){
   const p=await b.newPage();
   const errs=[];
   p.on('console',m=>{if(m.type()==='error')errs.push(m.text().slice(0,120));});
   p.on('pageerror',e=>errs.push('pageerror: '+e.message.slice(0,120)));
   await p.setViewport({width:w,height:h,deviceScaleFactor:1,isMobile:w<768,hasTouch:w<768});
   const resp=await p.goto(BASE+path,{waitUntil:'networkidle0',timeout:30000});
   const r=await p.evaluate(()=>{
    const de=document.documentElement;
    const over=[];
    document.querySelectorAll('body *').forEach(el=>{
      const st=getComputedStyle(el); if(st.display==='none'||st.visibility==='hidden')return;
      const rc=el.getBoundingClientRect(); if(rc.width===0&&rc.height===0)return;
      if(rc.right>de.clientWidth+1||rc.left<-1) over.push(el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:'')+' ['+Math.round(rc.left)+','+Math.round(rc.right)+']');
    });
    let minFs=99; const small=[];
    document.querySelectorAll('body *').forEach(el=>{
      const st=getComputedStyle(el); if(st.display==='none')return;
      if(el.children.length===0&&el.textContent.trim()){const fs2=parseFloat(st.fontSize); if(fs2<minFs)minFs=fs2;}
    });
    document.querySelectorAll('a,button,input,select,textarea,summary').forEach(el=>{
      const st=getComputedStyle(el); if(st.display==='none'||st.visibility==='hidden')return;
      const rc=el.getBoundingClientRect(); if(rc.width===0&&rc.height===0)return;
      if(rc.width<44||rc.height<44) small.push((el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:''))+' '+Math.round(rc.width)+'x'+Math.round(rc.height));
    });
    return {sw:de.scrollWidth,cw:de.clientWidth,over:[...new Set(over)].slice(0,5),minFs,small:[...new Set(small)].slice(0,6)};
   });
   const file=OUT+'/'+name+'_'+w+'.png';
   await p.screenshot({path:file,fullPage:true});
   console.log(name+' | '+w+'x'+h+' | '+(r.sw>r.cw+1?'**있음** '+r.sw+'/'+r.cw:'없음 '+r.sw+'/'+r.cw)+' | '+(r.over.length?r.over.join(' ; '):'0건')+' | '+(errs.length?errs.length+'건: '+errs[0]:'0건')+' | '+r.minFs+' | '+(r.small.length?r.small.join(' ; '):'0건')+' | '+file.split('/').pop());
   await p.close();
  }
 }
 await b.close();
})();
