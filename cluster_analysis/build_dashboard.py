#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة داشبورد الفرق المسجّلة من teams.json."""
import json

D = json.load(open("/home/user/khitba/cluster_analysis/teams.json", encoding="utf-8"))

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>لوحة الفرق المسجّلة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js"></script>
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#0b1c30;color:#e9eef5}
 a{color:#7cc4ff;text-decoration:none}
 .top{background:#0a3d62;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:10;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top h1{margin:0;font-size:19px;font-weight:800}
 .top .sp{flex:1}
 .btn{background:#1b6ca8;color:#fff;border:0;border-radius:8px;padding:8px 14px;font-family:'Tajawal';
   font-size:13px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
 .btn:hover{background:#2980b9} .btn.g{background:#2e7d32}.btn.g:hover{background:#388e3c}
 .wrap{max-width:1200px;margin:0 auto;padding:18px}
 .ages{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
 .agebtn{background:#16314f;border:1px solid #2a4a6e;color:#e9eef5;border-radius:20px;padding:7px 16px;
   cursor:pointer;font-family:'Tajawal';font-size:13px;font-weight:700}
 .agebtn.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 .kpis{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:18px}
 .kpi{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:16px 22px;flex:1;min-width:220px;text-align:center}
 .kpi .n{font-size:30px;font-weight:800;color:#ffd166;line-height:1.1}
 .kpi .l{font-size:12.5px;color:#9fb6d0;margin-top:4px}
 .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
 @media(max-width:800px){.grid{grid-template-columns:1fr}}
 .card{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:16px;margin-bottom:16px}
 .card h3{margin:0 0 12px;font-size:15px;color:#ffd166}
 .bar{display:flex;align-items:center;gap:8px;margin-bottom:7px;font-size:13px}
 .bar .lab{width:130px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}
 .bar .track{flex:1;background:#0b1c30;border-radius:6px;height:20px;overflow:hidden}
 .bar .fill{height:100%;background:linear-gradient(90deg,#1b6ca8,#3aa0e0);border-radius:6px;min-width:2px}
 .bar .val{width:34px;text-align:center;font-weight:700;color:#ffd166}
 .bar.clk{cursor:pointer;border-radius:7px;padding:3px 5px;margin:1px -5px}
 .bar.clk:hover{background:#16314f}
 .bar.wide .lab{width:230px;white-space:normal;text-overflow:clip}
 .lab .sub{font-size:10px;color:#7f97b3;line-height:1.35;margin-top:2px;font-weight:400}
 .chip{display:inline-block;background:#1b6ca8;color:#fff;border-radius:14px;padding:5px 13px;font-size:12px;cursor:pointer;margin-bottom:8px}
 .chip:hover{background:#2980b9}
 table{width:100%;border-collapse:collapse;font-size:13px}
 th,td{padding:7px 9px;text-align:right;border-bottom:1px solid #1c3a5e}
 th{color:#ffd166;font-weight:700;cursor:pointer;position:sticky;top:0;background:#12283f}
 tbody tr:hover{background:#16314f}
 .tblwrap{max-height:420px;overflow:auto;border-radius:8px}
 input.search{width:100%;padding:9px 11px;border-radius:8px;border:1px solid #2a4a6e;background:#0b1c30;
   color:#fff;font-family:'Tajawal';margin-bottom:10px}
 .muted{color:#9fb6d0;font-size:12px}
 .num{color:#ffd166;font-weight:700}
</style></head><body>
<div class="top">
 <h1>📊 لوحة الفرق المسجّلة</h1>
 <span class="muted" id="updated"></span>
 <span class="sp"></span>
 <label class="btn g" style="cursor:pointer">⬆️ تحديث من إكسل<input type="file" id="file" accept=".xlsx,.xls,.csv" style="display:none"></label>
 <a class="btn" href="./">🗺️ الخريطة</a>
</div>
<div class="wrap">
 <div class="ages" id="ages"></div>
 <div class="kpis" id="kpis"></div>
 <div class="grid">
  <div class="card" id="agecard"><h3>الفرق حسب الفئة العمرية</h3><div id="byage"></div></div>
  <div class="card" id="regcard"><h3 id="regh">الفرق حسب المنطقة</h3><div id="byregion"></div></div>
 </div>
 <div class="card" id="grpcard"><h3 id="grph">الفرق حسب المجموعة</h3><div id="bygroup"></div></div>
 <div class="card"><h3 id="cityh">الفرق حسب المدينة</h3>
  <div id="gfilter"></div>
  <input class="search" id="csearch" placeholder="ابحث عن مدينة أو مجموعة أو منطقة...">
  <div class="tblwrap"><table id="citytbl"><thead><tr>
   <th data-k="city">المدينة</th><th data-k="region">المنطقة</th><th data-k="group" class="grpcol">المجموعة</th><th data-k="count">الفرق</th>
  </tr></thead><tbody></tbody></table></div>
 </div>
</div>
<script>
let DATA = __DATA__;
let curAge='الكل';
let groupFilter=null;
const AGES=DATA.ages;
function rowsFor(age){return age==='الكل'?DATA.rows:DATA.rows.filter(r=>r.age===age);}
function sumBy(rows,key){const m={};rows.forEach(r=>{if(r.count)m[r.key===undefined?r[key]:r[key]]=(m[r[key]]||0)+r.count;});return m;}
function barChart(el,obj,{sort=true,limit=0,color,sub,wide,onClick}={}){
  let ent=Object.entries(obj).filter(([k,v])=>v>0);
  if(sort)ent.sort((a,b)=>b[1]-a[1]);
  if(limit)ent=ent.slice(0,limit);
  const mx=Math.max(1,...ent.map(e=>e[1]));
  el.innerHTML=ent.length?ent.map(([k,v])=>
    '<div class="bar'+(wide?' wide':'')+(onClick?' clk':'')+'" data-k="'+k.replace(/"/g,'&quot;')+'">'+
    '<div class="lab" title="'+k+'">'+k+((sub&&sub[k])?'<div class="sub">('+sub[k]+')</div>':'')+'</div>'+
    '<div class="track"><div class="fill" style="width:'+(v/mx*100)+'%'+(color?';background:'+color:'')+'"></div></div>'+
    '<div class="val">'+v+'</div></div>').join(''):'<div class="muted">لا توجد فرق.</div>';
  if(onClick)el.querySelectorAll('.bar.clk').forEach(b=>b.onclick=()=>onClick(b.getAttribute('data-k')));
}
function ageTotals(){const m={};AGES.forEach(a=>m[a]=0);DATA.rows.forEach(r=>m[r.age]=(m[r.age]||0)+r.count);return m;}
function render(){
  const rows=rowsFor(curAge);
  // KPIs
  const total=rows.reduce((s,r)=>s+r.count,0);
  const cities=new Set(rows.filter(r=>r.count>0).map(r=>r.city)).size;
  const groups=new Set(rows.filter(r=>r.count>0).map(r=>r.group)).size;
  const regions=new Set(rows.filter(r=>r.count>0).map(r=>r.region)).size;
  document.getElementById('kpis').innerHTML=
    kpi(total, curAge==='الكل'?'مجموع الفرق (كل الفئات)':'مجموع الفرق — '+curAge);
  // by age (يظهر فقط في صفحة الكل)
  const showAge=(curAge==='الكل');
  document.getElementById('agecard').style.display=showAge?'block':'none';
  document.getElementById('regcard').style.gridColumn=showAge?'':'1 / -1';
  if(showAge){const at=ageTotals();const ao={};AGES.forEach(a=>ao[a]=at[a]);
    barChart(document.getElementById('byage'),ao,{sort:false,color:'linear-gradient(90deg,#8e44ad,#c874f0)'});}
  // by region
  document.getElementById('regh').textContent='الفرق حسب المنطقة'+(curAge==='الكل'?'':' — '+curAge);
  barChart(document.getElementById('byregion'),agg(rows,'region'),{color:'linear-gradient(90deg,#16a085,#2ee6b6)'});
  // by group (يُخفى في صفحة الكل لأن التجميعات تختلف بين الفئات)
  document.getElementById('grpcard').style.display=(curAge==='الكل')?'none':'block';
  if(curAge!=='الكل'){document.getElementById('grph').textContent='الفرق حسب المجموعة — '+curAge;
    const gc={};rows.forEach(r=>{(gc[r.group]=gc[r.group]||[]).push(r.city);});
    const sub={};Object.keys(gc).forEach(g=>sub[g]=[...new Set(gc[g])].join('، '));
    barChart(document.getElementById('bygroup'),agg(rows,'group'),{sub,wide:true,
      onClick:g=>{groupFilter=g;document.getElementById('csearch').value='';renderTable();
        document.getElementById('cityh').scrollIntoView({behavior:'smooth',block:'start'});}});}
  document.getElementById('cityh').textContent='الفرق حسب المدينة'+(curAge==='الكل'?'':' — '+curAge);
  renderTable();
}
function agg(rows,key){const m={};rows.forEach(r=>{if(r.count)m[r[key]]=(m[r[key]]||0)+r.count;});return m;}
function kpi(n,l){return '<div class="kpi"><div class="n">'+n+'</div><div class="l">'+l+'</div></div>';}
let sortK='count',sortDir=-1;
function renderTable(){
  const showG=curAge!=='الكل';
  const gc=document.querySelector('#citytbl th.grpcol');if(gc)gc.style.display=showG?'':'none';
  const gf=document.getElementById('gfilter');
  const q=(document.getElementById('csearch').value||'').trim();
  let rows;
  if(showG&&groupFilter){
    rows=rowsFor(curAge).filter(r=>r.group===groupFilter);
    gf.innerHTML='<span class="chip" onclick="clearGroupFilter()">مدن «'+groupFilter+'» ✕ إظهار الكل</span>';
  } else {
    gf.innerHTML='';
    rows=rowsFor(curAge).filter(r=>r.count>0);
    if(!showG){const m={};rows.forEach(r=>{const k=r.city;if(!m[k])m[k]={city:r.city,region:r.region,count:0};m[k].count+=r.count;});rows=Object.values(m);}
  }
  if(q)rows=rows.filter(r=>(r.city+r.region+(r.group||'')).indexOf(q)>=0);
  const sk=(!showG&&sortK==='group')?'count':sortK;
  rows.sort((a,b)=>{const x=a[sk],y=b[sk];return (x>y?1:x<y?-1:0)*sortDir;});
  document.querySelector('#citytbl tbody').innerHTML=rows.map(r=>
    '<tr><td>'+r.city+'</td><td class="muted">'+r.region+'</td>'+(showG?'<td>'+(r.group||'')+'</td>':'')+'<td class="num">'+r.count+'</td></tr>').join('')
    ||'<tr><td colspan="'+(showG?4:3)+'" class="muted">لا نتائج.</td></tr>';
}
function clearGroupFilter(){groupFilter=null;renderTable();}
document.querySelectorAll('#citytbl th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;
  if(sortK===k)sortDir*=-1;else{sortK=k;sortDir=(k==='count')?-1:1;}renderTable();});
document.getElementById('csearch').oninput=()=>{groupFilter=null;renderTable();};
function buildAges(){const c=document.getElementById('ages');c.innerHTML='';
  ['الكل',...AGES].forEach(a=>{const b=document.createElement('button');b.className='agebtn'+(a===curAge?' on':'');
    b.textContent=a;b.onclick=()=>{curAge=a;groupFilter=null;buildAges();render();};c.appendChild(b);});}
// upload refresh
document.getElementById('file').onchange=e=>{const f=e.target.files[0];if(!f)return;
  const rd=new FileReader();rd.onload=ev=>{try{
    const wb=XLSX.read(ev.target.result,{type:'array'});
    const ws=wb.Sheets['عدد الفرق لكل مدينة']||wb.Sheets[wb.SheetNames[0]];
    const arr=XLSX.utils.sheet_to_json(ws,{header:1});
    const rows=[];let ages=[];
    arr.forEach(r=>{const a=(r[1]||'').toString().trim();
      if(!a||a==='الفئة العمرية')return;
      rows.push({age:a,city:(r[2]||'').toString().trim(),group:(r[3]||'').toString().trim(),
        region:regionOf((r[2]||'').toString().trim()),count:+(r[4]||0)});
      if(ages.indexOf(a)<0)ages.push(a);});
    ages.sort((x,y)=>(+x.replace(/\\D/g,''))-(+y.replace(/\\D/g,'')));
    DATA={rows,ages};curAge='الكل';buildAges();render();
    document.getElementById('updated').textContent='حُدّث من ملفك للتو';
  }catch(err){alert('تعذّر قراءة الملف: '+err.message);}};
  rd.readAsArrayBuffer(f);};
const REGION=__REGION__;
function regionOf(c){return REGION[c]||'غير محدد';}
buildAges();render();
</script></body></html>"""

# region map for client-side re-upload
import json as _j
region_map = {}
for r in D["rows"]:
    region_map.setdefault(r["city"], r["region"])

HTML = HTML.replace("__DATA__", json.dumps(D, ensure_ascii=False))
HTML = HTML.replace("__REGION__", json.dumps(region_map, ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/dashboard.html", "w", encoding="utf-8").write(HTML)
print("saved dashboard.html", len(HTML), "bytes")
