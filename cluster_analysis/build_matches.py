#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة matches.html: نفس الخريطة + عدد المباريات لكل مجموعة مكتملة (≥6)،
لكل فئة عمرية منفصلة. المجموعات غير المكتملة لا تظهر.
المباريات = دوري من دور واحد: N×(N−1)/2."""
import json
from collections import defaultdict

BASE = "/home/user/khitba/cluster_analysis/"
T = json.load(open(BASE + "teams2.json", encoding="utf-8"))
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
STRUCT, GRREG = M["STRUCT"], M.get("GRREG", {})
TARGET = T.get("target", 6)

# مدن كل مجموعة (موحّدة) ومنطقتها
gc = defaultdict(set)
greg = {}
for rg in STRUCT:
    for ag in STRUCT[rg]:
        for g, cities in STRUCT[rg][ag].items():
            for c in cities:
                gc[g].add(c)
            greg.setdefault(g, rg)

# عدّ الفرق لكل (فئة، مجموعة)
byga = defaultdict(int)
for r in T["rows"]:
    byga[(r["age"], r["group"])] += r["count"]

byAge = {}
for age in T["ages"]:
    arr = []
    for (a, g), n in byga.items():
        if a == age and n >= TARGET and g != "(غير مصنّف)":
            arr.append({"group": g, "region": greg.get(g, ""),
                        "cities": "، ".join(sorted(gc.get(g, []))),
                        "n": n, "matches": n * (n - 1) // 2})
    arr.sort(key=lambda x: -x["matches"])
    byAge[age] = arr

MDATA = {"ages": T["ages"], "byAge": byAge, "target": TARGET}

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>الخريطة وعدد المباريات لكل مجموعة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#04150e;color:#eafff3}
 .top{background:#006C35;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:10;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top .logo{height:46px;width:auto;filter:brightness(0) invert(1)}
 .top h1{margin:0;font-size:19px;font-weight:800}
 .wrap{max-width:1200px;margin:0 auto;padding:18px}
 .mapwrap{border-radius:14px;overflow:hidden;border:1px solid #12563a;height:520px;margin-bottom:18px}
 iframe{border:0;width:100%;height:100%}
 .tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
 .tab{background:#0d4b32;border:1px solid #1c7a52;color:#eafff3;border-radius:20px;padding:7px 16px;
   cursor:pointer;font-family:'Tajawal';font-size:14px;font-weight:700}
 .tab.on{background:#ffd166;color:#04150e;border-color:#ffd166}
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
 .bar .val{width:60px;text-align:center;font-weight:800;color:#ffd166}
 .bar .teams{width:64px;text-align:center;color:#8fdcb4;font-size:12px}
 .muted{color:#8fdcb4;font-size:12px}
 .hd{display:flex;gap:10px;color:#8fdcb4;font-size:11px;font-weight:700;padding:0 0 4px;border-bottom:1px solid #12563a;margin-bottom:8px}
 .hd .a{width:250px}.hd .b{flex:1}.hd .c{width:64px;text-align:center}.hd .d{width:60px;text-align:center}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد" onerror="this.remove()">
 <h1>الخريطة وعدد المباريات لكل مجموعة</h1>
</div>
<div class="wrap">
 <div class="mapwrap"><iframe src="./" title="الخريطة"></iframe></div>
 <div class="tabs" id="ageT"></div>
 <div class="kpis" id="kpis"></div>
 <div class="card"><h3 id="ttl"></h3>
   <div class="hd"><div class="a">المجموعة</div><div class="b"></div><div class="c">الفِرَق</div><div class="d">المباريات</div></div>
   <div id="list"></div>
 </div>
 <div class="muted" style="margin-top:12px">المباريات محسوبة بنظام الدوري من دور واحد: عدد المباريات = ن×(ن−1)÷2 لكل مجموعة. تظهر المجموعات المكتملة فقط (٦ فرق فأكثر).</div>
</div>
<script>
const MD=__MDATA__;
let cur=MD.ages[0];
function render(){
  document.getElementById('ageT').innerHTML=MD.ages.map(a=>'<button class="tab'+(a===cur?' on':'')+'" data-a="'+a+'">'+a+'</button>').join('');
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{cur=b.dataset.a;render();});
  const arr=MD.byAge[cur]||[];
  const totM=arr.reduce((s,x)=>s+x.matches,0), totT=arr.reduce((s,x)=>s+x.n,0);
  document.getElementById('kpis').innerHTML=
    '<div class="kpi"><div class="n">'+arr.length+'</div><div class="l">مجموعات مكتملة</div></div>'+
    '<div class="kpi"><div class="n">'+totT+'</div><div class="l">مجموع الفِرَق</div></div>'+
    '<div class="kpi"><div class="n">'+totM+'</div><div class="l">مجموع المباريات</div></div>';
  document.getElementById('ttl').textContent='المجموعات المكتملة — '+cur;
  const mx=Math.max(1,...arr.map(x=>x.matches));
  document.getElementById('list').innerHTML=arr.length?arr.map(x=>
    '<div class="bar"><div class="lab"><b>'+x.group+'</b>'+(x.region?' <span class="muted">'+x.region+'</span>':'')+
      (x.cities?'<div class="sub">('+x.cities+')</div>':'')+'</div>'+
    '<div class="track"><div class="fill" style="width:'+(x.matches/mx*100)+'%"></div></div>'+
    '<div class="teams">'+x.n+' فرق</div>'+
    '<div class="val">'+x.matches+'</div></div>').join(''):'<div class="muted">لا توجد مجموعات مكتملة في هذه الفئة بعد.</div>';
}
render();
</script>
</body></html>"""

HTML = HTML.replace("__MDATA__", json.dumps(MDATA, ensure_ascii=False))
open(BASE + "matches.html", "w", encoding="utf-8").write(HTML)
print("saved matches.html", len(HTML), "bytes")
for age in MDATA["ages"]:
    a = MDATA["byAge"][age]
    print("  %s: مكتملة=%d مباريات=%d" % (age, len(a), sum(x["matches"] for x in a)))
