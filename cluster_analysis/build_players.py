#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""players.html: نفس خريطة صفحة المباريات لكن المقياس «عدد اللاعبين».
لكل فئة: المجموعات المكتملة (الفرق ≥ الهدف) كنقاط عليها اسمها وعدد لاعبيها.
خيار «جميع الفئات»: كل نقطة تعرض عدد اللاعبين في كل فئة.
عدد اللاعبين مأخوذ من صفحة «عدد اللاعبين» في الإكسل (players_data.json)."""
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

# عدد الفرق واللاعبين لكل (فئة، مجموعة) — من صفحة «عدد اللاعبين» في الإكسل مباشرةً
PDATA_SRC = {}
try:
    PDATA_SRC = json.load(open(BASE + "players_data.json", encoding="utf-8"))
except Exception:
    pass
def teams_of(age, g):
    d = PDATA_SRC.get(age + "|" + g)
    return d["n"] if d else 0
def players_src(age, g):
    d = PDATA_SRC.get(age + "|" + g)
    return d["p"] if d else 0

groups_by_age = defaultdict(list)
for key in PDATA_SRC:
    a, g = key.split("|", 1)
    groups_by_age[a].append(g)

# لكل فئة: المجموعات المكتملة (الفرق واللاعبون من الإكسل)
byAge = {}
for age in T["ages"]:
    arr = []
    for g in groups_by_age.get(age, []):
        n = teams_of(age, g)
        if n >= TARGET and g != "(غير مصنّف)":
            ll = centroid(gc.get(g, []))
            arr.append({"group": g, "region": greg.get(g, ""),
                        "cities": "، ".join(sorted(gc.get(g, []))),
                        "n": n, "players": players_src(age, g),
                        "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
    arr.sort(key=lambda x: -x["players"])
    byAge[age] = arr

# «جميع الفئات»: المجموعات المكتملة في فئة واحدة على الأقل، مع الفرق واللاعبين لكل فئة
complete_groups = {x["group"] for age in T["ages"] for x in byAge[age]}
allGroups = []
for g in complete_groups:
    teamsByAge = {a: {"n": teams_of(a, g), "p": players_src(a, g)}
                  for a in T["ages"] if teams_of(a, g) >= TARGET}
    totPlayers = sum(v["p"] for v in teamsByAge.values())
    totTeams = sum(v["n"] for v in teamsByAge.values())
    ll = centroid(gc.get(g, []))
    allGroups.append({"group": g, "region": greg.get(g, ""),
                      "cities": "، ".join(sorted(gc.get(g, []))),
                      "teamsByAge": teamsByAge, "totalPlayers": totPlayers,
                      "totalTeams": totTeams,
                      "lat": ll[0] if ll else None, "lon": ll[1] if ll else None})
allGroups.sort(key=lambda x: -x["totalPlayers"])

# عدد المباريات (للشارت المجمّع في «جميع الفئات») — من matches_data.json
MATCHES_SRC = {}
try:
    MATCHES_SRC = json.load(open(BASE + "matches_data.json", encoding="utf-8"))
except Exception:
    pass
def matches_of(age, g):
    d = MATCHES_SRC.get(age + "|" + g)
    return d["m"] if d else 0

# إجمالي كل فئة (على المجموعات المكتملة): مباريات + لاعبون + فرق
perAge = {}
for age in T["ages"]:
    perAge[age] = {"m": sum(matches_of(age, x["group"]) for x in byAge[age]),
                   "p": sum(x["players"] for x in byAge[age]),
                   "n": sum(x["n"] for x in byAge[age])}

MDATA = {"ages": T["ages"], "byAge": byAge, "allGroups": allGroups,
         "perAge": perAge, "target": TARGET}

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>عدد اللاعبين لكل مجموعة</title>
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
 .wrap{max-width:1500px;margin:0 auto;padding:18px}
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
 .muted{color:#8fdcb4;font-size:12px}
 .row{padding:9px 10px;border-bottom:1px solid #0d3a26;font-size:14px}
 .row.clk{border-radius:8px}
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
 <h1>عدد اللاعبين لكل مجموعة</h1>
</div>
<div class="wrap">
 <nav class="nav">
   <a class="navlink" href="matches.html">عدد المباريات</a>
   <a class="navlink on" href="players.html">عدد اللاعبين</a>
 </nav>
 <div class="tabs" id="ageT"></div>
 <div style="color:#8fdcb4;font-size:12.5px;margin:2px 0 12px">💡 اختر فئة أو أكثر — تُجمع أرقامها تلقائيًا.</div>
 <div class="kpis" id="kpis"></div>
 <div class="card" id="chartCard" style="display:none;margin-bottom:16px"><h3>تفصيل اللاعبين لكل فئة</h3><div id="chart"></div></div>
 <div class="card"><h3 id="ttl"></h3>
   <div id="list"></div>
 </div>
</div>
<script>
const MD=__MDATA__;
const ALL='جميع الفئات';
// اختيار متعدّد للفئات — يبدأ بكل الفئات
let sel=new Set(MD.ages);
function selAges(){return MD.ages.filter(a=>sel.has(a));}
function isAllSel(){return sel.size===MD.ages.length;}
// تجميع مجموعة على الفئات المختارة (الأرقام مأخوذة من الإكسل، لا تُحسب هنا)
function aggGroup(x){let p=0,n=0;const per=[];
  selAges().forEach(a=>{const d=x.teamsByAge[a];if(d){p+=d.p;n+=d.n;per.push(a+': '+nPlayer(d.p)+' في '+nTeam(d.n));}});
  return {p:p,n:n,per:per};}
function gp(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function arCount(n,one,two,few,many){const m=n%100;
  if(n===1)return one; if(n===2)return two;
  if(m>=3&&m<=10)return gp(n)+' '+few; return gp(n)+' '+many;}
function nPlayer(n){return arCount(n,'لاعب واحد','لاعبان','لاعبين','لاعبًا');}
function nMatch(n){return arCount(n,'مباراة واحدة','مباراتان','مباريات','مباراةً');}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function chartHTML(){
  const ages=selAges(),P=MD.perAge;
  const mp=Math.max(1,...ages.map(a=>P[a].p));
  return ages.map(a=>{const d=P[a];return '<div class="crow"><div class="cage">'+a+'</div><div class="cbars">'+
      '<div class="cbar"><div class="cfill p" style="width:'+(100*d.p/mp).toFixed(1)+'%"></div><span class="cval">'+nPlayer(d.p)+'</span></div>'+
      '</div></div>';}).join('');
}
function regionSections(items,playersOf,teamsOf,rowFn){
  const R={},order=[];
  items.forEach(x=>{const r=x.region||'غير محدد';if(!R[r]){R[r]=[];order.push(r);}R[r].push(x);});
  order.sort((a,b)=>R[b].reduce((s,x)=>s+playersOf(x),0)-R[a].reduce((s,x)=>s+playersOf(x),0));
  return order.map(r=>{
    const tp=R[r].reduce((s,x)=>s+playersOf(x),0), tt=R[r].reduce((s,x)=>s+teamsOf(x),0);
    return '<div class="rhd">'+r+' <span class="rhdt">'+nTeam(tt)+' · '+nPlayer(tp)+'</span></div>'+R[r].map(rowFn).join('');
  }).join('');
}
function render(){
  const ages=selAges();
  document.getElementById('ageT').innerHTML=
    '<button class="tab'+(isAllSel()?' on':'')+'" data-all="1">'+ALL+'</button>'+
    MD.ages.map(a=>'<button class="tab'+(sel.has(a)?' on':'')+'" data-a="'+a+'">'+a+'</button>').join('');
  document.querySelectorAll('#ageT .tab').forEach(b=>b.onclick=()=>{
    if(b.dataset.all){sel=isAllSel()?new Set():new Set(MD.ages);}
    else{const a=b.dataset.a;if(sel.has(a))sel.delete(a);else sel.add(a);}
    render();
  });
  const K=document.getElementById('kpis'), L2=document.getElementById('list'), CC=document.getElementById('chartCard');
  if(ages.length>=2){CC.style.display='block';document.getElementById('chart').innerHTML=chartHTML();}
  else CC.style.display='none';
  if(!ages.length){K.innerHTML='';document.getElementById('ttl').textContent='';
    L2.innerHTML='<div class="muted">اختر فئة واحدة على الأقل.</div>';return;}
  const view=[];
  MD.allGroups.forEach(x=>{const a=aggGroup(x);if(a.n>0)view.push({group:x.group,region:x.region,cities:x.cities,p:a.p,n:a.n,per:a.per});});
  view.sort((p,q)=>q.p-p.p);
  const totP=view.reduce((s,x)=>s+x.p,0), totT=view.reduce((s,x)=>s+x.n,0);
  K.innerHTML='<div class="kpi"><div class="n">'+gp(totT)+'</div><div class="l">مجموع الفِرَق</div></div>'+
    '<div class="kpi"><div class="n">'+gp(totP)+'</div><div class="l">مجموع اللاعبين</div></div>';
  document.getElementById('ttl').textContent='المجموعات المكتملة — '+(isAllSel()?ALL:ages.map(a=>a.replace('تحت ','ت')).join('، '));
  L2.innerHTML=view.length?regionSections(view,x=>x.p,x=>x.n,x=>
    '<div class="row"><div><b>'+x.group+'</b> <span class="tot">'+nTeam(x.n)+' · '+nPlayer(x.p)+'</span>'+(x.cities?'<div class="cnames">'+x.cities+'</div>':'')+(x.per.length>1?'<div class="sub">'+x.per.join('<br>')+'</div>':'')+'</div></div>'):'<div class="muted">لا توجد مجموعات مكتملة في الفئات المختارة.</div>';
}
render();
</script>
</body></html>"""

HTML = HTML.replace("__MDATA__", json.dumps(MDATA, ensure_ascii=False))
open(BASE + "players.html", "w", encoding="utf-8").write(HTML)
print("saved players.html", len(HTML), "bytes | مجموعات مكتملة (كل الفئات):", len(allGroups))
