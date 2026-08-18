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

# عدد الفرق والمباريات لكل (فئة، مجموعة) — من صفحة «عدد المباريات» في الإكسل مباشرةً
MDATA_SRC = {}
try:
    MDATA_SRC = json.load(open(BASE + "matches_data.json", encoding="utf-8"))
except Exception:
    pass
def teams_of(age, g):
    d = MDATA_SRC.get(age + "|" + g)
    return d["n"] if d else 0
def matches_src(age, g):
    d = MDATA_SRC.get(age + "|" + g)
    return d["m"] if d else 0

byga = defaultdict(int)
for r in T["rows"]:
    byga[(r["age"], r["group"])] += r["count"]

# كل مجموعات كل فئة (من صفحة عدد المباريات) — تظهر إن كانت الفرق ≥6
groups_by_age = defaultdict(list)
for key in MDATA_SRC:
    a, g = key.split("|", 1)
    groups_by_age[a].append(g)

# لكل فئة: المجموعات المكتملة (الفرق والمباريات من الإكسل)
byAge = {}
for age in T["ages"]:
    arr = []
    for g in groups_by_age.get(age, []):
        n = teams_of(age, g)
        if n >= TARGET and g != "(غير مصنّف)":
            ll = centroid(gc.get(g, []))
            arr.append({"group": g, "region": greg.get(g, ""),
                        "cities": "، ".join(sorted(gc.get(g, []))),
                        "n": n, "matches": matches_src(age, g),
                        "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
    arr.sort(key=lambda x: -x["matches"])
    byAge[age] = arr

# «جميع الفئات»: المجموعات المكتملة في فئة واحدة على الأقل، مع الفرق والمباريات لكل فئة
complete_groups = {x["group"] for age in T["ages"] for x in byAge[age]}
allGroups = []
for g in complete_groups:
    teamsByAge = {a: {"n": teams_of(a, g), "m": matches_src(a, g)}
                  for a in T["ages"] if teams_of(a, g) >= TARGET}
    totMatches = sum(v["m"] for v in teamsByAge.values())
    totTeams = sum(v["n"] for v in teamsByAge.values())
    ll = centroid(gc.get(g, []))
    allGroups.append({"group": g, "region": greg.get(g, ""),
                      "cities": "، ".join(sorted(gc.get(g, []))),
                      "teamsByAge": teamsByAge, "totalMatches": totMatches,
                      "totalTeams": totTeams,
                      "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
allGroups.sort(key=lambda x: -x["totalMatches"])

# عدد اللاعبين (للشارت المجمّع في «جميع الفئات») — من players_data.json
PLAYERS_SRC = {}
try:
    PLAYERS_SRC = json.load(open(BASE + "players_data.json", encoding="utf-8"))
except Exception:
    pass
def players_of(age, g):
    d = PLAYERS_SRC.get(age + "|" + g)
    return d["p"] if d else 0

# إجمالي كل فئة (على المجموعات المكتملة): مباريات + لاعبون + فرق
perAge = {}
for age in T["ages"]:
    perAge[age] = {"m": sum(x["matches"] for x in byAge[age]),
                   "p": sum(players_of(age, x["group"]) for x in byAge[age]),
                   "n": sum(x["n"] for x in byAge[age])}

MDATA = {"ages": T["ages"], "byAge": byAge, "allGroups": allGroups,
         "perAge": perAge, "target": TARGET}

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
 .nav{display:flex;gap:8px;margin-bottom:14px}
 .navlink{background:#0b3524;border:1px solid #12563a;color:#eafff3;border-radius:20px;padding:8px 18px;
   text-decoration:none;font-size:14px;font-weight:800}
 .navlink.on{background:#ffd166;color:#04150e;border-color:#ffd166}
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
 .bar .lab{flex:1;min-width:0;white-space:normal}
 .bar .lab .sub{font-size:10px;color:#7fbfa0;margin-top:2px;font-weight:400}
 .bar .track{flex:1;background:#04150e;border-radius:6px;height:22px;overflow:hidden}
 .bar .fill{height:100%;background:linear-gradient(90deg,#159a80,#2fe6b8);border-radius:6px;min-width:3px}
 .bar.clk{cursor:pointer;border-radius:8px;padding:4px 6px;margin:1px -6px 8px} .bar.clk:hover{background:#0d4b32}
 .bar .val{width:70px;text-align:center;font-weight:800;color:#ffd166}
 .bar .teams{width:70px;text-align:center;color:#8fdcb4;font-size:12px}
 .muted{color:#8fdcb4;font-size:12px}
 .row{padding:9px 10px;border-bottom:1px solid #0d3a26;font-size:14px}
 .row.clk{cursor:pointer;border-radius:8px} .row.clk:hover{background:#0d4b32}
 .row b{font-size:15px} .row .tot{color:#ffd166;font-weight:800}
 .row .sub{font-size:11.5px;color:#8ff0b0;margin-top:4px;line-height:1.9;font-weight:500}
 .row .cnames{font-size:11px;color:#7fbfa0;margin-top:3px;font-weight:400;line-height:1.7}
 .rhd{color:#ffd166;font-weight:800;font-size:15px;border-top:1px solid #12563a;padding:10px 2px 6px;margin-top:10px}
 .rhd:first-child{border-top:0;margin-top:0}
 .rhd .rhdt{color:#8fdcb4;font-size:12px;font-weight:700}
 .clegend{font-size:12.5px;color:#8fdcb4;margin-bottom:14px;font-weight:700}
 .clegend .dot{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:middle;margin:0 6px 0 14px}
 .dot.m,.cfill.m{background:#2fe6b8} .dot.p,.cfill.p{background:#ffd166}
 .crow{display:flex;align-items:center;gap:12px;margin-bottom:13px}
 .crow .cage{width:56px;flex-shrink:0;font-weight:800;font-size:13px;color:#eafff3}
 .crow .cbars{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px}
 .cbar{display:flex;align-items:center;gap:8px}
 .cfill{height:15px;border-radius:5px;min-width:3px}
 .cval{font-size:11.5px;font-weight:700;color:#cdeede;white-space:nowrap}
 .trow{padding:7px 10px;border-bottom:1px solid #0d3a26;font-size:13.5px}
 .trow b{font-size:14px} .trow .tot{color:#ffd166;font-weight:800;margin-right:6px}
 .trow .sub{font-size:10.5px;color:#7fbfa0;margin-top:2px;font-weight:400}
 .hd{display:flex;gap:10px;color:#8fdcb4;font-size:11px;font-weight:700;padding:0 0 4px;border-bottom:1px solid #12563a;margin-bottom:8px}
 .hd .a{flex:1}.hd .c{width:70px;text-align:center}.hd .d{width:70px;text-align:center}
 .gtip{background:#04150e;border:1px solid #2fe6b8;color:#eafff3;border-radius:8px;font-family:'Tajawal';
   font-size:12px;font-weight:700;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.5);padding:5px 9px;line-height:1.5}
 .gtip b{color:#ffd166;font-size:13px}
 .gtip .ag{color:#8ff0b0;font-size:11px} .gtip .z{color:#6f9a86}
 .gtip:before{display:none}
 .leaflet-popup-content-wrapper{background:#04150e;color:#eafff3;border:1px solid #2fe6b8;border-radius:10px}
 .leaflet-popup-content{margin:9px 13px;font-family:'Tajawal';font-size:13px;font-weight:700;line-height:1.7;direction:rtl;text-align:right}
 .leaflet-popup-content b{color:#ffd166;font-size:14px}
 .leaflet-popup-content .ag{color:#8ff0b0;font-size:12px}
 .leaflet-popup-tip{background:#04150e;border-right:1px solid #2fe6b8;border-bottom:1px solid #2fe6b8}
 .leaflet-popup-close-button{color:#8fdcb4 !important}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد" onerror="this.remove()">
 <h1>الخريطة وعدد المباريات لكل مجموعة</h1>
</div>
<div class="wrap">
 <nav class="nav">
   <a class="navlink on" href="matches.html">عدد المباريات</a>
   <a class="navlink" href="players.html">عدد اللاعبين</a>
 </nav>
 <div class="tabs" id="ageT"></div>
 <div id="map"></div>
 <div class="kpis" id="kpis"></div>
 <div class="card" id="chartCard" style="display:none;margin-bottom:16px"><h3>تفصيل المباريات لكل فئة</h3><div id="chart"></div></div>
 <div class="card"><h3 id="ttl"></h3>
   <div id="list"></div>
 </div>
</div>
<script>
const MD=__MDATA__;
const ALL='جميع الفئات';
const AGES=[ALL].concat(MD.ages);
let cur=ALL;
function gp(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function arCount(n,one,two,few,many){const m=n%100;
  if(n===1)return one; if(n===2)return two;
  if(m>=3&&m<=10)return gp(n)+' '+few; return gp(n)+' '+many;}
function nMatch(n){return arCount(n,'مباراة واحدة','مباراتان','مباريات','مباراةً');}
function nPlayer(n){return arCount(n,'لاعب واحد','لاعبان','لاعبين','لاعبًا');}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function chartHTML(){
  const ages=MD.ages,P=MD.perAge;
  const mm=Math.max(1,...ages.map(a=>P[a].m));
  return ages.map(a=>{const d=P[a];return '<div class="crow"><div class="cage">'+a+'</div><div class="cbars">'+
      '<div class="cbar"><div class="cfill m" style="width:'+(100*d.m/mm).toFixed(1)+'%"></div><span class="cval">'+nMatch(d.m)+'</span></div>'+
      '</div></div>';}).join('');
}
function shortAge(a){return a.replace('تحت ','ت');}
let map=null, layer=null;
try{
  map=L.map('map',{attributionControl:false,zoomControl:true}).setView([24.2,45.5],5.4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:11,minZoom:4}).addTo(map);
  layer=L.layerGroup().addTo(map);
}catch(e){ var _m=document.getElementById('map'); if(_m)_m.style.display='none'; }
function zoomTo(lat,lon){ if(map&&lat!=null){ map.flyTo([lat,lon],9,{duration:.6}); document.getElementById('map').scrollIntoView({behavior:'smooth',block:'center'}); } }
function marker(x,radius,name,numbers){
  if(x.lat==null||!layer)return;
  const cm=L.circleMarker([x.lat,x.lon],{radius:radius,color:'#04150e',weight:1.5,fillColor:'#2fe6b8',fillOpacity:.9})
   .bindTooltip(name,{permanent:true,direction:'center',className:'gtip'})
   .bindPopup('<b>'+name+'</b>'+(x.region?' <span style="color:#8fdcb4;font-size:11px;font-weight:600">'+x.region+'</span>':'')+'<br>'+numbers,{className:'gpop',maxWidth:260})
   .on('click',function(){zoomTo(x.lat,x.lon);});
  cm.addTo(layer);
}
function drawMap(){
  if(!map||!layer)return; layer.clearLayers();
  if(cur===ALL){
    const mx=Math.max(1,...MD.allGroups.map(x=>x.totalMatches));
    MD.allGroups.forEach(x=>{
      const ages=MD.ages.filter(a=>x.teamsByAge[a])
        .map(a=>{const d=x.teamsByAge[a];return '<div class="ag">'+a+': '+nTeam(d.n)+' — '+nMatch(d.m)+'</div>';}).join('');
      const nums=(ages||'<div class="z">لا فرق</div>')+'<div style="color:#ffd166;margin-top:4px">إجمالي المباريات: '+nMatch(x.totalMatches)+'</div>';
      marker(x,7+11*(x.totalMatches/mx),x.group.replace('مجموعة ',''),nums);
    });
  } else {
    const arr=MD.byAge[cur]||[]; const mx=Math.max(1,...arr.map(x=>x.matches));
    arr.forEach(x=>marker(x,7+10*(x.matches/mx),x.group.replace('مجموعة ',''),
      nTeam(x.n)+' — '+nMatch(x.matches)));
  }
}
function regionSections(items,matchesOf,teamsOf,rowFn){
  const R={},order=[];
  items.forEach(x=>{const r=x.region||'غير محدد';if(!R[r]){R[r]=[];order.push(r);}R[r].push(x);});
  order.sort((a,b)=>R[b].reduce((s,x)=>s+matchesOf(x),0)-R[a].reduce((s,x)=>s+matchesOf(x),0));
  return order.map(r=>{
    const tm=R[r].reduce((s,x)=>s+matchesOf(x),0), tt=R[r].reduce((s,x)=>s+teamsOf(x),0);
    return '<div class="rhd">'+r+' <span class="rhdt">'+nTeam(tt)+' · '+nMatch(tm)+'</span></div>'+R[r].map(rowFn).join('');
  }).join('');
}
function render(){
  document.getElementById('ageT').innerHTML=AGES.map(a=>'<button class="tab'+(a===cur?' on':'')+'" data-a="'+a+'">'+a+'</button>').join('');
  document.querySelectorAll('#ageT .tab').forEach(b=>b.onclick=()=>{cur=b.dataset.a;render();});
  const K=document.getElementById('kpis'), L2=document.getElementById('list');
  const CC=document.getElementById('chartCard');
  if(cur===ALL){CC.style.display='block';document.getElementById('chart').innerHTML=chartHTML();}
  else CC.style.display='none';
  if(cur===ALL){
    const g=MD.allGroups, totM=g.reduce((s,x)=>s+x.totalMatches,0), totT=g.reduce((s,x)=>s+x.totalTeams,0);
    K.innerHTML='<div class="kpi"><div class="n">'+gp(totT)+'</div><div class="l">مجموع الفِرَق</div></div>'+
      '<div class="kpi"><div class="n">'+gp(totM)+'</div><div class="l">مجموع المباريات</div></div>';
    document.getElementById('ttl').textContent='المجموعات المكتملة — جميع الفئات';
    L2.innerHTML=regionSections(g,x=>x.totalMatches,x=>x.totalTeams,x=>{
      const ages=MD.ages.filter(a=>x.teamsByAge[a]).map(a=>{const d=x.teamsByAge[a];return a+': '+nTeam(d.n)+' — '+nMatch(d.m);}).join('<br>');
      return '<div class="row clk" data-lat="'+x.lat+'" data-lon="'+x.lon+'"><div><b>'+x.group+'</b> <span class="tot">'+nTeam(x.totalTeams)+' · '+nMatch(x.totalMatches)+'</span>'+(x.cities?'<div class="cnames">'+x.cities+'</div>':'')+'<div class="sub">'+ages+'</div></div></div>';});
  } else {
    const arr=MD.byAge[cur]||[], totM=arr.reduce((s,x)=>s+x.matches,0), totT=arr.reduce((s,x)=>s+x.n,0);
    K.innerHTML='<div class="kpi"><div class="n">'+gp(totT)+'</div><div class="l">مجموع الفِرَق</div></div>'+
      '<div class="kpi"><div class="n">'+gp(totM)+'</div><div class="l">مجموع المباريات</div></div>';
    document.getElementById('ttl').textContent='المجموعات المكتملة — '+cur;
    L2.innerHTML=arr.length?regionSections(arr,x=>x.matches,x=>x.n,x=>
      '<div class="row clk" data-lat="'+x.lat+'" data-lon="'+x.lon+'"><div><b>'+x.group+'</b> <span class="tot">'+nTeam(x.n)+' · '+nMatch(x.matches)+'</span>'+(x.cities?'<div class="sub">('+x.cities+')</div>':'')+'</div></div>'):'<div class="muted">لا توجد مجموعات مكتملة في هذه الفئة بعد.</div>';
  }
  document.querySelectorAll('#list .row.clk').forEach(b=>b.onclick=()=>{
    const la=parseFloat(b.dataset.lat), lo=parseFloat(b.dataset.lon);
    if(!isNaN(la))zoomTo(la,lo);
  });
  drawMap();
}
render();
setTimeout(()=>{try{map&&map.invalidateSize();}catch(e){}},300);
</script>
</body></html>"""

HTML = HTML.replace("__MDATA__", json.dumps(MDATA, ensure_ascii=False))
open(BASE + "matches.html", "w", encoding="utf-8").write(HTML)
print("saved matches.html", len(HTML), "bytes | مجموعات مكتملة (كل الفئات):", len(allGroups))
