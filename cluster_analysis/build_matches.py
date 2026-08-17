#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""matches.html: خريطة مخصّصة — لكل فئة: المجموعات المكتملة (≥6) كنقاط عليها اسمها وعدد مبارياتها.
خيار «جميع الفئات»: كل نقطة تعرض عدد الفرق في كل فئة. + زر جداول (المنطقة←الفئة←المجموعة).
المباريات = دوري من دور واحد: N×(N−1)/2."""
import json
from collections import defaultdict

BASE = "/home/user/khitba/cluster_analysis/"
T = json.load(open(BASE + "teams2.json", encoding="utf-8"))
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
STRUCT = M["STRUCT"]
TARGET = T.get("target", 6)

COORD = {}
try:
    for p in json.load(open(BASE + "points.json", encoding="utf-8")):
        COORD[p["n"]] = (p["lat"], p["lon"])
except Exception:
    pass

gc = defaultdict(set)
greg = {}
for rg in STRUCT:
    for ag in STRUCT[rg]:
        for g, cities in STRUCT[rg][ag].items():
            for c in cities:
                gc[g].add(c)
            greg.setdefault(g, rg)

def centroid(cities):
    pts = [COORD[c] for c in cities if c in COORD]
    if not pts:
        return None
    return [round(sum(p[0] for p in pts) / len(pts), 5),
            round(sum(p[1] for p in pts) / len(pts), 5)]

byga = defaultdict(int)
for r in T["rows"]:
    byga[(r["age"], r["group"])] += r["count"]

# لكل فئة: المجموعات المكتملة
byAge = {}
for age in T["ages"]:
    arr = []
    for (a, g), n in byga.items():
        if a == age and n >= TARGET and g != "(غير مصنّف)":
            ll = centroid(gc.get(g, []))
            arr.append({"group": g, "region": greg.get(g, ""),
                        "cities": "، ".join(sorted(gc.get(g, []))),
                        "n": n, "matches": n * (n - 1) // 2,
                        "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
    arr.sort(key=lambda x: -x["matches"])
    byAge[age] = arr

# «جميع الفئات»: المجموعات المكتملة في فئة واحدة على الأقل، مع عدد الفرق لكل فئة
complete_groups = {x["group"] for age in T["ages"] for x in byAge[age]}
allGroups = []
for g in complete_groups:
    teamsByAge = {a: byga.get((a, g), 0) for a in T["ages"]}
    totMatches = sum(n * (n - 1) // 2 for n in teamsByAge.values() if n >= TARGET)
    ll = centroid(gc.get(g, []))
    allGroups.append({"group": g, "region": greg.get(g, ""),
                      "cities": "، ".join(sorted(gc.get(g, []))),
                      "teamsByAge": teamsByAge, "totalMatches": totMatches,
                      "totalTeams": sum(teamsByAge.values()),
                      "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
allGroups.sort(key=lambda x: -x["totalMatches"])

MDATA = {"ages": T["ages"], "byAge": byAge, "allGroups": allGroups, "target": TARGET}

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>الخريطة وعدد المباريات لكل مجموعة</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#04150e;color:#eafff3}
 .top{background:#006C35;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:1000;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top .logo{height:46px;width:auto;filter:brightness(0) invert(1)}
 .top h1{margin:0;font-size:19px;font-weight:800}
 .wrap{max-width:1200px;margin:0 auto;padding:18px}
 .tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
 .tab{background:#0d4b32;border:1px solid #1c7a52;color:#eafff3;border-radius:20px;padding:7px 16px;
   cursor:pointer;font-family:'Tajawal';font-size:14px;font-weight:700}
 .tab.on{background:#ffd166;color:#04150e;border-color:#ffd166}
 #map{height:560px;border-radius:14px;border:1px solid #12563a;margin-bottom:16px;background:#0b3524}
 .kpis{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px}
 .kpi{background:#0b3524;border:1px solid #12563a;border-radius:12px;padding:14px 20px;flex:1;min-width:200px;text-align:center}
 .kpi .n{font-size:28px;font-weight:800;color:#ffd166}
 .kpi .l{font-size:12.5px;color:#8fdcb4;margin-top:4px}
 .card{background:#0b3524;border:1px solid #12563a;border-radius:12px;padding:16px}
 .card h3{margin:0 0 12px;font-size:15px;color:#ffd166}
 .bar{display:flex;align-items:center;gap:10px;margin-bottom:9px;font-size:13px}
 .bar .lab{width:250px;flex-shrink:0;white-space:normal}
 .bar .lab .sub{font-size:10px;color:#7fbfa0;margin-top:2px;font-weight:400}
 .bar .track{flex:1;background:#04150e;border-radius:6px;height:22px;overflow:hidden}
 .bar .fill{height:100%;background:linear-gradient(90deg,#159a80,#2fe6b8);border-radius:6px;min-width:3px}
 .bar.clk{cursor:pointer;border-radius:8px;padding:4px 6px;margin:1px -6px 8px} .bar.clk:hover{background:#0d4b32}
 .bar .val{width:70px;text-align:center;font-weight:800;color:#ffd166}
 .bar .teams{width:70px;text-align:center;color:#8fdcb4;font-size:12px}
 .muted{color:#8fdcb4;font-size:12px}
 .hd{display:flex;gap:10px;color:#8fdcb4;font-size:11px;font-weight:700;padding:0 0 4px;border-bottom:1px solid #12563a;margin-bottom:8px}
 .hd .a{width:250px}.hd .b{flex:1}.hd .c{width:70px;text-align:center}.hd .d{width:70px;text-align:center}
 .gtip{background:#04150e;border:1px solid #2fe6b8;color:#eafff3;border-radius:8px;font-family:'Tajawal';
   font-size:12px;font-weight:700;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.5);padding:5px 9px;line-height:1.5}
 .gtip b{color:#ffd166;font-size:13px}
 .gtip .ag{color:#8ff0b0;font-size:11px} .gtip .z{color:#6f9a86}
 .gtip:before{display:none}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد" onerror="this.remove()">
 <h1>الخريطة وعدد المباريات لكل مجموعة</h1>
</div>
<div class="wrap">
 <div class="tabs" id="ageT"></div>
 <div id="map"></div>
 <div class="kpis" id="kpis"></div>
 <div class="card"><h3 id="ttl"></h3>
   <div class="hd"><div class="a">المجموعة</div><div class="b"></div><div class="c">الفِرَق</div><div class="d">المباريات</div></div>
   <div id="list"></div>
 </div>
 <div style="margin:14px 0"><button class="tab" id="tblBtn" style="background:#ffd166;color:#04150e;border-color:#ffd166">📋 جداول المباريات (المنطقة ← الفئة ← المجموعة)</button></div>
 <div class="card" id="tablesCard" style="display:none"><h3>جداول المباريات حسب المنطقة ثم الفئة ثم المجموعة (المكتملة فقط)</h3><div id="tables"></div></div>
</div>
<script>
const MD=__MDATA__;
const ALL='جميع الفئات';
const AGES=[ALL].concat(MD.ages);
let cur=ALL;
function arCount(n,one,two,few,many){const m=n%100;
  if(n===1)return one; if(n===2)return two;
  if(m>=3&&m<=10)return n+' '+few; return n+' '+many;}
function nMatch(n){return arCount(n,'مباراة واحدة','مباراتان','مباريات','مباراةً');}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function shortAge(a){return a.replace('تحت ','ت');}
let map=null, layer=null;
try{
  map=L.map('map',{attributionControl:false,zoomControl:true}).setView([24.2,45.5],5.4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:11,minZoom:4}).addTo(map);
  layer=L.layerGroup().addTo(map);
}catch(e){ var _m=document.getElementById('map'); if(_m)_m.style.display='none'; }
function zoomTo(lat,lon){ if(map&&lat!=null){ map.flyTo([lat,lon],9,{duration:.6}); document.getElementById('map').scrollIntoView({behavior:'smooth',block:'center'}); } }
function marker(x,radius,html){
  if(x.lat==null||!layer)return;
  L.circleMarker([x.lat,x.lon],{radius:radius,color:'#04150e',weight:1.5,fillColor:'#2fe6b8',fillOpacity:.9})
   .bindTooltip(html,{permanent:true,direction:'center',className:'gtip'})
   .on('click',function(){zoomTo(x.lat,x.lon);}).addTo(layer);
}
function drawMap(){
  if(!map||!layer)return; layer.clearLayers();
  if(cur===ALL){
    const mx=Math.max(1,...MD.allGroups.map(x=>x.totalMatches));
    MD.allGroups.forEach(x=>{
      const ages=MD.ages.filter(a=>x.teamsByAge[a]>0)
        .map(a=>'<div class="ag">'+a+': '+nTeam(x.teamsByAge[a])+'</div>').join('');
      marker(x,7+11*(x.totalMatches/mx),'<b>'+x.group.replace('مجموعة ','')+'</b>'+(ages||'<div class="z">لا فرق</div>'));
    });
  } else {
    const arr=MD.byAge[cur]||[]; const mx=Math.max(1,...arr.map(x=>x.matches));
    arr.forEach(x=>marker(x,7+10*(x.matches/mx),'<b>'+x.group.replace('مجموعة ','')+'</b><br>'+nMatch(x.matches)));
  }
}
function render(){
  document.getElementById('ageT').innerHTML=AGES.map(a=>'<button class="tab'+(a===cur?' on':'')+'" data-a="'+a+'">'+a+'</button>').join('');
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{cur=b.dataset.a;render();});
  const K=document.getElementById('kpis'), L2=document.getElementById('list');
  if(cur===ALL){
    const g=MD.allGroups, totM=g.reduce((s,x)=>s+x.totalMatches,0), totT=g.reduce((s,x)=>s+x.totalTeams,0);
    K.innerHTML='<div class="kpi"><div class="n">'+g.length+'</div><div class="l">مجموعات مكتملة</div></div>'+
      '<div class="kpi"><div class="n">'+totT+'</div><div class="l">مجموع الفِرَق</div></div>'+
      '<div class="kpi"><div class="n">'+totM+'</div><div class="l">مجموع المباريات</div></div>';
    document.getElementById('ttl').textContent='المجموعات المكتملة — جميع الفئات';
    const mx=Math.max(1,...g.map(x=>x.totalMatches));
    L2.innerHTML=g.map(x=>{
      const ages=MD.ages.filter(a=>x.teamsByAge[a]>0).map(a=>a+': '+nTeam(x.teamsByAge[a])).join('<br>');
      return '<div class="bar clk" data-lat="'+x.lat+'" data-lon="'+x.lon+'"><div class="lab"><b>'+x.group+'</b>'+(x.region?' <span class="muted">'+x.region+'</span>':'')+
        '<div class="sub">'+ages+'</div></div>'+
        '<div class="track"><div class="fill" style="width:'+(x.totalMatches/mx*100)+'%"></div></div>'+
        '<div class="teams">'+x.totalTeams+'</div><div class="val">'+x.totalMatches+'</div></div>';}).join('');
  } else {
    const arr=MD.byAge[cur]||[], totM=arr.reduce((s,x)=>s+x.matches,0), totT=arr.reduce((s,x)=>s+x.n,0);
    K.innerHTML='<div class="kpi"><div class="n">'+arr.length+'</div><div class="l">مجموعات مكتملة</div></div>'+
      '<div class="kpi"><div class="n">'+totT+'</div><div class="l">مجموع الفِرَق</div></div>'+
      '<div class="kpi"><div class="n">'+totM+'</div><div class="l">مجموع المباريات</div></div>';
    document.getElementById('ttl').textContent='المجموعات المكتملة — '+cur;
    const mx=Math.max(1,...arr.map(x=>x.matches));
    L2.innerHTML=arr.length?arr.map(x=>
      '<div class="bar clk" data-lat="'+x.lat+'" data-lon="'+x.lon+'"><div class="lab"><b>'+x.group+'</b>'+(x.region?' <span class="muted">'+x.region+'</span>':'')+
        (x.cities?'<div class="sub">('+x.cities+')</div>':'')+'</div>'+
      '<div class="track"><div class="fill" style="width:'+(x.matches/mx*100)+'%"></div></div>'+
      '<div class="teams">'+nTeam(x.n)+'</div><div class="val">'+x.matches+'</div></div>').join(''):'<div class="muted">لا توجد مجموعات مكتملة في هذه الفئة بعد.</div>';
  }
  document.querySelectorAll('#list .bar.clk').forEach(b=>b.onclick=()=>{
    const la=parseFloat(b.dataset.lat), lo=parseFloat(b.dataset.lon);
    if(!isNaN(la))zoomTo(la,lo);
  });
  drawMap();
}
function buildTables(){
  const R={};
  MD.ages.forEach(age=>{(MD.byAge[age]||[]).forEach(x=>{
    (R[x.region]=R[x.region]||{});(R[x.region][age]=R[x.region][age]||[]).push(x);});});
  const regions=Object.keys(R).sort();let html='';let grand=0;
  regions.forEach(rg=>{
    let regTot=0;let sec='<div style="margin-top:16px"><div style="color:#ffd166;font-weight:800;font-size:15px;border-top:1px solid #12563a;padding-top:10px">'+rg+'</div>';
    MD.ages.forEach(age=>{const gs=R[rg][age];if(!gs||!gs.length)return;
      const at=gs.reduce((s,x)=>s+x.matches,0);regTot+=at;
      sec+='<div style="margin:8px 0 3px;color:#8fdcb4;font-weight:700">'+age+' <span style="color:#7fbfa0;font-size:11px">('+nMatch(at)+')</span></div>';
      sec+='<table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:4px">';
      gs.slice().sort((a,b)=>b.matches-a.matches).forEach(x=>{
        sec+='<tr><td style="padding:4px 8px;border-bottom:1px solid #0d3a26">'+x.group+'</td>'+
             '<td style="padding:4px 8px;border-bottom:1px solid #0d3a26;color:#8fdcb4;width:80px;text-align:center">'+nTeam(x.n)+'</td>'+
             '<td style="padding:4px 8px;border-bottom:1px solid #0d3a26;color:#ffd166;font-weight:700;width:100px;text-align:center">'+nMatch(x.matches)+'</td></tr>';});
      sec+='</table>';});
    sec+='<div style="color:#ffd166;font-weight:800;margin:4px 0 6px">إجمالي مباريات '+rg+': '+nMatch(regTot)+'</div></div>';
    grand+=regTot;html+=sec;});
  return '<div style="color:#eafff3;font-weight:800;margin-bottom:6px">إجمالي المباريات الكلي: '+nMatch(grand)+'</div>'+html;
}
document.getElementById('tblBtn').onclick=function(){
  const c=document.getElementById('tablesCard');const show=(c.style.display==='none'||!c.style.display);
  c.style.display=show?'block':'none';
  if(show){document.getElementById('tables').innerHTML=buildTables();c.scrollIntoView({behavior:'smooth',block:'start'});}
};
render();
setTimeout(()=>{try{map&&map.invalidateSize();}catch(e){}},300);
</script>
</body></html>"""

HTML = HTML.replace("__MDATA__", json.dumps(MDATA, ensure_ascii=False))
open(BASE + "matches.html", "w", encoding="utf-8").write(HTML)
print("saved matches.html", len(HTML), "bytes | مجموعات مكتملة (كل الفئات):", len(allGroups))
