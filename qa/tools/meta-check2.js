// QA cycle2 — DEF-001 재검증: 렌더 메타를 IA §6.2/§6.3 표와 문자열 단위 대조
const BASE = process.env.BASE || 'http://localhost:8001';
const IA = {
  '/':            { scr:'SCR-001', title:'강남 요가패스 | 강남 요가 스튜디오·수업 안내',
                    desc:'강남에 있는 요가 스튜디오 요가패스입니다. 수업과 강사를 확인하고 궁금한 점은 온라인 문의나 전화로 남겨주세요.' },
  '/instructors': { scr:'SCR-002', title:'요가 강사 소개 | 강남 요가패스',
                    desc:'강남 요가패스에서 수업을 진행하는 강사들을 소개합니다. 강사별 담당 수업과 자격·경력을 확인하고 체험 수업을 신청해 보세요.' },
  '/location':    { scr:'SCR-003', title:'오시는 길 | 강남 요가패스',
                    desc:'강남 요가패스 오시는 길입니다. 주소와 가까운 지하철역, 운영시간을 확인하고 길찾기로 바로 이동하세요.' },
  '/privacy':     { scr:'SCR-006', title:'개인정보 처리방침 | 강남 요가패스',
                    desc:'강남 요가패스 개인정보 처리방침입니다. 수집하는 개인정보 항목과 이용 목적, 보관 기간을 안내합니다.' },
  '/nope':        { scr:'SCR-008', title:'페이지를 찾을 수 없습니다 | 강남 요가패스', desc:null },
};
const dec = s => s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#(x?)([0-9a-fA-F]+);/g,(m,x,n)=>String.fromCodePoint(parseInt(n,x?16:10)));
const pick = (h,re) => { const m = h.match(re); return m ? dec(m[1]) : null; };
(async () => {
  let fail = 0; const titles = [];
  for (const [p, exp] of Object.entries(IA)) {
    const r = await fetch(BASE + p);
    const h = await r.text();
    const t  = pick(h, /<title>([^<]*)<\/title>/);
    const d  = pick(h, /<meta name="description" content="([^"]*)"/);
    const og = pick(h, /<meta property="og:title" content="([^"]*)"/);
    const ogd= pick(h, /<meta property="og:description" content="([^"]*)"/);
    const rob= pick(h, /<meta name="robots" content="([^"]*)"/);
    const can= pick(h, /<link rel="canonical" href="([^"]*)"/);
    const h1 = pick(h, /<h1[^>]*>([\s\S]*?)<\/h1>/);
    titles.push(t);
    const tOK = t === exp.title;
    const dOK = exp.desc === null ? (d === null) : (d === exp.desc);
    const len = d ? [...d].length : 0;
    const lenOK = exp.desc === null ? true : (len >= 50 && len <= 90);
    if (!tOK || !dOK || !lenOK) fail++;
    console.log(`--- ${p}  (${exp.scr})  HTTP ${r.status}`);
    console.log(`  title      ${tOK?'OK ':'NG '} "${t}"`);
    if (!tOK) console.log(`    expected "${exp.title}"`);
    console.log(`  desc       ${dOK?'OK ':'NG '} len=${len} "${d}"`);
    if (!dOK) console.log(`    expected "${exp.desc}"`);
    console.log(`  desc 50~90 ${lenOK?'OK':'NG'}`);
    console.log(`  og:title   "${og}"  | og:desc len=${ogd?[...ogd].length:0}`);
    console.log(`  robots     "${rob}" | canonical "${can}"`);
    console.log(`  h1         "${h1?h1.replace(/<[^>]*>/g,'').trim().replace(/\s+/g,' '):null}"`);
    console.log(`  '강남' in title/h1: ${t.includes('강남')} / ${h1?h1.includes('강남'):false}`);
    // 구조화 데이터
    const types = [...h.matchAll(/"@type"\s*:\s*"([^"]+)"/g)].map(m=>m[1]);
    console.log(`  JSON-LD @type: ${JSON.stringify(types)}`);
    // 인라인 style
    const inline = (h.match(/ style="/g)||[]).length;
    console.log(`  inline style 개수: ${inline}`);
    // 중복 id
    const ids = [...h.matchAll(/ id="([^"]+)"/g)].map(m=>m[1]);
    const dup = ids.filter((v,i)=>ids.indexOf(v)!==i);
    console.log(`  중복 id: ${dup.length?JSON.stringify([...new Set(dup)]):'0건'}`);
    if (inline || dup.length) fail++;
  }
  const uniq = new Set(titles);
  console.log(`\ntitle 유일성: ${titles.length}개 중 고유 ${uniq.size}개 → ${uniq.size===titles.length?'OK':'NG'}`);
  console.log(`\n총 불일치(화면 단위): ${fail}`);
  process.exit(fail ? 1 : 0);
})();
