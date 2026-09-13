// QA cycle2 — 문의 폼 응답 형태 7종 (기술 설계 §9.6) 재검증
const BASE=process.env.BASE||'http://localhost:8030';       // 빈도 제한 off
const BASE25=process.env.BASE25||'http://localhost:8040';   // 빈도 제한 off + 시계 +25h
const pick=(h,re)=>{const m=h.match(re);return m?m[1]:null;};
const attr=(h,id,name)=>{const t=h.match(new RegExp('<(?:input|textarea)[^>]*id="'+id+'"[\s\S]{0,400}?>'));if(!t)return null;const v=t[0].match(new RegExp(name+'="([^"]*)"'));return v?v[1]:null;};
const checked=(h,id)=>{const t=h.match(new RegExp('<input[^>]*id="'+id+'"[\s\S]{0,400}?>'));return t?/\schecked/.test(t[0]):false;};
const textarea=h=>{const t=h.match(/<textarea[\s\S]*?>([\s\S]*?)<\/textarea>/);return t?t[1].trim():null;};
const jar=new Map();
async function req(url,opt={}){
  const host=new URL(url).port;
  const headers=Object.assign({},opt.headers||{});
  if(jar.get(host)) headers['Cookie']=jar.get(host);
  const r=await fetch(url,{...opt,headers,redirect:'manual'});
  const sc=r.headers.getSetCookie?r.headers.getSetCookie():[];
  if(sc.length){const cur=new Map((jar.get(host)||'').split('; ').filter(Boolean).map(c=>[c.split('=')[0],c]));sc.forEach(c=>{const kv=c.split(';')[0];cur.set(kv.split('=')[0],kv);});jar.set(host,[...cur.values()].join('; '));}
  return {status:r.status,body:await r.text(),headers:r.headers};
}
async function form(base){const r=await req(base+'/location');return {csrf:pick(r.body,/name="csrfmiddlewaretoken" value="([^"]*)"/),token:pick(r.body,/name="submit_token" value="([^"]*)"/)};}
async function post(base,f,d){
  const b=new URLSearchParams();
  b.set('csrfmiddlewaretoken',f.csrf); b.set('submit_token',d.token??f.token);
  b.set('name',d.name??''); b.set('phone',d.phone??''); b.set('message',d.message??'');
  if(d.consent) b.set('consent','on');
  b.set('company_ref',d.hp??'');
  return req(base+'/location',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','Referer':base+'/location'},body:b.toString()});
}
function report(label,r,exp){
  const h=r.body;
  const o={
    status:r.status,
    formRerendered:/name="submit_token"/.test(h),
    roleStatus:(h.match(/role="status"/g)||[]).length,
    roleAlert:(h.match(/role="alert"/g)||[]).length,
    ariaInvalid:(h.match(/aria-invalid="true"/g)||[]).length,
    newToken:(pick(h,/name="submit_token" value="([^"]{0,16})/)||'-')+'…',
    keep:{name:attr(h,'f-name','value'),phone:attr(h,'f-phone','value'),message:textarea(h),consent:checked(h,'f-consent')},
    msg:[...new Set((h.match(/문의가 접수되었습니다|시간이 지나 문의가 접수되지 않았습니다|입력 내용을 확인해 주세요|잠시 후 다시 시도해 주세요/g)||[]))],
    retryAfter:r.headers.get('retry-after'),
  };
  console.log('### '+label);
  console.log('  HTTP='+o.status+'  Retry-After='+(o.retryAfter||'-'));
  console.log('  화면: 폼재렌더='+o.formRerendered+' role=status:'+o.roleStatus+' role=alert:'+o.roleAlert+' aria-invalid='+o.ariaInvalid+' 새토큰='+o.newToken);
  console.log('  입력값 보존: name="'+o.keep.name+'" phone="'+o.keep.phone+'" message="'+(o.keep.message||'').slice(0,24)+'" consent='+o.keep.consent);
  console.log('  문구: '+JSON.stringify(o.msg));
  return o;
}
(async()=>{
  console.log('대상: '+BASE+' (QA_RATE_LIMIT_MODE=off) / 만료용 '+BASE25+' (+25h)\n');
  let f=await form(BASE);
  const D={name:'QA2-정상',phone:'010-5555-0001',message:'QA2 정상 접수 본문',consent:true};
  report('① 정상 접수', await post(BASE,f,D));
  console.log('');
  report('⑤ 토큰 재사용 (같은 토큰 재제출)', await post(BASE,f,{...D,name:'QA2-재사용',phone:'010-5555-0002',message:'QA2 재사용 본문'}));
  console.log('');
  f=await form(BASE);
  report('② 서버 검증 실패 (이름 공백·전화 형식 오류·동의 없음)', await post(BASE,f,{name:'',phone:'abc',message:'QA2 검증 실패 본문',consent:false}));
  console.log('');
  f=await form(BASE);
  report('③ honeypot', await post(BASE,f,{name:'QA2-허니팟',phone:'010-5555-0003',message:'QA2 허니팟 본문',consent:true,hp:'bot'}));
  console.log('');
  f=await form(BASE);
  report('⑦-a 토큰 부재(missing)', await post(BASE,f,{token:'',name:'QA2-부재',phone:'010-5555-0004',message:'QA2 토큰 부재 본문',consent:true}));
  console.log('');
  f=await form(BASE);
  report('⑦-b 토큰 변조(invalid)', await post(BASE,f,{token:f.token+'TAMPER',name:'QA2-변조',phone:'010-5555-0005',message:'QA2 토큰 변조 본문',consent:true}));
  console.log('');
  const fn=await form(BASE);           // 정상 시계에서 토큰 발급
  const f25=await form(BASE25);        // +25h 컨테이너의 csrf·세션
  console.log('  (정상 시계 발급 토큰 '+fn.token.slice(0,20)+'… 을 +25h 컨테이너에 제출)');
  report('⑦-c 토큰 만료(expired)', await post(BASE25,f25,{token:fn.token,name:'QA2-만료',phone:'010-5555-0006',message:'QA2 토큰 만료 본문',consent:true}));
})();
