#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة «مكاتب الوزارة» (offices.html) بنمط لوحة بيانات الفرق:
لكل مكتب: مجموعاته (من ربط المجموعة→المكتب في «المدخلات»)، وعدد فرقها،
مقسّمة على المدن (لفئة محددة) أو على الفئات (في «جميع الفئات»)، مع حالة الاكتمال.
المصدر: split_data.json + ربط GROFF من _maps.json."""
import json

BASE = "/home/user/khitba/cluster_analysis/"
S = json.load(open(BASE + "split_data.json", encoding="utf-8"))
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
GROFF = M.get("GROFF", {})

# إضافة المكتب لكل مجموعة (من ربط المجموعة→المكتب)
for age in S["byAge"]:
    for g in S["byAge"][age]:
        g["office"] = GROFF.get(g["group"], "غير محدد")
S["offices"] = sorted({g["office"] for age in S["byAge"] for g in S["byAge"][age]})

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>مكاتب الوزارة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#0b1c30;color:#e9eef5}
 a{color:#7cc4ff;text-decoration:none}
 .top{background:#0a3d62;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:10;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top h1{margin:0;font-size:19px;font-weight:800} .top .sp{flex:1}
 .top .logo{height:46px;width:auto;display:block;flex-shrink:0;filter:brightness(0) invert(1)}
 .btn{background:#1b6ca8;color:#fff;border:0;border-radius:8px;padding:8px 14px;font-family:'Tajawal';
   font-size:13px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
 .btn:hover{background:#2980b9}
 .wrap{max-width:1200px;margin:0 auto;padding:18px}
 .flt{margin-bottom:14px} .flt .lab{font-size:12px;color:#9fb6d0;margin-bottom:5px;font-weight:700}
 .tabs{display:flex;flex-wrap:wrap;gap:8px}
 .tab{background:#16314f;border:1px solid #2a4a6e;color:#e9eef5;border-radius:20px;padding:6px 15px;
   cursor:pointer;font-family:'Tajawal';font-size:13px;font-weight:700}
 .tab.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 select.rgn{padding:8px 12px;border-radius:8px;border:1px solid #2a4a6e;background:#13294a;color:#fff;
   font-family:'Tajawal';font-size:13px;font-weight:700;min-width:200px}
 .kpis{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0 18px}
 .kpi{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:16px 22px;flex:1;min-width:200px;text-align:center}
 .kpi .n{font-size:30px;font-weight:800;color:#ffd166;line-height:1.1}
 .kpi .l{font-size:12.5px;color:#9fb6d0;margin-top:4px}
 .rhd{color:#ffd166;font-weight:800;font-size:16px;border-top:2px solid #1c3a5e;padding:14px 2px 4px;margin-top:12px}
 .rhd:first-of-type{border-top:0;margin-top:0}
 .rhd .rg{color:#8fb3cf;font-size:12.5px;font-weight:700}
 .rhd .rt{color:#9fb6d0;font-size:12.5px;font-weight:700}
 .gcard{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:13px 15px;margin:10px 0}
 .gcard.done{border-color:#2e7d5b}
 .ghead{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:9px}
 .ghead b{font-size:15.5px}
 .badge{font-size:12px;font-weight:800;color:#ffd166}
 .st{font-size:11.5px;font-weight:700;border-radius:8px;padding:2px 9px}
 .st.ok{background:#123a2b;color:#7ee0a0} .st.no{background:#3a1c1c;color:#ff9a9a}
 .crow{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:13px}
 .crow .cn{width:150px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .crow .track{flex:1;background:#0b1c30;border-radius:6px;height:18px;overflow:hidden}
 .crow .fill{height:100%;background:linear-gradient(90deg,#1b6ca8,#3aa0e0);border-radius:6px;min-width:3px}
 .crow .v{width:64px;text-align:center;font-weight:800;color:#ffd166}
 .muted{color:#9fb6d0;font-size:12px}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد السعودي لكرة القدم" onerror="this.remove()">
 <h1>🏛️ مكاتب الوزارة</h1>
 <span class="sp"></span>
 <a class="btn" href="split.html">🧩 تقسيم الفرق</a>
 <a class="btn" href="dashboard.html">📊 بيانات الفرق</a>
 <a class="btn" href="./">🗺️ الخريطة</a>
</div>
<div class="wrap">
 <div class="flt"><div class="lab">الفئة العمرية:</div><div class="tabs" id="ageT"></div></div>
 <div class="flt"><div class="lab">المكتب:</div><select class="rgn" id="rgn"></select></div>
 <div class="flt"><div class="lab">حالة الاكتمال:</div><div class="tabs" id="statT"></div></div>
 <div class="kpis" id="kpis"></div>
 <div id="content"></div>
</div>
<script>
const S=__SPLIT__;
const TARGET=S.target||6;
const ALL='جميع الفئات';
let curAge=ALL, curOffice='الكل', curStatus='الكل';
function arCount(n,one,two,few,many){const m=n%100;
  if(n===1)return one; if(n===2)return two;
  if(m>=3&&m<=10)return n+' '+few; return n+' '+many;}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function nGroup(n){return arCount(n,'مجموعة واحدة','مجموعتان','مجموعات','مجموعة');}
function nCity(n){return arCount(n,'مدينة واحدة','مدينتان','مدن','مدينة');}
function nCat(n){const m=n%100; return (m>=3&&m<=10)?'فئات':'فئة';}

function ageTabs(){
  const AGES=[ALL].concat(S.ages);
  const el=document.getElementById('ageT');
  el.innerHTML=AGES.map(a=>'<button class="tab'+(a===curAge?' on':'')+'" data-a="'+a+'">'+a+'</button>').join('');
  el.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{curAge=b.dataset.a;render();});
}
function allAgesData(){
  const map={};
  S.ages.forEach(age=>{(S.byAge[age]||[]).forEach(g=>{
    const d=map[g.group]||(map[g.group]={region:g.region,office:g.office,cities:{},ages:{}});
    g.cities.forEach(c=>{d.cities[c.city]=(d.cities[c.city]||0)+c.n;});
    d.ages[age]=(d.ages[age]||0)+g.total;});});
  return Object.keys(map).map(grp=>{
    const d=map[grp];
    const ageList=S.ages.filter(a=>a in d.ages);
    const doneAges=ageList.filter(a=>d.ages[a]>=TARGET).length;
    const cities=Object.entries(d.cities).sort((a,b)=>b[1]-a[1]).map(([city,n])=>({city,n}));
    return {group:grp,region:d.region,office:d.office,total:cities.reduce((s,c)=>s+c.n,0),cities:cities,ages:d.ages,
            agesN:ageList.length,doneAges:doneAges,allDone:ageList.length>0&&doneAges===ageList.length};
  }).sort((a,b)=>b.total-a.total);
}
function curData(){ return curAge===ALL?allAgesData():(S.byAge[curAge]||[]).slice(); }
function officeOptions(){
  const arr=curData();
  const offs=[...new Set(arr.map(g=>g.office))].sort();
  const sel=document.getElementById('rgn');
  if(!offs.includes(curOffice))curOffice='الكل';
  sel.innerHTML='<option value="الكل">كل المكاتب</option>'+offs.map(o=>'<option'+(o===curOffice?' selected':'')+'>'+o+'</option>').join('');
  sel.onchange=()=>{curOffice=sel.value;render();};
}
function statusTabs(){
  const opts=['الكل','المكتملة','غير المكتملة'];
  const el=document.getElementById('statT');
  el.innerHTML=opts.map(o=>'<button class="tab'+(o===curStatus?' on':'')+'" data-s="'+o+'">'+o+'</button>').join('');
  el.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{curStatus=b.dataset.s;render();});
}
function officeRegion(gs){ // المنطقة الغالبة لمجموعات المكتب
  const c={}; gs.forEach(g=>{c[g.region]=(c[g.region]||0)+1;});
  return Object.entries(c).sort((a,b)=>b[1]-a[1])[0][0];
}
function render(){
  ageTabs(); officeOptions(); statusTabs();
  const isAll=curAge===ALL;
  const isDone=g=>isAll?g.allDone:(g.total>=TARGET);
  let arr=curData();
  if(curOffice!=='الكل')arr=arr.filter(g=>g.office===curOffice);
  if(curStatus==='المكتملة')arr=arr.filter(isDone);
  else if(curStatus==='غير المكتملة')arr=arr.filter(g=>!isDone(g));
  const done=arr.filter(isDone).length;
  const totTeams=arr.reduce((s,g)=>s+g.total,0);
  const offs=new Set(arr.map(g=>g.office));
  document.getElementById('kpis').innerHTML=
    '<div class="kpi"><div class="n">'+offs.size+'</div><div class="l">عدد المكاتب</div></div>'+
    '<div class="kpi"><div class="n">'+arr.length+'</div><div class="l">عدد المجموعات</div></div>'+
    '<div class="kpi"><div class="n" style="color:#7ee0a0">'+done+'</div><div class="l">'+(isAll?'مكتملة في كل الفئات':'مجموعات مكتملة')+'</div></div>'+
    '<div class="kpi"><div class="n">'+totTeams+'</div><div class="l">مجموع الفِرَق</div></div>';
  // تجميع حسب المكتب
  const R={},order=[];
  arr.forEach(g=>{if(!R[g.office]){R[g.office]=[];order.push(g.office);}R[g.office].push(g);});
  order.sort((a,b)=>R[b].reduce((s,g)=>s+g.total,0)-R[a].reduce((s,g)=>s+g.total,0));
  let html='';
  order.forEach(off=>{
    const gs=R[off]; const rt=gs.reduce((s,g)=>s+g.total,0), rd=gs.filter(isDone).length;
    html+='<div class="rhd">مكتب '+off+' <span class="rg">('+officeRegion(gs)+')</span> <span class="rt">— '+nTeam(rt)+' · '+nGroup(gs.length)+' ('+rd+'/'+gs.length+' مكتملة)</span></div>';
    gs.forEach(g=>{
      const ok=isDone(g);
      const stTxt=isAll
        ?(g.allDone?'مكتملة في كل الفئات':'مكتملة في '+g.doneAges+' من '+g.agesN+' '+nCat(g.agesN))
        :(ok?'مكتمل'+(g.total>TARGET?' (زائد '+(g.total-TARGET)+')':''):'باقٍ '+(TARGET-g.total)+' للوصول إلى '+TARGET);
      html+='<div class="gcard'+(ok?' done':'')+'"><div class="ghead"><b>'+g.group+'</b>'+
        '<span class="badge">'+nTeam(g.total)+'</span>'+
        '<span class="st '+(ok?'ok':'no')+'">'+stTxt+'</span>'+
        '<span class="muted">'+nCity(g.cities.length)+'</span></div>';
      if(isAll){
        const ags=S.ages.filter(a=>g.ages[a]!=null);
        const mxa=Math.max(TARGET,1,...ags.map(a=>g.ages[a]));
        html+=ags.map(a=>{const n=g.ages[a],dn=n>=TARGET;
          return '<div class="crow"><div class="cn">'+a+'</div>'+
            '<div class="track"><div class="fill" style="width:'+(n/mxa*100)+'%;background:'+(dn?'linear-gradient(90deg,#1a9850,#2ecc71)':'linear-gradient(90deg,#c0392b,#e74c3c)')+'"></div></div>'+
            '<div class="v" style="color:'+(dn?'#7ee0a0':'#ff9a9a')+'">'+nTeam(n)+'</div></div>';}).join('');
      } else {
        const mx=Math.max(TARGET,1,...g.cities.map(c=>c.n));
        html+=g.cities.map(c=>'<div class="crow"><div class="cn">'+c.city+'</div>'+
          '<div class="track"><div class="fill" style="width:'+(c.n/mx*100)+'%"></div></div>'+
          '<div class="v">'+nTeam(c.n)+'</div></div>').join('');
      }
      html+='</div>';
    });
  });
  document.getElementById('content').innerHTML=html||'<div class="muted">لا توجد بيانات.</div>';
}
render();
</script>
</body></html>"""

HTML = HTML.replace("__SPLIT__", json.dumps(S, ensure_ascii=False))
open(BASE + "offices.html", "w", encoding="utf-8").write(HTML)
print("saved offices.html", len(HTML), "bytes | مكاتب:", len(S["offices"]))
