#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة داشبورد الفِرَق المسجَّلة (فلاتر: الفئة، الصفة، المنطقة) من teams2.json."""
import json, datetime, os

D = json.load(open("/home/user/khitba/cluster_analysis/teams2.json", encoding="utf-8"))
MAPS = json.load(open("/home/user/khitba/cluster_analysis/_maps.json", encoding="utf-8"))

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>لوحة الفِرَق المسجَّلة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.sheetjs.com/xlsx-0.20.2/package/dist/xlsx.full.min.js"></script>
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#0b1c30;color:#e9eef5}
 a{color:#7cc4ff;text-decoration:none}
 .top{background:#0a3d62;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:10;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top h1{margin:0;font-size:19px;font-weight:800} .top .sp{flex:1}
 .top .logo{height:46px;width:auto;display:block;flex-shrink:0;filter:brightness(0) invert(1)}
 .btn{background:#1b6ca8;color:#fff;border:0;border-radius:8px;padding:8px 14px;font-family:'Tajawal';
   font-size:13px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
 .btn:hover{background:#2980b9} .btn.g{background:#2e7d32}.btn.g:hover{background:#388e3c}
 .wrap{max-width:1200px;margin:0 auto;padding:18px}
 .flt{margin-bottom:14px} .flt .lab{font-size:12px;color:#9fb6d0;margin-bottom:5px;font-weight:700}
 .tabs{display:flex;flex-wrap:wrap;gap:8px}
 .tab{background:#16314f;border:1px solid #2a4a6e;color:#e9eef5;border-radius:20px;padding:6px 15px;
   cursor:pointer;font-family:'Tajawal';font-size:13px;font-weight:700}
 .tab.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 select.rgn{padding:8px 12px;border-radius:8px;border:1px solid #2a4a6e;background:#13294a;color:#fff;
   font-family:'Tajawal';font-size:13px;font-weight:700;min-width:200px}
 .kpis{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0 18px}
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
 .bar .val{width:40px;text-align:center;font-weight:700;color:#ffd166}
 .bar.clk{cursor:pointer;border-radius:7px;padding:3px 5px;margin:1px -5px} .bar.clk:hover{background:#16314f}
 .bar.wide .lab{width:240px;white-space:normal;text-overflow:clip}
 .lab .sub{font-size:10px;color:#7f97b3;line-height:1.35;margin-top:2px;font-weight:400}
 .chip{display:inline-block;background:#1b6ca8;color:#fff;border-radius:14px;padding:5px 13px;font-size:12px;cursor:pointer;margin-bottom:8px}
 .chip:hover{background:#2980b9}
 table{width:100%;border-collapse:collapse;font-size:13px}
 th,td{padding:7px 9px;text-align:right;border-bottom:1px solid #1c3a5e}
 th{color:#ffd166;font-weight:700;cursor:pointer;position:sticky;top:0;background:#12283f}
 tbody tr:hover{background:#16314f}
 .tblwrap{max-height:440px;overflow:auto;border-radius:8px}
 input.search{width:100%;padding:9px 11px;border-radius:8px;border:1px solid #2a4a6e;background:#0b1c30;
   color:#fff;font-family:'Tajawal';margin-bottom:10px}
 .muted{color:#9fb6d0;font-size:12px} .num{color:#ffd166;font-weight:700}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد السعودي لكرة القدم" onerror="this.remove()">
 <h1>📊 لوحة الفِرَق المسجَّلة</h1>
 <span class="muted" id="updated"></span>
 <span class="sp"></span>
 <label class="btn g" style="cursor:pointer">⬆️ تحديث من إكسل<input type="file" id="file" accept=".xlsx,.xls" style="display:none"></label>
 <a class="btn" href="./">🗺️ الخريطة</a>
</div>
<div class="wrap">
 <div class="flt"><div class="lab">الفئة العمرية:</div><div class="tabs" id="ageT"></div></div>
 <div class="flt"><div class="lab">صفة الفريق: <span style="font-weight:400;font-size:11px;opacity:.75">(يمكنك اختيار أكثر من خيار)</span></div><div class="tabs" id="sifaT"></div></div>
 <div class="flt"><div class="lab">المنطقة:</div><select class="rgn" id="rgn"></select></div>
 <div class="flt" id="offFlt" style="display:none"><div class="lab">مكتب الوزارة:</div><select class="rgn" id="off"></select></div>
 <div class="flt" style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn g" id="dlSum" style="cursor:pointer">📷 تنزيل صورة ملخص المكاتب والفئات</button><button class="btn g" id="cmpBtn" style="cursor:pointer">📈 مقارنة اليوم بأمس</button></div>

 <div class="kpis" id="kpis"></div>

 <div class="grid" id="topcharts">
  <div class="card" id="agecard"><h3>الفِرَق بحسب الفئة العمرية</h3><div id="byage"></div></div>
  <div class="card" id="regcard"><h3 id="regh">الفِرَق بحسب المنطقة</h3><div id="byregion"></div></div>
 </div>
 <div class="card" id="sifacard"><h3 id="sifah">الفِرَق بحسب صفة الفريق</h3><div id="bysifa"></div></div>
 <div class="card" id="offcard" style="display:none"><h3>الفِرَق بحسب مكتب الوزارة</h3><div id="byoffice"></div></div>
 <div class="card" id="grpcard"><h3 id="grph">الفِرَق بحسب المجموعة</h3><div id="bygroup"></div></div>
 <div class="card" id="regionPanel"></div>
 <div class="card" id="officePanel"></div>
 <div class="card" id="emptyCard" style="display:none"></div>
 <div class="card" id="cmpCard" style="display:none"></div>

 <div class="card"><h3 id="cityh">الفِرَق بحسب المدينة</h3>
  <div id="gfilter"></div>
  <input class="search" id="csearch" placeholder="ابحث بالمدينة أو المجموعة أو المنطقة...">
  <div class="tblwrap"><table id="citytbl"><thead><tr>
   <th data-k="city">المدينة</th><th data-k="region">المنطقة</th><th data-k="group" class="grpcol">المجموعة</th><th data-k="count">الفِرَق</th>
  </tr></thead><tbody></tbody></table></div>
 </div>
</div>
<script>
let DATA=__DATA__;
const C2G=__C2G__, REG=__REG__, STRUCT=__STRUCT__, GROFF=__GROFF__;
const PREV=__PREV__, TODAY=__TODAY__;
function structFor(age,region){
  if(region!=='الكل')return (STRUCT[region]&&STRUCT[region][age])||{};
  const m={};Object.keys(STRUCT).forEach(rg=>{const s=STRUCT[rg][age];if(s)Object.keys(s).forEach(g=>{m[g]=(m[g]||[]).concat(s[g]);});});
  Object.keys(m).forEach(g=>m[g]=[...new Set(m[g])]);return m;}
const TARGET=DATA.target||6;
let curAge='الكل', curSifas=[], curRegion='الكل', curOffice='الكل', groupFilter=null;
function sifaMatch(r){return curSifas.length===0||curSifas.includes(r.sifa);}
function sifaLabel(){return curSifas.length===0?'كل الصفات':curSifas.join('، ');}
let sortK='count', sortDir=-1;

function base(){ // كل الصفوف مع فلترة الفئة والمنطقة ومكتب الوزارة (بدون الصفة) — للبنية
  return DATA.rows.filter(r=>(curAge==='الكل'||r.age===curAge)&&(curRegion==='الكل'||r.region===curRegion)&&(curOffice==='الكل'||(r.office||'')===curOffice));
}
function filtered(){ return base().filter(sifaMatch); }
function agg(rows,key){const m={};rows.forEach(r=>{if(r.count)m[r[key]]=(m[r[key]]||0)+r.count;});return m;}

function barChart(el,obj,{sort=true,color}={}){
  let ent=Object.entries(obj).filter(([k,v])=>v>0);
  if(sort)ent.sort((a,b)=>b[1]-a[1]);
  const mx=Math.max(1,...ent.map(e=>e[1]));
  el.innerHTML=ent.length?ent.map(([k,v])=>
    '<div class="bar"><div class="lab" title="'+k+'">'+k+'</div>'+
    '<div class="track"><div class="fill" style="width:'+(v/mx*100)+'%'+(color?';background:'+color:'')+'"></div></div>'+
    '<div class="val">'+v+'</div></div>').join(''):'<div class="muted">لا توجد فِرَق.</div>';
}
function ageChartData(){const m={};DATA.ages.forEach(a=>m[a]=0);
  base().filter(sifaMatch).forEach(r=>m[r.age]=(m[r.age]||0)+r.count);return m;}
function groupChart(el){
  // البنية من التقسيمة (كل المجموعات حتى الفارغة) — العدّ حسب الفلاتر
  const struct=structFor(curAge,curRegion);
  const om=groupOffSet();
  const cnt={};filtered().forEach(r=>{cnt[r.group]=(cnt[r.group]||0)+r.count;});
  let arr;
  if(curOffice!=='الكل'){ // عند فلترة مكتب: مجموعات هذا المكتب فقط
    const gc=groupCities();
    arr=Object.keys(cnt).filter(g=>cnt[g]>0).map(g=>({group:g,count:cnt[g],cities:(struct[g]||gc[g]||[]).join('، ')}));
  } else {
    arr=Object.keys(struct).map(g=>({group:g,count:cnt[g]||0,cities:struct[g].join('، ')}));
    Object.keys(cnt).forEach(g=>{if(!struct[g]&&cnt[g]>0)arr.push({group:g,count:cnt[g],cities:''});});
  }
  arr.sort((a,b)=>b.count-a.count);
  const mx=Math.max(TARGET,1,...arr.map(a=>a.count));
  el.innerHTML=arr.length?arr.map(a=>{
    const ok=a.count>=TARGET;
    const col=ok?'linear-gradient(90deg,#1a9850,#2ecc71)':'linear-gradient(90deg,#c0392b,#e74c3c)';
    const note=ok?('مكتمل'+(a.count>TARGET?' (زائد '+(a.count-TARGET)+')':'')):('المتبقّي '+(TARGET-a.count)+' فريق للوصول إلى '+TARGET);
    const offs=[...(om[a.group]||[])];const shared=(curOffice==='الكل')?(offs.length>1?offs:[]):offs.filter(o=>o!==curOffice);
    return '<div class="bar wide clk" data-k="'+a.group.replace(/"/g,'&quot;')+'">'+
      '<div class="lab"><b>'+a.group+'</b>'+
      (shared.length?'<div class="sub" style="color:#ffe9a8">🔗 مشترك بين مكاتب: '+shared.join('، ')+'</div>':'')+
      '<div class="sub">('+a.cities+')</div>'+
      '<div class="sub" style="color:'+(ok?'#7ee0a0':'#ff9a9a')+';font-weight:700">'+note+'</div></div>'+
      '<div class="track"><div class="fill" style="width:'+(a.count/mx*100)+'%;background:'+col+'"></div></div>'+
      '<div class="val" style="color:'+(ok?'#7ee0a0':'#ff9a9a')+'">'+a.count+'</div></div>';
  }).join(''):'<div class="muted">لا توجد مجموعات.</div>';
  el.querySelectorAll('.bar.clk').forEach(b=>b.onclick=()=>{groupFilter=b.getAttribute('data-k');
    document.getElementById('csearch').value='';renderTable();
    document.getElementById('cityh').scrollIntoView({behavior:'smooth',block:'start'});});
}
function kpi(n,l){return '<div class="kpi"><div class="n">'+n+'</div><div class="l">'+l+'</div></div>';}
function regionPanel(el){
  let html='<h3>مجموعات '+curRegion+' حسب الفئة العمرية'+(curSifas.length?' — '+curSifas.join('، '):'')+' (المطلوب: '+TARGET+' لكل مجموعة)</h3>';
  DATA.ages.forEach(age=>{
    const struct=(STRUCT[curRegion]&&STRUCT[curRegion][age])||{};
    const cnt={};DATA.rows.filter(r=>r.region===curRegion&&r.age===age&&sifaMatch(r)).forEach(r=>cnt[r.group]=(cnt[r.group]||0)+r.count);
    let arr=Object.keys(struct).map(g=>({group:g,count:cnt[g]||0,cities:struct[g].join('، ')}));
    Object.keys(cnt).forEach(g=>{if(!struct[g]&&cnt[g]>0)arr.push({group:g,count:cnt[g],cities:''});});
    if(!arr.length)return;
    arr.sort((a,b)=>b.count-a.count);
    const tot=arr.reduce((s,a)=>s+a.count,0),mx=Math.max(TARGET,1,...arr.map(a=>a.count));
    html+='<div style="margin-top:14px"><div style="color:#ffd166;font-weight:700;margin-bottom:6px;font-size:14px;border-top:1px solid #1c3a5e;padding-top:10px">'+age+'</div>';
    html+=arr.map(a=>{const ok=a.count>=TARGET,col=ok?'#1a9850':'#c0392b';
      return '<div class="bar"><div class="lab" style="width:210px;white-space:normal" title="'+a.cities+'"><b>'+a.group+'</b>'+
        ' <span style="color:'+(ok?'#7ee0a0':'#ff9a9a')+';font-size:10px">'+(ok?'مكتمل':'باقٍ '+(TARGET-a.count))+'</span>'+
        (a.cities?'<div class="sub">('+a.cities+')</div>':'')+'</div>'+
        '<div class="track"><div class="fill" style="width:'+(a.count/mx*100)+'%;background:'+col+'"></div></div>'+
        '<div class="val" style="color:'+(ok?'#7ee0a0':'#ff9a9a')+'">'+a.count+'</div></div>';}).join('');
    html+='</div>';
  });
  el.innerHTML=html;
}
// خريطة المجموعة->مدنها (من التقسيمة، موحّدة عبر المناطق)
function groupCities(){const m={};Object.keys(STRUCT).forEach(rg=>Object.keys(STRUCT[rg]).forEach(ag=>{
  const s=STRUCT[rg][ag];Object.keys(s).forEach(g=>{m[g]=[...new Set((m[g]||[]).concat(s[g]))];});}));return m;}
function allGroupsCard(el){
  // كل المجموعات مرتّبة بالفئات ثم المجموعات (لكل فئة: مجموعاتها وحالتها)
  const om=groupOffSet();
  let html='<h3>حالة المجموعات حسب الفئة العمرية'+(curRegion==='الكل'?'':' — '+curRegion)+(curSifas.length?' — '+curSifas.join('، '):'')+' (المطلوب: '+TARGET+' لكل مجموعة)</h3>';
  DATA.ages.forEach(age=>{
    let struct;
    if(curRegion==='الكل'){struct={};Object.keys(STRUCT).forEach(rg=>{const s=STRUCT[rg][age];if(s)Object.keys(s).forEach(g=>{struct[g]=s[g];});});}
    else struct=(STRUCT[curRegion]&&STRUCT[curRegion][age])||{};
    const cnt={};filtered().filter(r=>r.age===age).forEach(r=>cnt[r.group]=(cnt[r.group]||0)+r.count);
    let arr=Object.keys(struct).map(g=>({group:g,count:cnt[g]||0,cities:struct[g].join('، ')}));
    Object.keys(cnt).forEach(g=>{if(!struct[g]&&cnt[g]>0)arr.push({group:g,count:cnt[g],cities:''});});
    if(!arr.length)return;
    arr.sort((a,b)=>b.count-a.count);
    const mx=Math.max(TARGET,1,...arr.map(a=>a.count)), doneN=arr.filter(a=>a.count>=TARGET).length;
    html+='<div style="margin-top:14px"><div style="color:#ffd166;font-weight:700;margin-bottom:6px;font-size:14px;border-top:1px solid #1c3a5e;padding-top:10px">'+age+' <span style="color:#9fb6d0;font-size:11px;font-weight:400">('+doneN+'/'+arr.length+' مكتملة)</span></div>';
    html+=arr.map(a=>{const ok=a.count>=TARGET,col=ok?'#1a9850':'#c0392b',shared=[...(om[a.group]||[])];
      return '<div class="bar"><div class="lab" style="width:240px;white-space:normal" title="'+a.cities+'"><b>'+a.group+'</b>'+
        ' <span style="color:'+(ok?'#7ee0a0':'#ff9a9a')+';font-size:10px">'+(ok?'مكتمل':'باقٍ '+(TARGET-a.count))+'</span>'+
        (shared.length>1?' <span style="background:#8e6b1f;color:#ffe9a8;font-size:10px;border-radius:8px;padding:1px 6px">🔗 '+shared.join('، ')+'</span>':'')+
        (a.cities?'<div class="sub">('+a.cities+')</div>':'')+'</div>'+
        '<div class="track"><div class="fill" style="width:'+(a.count/mx*100)+'%;background:'+col+'"></div></div>'+
        '<div class="val" style="color:'+(ok?'#7ee0a0':'#ff9a9a')+'">'+a.count+'</div></div>';}).join('');
    html+='</div>';
  });
  el.innerHTML=html;
}
// المجموعة -> مكاتب فرقها (من التسجيل). أكثر من مكتب = مشتركة
function groupOffSet(){const m={};DATA.rows.forEach(r=>{const o=(r.office||'');if(o&&r.count>0){(m[r.group]=m[r.group]||new Set()).add(o);}});return m;}
function officePanel(el){
  const gc=groupCities(), om=groupOffSet();
  const tot={};DATA.rows.forEach(r=>{tot[r.group]=(tot[r.group]||0)+r.count;}); // إجمالي كل مجموعة (لمعرفة الفارغة)
  let html='<h3>مجموعات مكتب '+curOffice+' حسب الفئة العمرية'+(curSifas.length?' — '+curSifas.join('، '):'')+(curRegion==='الكل'?'':' · '+curRegion)+' (المطلوب: '+TARGET+' لكل مجموعة)</h3>';
  DATA.ages.forEach(age=>{
    const cnt={};DATA.rows.filter(r=>(r.office||'')===curOffice&&r.age===age&&sifaMatch(r)&&(curRegion==='الكل'||r.region===curRegion)).forEach(r=>cnt[r.group]=(cnt[r.group]||0)+r.count);
    let arr=Object.keys(cnt).filter(g=>cnt[g]>0).map(g=>({group:g,count:cnt[g],cities:(gc[g]||[]).join('، '),
      shared:[...(om[g]||[])].filter(o=>o!==curOffice)}));
    // كل مجموعات هذا المكتب في هذه الفئة (من جدول المجموعة→المكتب) — تظهر بصفر حيث لا فرق
    if(curRegion==='الكل'&&!curSifas.length){
      [...new Set(Object.values(C2G[age]||{}))].forEach(g=>{if(GROFF[g]===curOffice&&!cnt[g])
        arr.push({group:g,count:0,cities:(gc[g]||[]).join('، '),shared:[...(om[g]||[])].filter(o=>o!==curOffice)});});
    }
    if(!arr.length)return;
    arr.sort((a,b)=>b.count-a.count);
    const mx=Math.max(TARGET,1,...arr.map(a=>a.count));
    html+='<div style="margin-top:14px"><div style="color:#ffd166;font-weight:700;margin-bottom:6px;font-size:14px;border-top:1px solid #1c3a5e;padding-top:10px">'+age+'</div>';
    html+=arr.map(a=>{const ok=a.count>=TARGET,col=ok?'#1a9850':'#c0392b';
      return '<div class="bar"><div class="lab" style="width:230px;white-space:normal" title="'+a.cities+'"><b>'+a.group+'</b>'+
        ' <span style="color:'+(ok?'#7ee0a0':'#ff9a9a')+';font-size:10px">'+(ok?'مكتمل':'باقٍ '+(TARGET-a.count))+'</span>'+
        (a.shared.length?' <span style="background:#8e6b1f;color:#ffe9a8;font-size:10px;border-radius:8px;padding:1px 6px">🔗 مشترك مع: '+a.shared.join('، ')+'</span>':'')+
        (a.cities?'<div class="sub">('+a.cities+')</div>':'')+'</div>'+
        '<div class="track"><div class="fill" style="width:'+(a.count/mx*100)+'%;background:'+col+'"></div></div>'+
        '<div class="val" style="color:'+(ok?'#7ee0a0':'#ff9a9a')+'">'+a.count+'</div></div>';}).join('');
    html+='</div>';
  });
  el.innerHTML=html;
}
function render(){
  const rows=filtered();
  const total=rows.reduce((s,r)=>s+r.count,0);
  const parts=[curAge==='الكل'?'جميع الفئات':curAge, sifaLabel(), curRegion==='الكل'?'كل المناطق':curRegion];
  if(curOffice!=='الكل')parts.push(curOffice);
  document.getElementById('kpis').innerHTML=kpi(total,'مجموع الفِرَق — '+parts.join(' · '));
  const isAll=(curAge==='الكل');
  // المخططات العلوية (فئة + منطقة) تظهر في صفحة الكل فقط
  document.getElementById('topcharts').style.display=isAll?'grid':'none';
  document.getElementById('agecard').style.display=isAll?'block':'none';
  const showReg=isAll&&curRegion==='الكل';
  document.getElementById('regcard').style.display=showReg?'block':'none';
  document.getElementById('agecard').style.gridColumn=showReg?'':'1 / -1';
  if(isAll){ barChart(document.getElementById('byage'),ageChartData(),{sort:false,color:'linear-gradient(90deg,#8e44ad,#c874f0)'});
    if(showReg)barChart(document.getElementById('byregion'),agg(rows,'region'),{color:'linear-gradient(90deg,#16a085,#2ee6b6)'}); }
  // مخطط الصفة يظهر فقط عند اختيار «كل الصفات»
  const showSifa=(curSifas.length===0);
  document.getElementById('sifacard').style.display=showSifa?'block':'none';
  if(showSifa)barChart(document.getElementById('bysifa'),agg(base(),'sifa'),{color:'linear-gradient(90deg,#d68910,#f5b041)'});
  // مخطط مكاتب الوزارة — يظهر في صفحة الكل عند وجود مكاتب واختيار «كل المكاتب»
  const showOff=isAll&&(DATA.offices||[]).length&&curOffice==='الكل';
  document.getElementById('offcard').style.display=showOff?'block':'none';
  if(showOff)barChart(document.getElementById('byoffice'),agg(base(),'office'),{color:'linear-gradient(90deg,#16a085,#2ee6b6)'});
  // مخطط المجموعة (لفئة محددة فقط)
  document.getElementById('grpcard').style.display=isAll?'none':'block';
  if(!isAll){document.getElementById('grph').textContent='الفِرَق بحسب المجموعة — '+curAge+(curRegion==='الكل'?'':' · '+curRegion)+' (المطلوب: '+TARGET+' فِرَق لكل مجموعة)';
    groupChart(document.getElementById('bygroup'));}
  // صفحة المنطقة: كل الفئات ومجموعاتها (عند اختيار منطقة والفئة=الكل)
  const rp=document.getElementById('regionPanel');
  if(curRegion!=='الكل'&&isAll){rp.style.display='block';regionPanel(rp);}else{rp.style.display='none';}
  // صفحة المكتب: مجموعات المكتب المحدّد حسب الفئة (عند اختيار مكتب والفئة=الكل)
  const op=document.getElementById('officePanel');
  if(curOffice!=='الكل'&&isAll){op.style.display='block';officePanel(op);}else{op.style.display='none';}
  // بطاقة المجموعات الفارغة (0 فريق) — في الصفحة الرئيسية
  // بطاقة حالة كل المجموعات — في الصفحة الرئيسية (وضع كل الفئات وكل المكاتب)
  const ec=document.getElementById('emptyCard');
  if(isAll&&curOffice==='الكل'){ec.style.display='block';allGroupsCard(ec);}else{ec.style.display='none';}
  renderTable();
}
function renderTable(){
  const showG=curAge!=='الكل';
  const gc=document.querySelector('#citytbl th.grpcol');if(gc)gc.style.display=showG?'':'none';
  const gf=document.getElementById('gfilter');
  const q=(document.getElementById('csearch').value||'').trim();
  let rows;
  if(showG&&groupFilter){ rows=filtered().filter(r=>r.group===groupFilter);
    gf.innerHTML='<span class="chip" onclick="clearGF()">مُدن مجموعة «'+groupFilter+'» — إظهار الكل ✕</span>'; }
  else { gf.innerHTML=''; rows=filtered().filter(r=>r.count>0); }
  // دمج الصفوف: عند فئة محددة نجمع حسب (المدينة+المجموعة+المنطقة)، وإلا حسب المدينة فقط
  if(showG){const m={};rows.forEach(r=>{const k=r.city+'|'+r.group+'|'+r.region;
      if(!m[k])m[k]={city:r.city,group:r.group,region:r.region,count:0};m[k].count+=r.count;});rows=Object.values(m);}
  else {const m={};rows.forEach(r=>{const k=r.city;if(!m[k])m[k]={city:r.city,region:r.region,count:0};m[k].count+=r.count;});rows=Object.values(m);}
  if(q)rows=rows.filter(r=>(r.city+r.region+(r.group||'')).indexOf(q)>=0);
  const sk=(!showG&&sortK==='group')?'count':sortK;
  rows.sort((a,b)=>{const x=a[sk],y=b[sk];return (x>y?1:x<y?-1:0)*sortDir;});
  document.querySelector('#citytbl tbody').innerHTML=rows.map(r=>
    '<tr><td>'+r.city+'</td><td class="muted">'+r.region+'</td>'+(showG?'<td>'+(r.group||'')+'</td>':'')+'<td class="num">'+r.count+'</td></tr>').join('')
    ||'<tr><td colspan="'+(showG?4:3)+'" class="muted">لا نتائج.</td></tr>';
}
function clearGF(){groupFilter=null;renderTable();}
document.querySelectorAll('#citytbl th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;
  if(sortK===k)sortDir*=-1;else{sortK=k;sortDir=(k==='count')?-1:1;}renderTable();});
document.getElementById('csearch').oninput=()=>{groupFilter=null;renderTable();};

function tabs(el,items,cur,fn){el.innerHTML='';items.forEach(it=>{const b=document.createElement('button');
  b.className='tab'+(it===cur?' on':'');b.textContent=it;b.onclick=()=>fn(it);el.appendChild(b);});}
function sifaTabs(){ // فلتر الصفة متعدّد الاختيار: «الكل» يمسح التحديد، وكل صفة تُبدَّل بالضغط
  const el=document.getElementById('sifaT');el.innerHTML='';
  const mk=(txt,on,fn)=>{const b=document.createElement('button');b.className='tab'+(on?' on':'');
    b.textContent=txt;b.onclick=fn;el.appendChild(b);};
  mk('الكل',curSifas.length===0,()=>{curSifas=[];buildFilters();render();});
  DATA.sifas.forEach(s=>mk(s,curSifas.includes(s),()=>{
    const i=curSifas.indexOf(s);if(i>=0)curSifas.splice(i,1);else curSifas.push(s);
    buildFilters();render();}));
}
function buildFilters(){
  tabs(document.getElementById('ageT'),['الكل',...DATA.ages],curAge,a=>{curAge=a;groupFilter=null;buildFilters();render();});
  sifaTabs();
  const rg=document.getElementById('rgn');
  rg.innerHTML='<option value="الكل">كل المناطق</option>'+DATA.regions.map(r=>'<option'+(r===curRegion?' selected':'')+'>'+r+'</option>').join('');
  rg.onchange=()=>{curRegion=rg.value;groupFilter=null;buildFilters();render();};
  // فلتر مكتب الوزارة — يظهر فقط عند وجود مكاتب مُدخلة
  const offs=DATA.offices||[];const offFlt=document.getElementById('offFlt');
  if(offs.length){offFlt.style.display='';const os=document.getElementById('off');
    os.innerHTML='<option value="الكل">كل المكاتب</option>'+offs.map(o=>'<option'+(o===curOffice?' selected':'')+'>'+o+'</option>').join('');
    os.onchange=()=>{curOffice=os.value;groupFilter=null;buildFilters();render();};}
  else{offFlt.style.display='none';curOffice='الكل';}
}
// ===== تحديث من إكسل (يعيد البناء من صفحة بيانات التسجيل) =====
const CANON={'جيزان':'جازان'}, SIFA={'هواة':'هواة','اكاديمية':'أكاديمية','اكاديمة':'أكاديمية','نادي':'نادي','نالدي خاص':'نادي'};
const _fileInp=document.getElementById('file');
if(_fileInp)_fileInp.onchange=e=>{const f=e.target.files[0];if(!f)return;
  const rd=new FileReader();rd.onload=ev=>{try{
    const wb=XLSX.read(ev.target.result,{type:'array'});
    const ws=wb.Sheets['بيانات التسجيل'];if(!ws){alert('لم أجد صفحة «بيانات التسجيل»');return;}
    const A=XLSX.utils.sheet_to_json(ws,{header:1});
    let hi=A.findIndex(r=>r&&r.indexOf('الصفة')>=0);const H={};A[hi].forEach((c,j)=>{if(c)H[String(c).trim()]=j;});
    const agecols=Object.keys(H).filter(k=>k.indexOf('المشاركة')>=0);
    const rows=[],ages=[],sifset=new Set(),regset=new Set(),offset=new Set();
    for(let i=hi+1;i<A.length;i++){const r=A[i];if(!r||!r.length)continue;
      let sifa=SIFA[String(r[H['الصفة']]||'').trim()]||(r[H['الصفة']]?String(r[H['الصفة']]).trim():'غير محدد');
      let city=String(r[H['المدينة']]||'').trim();city=CANON[city]||city;
      let office=(H['مكتب الوزارة']!=null&&r[H['مكتب الوزارة']]!=null)?String(r[H['مكتب الوزارة']]).trim():'';
      agecols.forEach(cn=>{const v=r[H[cn]];if(typeof v!=='number'||v<=0)return;
        const age='تحت '+cn.replace(/\D/g,'');const grp=(C2G[age]&&C2G[age][city])||'(غير مصنّف)';
        const region=REG[city]||'غير محدد';
        rows.push({age,city:city||'غير محدد',group:grp,region,sifa,office,count:v});
        if(ages.indexOf(age)<0)ages.push(age);sifset.add(sifa);regset.add(region);if(office)offset.add(office);});}
    ages.sort((x,y)=>(+x.replace(/\D/g,''))-(+y.replace(/\D/g,'')));
    DATA={rows,ages,sifas:['هواة','نادي','أكاديمية'].filter(s=>sifset.has(s)),offices:[...offset].sort(),
      regions:[...regset].filter(r=>r!=='غير محدد').sort().concat(regset.has('غير محدد')?['غير محدد']:[]),target:TARGET};
    curAge='الكل';curSifas=[];curRegion='الكل';curOffice='الكل';groupFilter=null;buildFilters();render();
    document.getElementById('updated').textContent='حُدِّثت البيانات من ملفك';
  }catch(err){alert('تعذّر قراءة الملف: '+err.message);}};
  rd.readAsArrayBuffer(f);};
// ===== زر تنزيل صورة ملخص المكاتب × الفئات (canvas — بدون مكتبات) =====
function drawSummaryImage(){
  const ages=DATA.ages.slice(); // تصاعدي تحت5..تحت14
  const rows=DATA.rows.filter(r=>sifaMatch(r)&&(curRegion==='الكل'||r.region===curRegion)&&r.office);
  const cell={},offTot={},ageTot={};let grand=0;ages.forEach(a=>ageTot[a]=0);
  rows.forEach(r=>{const o=r.office;(cell[o]=cell[o]||{})[r.age]=((cell[o]||{})[r.age]||0)+r.count;
    offTot[o]=(offTot[o]||0)+r.count;ageTot[r.age]=(ageTot[r.age]||0)+r.count;grand+=r.count;});
  const offices=Object.keys(offTot).sort((a,b)=>offTot[b]-offTot[a]);
  if(!offices.length){alert('لا توجد بيانات مكاتب للعرض');return;}
  const S=2,PAD=24,titleH=66,headH=54,rowH=44,footH=50,totalW=120,ageW=104,offW=220;
  const AGE_TARGET={'تحت 5':510,'تحت 7':510,'تحت 9':510,'تحت 11':276,'تحت 12':276,'تحت 13':276,'تحت 14':276};
  const W=PAD*2+totalW+ages.length*ageW+offW, H=PAD*2+titleH+headH+offices.length*rowH+footH*2;
  const cv=document.createElement('canvas');cv.width=W*S;cv.height=H*S;const ctx=cv.getContext('2d');ctx.scale(S,S);
  const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#0a3d2a');g.addColorStop(1,'#062015');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.textBaseline='middle';
  const _mo=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
  const _d=new Date(),dateStr=_d.getDate()+' '+_mo[_d.getMonth()]+' '+_d.getFullYear();
  ctx.fillStyle='#ffd166';ctx.font='800 26px Tajawal, sans-serif';ctx.textAlign='right';
  ctx.fillText('ملخص الفِرَق حسب المكتب والفئة العمرية — حتى '+dateStr+(curRegion==='الكل'?'':' — '+curRegion)+(curSifas.length?' — '+curSifas.join('، '):''),W-PAD,PAD+titleH/2);
  const xs=[];let x=PAD;xs.push([x,totalW]);x+=totalW;ages.forEach(()=>{xs.push([x,ageW]);x+=ageW;});xs.push([x,offW]);
  const last=xs.length-1, hy=PAD+titleH;
  function rect(ci,y,h,bg){const c=xs[ci];ctx.fillStyle=bg;ctx.fillRect(c[0],y,c[1],h);ctx.strokeStyle='#14442f';ctx.lineWidth=1;ctx.strokeRect(c[0],y,c[1],h);}
  function txt(ci,y,h,t,color,align,font){const c=xs[ci];ctx.fillStyle=color;ctx.font=font;ctx.textAlign=align;
    const tx=align==='center'?c[0]+c[1]/2:align==='right'?c[0]+c[1]-10:c[0]+10;ctx.fillText(''+t,tx,y+h/2);}
  const heads=['المجموع',...ages,'المكتب/الفرع'];
  heads.forEach((l,ci)=>{rect(ci,hy,headH,ci===last?'#093a26':'#0d6b45');txt(ci,hy,headH,l,'#fff','center','800 17px Tajawal, sans-serif');});
  offices.forEach((o,ri)=>{const y=hy+headH+ri*rowH;
    xs.forEach((_,ci)=>rect(ci,y,rowH,ri%2?'#0c2c1e':'#0a2417'));
    txt(last,y,rowH,o,'#eafff3','right','700 17px Tajawal, sans-serif');
    ages.forEach((a,ai)=>{const n=(cell[o]&&cell[o][a])||0;txt(1+ai,y,rowH,n,n?'#dbeee3':'#4f7a63','center','16px Tajawal, sans-serif');});
    rect(0,y,rowH,'#124a30');txt(0,y,rowH,offTot[o],'#ffd166','center','800 17px Tajawal, sans-serif');});
  const fy=hy+headH+offices.length*rowH;
  xs.forEach((_,ci)=>rect(ci,fy,footH,'#0d6b45'));
  txt(last,fy,footH,'المجموع','#ffd166','right','800 17px Tajawal, sans-serif');
  ages.forEach((a,ai)=>txt(1+ai,fy,footH,ageTot[a],'#ffd166','center','800 17px Tajawal, sans-serif'));
  rect(0,fy,footH,'#ffd166');txt(0,fy,footH,grand,'#04150e','center','800 18px Tajawal, sans-serif');
  // صف المُستهدَف
  const ty=fy+footH;let tg=0;ages.forEach(a=>tg+=(AGE_TARGET[a]||0));
  xs.forEach((_,ci)=>rect(ci,ty,footH,'#7a5f00'));
  txt(last,ty,footH,'المُستهدَف','#ffe9a8','right','800 17px Tajawal, sans-serif');
  ages.forEach((a,ai)=>txt(1+ai,ty,footH,(AGE_TARGET[a]||0),'#ffe9a8','center','800 17px Tajawal, sans-serif'));
  rect(0,ty,footH,'#b8860b');txt(0,ty,footH,tg,'#1a1400','center','800 18px Tajawal, sans-serif');
  const a=document.createElement('a');a.download='ملخص-المكاتب-والفئات.png';a.href=cv.toDataURL('image/png');a.click();
}
const _dl=document.getElementById('dlSum');
if(_dl)_dl.onclick=()=>{ if(document.fonts&&document.fonts.ready){document.fonts.ready.then(drawSummaryImage);}else{drawSummaryImage();} };
// ===== مقارنة اليوم بأمس =====
function cmpRender(){
  const el=document.getElementById('cmpCard');
  if(!PREV){el.innerHTML='<h3>📈 مقارنة اليوم بأمس</h3><div class="muted">لا توجد لقطة أمس للمقارنة بعد — ستتوفّر المقارنة اعتبارًا من اليوم التالي.</div>';return;}
  const today={};DATA.rows.forEach(r=>{if(r.count){const k=r.group+'|'+r.age;today[k]=(today[k]||0)+r.count;}});
  const prev=PREV.byGA||{};
  let tTot=0,pTot=0;Object.values(today).forEach(v=>tTot+=v);Object.values(prev).forEach(v=>pTot+=v);
  const ageInc={};DATA.ages.forEach(a=>ageInc[a]=0);
  const keys=new Set([...Object.keys(today),...Object.keys(prev)]);const done=[];
  keys.forEach(k=>{const i=k.lastIndexOf('|');const g=k.slice(0,i),a=k.slice(i+1);const t=today[k]||0,p=prev[k]||0;
    if(ageInc[a]===undefined)ageInc[a]=0;ageInc[a]+=(t-p);
    if(t>=TARGET&&p<TARGET)done.push({group:g,age:a,count:t,prev:p});});
  done.sort((x,y)=>DATA.ages.indexOf(x.age)-DATA.ages.indexOf(y.age)||(x.group<y.group?-1:1));
  const inc=tTot-pTot;
  let html='<h3>📈 مقارنة اليوم ('+TODAY+') بأمس ('+PREV.date+')</h3>';
  html+='<div class="kpis"><div class="kpi"><div class="n" style="color:'+(inc>=0?'#7ee0a0':'#ff9a9a')+'">'+(inc>=0?'+':'')+inc+'</div><div class="l">زيادة الفِرَق عن أمس · اليوم '+tTot+' مقابل '+pTot+'</div></div>'+
    '<div class="kpi"><div class="n" style="color:#7ee0a0">'+done.length+'</div><div class="l">مجموعات اكتملت اليوم (لم تكن مكتملة أمس)</div></div></div>';
  html+='<div style="margin:4px 0 14px;display:flex;flex-wrap:wrap;gap:6px">'+DATA.ages.map(a=>{const v=ageInc[a]||0;
    return '<span style="font-size:12px;border-radius:8px;padding:3px 9px;background:'+(v>0?'#14532a':v<0?'#5a1e1e':'#16314f')+';color:'+(v>0?'#8ff0b0':v<0?'#ff9a9a':'#cfe0f0')+'">'+a+': '+(v>0?'+':'')+v+'</span>';}).join('')+'</div>';
  html+='<h3 style="font-size:14px">المجموعات التي اكتملت اليوم</h3>';
  html+=done.length?done.map(d=>'<div class="bar"><div class="lab" style="width:250px;white-space:normal"><b>'+d.group+'</b> <span style="color:#9fb6d0;font-size:11px">'+d.age+'</span></div>'+
    '<div class="track"><div class="fill" style="width:100%;background:#1a9850"></div></div>'+
    '<div class="val" style="color:#7ee0a0">'+d.count+'</div></div>').join(''):'<div class="muted">لا توجد مجموعات جديدة اكتملت اليوم.</div>';
  el.innerHTML=html;
}
const _cmp=document.getElementById('cmpBtn');
if(_cmp)_cmp.onclick=()=>{const c=document.getElementById('cmpCard');const show=(c.style.display==='none'||!c.style.display);
  c.style.display=show?'block':'none';if(show){cmpRender();c.scrollIntoView({behavior:'smooth',block:'start'});}};
buildFilters();render();
</script></body></html>"""

# ===== لقطة يومية للمقارنة (اليوم مقابل أمس) =====
_SNAP = "/home/user/khitba/cluster_analysis/snapshots.json"
_today = datetime.date.today().isoformat()
_cur = {}
for _r in D["rows"]:
    if _r["count"]:
        _k = _r["group"] + "|" + _r["age"]
        _cur[_k] = _cur.get(_k, 0) + _r["count"]
_snaps = json.load(open(_SNAP, encoding="utf-8")) if os.path.exists(_SNAP) else {}
_prev_dates = sorted(d for d in _snaps if d < _today)
_prev_date = _prev_dates[-1] if _prev_dates else None
_prev = _snaps.get(_prev_date) if _prev_date else None
_snaps[_today] = _cur
json.dump(_snaps, open(_SNAP, "w", encoding="utf-8"), ensure_ascii=False)
_PREV = {"date": _prev_date, "byGA": _prev} if _prev is not None else None

HTML = HTML.replace("__PREV__", json.dumps(_PREV, ensure_ascii=False))
HTML = HTML.replace("__TODAY__", json.dumps(_today, ensure_ascii=False))
HTML = HTML.replace("__DATA__", json.dumps(D, ensure_ascii=False))
HTML = HTML.replace("__C2G__", json.dumps(MAPS["C2G"], ensure_ascii=False))
HTML = HTML.replace("__REG__", json.dumps(MAPS["REG"], ensure_ascii=False))
HTML = HTML.replace("__STRUCT__", json.dumps(MAPS["STRUCT"], ensure_ascii=False))
HTML = HTML.replace("__GROFF__", json.dumps(MAPS.get("GROFF", {}), ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/dashboard.html", "w", encoding="utf-8").write(HTML)
print("saved dashboard.html", len(HTML), "bytes")

# ===== نسخة العرض فقط بالهوية الخضراء للاتحاد =====
VIEW = HTML
VIEW = VIEW.replace("<title>لوحة الفِرَق المسجَّلة</title>",
                    "<title>بيانات الفرق المسجلة — بطولات الواعدين والبراعم 26/27</title>")
VIEW = VIEW.replace("<h1>📊 لوحة الفِرَق المسجَّلة</h1>",
                    "<h1>بيانات الفرق المسجلة في بطولات الواعدين والبراعم لموسم 26/27</h1>")
# إزالة زرّي الإكسل والخريطة (regex متين ضد اختلاف الإيموجي)
import re as _re
VIEW = _re.sub(r'<label class="btn g"[^>]*>.*?id="file".*?</label>', "", VIEW, flags=_re.S)
VIEW = _re.sub(r'<a class="btn" href="\./">[^<]*</a>', "", VIEW)
# لوح الألوان الأخضر (هوية الاتحاد)
GREEN = {
 "#0b1c30": "#04150e", "#0a3d62": "#006C35", "#12283f": "#0b3524",
 "#1c3a5e": "#12563a", "#16314f": "#0d4b32", "#2a4a6e": "#1c7a52",
 "#1b6ca8": "#0a7d43", "#2980b9": "#0aa257", "#3aa0e0": "#2ecc71",
 "#13294a": "#0b3524", "#0a5c36": "#006C35",
}
for a, b in GREEN.items():
    VIEW = VIEW.replace(a, b)
open("/home/user/khitba/cluster_analysis/dashboard_view.html", "w", encoding="utf-8").write(VIEW)
print("saved dashboard_view.html", len(VIEW), "bytes")
