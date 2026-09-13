const puppeteer=require('puppeteer-core');
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
(async()=>{
 const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--no-sandbox','--disable-gpu']});
 for(const p0 of ['/','/instructors','/location','/privacy','/nope']){
  const p=await b.newPage(); await p.setViewport({width:360,height:780,isMobile:true,hasTouch:true});
  await p.goto('http://localhost:8001'+p0,{waitUntil:'networkidle0'});
  const r=await p.evaluate(()=>{
   const m=document.querySelector('meta[name="viewport"]');
   return {content:m?m.getAttribute('content'):null,
     vkFallback:document.documentElement.getAttribute('data-vk-fallback'),
     scrollPadBottom:getComputedStyle(document.documentElement).scrollPaddingBottom,
     dfb:document.documentElement.getAttribute('data-fixed-bar')};
  });
  console.log(`  ${p0.padEnd(14)} viewport="${r.content}"  interactive-widget=${/interactive-widget/.test(r.content||'')?'있음':'**없음**'}  data-vk-fallback=${r.vkFallback}  scroll-padding-bottom=${r.scrollPadBottom}  data-fixed-bar=${r.dfb}`);
  await p.close();
 }
 await b.close();
})();
