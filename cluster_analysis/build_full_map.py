#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""خريطة شاملة: كل المحافظات + المجموعات + أداة قياس المسافة بين أي مدينتين."""
import json, re

recs = json.load(open("/home/user/khitba/cluster_analysis/governorates_geo.json"))["records"]
D = json.load(open("/home/user/khitba/cluster_analysis/data.json"))
clusters = D["clusters"]; COORDS = D["coords"]
summary = {s["Cluster"]: s for s in D["summary"]}
pairs = D["pairs"]

# خريطة اسم المدينة (إنجليزي بملف الكلاستر) -> الاسم العربي بجدول المحافظات
EN2AR = {
 "AlDammam":"الدمام","AlDhahran":"الظهران","AlKhobar":"الخبر","Ras Tanura":"رأس تنورة",
 "Bqaiq":"بقيق","AlQatif":"القطيف","Saihat":"سيهات","Safwa":"صفوى","AlJubail":"الجبيل",
 "Aljarudiyah":"الجارودية","AlAhsa":"الأحساء","Mubarraz":"المبرز","Hafar albatin":"حفر الباطن",
 "AlQaisumah":"القيصومة","AlKhafji":"الخفجي","Riyadh":"الرياض","AlMuzahmiyya":"المزاحمية",
 "AlKharj":"الخرج","AlDilam":"الدلم","Howtat Bani Tamim":"حوطة بني تميم","AlMajma'ah":"المجمعة",
 "Al-Ghat":"الغاط","AlZulfi":"الزلفي","AlQuway'iyah":"القويعية","Afif":"عفيف","AlDuwadimi":"الدوادمي",
 "Shaqra":"شقراء","Wadi Aldwasir":"وادي الدواسر","Makkah":"مكة المكرمة","Jeddah":"جدة","Taif":"الطائف",
 "AlQunfudhah":"القنفذة","AlLith":"الليث","Madinah":"المدينة المنورة","Yanbu":"ينبع","AlUla":"العلا",
 "Buraidah":"بريدة","Unaizah":"عنيزة","Al-Bukiryah":"البكيرية","Al-Badayea":"البدائع","AlRass":"الرس",
 "Al-Mithnab":"المذنب","AlJewa":"الجوا","AlKhabra":"الخبراء","AlAsayah":"الأسياح","Dukhnah":"دخنة",
 "Abha":"أبها","Khamis Mushait":"خميس مشيط","Ahad Rufaidah":"أحد رفيدة","Sarat Abidah":"سراة عبيدة",
 "Rijal Almaa":"رجال ألمع","Muhail Aseer":"محايل عسير","Al-Majardah":"المجاردة","Bisha":"بيشة",
 "Tabuk":"تبوك","Tayma":"تيماء","Hail":"حائل","Arar":"عرعر","Rafha":"رفحاء","Turaif":"طريف",
 "Sakaka":"سكاكا","Dumat AlJandal":"دومة الجندل","Tabarjal":"طبرجل","Jazan":"جازان","Abu Arish":"أبو عريش",
 "Sabya":"صبيا","Samtah":"صامطة","Ahad Al-Masarihah":"أحد المسارحة","Baish":"بيش","Damad":"ضمد",
 "Al-Dayer":"الدائر","Al-Darb":"الدرب","Al-Shuqayq":"الشقيق","Faifa":"فيفاء","Farasan":"فرسان",
 "Najran":"نجران","Hubuna":"حبونا","Khabash":"خباش","Sharura":"شرورة","AlBaha":"الباحة",
 "Al-Aqiq":"العقيق","Al-Mandaq":"المندق","Al-Makhwah":"المخواة",
}

def cl_num(c): return int(re.search(r"\d+", c).group())
ordered = sorted(clusters, key=cl_num)
PALETTE = ["#e6194B","#3cb44b","#4363d8","#f58231","#911eb4","#1ab2c4","#f032e6",
           "#9A6324","#469990","#800000","#808000","#000075","#e07b00","#2e8b57",
           "#c71585","#1e90ff","#b8860b","#008080","#8b008b","#556b2f","#ff4500",
           "#4682b4","#a0522d","#6a5acd","#d2691e","#008b45","#cd5c5c"]
CL_COLOR = {cl: PALETTE[i % len(PALETTE)] for i, cl in enumerate(ordered)}
VERDICT_COLOR = {"ممتاز":"#1a9850","جيد":"#66bd63","مدينة واحدة":"#878787",
                 "مقبول/مراجعة":"#f59e0b","بعيد - يُفضّل الفصل":"#d73027"}

# نقطة لكل مدينة: نبدأ من جدول المحافظات (154) ونضيف مدن الكلاستر غير الموجودة
points = {}   # name_ar -> {lat,lon,region,cat,cluster}
for r in recs:
    points[r["name"]] = {"lat": r["lat"], "lon": r["lon"], "region": r["region"],
                         "cat": r["cat"], "cluster": None}

# ربط المجموعات
cluster_members = {cl: [] for cl in ordered}
for cl in ordered:
    for city_en in clusters[cl]["cities"]:
        ar = EN2AR.get(city_en, city_en)
        if ar not in points:                      # مدينة كلاستر ليست محافظة مستقلة
            lat, lon = COORDS[city_en]
            points[ar] = {"lat": lat, "lon": lon, "region": clusters[cl]["region"],
                          "cat": "مجموعة", "cluster": None}
        cluster_members[cl].append(ar)

# تعداد سكاني تقريبي (بالآلاف) لاختيار أكبر مدينة تكون اسم الكلاستر
POP = {
 "الدمام":1250,"الظهران":240,"الخبر":410,"رأس تنورة":95,"بقيق":50,
 "الجبيل":470,"القطيف":110,"سيهات":95,"صفوى":50,"الجارودية":20,
 "الأحساء":660,"المبرز":290,"حفر الباطن":390,"القيصومة":30,"الخفجي":100,
 "الرياض":7000,"المزاحمية":45,"الخرج":380,"الدلم":40,"حوطة بني تميم":25,
 "المجمعة":75,"الغاط":20,"الزلفي":70,"القويعية":53,"عفيف":65,"الدوادمي":73,
 "شقراء":40,"وادي الدواسر":106,"مكة المكرمة":2040,"جدة":4000,"الطائف":690,
 "القنفذة":78,"الليث":72,"المدينة المنورة":1490,"ينبع":330,"العلا":60,
 "بريدة":670,"عنيزة":180,"البكيرية":70,"البدائع":50,"الرس":133,"المذنب":60,
 "الجوا":15,"الخبراء":30,"الأسياح":30,"دخنة":10,"أبها":510,"خميس مشيط":630,
 "أحد رفيدة":90,"سراة عبيدة":60,"رجال ألمع":60,"محايل عسير":100,"المجاردة":50,
 "بيشة":110,"تبوك":670,"تيماء":65,"حائل":480,"عرعر":210,"رفحاء":90,"طريف":50,
 "سكاكا":250,"دومة الجندل":50,"طبرجل":60,"جازان":170,"أبو عريش":160,"صبيا":230,
 "صامطة":90,"أحد المسارحة":60,"بيش":80,"ضمد":40,"الدائر":30,"الدرب":50,
 "الشقيق":30,"فيفاء":60,"فرسان":18,"نجران":380,"حبونا":30,"خباش":20,"شرورة":85,
 "الباحة":110,"العقيق":40,"المندق":30,"المخواة":60,
}
import os
_mp = "/home/user/khitba/cluster_analysis/matrix.json"
MX = json.load(open(_mp, encoding="utf-8")) if os.path.exists(_mp) else {}
def _sec(a, b):
    if a == b: return 0
    for k in (a + "|" + b, b + "|" + a):
        if k in MX:
            v = MX[k]; return v["sec"] if v else 9e9
    return 9e9
def fmt_t(sec):
    if sec >= 9e8: return "—"
    m = round(sec / 60); h, m = divmod(m, 60)
    return (f"{h}س {m}د" if h else f"{m}د")
def name_for(cities):
    if len(cities) == 1:
        return "مجموعة " + cities[0]
    rank_pop = {c: i for i, c in enumerate(sorted(cities, key=lambda c: -POP.get(c, 0)))}
    avg = {c: sum(_sec(c, o) for o in cities if o != c) / (len(cities) - 1) for c in cities}
    rank_cen = {c: i for i, c in enumerate(sorted(cities, key=lambda c: avg[c]))}
    best = min(cities, key=lambda c: (rank_pop[c] + rank_cen[c], -POP.get(c, 0)))
    return "مجموعة " + best
def verdict_of(maxsec, n):
    if n <= 1: return "مدينة واحدة"
    m = maxsec / 60
    if m <= 60: return "ممتاز"
    if m <= 90: return "جيد"
    if m <= 150: return "مقبول/مراجعة"
    return "بعيد - يُفضّل الفصل"
def cluster_maxsec(cities):
    mx = 0
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            s = _sec(cities[i], cities[j])
            if s < 9e8 and s > mx: mx = s
    return mx
def build_dataset(groups):
    out = []
    for i, (region, cities_en) in enumerate(groups):
        cities = [EN2AR.get(c, c) for c in cities_en]
        mx = cluster_maxsec(cities)
        v = verdict_of(mx, len(cities))
        out.append({"id": name_for(cities), "region": region, "color": PALETTE[i % len(PALETTE)],
                    "verdict": v, "vcolor": VERDICT_COLOR.get(v, "#888"),
                    "maxdrive": fmt_t(mx) if len(cities) > 1 else "—", "cities": cities})
    ids = [c["id"] for c in out]
    assert len(set(ids)) == len(ids), "أسماء مكررة: " + str([x for x in ids if ids.count(x) > 1])
    return out

# تجميعة 11-14 (من ملف المجموعات الأصلي)
groups_1114 = [(clusters[cl]["region"], clusters[cl]["cities"]) for cl in ordered]
# تجميعة 5-9 (من الجدول الجديد — نفس المدن بتجميع أدق)
groups_59 = groups_1114  # تحت 5-9 بنفس تجميع 11-14
DATASETS = {}
for _age in ["11-14", "5-9"]:
    for _i in (1, 2, 3):
        DATASETS[f"{_age} — خيار {_i}"] = build_dataset(groups_1114)
    DATASETS[f"{_age} — تجربة"] = build_dataset(groups_1114)

# خيار «اكسل»: تجميع رسمي من ملف الإكسل (يُحدَّث عبر update_from_excel.py)
_egp = "/home/user/khitba/cluster_analysis/excel_groups.json"
if os.path.exists(_egp):
    def build_dataset_excel(groups):
        out = []
        for i, (region, gname, cities_ar) in enumerate(groups):
            cities = [c for c in cities_ar if c in points]  # مدن لها إحداثيات فقط
            if not cities:
                continue
            mx = cluster_maxsec(cities)
            v = verdict_of(mx, len(cities))
            out.append({"id": gname, "region": region, "color": PALETTE[i % len(PALETTE)],
                        "verdict": v, "vcolor": VERDICT_COLOR.get(v, "#888"),
                        "maxdrive": fmt_t(mx) if len(cities) > 1 else "—", "cities": cities})
        return out
    _eg = json.load(open(_egp, encoding="utf-8"))
    for _age in ["11-14", "5-9"]:
        if _eg.get(_age):
            DATASETS[f"{_age} — اكسل"] = build_dataset_excel(_eg[_age])

matrix = MX
print("مصفوفة قوقل محمّلة:", len(matrix), "زوج")
print("عدد خيارات التجميع:", len(DATASETS), "->", list(DATASETS.keys()))

P = [{"n": n, "lat": v["lat"], "lon": v["lon"], "region": v["region"],
      "cat": v["cat"]} for n, v in points.items()]
DATA = {"points": P, "datasets": DATASETS, "vcolor": VERDICT_COLOR, "matrix": matrix, "pop": POP}

json.dump(P, open("/home/user/khitba/cluster_analysis/points.json", "w", encoding="utf-8"),
          ensure_ascii=False)
print("نقاط على الخريطة:", len(P), "| محافظات الجدول:", len(recs),
      "| مدن كلاستر إضافية:", len(P) - len(recs))
missing_tbl = [n for n in points if points[n]["cat"] != "مجموعة"]
print("كل محافظات الجدول مرسومة:", len(missing_tbl) == len(recs))

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>خريطة محافظات المملكة — المجموعات وقياس المسافات</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-database-compat.js"></script>
<style>
 *{box-sizing:border-box}
 body{margin:0;font-family:'Tajawal',sans-serif}
 .leaflet-container{font-family:'Tajawal',sans-serif}
 #wrap{display:flex;height:100vh}
 #side{width:352px;background:#0f2540;color:#e9eef5;overflow-y:auto;flex-shrink:0;font-size:13px;line-height:1.55}
 #side::-webkit-scrollbar{width:9px}
 #side::-webkit-scrollbar-thumb{background:#2a4a6e;border-radius:6px}
 #side::-webkit-scrollbar-track{background:#0f2540}
 #map{flex:1}
 .hd{background:#0a3d62;padding:14px 16px;font-weight:700;font-size:15.5px;position:sticky;top:0;z-index:5;
   box-shadow:0 2px 8px rgba(0,0,0,.35)}
 .sec{padding:14px 16px;border-bottom:1px solid #1c3a5e}
 .sec h3{margin:0 0 10px;font-size:14px;font-weight:700;color:#ffd166}
 .lab{font-size:12px;color:#9fb6d0;margin:0 0 6px;font-weight:500}
 .hint{font-size:11.5px;color:#8aa3bf;line-height:1.6;margin-top:7px}
 .note{font-size:11.5px;color:#9fdca0;margin:4px 0 7px}
 select,input[type=text]{width:100%;padding:9px 10px;border-radius:8px;border:1px solid #2a4a6e;
   background:#13294a;color:#fff;font-size:13px;margin-bottom:7px;font-family:'Tajawal',sans-serif}
 button{width:100%;padding:9px 10px;border-radius:8px;border:0;background:#1b6ca8;color:#fff;
   font-family:'Tajawal',sans-serif;font-size:13px;font-weight:700;cursor:pointer;margin-bottom:7px;transition:background .15s}
 button:hover{background:#2980b9}
 .gmaps{background:#2e7d32} .gmaps:hover{background:#388e3c}
 .danger{background:#9b3535} .danger:hover{background:#c0392b}
 .row{display:flex;gap:7px} .row button{margin-bottom:0;flex:1}
 .dsbtn{width:auto;flex:0 0 auto;padding:7px 14px;border-radius:18px;background:#16314f;
   border:1px solid #2a4a6e;font-size:13px;margin:0}
 .dsbtn:hover{background:#1d3e63} .dsbtn.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 .dsbtn.on:hover{background:#ffd166}
 .res{background:#13294a;border-radius:8px;padding:9px 10px;font-size:12.5px;line-height:1.7;margin-bottom:7px}
 .res b{color:#ffd166}
 .cl{padding:8px 10px;border-radius:7px;margin-bottom:6px;cursor:pointer;background:#16314f;
   border-right:5px solid #888;font-size:12.5px;line-height:1.5}
 .cl:hover{background:#1d3e63}
 .cl .v{float:left;font-size:10.5px;padding:2px 7px;border-radius:10px;color:#fff;font-weight:700}
 .cl .cbx{float:right;width:auto;margin:2px 0 0 7px;cursor:pointer;transform:scale(1.1)}
 .cl .ct{color:#aac4e0;font-size:11px;margin-top:4px;line-height:1.55}
 .lbl{font-size:11px;color:#111;font-weight:700;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff}
 .leaflet-tooltip.glbl{background:rgba(10,61,98,.92);color:#fff;font-weight:700;border:1px solid #ffd166;
   border-radius:11px;box-shadow:0 1px 4px rgba(0,0,0,.5);padding:2px 8px;white-space:nowrap;font-family:'Tajawal',sans-serif}
 .leaflet-tooltip.glbl:before{display:none!important}
 .mapopts{background:rgba(15,37,64,.93);color:#e9eef5;padding:9px 11px;border-radius:9px;font-size:12.5px;
   box-shadow:0 2px 10px rgba(0,0,0,.45);font-family:'Tajawal',sans-serif;line-height:1.95;max-width:215px;direction:rtl}
 .mapopts .moh{color:#ffd166;font-weight:700;margin-bottom:5px;font-size:13px}
 .mapopts label{display:block;cursor:pointer}
 .mapopts input{width:auto;margin:0 0 0 6px;vertical-align:-2px;cursor:pointer}
 .leaflet-tooltip.lbl{background:transparent!important;border:0!important;box-shadow:none!important;padding:0}
 .leaflet-tooltip.lbl:before{display:none!important}
 .leg{background:#13294a;font-size:11.5px;line-height:1.9}
 small{color:#9fb6d0;font-size:11.5px;line-height:1.6;display:block}
 hr{border:0;border-top:1px solid #1c3a5e;margin:11px 0}
 label{font-size:13px;cursor:pointer;display:inline-block;margin-bottom:4px}
 input[type=checkbox]{width:auto;margin:0 0 0 7px;vertical-align:-2px;cursor:pointer}
</style></head><body>
<div id="errbar" style="display:none;position:fixed;top:0;left:0;right:0;z-index:99999;background:#b00020;color:#fff;padding:8px 12px;font-size:13px;font-family:Tajawal"></div>
<div id="wrap">
 <div id="side">
  <div class="hd">🗺️ محافظات المملكة — المجموعات وقياس المسافات <span style="font-size:10px;color:#9fb6d0;font-weight:400">نسخة __BUILD__</span>
   <a href="dashboard.html" style="float:left;background:#2e7d32;color:#fff;padding:4px 10px;border-radius:7px;font-size:12px;font-weight:700;text-decoration:none">📊 لوحة الفرق</a></div>

  <div class="sec"><div class="lab">الفئة العمرية:</div>
   <div id="agetabs" style="display:flex;gap:6px;flex-wrap:wrap"></div>
   <div class="lab" style="margin-top:10px">خيار التجميع:</div>
   <div id="opttabs" style="display:flex;gap:6px;flex-wrap:wrap"></div>
   <div id="diffbox" style="margin-top:8px;max-height:160px;overflow-y:auto;font-size:12px"></div>
  </div>

  <div class="sec">
   <div class="lab">أقصى زمن قيادة داخل المجموعة (دقيقة) — كل ما زاد قلّ العدد:</div>
   <div class="row">
    <input type="text" id="optmins" value="90" style="flex:0 0 72px;text-align:center" inputmode="numeric">
    <button class="gmaps" onclick="optimize()">🪄 احسب أفضل تقسيمة</button>
   </div>
   <div id="optstat" class="hint"></div>
   <hr>
   <div class="lab">أو حدّد عدد المجموعات — ونوزّعها لتقليل أقصى مدة في أسوأ مجموعة:</div>
   <div class="row">
    <input type="text" id="optk" value="20" style="flex:0 0 72px;text-align:center" inputmode="numeric">
    <button class="gmaps" onclick="optimizeK()">🎯 وزّع على هذا العدد</button>
   </div>
   <div id="optstat2" class="hint"></div>
  </div>

  <div class="sec">
   <h3>📏 قياس المسافة بين مدينتين</h3>
   <select id="pa"></select>
   <select id="pb"></select>
   <div class="res" id="dres">اختر مدينتين لعرض المسافة.</div>
   <button class="gmaps" id="gbtn" onclick="openGmaps()">افتح المسار في قوقل مابس ↗</button>
   <small>المسافة والزمن بالأعلى <b>حقيقية من قوقل مابس</b> (محسوبة مسبقًا لكل الأزواج). الزر يفتح المسار المباشر للتأكد/الازدحام اللحظي.</small>
  </div>

  <div class="sec">
   <h3>✏️ تعديل المجموعات</h3>
   <select id="ecity"></select>
   <select id="etarget"></select>
   <button onclick="moveCity()">↪️ نقل المدينة للمجموعة المحددة</button>
   <div class="res" id="estat">اختر مدينة، ثم مجموعة الوجهة (أو «مجموعة جديدة»)، واضغط نقل. لإعادة تسمية مجموعة استخدم زر ✏️ في قائمة المجموعات بالأسفل.</div>
   <div class="note">☁️ تعديلاتك تُحفظ تلقائيًا في السحابة وتظهر على أي جهاز يفتح الرابط.</div>
   <div id="savestat" style="font-size:11px;margin:0 0 6px;min-height:14px"></div>
   <button class="gmaps" onclick="exportCsv()">⬇️ تصدير التقسيمة المعدّلة (CSV)</button>
   <button class="gmaps" onclick="exportAll()">⬇️ تنزيل كل المدن في كل الخيارات (CSV)</button>
   <button id="resetbtn" class="danger" onclick="resetAll()">♻️ استرجاع التقسيمة الأصلية</button>
  </div>

  <div class="sec"><h3>📋 المجموعات — العدد: <span id="clcount">0</span></h3>
   <div class="hint" style="margin:0 0 8px">✓ للإظهار · اضغط الصف للتمييز على الخريطة</div>
   <div class="row" style="margin-bottom:8px">
     <button onclick="showAll(true)">إظهار الكل</button>
     <button onclick="showAll(false)">إخفاء الكل</button>
   </div>
   <div id="cllist"></div></div>

  <div class="sec leg"><h3>دليل الألوان</h3>
   <b>الخطوط (زمن القيادة بين مدينتين):</b><br>
   <span style="color:#1a9850">▬</span> أخضر: أقل من ساعة ·
   <span style="color:#f5b301">▬</span> أصفر: ساعة – ساعتين ·
   <span style="color:#d73027">▬</span> أحمر: أكثر من ساعتين<br>
   <small>الخط المتقطّع = زمن تقديري (لا يتوفر مسار قوقل). النقاط الرمادية = محافظات خارج المجموعات.</small>
  </div>
 </div>
 <div id="map"></div>
</div>
<script>
window.onerror=function(m,s,l){var b=document.getElementById('errbar');
  if(b){b.style.display='block';b.textContent='⚠ خطأ: '+m+'  (سطر '+l+')';}return false;};
const DATA = __DATA__;
const map = L.map('map').setView([24.2,45.5],6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {maxZoom:18, attribution:'© OpenStreetMap'}).addTo(map);
const optCtl=L.control({position:'topright'});
optCtl.onAdd=function(){const d=L.DomUtil.create('div','mapopts');
  d.innerHTML='<div class="moh">🎛️ خيارات العرض</div>'+
    '<label><input type="checkbox" id="names" onchange="toggleNames()"> أسماء كل المدن</label>'+
    '<label><input type="checkbox" id="gnames" onchange="renderGroupLabels()"> أسماء المجموعات</label>'+
    '<label><input type="checkbox" id="lines" checked onchange="toggleLines()"> خطوط المجموعات</label>'+
    '<label><input type="checkbox" id="vnone" checked onchange="toggleNone()"> محافظات خارج المجموعات</label>';
  L.DomEvent.disableClickPropagation(d);L.DomEvent.disableScrollPropagation(d);return d;};
optCtl.addTo(map);

const byName={}; DATA.points.forEach(p=>byName[p.n]=p);
const markers={};
let connectFrom=null, rubber=null;
const VC=DATA.vcolor;
const PALETTE=['#e6194B','#3cb44b','#4363d8','#f58231','#911eb4','#16b2c4','#f032e6','#bf40bf',
 '#1f9e89','#d2691e','#2e8b57','#c71585','#1e90ff','#b8860b','#8b008b','#ff4500','#556b2f',
 '#008b8b','#9932cc','#cd5c5c','#6a5acd','#a0522d','#008b45','#b22222','#4682b4'];

// حالة قابلة للتعديل
const DS=DATA.datasets;
let CL={}, ptCl={}, hidden=new Set(), newCount=0, hideNone=false, curKey='11-14', excluded=new Set();
const store={};
const LSKEY='ksa_map_state_v4';
// ===== Firebase (حفظ سحابي دائم ومشترك) =====
let STATE_REF=null;
try{firebase.initializeApp({apiKey:"AIzaSyDt8Ci7c6yMReMYo54Kkh9AU_OGZ1Y9BME",
  authDomain:"u5-u14-city-clusters.firebaseapp.com",
  databaseURL:"https://u5-u14-city-clusters-default-rtdb.firebaseio.com",
  projectId:"u5-u14-city-clusters",storageBucket:"u5-u14-city-clusters.firebasestorage.app",
  messagingSenderId:"760460103213",appId:"1:760460103213:web:3366fc514fb443d912f2a4"});
  STATE_REF=firebase.database().ref('clustersMap/state_v4');}catch(e){STATE_REF=null;}
function buildLive(key){const cl={},pt={};
  DS[key].forEach(c=>cl[c.id]={region:c.region,color:c.color,cities:c.cities.slice(),manual:false});
  DATA.points.forEach(p=>pt[p.n]=null);
  DS[key].forEach(c=>c.cities.forEach(x=>pt[x]=c.id));
  return {CL:cl,ptCl:pt,hidden:new Set(),newCount:0,excluded:new Set()};}
function snapshot(){store[curKey]={CL,ptCl,hidden,newCount,excluded};
  const o={curKey,hideNone,store:{}};
  for(const k in store){const s=store[k];
    o.store[k]={CL:s.CL,ptCl:s.ptCl,hidden:[...s.hidden],newCount:s.newCount,excluded:[...(s.excluded||[])]};}
  return o;}
function setSaveStatus(s){const el=document.getElementById('savestat');if(!el)return;
  if(s==='ok'){el.textContent='✔ تم الحفظ في السحابة';el.style.color='#9fdca0';}
  else if(s==='local'){el.textContent='⚠ حُفظ محليًا فقط — الحفظ السحابي مرفوض (افتح قواعد قاعدة البيانات)';el.style.color='#ffb4b4';}
  else if(s==='saving'){el.textContent='⏳ جارٍ الحفظ...';el.style.color='#ffd166';}}
function saveState(){const o=snapshot();
  try{localStorage.setItem(LSKEY,JSON.stringify(o));}catch(e){}
  if(STATE_REF){setSaveStatus('saving');
    STATE_REF.set(o).then(()=>setSaveStatus('ok')).catch(()=>setSaveStatus('local'));}
  else setSaveStatus('local');}
const RENAMES={'صيهات':'سيهات'};  // تصحيح أسماء قديمة محفوظة سحابيًا
function applyStateObj(o){if(!o||!o.store)return false;
  const valid=new Set(DATA.points.map(p=>p.n));
  for(const k in o.store){const s=o.store[k];const cl={};
    Object.keys(s.CL||{}).forEach(id=>{const c=s.CL[id]||{};
      const cities=(c.cities||[]).map(x=>RENAMES[x]||x).filter(x=>valid.has(x));
      if(cities.length)cl[id]={region:c.region,color:c.color||'#888',cities:cities,manual:!!c.manual};});
    const pt={};DATA.points.forEach(p=>pt[p.n]=null);
    Object.keys(cl).forEach(id=>cl[id].cities.forEach(c=>pt[c]=id));
    const hid=Array.isArray(s.hidden)?s.hidden:Object.values(s.hidden||{});
    store[k]={CL:cl,ptCl:pt,hidden:new Set(hid.filter(h=>cl[h])),newCount:s.newCount||0,excluded:new Set((Array.isArray(s.excluded)?s.excluded:Object.values(s.excluded||{})).map(x=>RENAMES[x]||x).filter(x=>valid.has(x)))};}
  // خيار «اكسل» يُعاد بناؤه دائمًا من أحدث بيانات مضمّنة (لا تحجبه الحالة المحفوظة)
  Object.keys(DS).forEach(k=>{if(!store[k]||optOf(k)==='اكسل')store[k]=buildLive(k);});
  curKey=(o.curKey&&store[o.curKey]&&DS[o.curKey])?o.curKey:Object.keys(DS)[0];
  hideNone=!!o.hideNone;
  const s=store[curKey];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;excluded=s.excluded||new Set();return true;}
function loadLocal(){try{const r=localStorage.getItem(LSKEY);return r?applyStateObj(JSON.parse(r)):false;}catch(e){return false;}}
function defaultInit(){Object.keys(DS).forEach(k=>store[k]=buildLive(k));
  curKey=Object.keys(DS)[0];hideNone=false;const s=store[curKey];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;excluded=s.excluded||new Set();}
let _resetArm=0;
function resetAll(){const b=document.getElementById('resetbtn');const now=Date.now();
  if(now-_resetArm>4000){_resetArm=now;if(b)b.textContent='⚠ اضغط مرة أخرى للتأكيد';
    setTimeout(()=>{if(b&&Date.now()-_resetArm>=4000)b.textContent='♻️ استرجاع التقسيمة الأصلية';},4100);return;}
  _resetArm=0;if(b)b.textContent='♻️ استرجاع التقسيمة الأصلية';
  try{localStorage.removeItem(LSKEY);}catch(e){}
  if(STATE_REF){try{STATE_REF.remove();}catch(e){}}
  for(const k in store)delete store[k];defaultInit();
  const v=document.getElementById('vnone');if(v)v.checked=true;
  updateDsUI();refreshSelectors();renderAll();}
function swapOpt23(){const age=ageOf(curKey);const k2=age+' — خيار 2',k3=age+' — خيار 3';
  if(!DS[k2]||!DS[k3])return;
  store[curKey]={CL,ptCl,hidden,newCount,excluded};
  if(!store[k2])store[k2]=buildLive(k2);
  if(!store[k3])store[k3]=buildLive(k3);
  const tmp=store[k2];store[k2]=store[k3];store[k3]=tmp;
  const s=store[curKey];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;excluded=s.excluded||new Set();
  saveState();updateDsUI();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='🔄 تبدّل محتوى «خيار 2» و«خيار 3» لفئة '+dsLabel(age);}
function switchDataset(key){if(key===curKey)return;
  store[curKey]={CL,ptCl,hidden,newCount,excluded};curKey=key;
  if(!store[key])store[key]=buildLive(key);
  const s=store[key];CL=s.CL;ptCl=s.ptCl;hidden=s.hidden;newCount=s.newCount;excluded=s.excluded||new Set();
  saveState();updateDsUI();renderAll();refreshSelectors();}
function copy1114to59(){
  store[curKey]={CL,ptCl,hidden,newCount,excluded};
  ['خيار 1','خيار 2','خيار 3','تجربة'].forEach(o=>{const src='11-14 — '+o,dst='5-9 — '+o;
    if(!DS[src]||!DS[dst])return;
    if(!store[src])store[src]=buildLive(src);
    const s=store[src];const CLc={};
    Object.keys(s.CL).forEach(id=>CLc[id]={region:s.CL[id].region,color:s.CL[id].color,cities:s.CL[id].cities.slice(),manual:s.CL[id].manual});
    const ptc={};DATA.points.forEach(p=>ptc[p.n]=s.ptCl[p.n]||null);
    store[dst]={CL:CLc,ptCl:ptc,hidden:new Set([...s.hidden]),newCount:s.newCount,excluded:new Set([...(s.excluded||[])])};});
  const cs=store[curKey];CL=cs.CL;ptCl=cs.ptCl;hidden=cs.hidden;newCount=cs.newCount;excluded=cs.excluded||new Set();
  saveState();updateDsUI();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='✓ صارت كل خيارات «تحت 5-9» مطابقة لنظيرتها في «تحت 11-14»';}
function copyFirstTo23(){const age=ageOf(curKey);const src=age+' — خيار 1';
  store[curKey]={CL,ptCl,hidden,newCount,excluded};
  if(!store[src])store[src]=buildLive(src);const s=store[src];
  ['خيار 2','خيار 3'].forEach(o=>{const dst=age+' — '+o;if(!DS[dst])return;
    const CLc={};Object.keys(s.CL).forEach(id=>CLc[id]={region:s.CL[id].region,color:s.CL[id].color,cities:s.CL[id].cities.slice(),manual:s.CL[id].manual});
    const ptc={};DATA.points.forEach(p=>ptc[p.n]=s.ptCl[p.n]||null);
    store[dst]={CL:CLc,ptCl:ptc,hidden:new Set([...s.hidden]),newCount:s.newCount,excluded:new Set([...(s.excluded||[])])};});
  const cs=store[curKey];CL=cs.CL;ptCl=cs.ptCl;hidden=cs.hidden;newCount=cs.newCount;excluded=cs.excluded||new Set();
  saveState();updateDsUI();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='✓ نُسخ «خيار 1» إلى «خيار 2» و«خيار 3» لفئة '+dsLabel(age);}
function copyOpt2to3(){const age=ageOf(curKey);const src=age+' — خيار 2',dst=age+' — خيار 3';
  if(!DS[src]||!DS[dst])return;
  store[curKey]={CL,ptCl,hidden,newCount,excluded};
  if(!store[src])store[src]=buildLive(src);const s=store[src];
  const CLc={};Object.keys(s.CL).forEach(id=>CLc[id]={region:s.CL[id].region,color:s.CL[id].color,cities:s.CL[id].cities.slice(),manual:s.CL[id].manual});
  const ptc={};DATA.points.forEach(p=>ptc[p.n]=s.ptCl[p.n]||null);
  store[dst]={CL:CLc,ptCl:ptc,hidden:new Set([...s.hidden]),newCount:s.newCount,excluded:new Set([...(s.excluded||[])])};
  const cs=store[curKey];CL=cs.CL;ptCl=cs.ptCl;hidden=cs.hidden;newCount=cs.newCount;excluded=cs.excluded||new Set();
  saveState();updateDsUI();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='✓ صار «خيار 3» مثل «خيار 2» لفئة '+dsLabel(age);}
function ageOf(k){return k.split(' — ')[0];}
function optOf(k){return k.split(' — ')[1]||k;}
function dsLabel(age){return /^[0-9]/.test(age)?'تحت '+age:age;}
function ages(){const a=[];Object.keys(DS).forEach(k=>{const g=ageOf(k);if(!a.includes(g))a.push(g);});return a;}
function firstKeyOfAge(age){return Object.keys(DS).find(k=>ageOf(k)===age);}
function clMapOf(key){if(key===curKey)return CL;if(store[key])return store[key].CL;return buildLive(key).CL;}
function worstClusterSec(clmap){let w=0;for(const id in clmap){const st=stats(clmap[id].cities);if(st.mx>w)w=st.mx;}return w;}
function updateDsUI(){
  const at=document.getElementById('agetabs');if(at){at.innerHTML='';
    ages().forEach(age=>{const b=document.createElement('button');b.className='dsbtn'+(ageOf(curKey)===age?' on':'');
      b.textContent=dsLabel(age);b.onclick=()=>{const want=age+' — '+optOf(curKey);switchDataset(DS[want]?want:firstKeyOfAge(age));};at.appendChild(b);});}
  const ot=document.getElementById('opttabs');if(ot){ot.innerHTML='';
    Object.keys(DS).filter(k=>ageOf(k)===ageOf(curKey)).forEach(key=>{const b=document.createElement('button');
      b.className='dsbtn'+(key===curKey?' on':'');const w=worstClusterSec(clMapOf(key));
      b.innerHTML=optOf(key)+'<br><span style="font-size:10px;font-weight:400;opacity:.9">أسوأ: '+(w?fmt(w/60):'—')+'</span>';
      b.onclick=()=>switchDataset(key);ot.appendChild(b);});}
  const cf=document.getElementById('copyfirst');if(cf)cf.style.display=(curKey===firstKeyOfAge(ageOf(curKey)))?'none':'block';}
function copyFromFirst(){const first=firstKeyOfAge(ageOf(curKey));if(curKey===first)return;
  const base=store[first]||buildLive(first);
  CL={};Object.keys(base.CL).forEach(id=>CL[id]={region:base.CL[id].region,color:base.CL[id].color,
    cities:base.CL[id].cities.slice(),manual:base.CL[id].manual});
  ptCl={};DATA.points.forEach(p=>ptCl[p.n]=base.ptCl[p.n]||null);
  hidden=new Set();saveState();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='✓ هذا الخيار صار مثل «'+dsLabel(ageOf(first))+' — '+optOf(first)+'»';}
function isVisible(n){const id=ptCl[n];return id?!hidden.has(id):!hideNone;}
function showAll(v){if(v)hidden.clear();else hidden=new Set(Object.keys(CL));saveState();renderAll();}
function toggleNone(){hideNone=!document.getElementById('vnone').checked;saveState();renderMarkers();}

function getG(a,b){let g=DATA.matrix[a+'|'+b]; if(g===undefined)g=DATA.matrix[b+'|'+a]; return g;}
// زمن/مسافة: قوقل إن توفّر، وإلا تقدير (خط مستقيم ×1.3) حتى لا تظهر «لا يوجد مسار»
function gd(a,b){const g=getG(a,b); if(g)return{km:g.km,sec:g.sec,est:false};
  const A=byName[a],B=byName[b]; if(!A||!B)return{km:0,sec:0,est:true};
  const air=haversine(A,B),road=air*1.3,v=road>=150?100:road>=80?90:road>=30?75:50;
  return{km:Math.round(road),sec:road/v*3600,est:true};}
function fmt(min){let h=Math.floor(min/60),m=Math.round(min%60);if(m===60){h++;m=0;}return h?h+'س '+m+'د':m+'د';}
function haversine(a,b){const R=6371,d=x=>x*Math.PI/180;const dla=d(b.lat-a.lat),dlo=d(b.lon-a.lon);
  const h=Math.sin(dla/2)**2+Math.cos(d(a.lat))*Math.cos(d(b.lat))*Math.sin(dlo/2)**2;return 2*R*Math.asin(Math.sqrt(h));}
function verdict(min,n){if(n<=1)return['مدينة واحدة',VC['مدينة واحدة']];
  if(min<=60)return['ممتاز',VC['ممتاز']]; if(min<=90)return['جيد',VC['جيد']];
  if(min<=150)return['مقبول/مراجعة',VC['مقبول/مراجعة']]; return['بعيد - يُفضّل الفصل',VC['بعيد - يُفضّل الفصل']];}
function stats(cities){let mx=0,nr=0;for(let i=0;i<cities.length;i++)for(let j=i+1;j<cities.length;j++){
  const g=gd(cities[i],cities[j]); if(g.est)nr++; if(g.sec>mx)mx=g.sec;} return{mx,nr};}
function clKey(id){const m=id.match(/\d+/);return (id.indexOf('جديد')>=0?1000:0)+(m?parseInt(m[0]):9999);}
function uniqueName(base){if(!CL[base])return base;let i=2;while(CL[base+' '+i])i++;return base+' '+i;}
function nameFor(cities){if(cities.length===1)return 'مجموعة '+cities[0];
  const pop=DATA.pop||{};const rp={},rc={},avg={};
  [...cities].sort((a,b)=>(pop[b]||0)-(pop[a]||0)).forEach((c,i)=>rp[c]=i);
  cities.forEach(c=>{let s=0,n=0;cities.forEach(o=>{if(o!==c){s+=gd(c,o).sec;n++;}});avg[c]=n?s/n:0;});
  [...cities].sort((a,b)=>avg[a]-avg[b]).forEach((c,i)=>rc[c]=i);
  let best=cities[0],bs=1e9;
  cities.forEach(c=>{const sc=rp[c]+rc[c];if(sc<bs||(sc===bs&&(pop[c]||0)>(pop[best]||0))){bs=sc;best=c;}});
  return 'مجموعة '+best;}
function renameKey(oldId,newId){if(oldId===newId||CL[newId])return oldId;
  const e=Object.keys(CL).map(k=>k===oldId?[newId,CL[oldId]]:[k,CL[k]]);
  CL={};e.forEach(([k,v])=>CL[k]=v);CL[newId].cities.forEach(x=>ptCl[x]=newId);return newId;}
function autoRename(id){if(!CL[id]||CL[id].manual)return id;
  let want=nameFor(CL[id].cities);if(want===id)return id;
  if(CL[want])want=uniqueName(want);return renameKey(id,want);}
function optimize(){const os=document.getElementById('optstat');
 try{
  const cities=Object.values(CL).flatMap(c=>c.cities);
  if(!cities.length){if(os){os.textContent='⚠ لا توجد مدن في هذا الخيار';os.style.color='#ffb4b4';}return;}
  const el=document.getElementById('optmins');
  const raw=(el?el.value:'90').replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[^0-9]/g,'');
  const T=parseInt(raw);
  if(!T||T<=0){if(os){os.textContent='⚠ اكتب عدد دقائق صحيح في الحقل';os.style.color='#ffb4b4';}return;}
  const sorted=[...cities].filter(c=>byName[c]).sort((a,b)=>{const A=byName[a],B=byName[b];return A.lat-B.lat||A.lon-B.lon;});
  const groups=[];
  sorted.forEach(city=>{let placed=false;
    for(const g of groups){if(g.every(o=>gd(city,o).sec/60<=T)){g.push(city);placed=true;break;}}
    if(!placed)groups.push([city]);});
  CL={};DATA.points.forEach(p=>ptCl[p.n]=null);
  groups.forEach((g,i)=>{const id=uniqueName(nameFor(g));
    CL[id]={region:byName[g[0]].region,color:PALETTE[i%PALETTE.length],cities:g,manual:false};
    g.forEach(c=>ptCl[c]=id);});
  hidden=new Set();saveState();refreshSelectors();renderAll();
  if(os){os.textContent='✓ أفضل تقسيمة: '+groups.length+' مجموعة (أقصى زمن داخلي ≤ '+T+' دقيقة)';os.style.color='#9fdca0';}
 }catch(e){if(os){os.textContent='⚠ خطأ: '+e.message;os.style.color='#ffb4b4';}}}
function greedyCover(cities,Tmin){const sorted=[...cities].filter(c=>byName[c]).sort((a,b)=>{const A=byName[a],B=byName[b];return A.lat-B.lat||A.lon-B.lon;});
  const groups=[];sorted.forEach(city=>{let placed=false;
    for(const g of groups){if(g.every(o=>gd(city,o).sec/60<=Tmin)){g.push(city);placed=true;break;}}
    if(!placed)groups.push([city]);});return groups;}
function clusterDiam(g){let mx=0;for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++){const s=gd(g[i],g[j]).sec;if(s>mx)mx=s;}return mx;}
function optimizeK(){const os=document.getElementById('optstat2');
 try{
  const cities=Object.values(CL).flatMap(c=>c.cities).filter(c=>byName[c]&&!excluded.has(c));
  if(!cities.length){if(os){os.textContent='⚠ لا توجد مدن';os.style.color='#ffb4b4';}return;}
  const el=document.getElementById('optk');
  let K=parseInt((el?el.value:'').replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[^0-9]/g,''));
  if(!K||K<1){if(os){os.textContent='⚠ اكتب عدد مجموعات صحيح';os.style.color='#ffb4b4';}return;}
  if(K>cities.length)K=cities.length;
  const set=new Set();
  for(let i=0;i<cities.length;i++)for(let j=i+1;j<cities.length;j++)set.add(Math.ceil(gd(cities[i],cities[j]).sec/60));
  const cand=[...set].sort((a,b)=>a-b);if(!cand.length)cand.push(0);
  let lo=0,hi=cand.length-1,best=null;
  while(lo<=hi){const mid=(lo+hi)>>1;const g=greedyCover(cities,cand[mid]);
    if(g.length<=K){best=g;hi=mid-1;}else lo=mid+1;}
  let groups=best||greedyCover(cities,cand[cand.length-1]);
  let guard=0;
  while(groups.length<K && guard++<cities.length+2){
    let gi=-1,gdm=-1;groups.forEach((g,idx)=>{if(g.length>1){const d=clusterDiam(g);if(d>gdm){gdm=d;gi=idx;}}});
    if(gi<0)break;const g=groups[gi];
    let pa=0,pb=1,mx=-1;for(let i=0;i<g.length;i++)for(let j=i+1;j<g.length;j++){const s=gd(g[i],g[j]).sec;if(s>mx){mx=s;pa=i;pb=j;}}
    const avg=x=>{let s=0;g.forEach(o=>{if(o!==x)s+=gd(x,o).sec;});return s;};
    const rem=avg(g[pa])>=avg(g[pb])?g[pa]:g[pb];
    groups[gi]=g.filter(x=>x!==rem);groups.push([rem]);}
  CL={};DATA.points.forEach(p=>ptCl[p.n]=null);
  groups.forEach((g,i)=>{const id=uniqueName(nameFor(g));
    CL[id]={region:byName[g[0]].region,color:PALETTE[i%PALETTE.length],cities:g,manual:false};
    g.forEach(c=>ptCl[c]=id);});
  let worst=0;groups.forEach(g=>{const d=clusterDiam(g);if(d>worst)worst=d;});
  hidden=new Set();saveState();refreshSelectors();renderAll();
  if(os){os.textContent='✓ '+groups.length+' مجموعة · أقصى مدة في أسوأ مجموعة ≈ '+fmt(worst/60);os.style.color='#9fdca0';}
 }catch(e){if(os){os.textContent='⚠ خطأ: '+e.message;os.style.color='#ffb4b4';}}}

// النقاط
function colorOf(n){const id=ptCl[n];return id&&CL[id]?CL[id].color:'#9aa7b4';}
function popBtn(parent,txt,bg,fn){const b=document.createElement('button');b.textContent=txt;
  b.style.cssText='margin-top:7px;display:block;width:100%;cursor:pointer;background:'+bg+';color:#fff;border:0;border-radius:5px;padding:6px;font-family:Tajawal';
  b.onclick=fn;parent.appendChild(b);}
function groupBlock(id){const c=CL[id];const d=document.createElement('div');d.style.cssText='font-size:12.5px';
  if(!c){d.textContent='—';return d;}
  const st=stats(c.cities);const[v,vc]=verdict(st.mx/60,c.cities.length);
  d.innerHTML='📦 <b style="color:#ffd166">'+id+'</b><br>عدد المدن: '+c.cities.length+
    '<br>أقصى مسافة/زمن: <b>'+(c.cities.length>1?fmt(st.mx/60):'—')+'</b>'+
    '<br>التقييم: <b style="color:'+vc+'">'+v+'</b>'+(st.nr?'<br><span style="color:#e6a">'+st.nr+' مسار تقديري</span>':'')+
    '<div style="color:#9fb6d0;font-size:11px;margin-top:3px">'+c.cities.join('، ')+'</div>';
  popBtn(d,'🔍 تقريب على المجموعة','#1b6ca8',()=>{map.closePopup();focusCluster(id);});
  const inp=document.createElement('input');inp.type='text';inp.value=id;
  inp.style.cssText='margin-top:7px;width:100%;padding:6px;border-radius:5px;border:1px solid #2a4a6e;background:#13294a;color:#fff;font-family:Tajawal';
  d.appendChild(inp);
  popBtn(d,'✒️ تغيير اسم المجموعة','#6a4aa0',()=>{const nn=inp.value.trim();if(!nn)return;
    if(nn!==id&&CL[nn]){inp.style.borderColor='#ff5252';return;}
    if(nn!==id){renameKey(id,nn);CL[nn].manual=true;saveState();renderAll();refreshSelectors();}
    map.closePopup();document.getElementById('estat').innerHTML='✒️ اسم المجموعة صار <b>'+nn+'</b>';});
  return d;}
function popupHtml(n){const p=byName[n],id=ptCl[n],ex=excluded.has(n);const d=document.createElement('div');
  d.style.cssText='direction:rtl;font-family:Tajawal,sans-serif;font-size:13px;min-width:180px';
  let s='<b>'+n+'</b> <span style="color:#9fb6d0;font-size:11px">('+p.region+' · '+p.cat+')</span>';
  if(ex)s+='<br><b style="color:#ff8a8a">🚫 مستبعدة من التجميع</b>';
  else if(!id||!CL[id])s+='<br>بدون مجموعة';
  d.innerHTML=s;
  if(ex){popBtn(d,'↩️ أرجعها للتجميع','#2e7d32',()=>includeCity(n));}
  else if(id&&CL[id]){
    const sep=document.createElement('div');sep.style.cssText='margin-top:6px;border-top:1px solid #2a4a6e;padding-top:6px';
    sep.appendChild(groupBlock(id));d.appendChild(sep);
    if(CL[id].cities.length===1)popBtn(d,'🗑️ احذف هذه المجموعة','#7a2e2e',()=>ejectCity(n));
    popBtn(d,'🚫 استبعد '+n+' من التجميع','#8a5a00',()=>excludeCity(n));
  } else {
    popBtn(d,'➕ اجعلها مجموعة مستقلة','#1b6ca8',()=>{const w=applyMove(n,'__new__');map.closePopup();document.getElementById('estat').innerHTML='➕ أنشئت <b>'+w+'</b>';});
    popBtn(d,'🚫 استبعدها من التجميع','#8a5a00',()=>excludeCity(n));
  }
  return d;}
DATA.points.forEach(p=>{const m=L.circleMarker([p.lat,p.lon],{radius:p.cat==='مقر'?8:5.5,
   color:'#222',weight:1,fillColor:colorOf(p.n),fillOpacity:0.95});
  m.bindPopup(()=>popupHtml(p.n)); m.bindTooltip(p.n,{direction:'top'}); m.addTo(map); markers[p.n]=m;
  m.on('mousedown',e=>{connectFrom=p.n;map.dragging.disable();L.DomEvent.stop(e);});});
map.on('mousemove',e=>{if(!connectFrom)return;const a=byName[connectFrom];
  if(rubber)map.removeLayer(rubber);
  rubber=L.polyline([[a.lat,a.lon],[e.latlng.lat,e.latlng.lng]],{color:'#e63946',weight:3,dashArray:'6,6'}).addTo(map);});
map.on('mouseup',e=>{if(!connectFrom)return;const src=connectFrom;connectFrom=null;
  setTimeout(()=>map.dragging.enable(),0);
  if(rubber){map.removeLayer(rubber);rubber=null;}
  const pt=map.latLngToContainerPoint(e.latlng);let best=null,bd=1e9;
  DATA.points.forEach(p=>{const q=map.latLngToContainerPoint([p.lat,p.lon]);const d=pt.distanceTo(q);if(d<bd){bd=d;best=p.n;}});
  if(best&&bd<30){if(best===src){const gid=ptCl[src];if(gid&&CL[gid])focusCluster(gid);else map.setView([byName[src].lat,byName[src].lon],9);
      ec.value=src;ec.dispatchEvent(new Event('change'));
      document.getElementById('estat').innerHTML='📍 <b>'+src+'</b> — استخدم أدوات اليمين للتعديل';}
    else connectDrop(src,best);}});
function renderMarkers(){DATA.points.forEach(p=>{const m=markers[p.n];const ex=excluded.has(p.n);
  m.setStyle({fillColor:ex?'#555':colorOf(p.n),color:ex?'#ff5252':'#222',weight:ex?2:1,dashArray:ex?'3,3':null});
  if(isVisible(p.n)){if(!map.hasLayer(m))m.addTo(map);}else if(map.hasLayer(m))map.removeLayer(m);});}

// خطوط المجموعات
const lineLayer=L.layerGroup().addTo(map);
const glabels=L.layerGroup().addTo(map);
function renderGroupLabels(){glabels.clearLayers();
  const cb=document.getElementById('gnames');if(!cb||!cb.checked)return;
  const z=map.getZoom();
  const fs=z<=5?7:z<=6?8:z<=7?10:z<=8?11:z<=9?12:13;
  Object.keys(CL).forEach(id=>{if(hidden.has(id))return;const cs=CL[id].cities;if(!cs.length)return;
    let la=0,lo=0,n=0;cs.forEach(c=>{const p=byName[c];if(p){la+=p.lat;lo+=p.lon;n++;}});if(!n)return;la/=n;lo/=n;
    let anchor=cs[0],bd=1e9;cs.forEach(c=>{const q=byName[c];if(!q)return;const d=(q.lat-la)*(q.lat-la)+(q.lon-lo)*(q.lon-lo);if(d<bd){bd=d;anchor=c;}});
    const nm=id.replace(/^مجموعة /,'');if(byName[nm]&&cs.indexOf(nm)>=0)anchor=nm;
    const p=byName[anchor];if(!p)return;
    const t=L.tooltip({permanent:true,direction:'center',className:'glbl',interactive:true})
      .setLatLng([p.lat,p.lon]).setContent('<span style="font-size:'+fs+'px">'+id+'</span>');
    glabels.addLayer(t);t.on('click',()=>focusCluster(id));});}
map.on('zoomend',renderGroupLabels);
function lineColor(min){return min>120?'#d73027':min>=60?'#f5b301':'#1a9850';}
function renderLines(){lineLayer.clearLayers();
  Object.keys(CL).forEach(id=>{if(hidden.has(id))return;const c=CL[id],ct=c.cities;
    for(let i=0;i<ct.length;i++)for(let j=i+1;j<ct.length;j++){const a=byName[ct[i]],b=byName[ct[j]];if(!a||!b)continue;
      const A=ct[i],B=ct[j];const g=gd(A,B);const lbl=A+' ↔ '+B+': '+g.km+' كم / '+fmt(g.sec/60)+(g.est?' ≈ تقديري':'');
      L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:lineColor(g.sec/60),weight:4,opacity:0.75,
        dashArray:g.est?'5,5':null}).bindTooltip(lbl).bindPopup(()=>linePopup(A,B)).addTo(lineLayer);}});
  document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}
function linePopup(A,B){const g=gd(A,B);const d=document.createElement('div');
  d.style.cssText='direction:rtl;font-family:Tajawal;font-size:13px;min-width:150px';
  d.innerHTML='<b>'+A+'</b> ↔ <b>'+B+'</b><br>'+g.km+' كم / '+fmt(g.sec/60)+(g.est?' ≈ تقديري':'')+'<hr style="margin:5px 0">حذف الرابط بإخراج:';
  [A,B].forEach(nm=>{const b=document.createElement('button');b.textContent='🗑️ '+nm;
    b.style.cssText='margin-top:5px;display:block;width:100%;cursor:pointer;background:#7a2e2e;color:#fff;border:0;border-radius:5px;padding:6px;font-family:Tajawal';
    b.onclick=()=>ejectCity(nm);d.appendChild(b);});
  return d;}
function ejectCity(c){applyMove(c,'__none__');map.closePopup();
  document.getElementById('estat').innerHTML='🗑️ أُخرجت <b>'+c+'</b> من مجموعتها (حُذف الرابط)';}
function excludeCity(n){const old=ptCl[n];
  Object.keys(CL).forEach(id=>{CL[id].cities=CL[id].cities.filter(x=>x!==n);});
  Object.keys(CL).forEach(id=>{if(CL[id].cities.length===0)delete CL[id];});
  ptCl[n]=null;if(old&&CL[old])autoRename(old);
  excluded.add(n);map.closePopup();saveState();renderAll();refreshSelectors();
  document.getElementById('estat').innerHTML='🚫 استُبعدت <b>'+n+'</b> من التجميع (تبقى ظاهرة على الخريطة)';}
function includeCity(n){excluded.delete(n);map.closePopup();saveState();renderAll();
  document.getElementById('estat').innerHTML='↩️ رجعت <b>'+n+'</b> للتجميع (بدون مجموعة الآن)';}
function toggleLines(){document.getElementById('lines').checked?map.addLayer(lineLayer):map.removeLayer(lineLayer);}

// أسماء دائمة
function toggleNames(){const on=document.getElementById('names').checked;
  DATA.points.forEach(p=>{const m=markers[p.n];
    if(on)m.bindTooltip(p.n,{permanent:true,direction:'right',className:'lbl',offset:[6,0]}).openTooltip();
    else{m.unbindTooltip();m.bindTooltip(p.n,{direction:'top'});}});}

// قائمة المجموعات
function renderList(){const cl=document.getElementById('cllist');cl.innerHTML='';
  const cc=document.getElementById('clcount');if(cc)cc.textContent=Object.keys(CL).length;
  Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b)).forEach(id=>{const c=CL[id],st=stats(c.cities);
    const[v,vc]=verdict(st.mx/60,c.cities.length);
    const d=document.createElement('div');d.className='cl';d.style.borderRightColor=c.color;
    const cb=document.createElement('input');cb.type='checkbox';cb.className='cbx';cb.checked=!hidden.has(id);
    cb.onclick=e=>e.stopPropagation();cb.onchange=()=>toggleCluster(id,cb.checked);
    const rb=document.createElement('button');rb.textContent='✏️';rb.title='إعادة تسمية';
    rb.style.cssText='float:left;width:auto;margin:0 0 0 5px;padding:1px 7px;font-size:11px;background:#6a4aa0;border:0;border-radius:6px;color:#fff;cursor:pointer';
    rb.onclick=e=>{e.stopPropagation();startRename(d,id);};
    const body=document.createElement('div');
    body.innerHTML='<span class="v" style="background:'+vc+'">'+v+'</span><b>'+id+'</b> — '+c.region+
      '<div class="ct">أقصى زمن: '+(c.cities.length>1?fmt(st.mx/60):'—')+' · '+c.cities.length+' مدن'+
      (st.nr?' · '+st.nr+' تقديري':'')+'<br>'+c.cities.join('، ')+'</div>';
    d.appendChild(cb);d.appendChild(rb);d.appendChild(body);d.onclick=()=>focusCluster(id);cl.appendChild(d);});}
function startRename(d,id){d.onclick=null;d.innerHTML='';
  const inp=document.createElement('input');inp.type='text';inp.value=id;
  inp.style.cssText='width:68%;padding:5px;border-radius:5px;border:1px solid #2a4a6e;background:#13294a;color:#fff;font-family:Tajawal,sans-serif';
  inp.onclick=e=>e.stopPropagation();
  const ok=document.createElement('button');ok.textContent='✓ حفظ';
  ok.style.cssText='width:auto;margin:0 5px;padding:5px 10px;background:#2e7d32;border:0;border-radius:5px;color:#fff;cursor:pointer;font-family:Tajawal';
  ok.onclick=e=>{e.stopPropagation();const nn=inp.value.trim();
    if(nn&&nn!==id){if(CL[nn]){inp.style.borderColor='#ff5252';return;}renameKey(id,nn);CL[nn].manual=true;saveState();
      document.getElementById('estat').innerHTML='✒️ صار الاسم <b>'+nn+'</b>';}
    renderAll();refreshSelectors();};
  d.appendChild(inp);d.appendChild(ok);inp.focus();}
function toggleCluster(id,show){if(show)hidden.delete(id);else hidden.add(id);saveState();renderMarkers();renderLines();}
let hi=[];
function focusCluster(id){hi.forEach(m=>m.setStyle&&m.setStyle({weight:1,radius:m._r0||5.5}));hi=[];const pts=[];
  (CL[id]?CL[id].cities:[]).forEach(n=>{const m=markers[n],p=byName[n];if(!m)return;
    m._r0=m._r0||m.options.radius;m.setStyle({weight:3,color:'#000',radius:9});hi.push(m);pts.push([p.lat,p.lon]);});
  if(pts.length>1)map.fitBounds(pts,{padding:[60,60]});else if(pts.length===1)map.setView(pts[0],10);}

function renderDiff(){const el=document.getElementById('diffbox');if(!el)return;
  const first=firstKeyOfAge(ageOf(curKey));
  if(curKey===first){el.innerHTML='<small style="color:#9fdca0">هذا هو الخيار الأول لهذه الفئة (المرجع للمقارنة).</small>';return;}
  const base=store[first]||buildLive(first);
  const trans={};
  DATA.points.forEach(p=>{const c=p.n;const bg=base.ptCl[c]||null,cg=ptCl[c]||null;
    if(bg===cg)return;
    const key=(bg||'∅')+'|'+(cg||'∅');
    (trans[key]=trans[key]||{from:bg,to:cg,cities:[]}).cities.push(c);});
  const keys=Object.keys(trans);
  if(!keys.length){el.innerHTML='<small style="color:#9fdca0">لا فروقات عن الخيار الأول حتى الآن.</small>';return;}
  let html='<div style="color:#ffd166;margin-bottom:4px">🔀 الفروقات عن «'+dsLabel(ageOf(first))+' — '+optOf(first)+'» ('+keys.length+'):</div>';
  keys.forEach(k=>{const t=trans[k];
    const fromCl=t.from?base.CL[t.from]:null,toCl=t.to?CL[t.to]:null;
    const fullFrom=fromCl&&t.cities.length===fromCl.cities.length;
    const fullTo=toCl&&t.cities.length===toCl.cities.length;
    let icon,label;
    if(t.to===null){icon='🗑️';label='حُذفت «'+t.from+'» — مدنها صارت بدون مجموعة';}
    else if(t.from===null){icon='➕';label='أُضيفت إلى «'+t.to+'»';}
    else if(fullFrom&&fullTo){icon='✏️';label='«'+t.from+'» أُعيدت تسميتها إلى «'+t.to+'»';}
    else if(fullFrom){icon='📦';label='«'+t.from+'» بالكامل ضُمّت إلى «'+t.to+'»';}
    else{icon='↪️';label='نُقلت من «'+t.from+'» إلى «'+t.to+'»';}
    html+='<div style="padding:4px 0;border-bottom:1px solid #1c3a5e"><b>'+icon+' '+label+'</b>'+
      ((fullFrom&&fullTo)?'':'<br><span style="color:#9fb6d0;font-size:11px">'+t.cities.join('، ')+'</span>')+'</div>';});
  el.innerHTML=html;}
function renderAll(){renderMarkers();renderLines();renderList();renderDiff();renderGroupLabels();}

// أداة المسافة
const pa=document.getElementById('pa'),pb=document.getElementById('pb');
const names=DATA.points.map(p=>p.n).sort((a,b)=>a.localeCompare(b,'ar'));
function fill(sel,ph){sel.innerHTML='<option value="">'+ph+'</option>'+names.map(n=>'<option>'+n+'</option>').join('');}
fill(pa,'— المدينة الأولى —');fill(pb,'— المدينة الثانية —');
let measureLine=null;
function calc(){const a=byName[pa.value],b=byName[pb.value],res=document.getElementById('dres');
  if(!a||!b){res.innerHTML='اختر مدينتين لعرض المسافة.';if(measureLine){map.removeLayer(measureLine);measureLine=null;}return;}
  const g=gd(a.n,b.n);let html='<b>'+a.n+'</b> ↔ <b>'+b.n+'</b><br>';
  html+='المسافة'+(g.est?' (تقديرية)':' (قوقل مابس)')+': <b>'+g.km+' كم</b><br>'+
        'زمن القيادة'+(g.est?' (تقديري)':' (قوقل مابس)')+': <b style="color:#7CFC00">'+fmt(g.sec/60)+'</b>'+
        (g.est?'<br><small style="color:#ffd6a0">لا يتوفر مسار من قوقل لهذه النقطة (منطقة نائية/جزيرة) — الرقم تقديري.</small>':'');
  res.innerHTML=html;if(measureLine)map.removeLayer(measureLine);
  measureLine=L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:'#e63946',weight:3,dashArray:'6,6'}).addTo(map);
  map.fitBounds([[a.lat,a.lon],[b.lat,b.lon]],{padding:[80,80]});}
pa.onchange=calc;pb.onchange=calc;
function openGmaps(){const a=byName[pa.value],b=byName[pb.value];if(!a||!b){document.getElementById('dres').innerHTML='اختر مدينتين أولاً';return;}
  window.open('https://www.google.com/maps/dir/?api=1&origin='+a.lat+','+a.lon+'&destination='+b.lat+','+b.lon+'&travelmode=driving','_blank');}

// تعديل المجموعات
const ec=document.getElementById('ecity'),et=document.getElementById('etarget'),rcl=document.getElementById('rcl');
function refreshCity(){const cur=ec.value;ec.innerHTML='<option value="">— اختر مدينة —</option>'+
  names.map(n=>'<option value="'+n+'">'+n+' ('+(ptCl[n]||'بدون')+')</option>').join('');ec.value=cur;}
function refreshTarget(){et.innerHTML=Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b))
  .map(id=>'<option value="'+id+'">'+id+' — '+CL[id].region+'</option>').join('')+
  '<option value="__none__">— بدون مجموعة —</option><option value="__new__">+ مجموعة جديدة</option>'+
  '<option value="__exclude__">🚫 استبعاد من التجميع</option>';}
function refreshRcl(){if(!rcl)return;const cur=rcl.value;rcl.innerHTML=Object.keys(CL).sort((a,b)=>clKey(a)-clKey(b))
  .map(id=>'<option value="'+id+'">'+id+'</option>').join('');if(CL[cur])rcl.value=cur;}
function refreshSelectors(){refreshCity();refreshTarget();refreshRcl();}
ec.onchange=function(){const c=ec.value;if(c&&ptCl[c]&&CL[ptCl[c]])et.value=ptCl[c];};
function renameCluster(){const old=rcl.value,nn=document.getElementById('rname').value.trim();
  const st=document.getElementById('estat');
  if(!old){st.innerHTML='اختر مجموعة';return;} if(!nn){st.innerHTML='اكتب الاسم الجديد';return;}
  if(nn===old){document.getElementById('rname').value='';return;}
  if(CL[nn]){st.innerHTML='⚠ الاسم مستخدم بالفعل';return;}
  // أعد بناء CL مع الحفاظ على الترتيب وتغيير المفتاح القديم للجديد
  const entries=Object.keys(CL).map(k=>k===old?[nn,CL[old]]:[k,CL[k]]);
  CL={};entries.forEach(([k,v])=>CL[k]=v);
  CL[nn].cities.forEach(x=>ptCl[x]=nn);CL[nn].manual=true;
  document.getElementById('rname').value='';
  saveState();renderAll();refreshSelectors();rcl.value=nn;
  document.getElementById('estat').innerHTML='✒️ تغيّر الاسم إلى <b>'+nn+'</b> (محفوظ)';}
function applyMove(city,tgt){
  const old=ptCl[city];
  if(tgt!=='__none__')excluded.delete(city);   // الانضمام لمجموعة يلغي الاستبعاد
  Object.keys(CL).forEach(id=>{CL[id].cities=CL[id].cities.filter(x=>x!==city);});
  if(tgt==='__none__')ptCl[city]=null;
  else{if(tgt==='__new__'){tgt=uniqueName(nameFor([city]));
      CL[tgt]={region:byName[city].region,color:PALETTE[Object.keys(CL).length%PALETTE.length],cities:[],manual:false};}
    if(!CL[tgt])CL[tgt]={region:byName[city].region,color:'#888',cities:[],manual:false};
    CL[tgt].cities.push(city);ptCl[city]=tgt;}
  Object.keys(CL).forEach(id=>{if(CL[id].cities.length===0)delete CL[id];});
  if(old&&CL[old])autoRename(old);
  if(tgt!=='__none__'&&CL[tgt])tgt=autoRename(tgt);
  saveState();renderAll();refreshSelectors();return tgt;}
function moveCity(){const city=ec.value;if(!city){document.getElementById('estat').innerHTML='اختر مدينة أولاً';return;}
  if(et.value==='__exclude__'){excludeCity(city);return;}
  const tgt=applyMove(city,et.value);
  document.getElementById('estat').innerHTML='✓ نُقلت <b>'+city+'</b> إلى <b>'+(tgt==='__none__'?'بدون مجموعة':tgt)+'</b> (محفوظ)';}
// السحب على الخريطة: اربط مدينتين في نفس المجموعة
function connectDrop(src,t){if(src===t)return;
  const tc=ptCl[t];let where;
  if(tc){where=applyMove(src,tc);}
  else{const nid=applyMove(src,'__new__');where=applyMove(t,nid);}
  const g=gd(src,t);
  document.getElementById('estat').innerHTML='🔗 ضممت <b>'+src+'</b> و<b>'+t+'</b> ('+g.km+' كم / '+fmt(g.sec/60)+') في <b>'+where+'</b>';}
function exportCsv(){let rows=[['City','Region','Group']];
  DATA.points.forEach(p=>rows.push([p.n,p.region,ptCl[p.n]||'']));
  const csv='﻿'+rows.map(r=>r.map(x=>'"'+x+'"').join(',')).join('\\r\\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='clusters_edited.csv';a.click();}
function exportAll(){
  store[curKey]={CL,ptCl,hidden,newCount,excluded};
  const keys=Object.keys(DS);keys.forEach(k=>{if(!store[k])store[k]=buildLive(k);});
  const rows=[['الخيار','المجموعة','عدد المدن','أقصى مدة','المدن']];
  keys.forEach(k=>{const s=store[k];const label=dsLabel(ageOf(k))+' — '+optOf(k);
    Object.keys(s.CL).sort((a,b)=>clKey(a)-clKey(b)).forEach(id=>{const cs=s.CL[id].cities;
      rows.push([label,id,cs.length,cs.length>1?fmt(stats(cs).mx/60):'—',cs.join('، ')]);});
    if(s.excluded&&s.excluded.size){rows.push([label,'🚫 مستبعدة من التجميع',s.excluded.size,'—',[...s.excluded].join('، ')]);}
    rows.push(['','','','','']);});
  const csv='﻿'+rows.map(r=>r.map(x=>'"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\\r\\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='groups_by_option.csv';a.click();}

function finishInit(){const v=document.getElementById('vnone');if(v)v.checked=!hideNone;
  updateDsUI();refreshSelectors();renderAll();}
function bootstrap(){
  if(!loadLocal())defaultInit();   // ارسم فورًا (لا ننتظر السحابة)
  finishInit();
  if(STATE_REF){STATE_REF.once('value').then(s=>{   // ثم زامن من السحابة إن توفّرت
      const v=s.val(); if(v&&v.store){applyStateObj(v);finishInit();}
    }).catch(()=>{});}
}
bootstrap();
</script></body></html>"""

import datetime
HTML = HTML.replace("__BUILD__", datetime.datetime.now().strftime("%m-%d %H:%M"))
HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open("/home/user/khitba/cluster_analysis/governorates_map.html", "w", encoding="utf-8").write(HTML)
print("تم حفظ governorates_map.html")
