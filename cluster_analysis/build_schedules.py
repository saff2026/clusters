#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة «الجداول» متعددة الفئات (schedules.html) من ملفات JSON.
لكل فئة: schedule_src_<ds>.json (قوالب/ملخص/إعدادات) + schedule_groups_<key>.json (المجموعات→الفرق).
تُولَّد ملفات src عبر extract_schedules.py، والمجموعات عبر derive_rosters (داخل publish)."""
import json, os, re

BRAEM = {"تحت 5", "تحت 7", "تحت 9"}

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

# (المفتاح، الاسم، ملف القوالب، ملف المجموعات)
AGES = [
    ("u5",  "تحت 5",  "schedule_src_u5.json",     "schedule_groups_u5.json"),
    ("u7",  "تحت 7",  "schedule_src_u7_9.json",   "schedule_groups_u7.json"),
    ("u9",  "تحت 9",  "schedule_src_u7_9.json",   "schedule_groups_u9.json"),
    ("u11", "تحت 11", "schedule_src_u11_12.json", "schedule_groups_u11.json"),
    ("u12", "تحت 12", "schedule_src_u11_12.json", "schedule_groups_u12.json"),
    ("u13", "تحت 13", "schedule_src_u13.json",    "schedule_groups_u13.json"),
    ("u14", "تحت 14", "schedule_src_u14.json",    "schedule_groups_u14.json"),
]

def load(fn):
    return json.load(open(BASE + fn, encoding="utf-8"))

# عدد الملاعب المطلوبة لكل مجموعة (من ورقة «عدد الملاعب» في ملف التسجيل)
try:
    PIT = load("schedule_pitches.json")
except Exception:
    PIT = {}

# تواريخ الجولات لكل فئة (من التقويم الموسمي)
try:
    DATES = load("schedule_dates.json")
except Exception:
    DATES = {}

ages = []
for key, label, srcf, grpf in AGES:
    if not (os.path.exists(BASE + srcf) and os.path.exists(BASE + grpf)):
        continue
    src = load(srcf); G = load(grpf)
    templates = src["templates"]
    avail = set(int(k) for k in templates.keys())
    pmap = PIT.get(label, {})
    groups = []
    for g in G["groups"]:
        teams = [t["name"] for t in g["teams"]]
        cities = [t.get("city", "") for t in g["teams"]]
        size = len(teams)
        pi = pmap.get(g["group"], {})
        groups.append({"group": g["group"], "region": g.get("region", ""),
                       "teams": teams, "cities": cities, "size": size,
                       "tmpl": size if size in avail else None,
                       "pitches": pi.get("pitches", 0), "pday": pi.get("day", ""),
                       "pmatches": pi.get("matchesDay", 0)})
    # إجماليات الفئة من القوالب المطبَّقة على المجموعات
    n_matches = n_fest = 0
    for g in groups:
        t = templates.get(str(g["size"]))
        if not t:
            continue
        n_matches += sum(1 for d in t["days"] for s in d["slots"] for c in s["cells"]
                         if re.match(r"^\d+\s*ضد\s*\d+$", str(c)))
        n_fest += len(t["days"])
    ages.append({"key": key, "label": label, "settings": src["settings"],
                 "summary": src["summary"], "templates": templates, "groups": groups,
                 "principles": src.get("principles", []),
                 "dates": DATES.get(label, []),
                 "matches": n_matches, "festivals": n_fest, "braem": label in BRAEM})

DATA = {"ages": ages}

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>جداول البطولات</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#04150e;color:#eafff3}
.top{background:#006C35;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.top img.logo{height:46px;width:auto;filter:brightness(0) invert(1)}
.top h1{font-size:19px;margin:0;font-weight:800}
.wrap{max-width:1500px;margin:0 auto;padding:16px}
.agebar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.agebtn{background:#0d3f2d;border:1px solid #1c6b49;color:#eafff3;border-radius:10px;padding:9px 18px;cursor:pointer;font-family:'Tajawal';font-size:15px;font-weight:800}
.agebtn.on{background:#ffd166;color:#04150e;border-color:#ffd166}
.cards{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.card{background:#0d3f2d;border:1px solid #1c6b49;border-radius:12px;padding:12px 16px;flex:1;min-width:150px}
.card .l{color:#8fdcb4;font-size:12px} .card .v{font-size:18px;font-weight:800;margin-top:3px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.tab{background:#0d4b32;border:1px solid #1c7a52;color:#eafff3;border-radius:20px;padding:8px 18px;cursor:pointer;font-family:'Tajawal';font-size:14px;font-weight:700}
.tab.on{background:#ffd166;color:#04150e;border-color:#ffd166}
.panel{background:#0b2c1f;border:1px solid #14543a;border-radius:14px;padding:14px}
.sel{display:block;background:#0d3f2d;color:#eafff3;border:1px solid #1c6b49;border-radius:10px;padding:10px 14px;font-family:'Tajawal';font-weight:700;font-size:14px;width:100%;max-width:520px;margin-bottom:10px;cursor:pointer}
.sel option{background:#0b2c1f;color:#eafff3}
.sellbl{color:#8fdcb4;font-size:12px;font-weight:700;margin:6px 0 3px}
.roster{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}
.rteam{background:#0d3f2d;border:1px solid #1c6b49;border-radius:8px;padding:5px 10px;font-size:12.5px}
.rteam b{color:#ffd166;margin-left:5px}
table.rtbl{width:100%;max-width:640px;border-collapse:collapse;font-size:13px;margin:6px 0 16px}
table.rtbl th{background:#0d4b32;color:#cdeede;font-weight:700;font-size:12px;padding:7px 10px;text-align:right;border:1px solid #14543a}
table.rtbl td{padding:7px 10px;border:1px solid #123f2b;background:#0a2418;text-align:right}
table.rtbl tr:nth-child(even) td{background:#0c2c1d}
table.rtbl tr:hover td{background:#123f2b}
table.rtbl td.rnum{width:44px;text-align:center;color:#ffd166;font-weight:800;background:#0d3f2d}
table.rtbl td.rname{font-weight:700}
table.rtbl td.rcity{color:#8fdcb4;width:130px}
.subttl{color:#04150e;background:#ffd166;font-weight:800;font-size:13px;margin:16px 0 2px;
 display:inline-block;padding:3px 12px;border-radius:8px}
h3.sec{color:#ffd166;font-size:15px;margin:16px 0 8px;border-bottom:1px solid #14543a;padding-bottom:5px}
.dayttl{color:#eafff3;font-weight:800;font-size:13px;margin:14px 0 6px;background:#0d4b32;border:1px solid #1c7a52;border-radius:8px;padding:5px 12px;display:inline-block}
.dayttl .dt{color:#ffd166;font-weight:700}
td.dt{color:#8fdcb4;white-space:nowrap;font-weight:700}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin-bottom:6px}
th,td{border:1px solid #14543a;padding:6px 8px;text-align:center}
th{background:#0d4b32;color:#eafff3;font-weight:700} td{background:#0a2418}
td.time{background:#0d3f2d;color:#ffd166;font-weight:700;white-space:nowrap;direction:ltr;unicode-bidi:isolate}
td.rest{color:#6f9a86;font-style:italic;background:#08190f}
.mtch b{color:#bfe9d4}
.note{color:#ffcf8a;background:#3a2f00;border:1px solid #ffd16655;border-radius:8px;padding:8px 11px;font-size:12.5px;margin-top:8px}
.muted{color:#8fdcb4;font-size:13px}
.stbl{overflow-x:auto}
.hint{color:#8fdcb4;font-size:12.5px;margin:2px 0 12px}
.prin{display:flex;gap:12px;align-items:flex-start;background:#0d3f2d;border:1px solid #1c6b49;border-radius:12px;padding:12px 14px;margin-bottom:10px}
.prin .pn{flex:0 0 32px;height:32px;border-radius:50%;background:#ffd166;color:#04150e;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:15px}
.prin .pt{font-weight:800;font-size:14.5px;color:#eafff3;margin-bottom:3px}
.prin .pe{color:#bfe9d4;font-size:12.5px;line-height:1.7}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد" onerror="this.remove()">
 <h1>🗓️ جداول البطولات</h1>
</div>
<div class="wrap">
 <div class="agebar" id="agebar"></div>
 <div class="tabs" id="tabs"></div>
 <div class="panel" id="panel"></div>
</div>
<script>
const D=__DATA__;
const PR=(D.ages.slice().sort((a,b)=>((b.principles||[]).length)-((a.principles||[]).length))[0]||{}).principles||[];
function gp(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function arCount(n,one,two,few,many){const m=n%100;if(n===1)return one;if(n===2)return two;
  if(m>=3&&m<=10)return gp(n)+' '+few;return gp(n)+' '+many;}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function nMatch(n){return arCount(n,'مباراة واحدة','مباراتان','مباريات','مباراةً');}
function nPitch(n){return arCount(n,'ملعب واحد','ملعبان','ملاعب','ملعبًا');}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function dayNum(d){return String(d).replace(/^\s*اليوم\s*/,'');}
function subLabelOf(subs,num){for(const s of subs){if(s.teams.indexOf(num)>=0)return s.label;}return '';}
function rosterTable(nums,teams,cities){
  const list=nums||teams.map((_,i)=>i+1);
  let h='<div class="stbl"><table class="rtbl"><thead><tr><th class="rnum">#</th><th>الفريق</th><th>المدينة</th></tr></thead><tbody>';
  list.forEach(n=>{h+='<tr><td class="rnum">'+n+'</td><td class="rname">'+esc(teams[n-1]||('#'+n))+
    '</td><td class="rcity">'+esc((cities&&cities[n-1])||'')+'</td></tr>';});
  return h+'</tbody></table></div>';
}
function toAr(n){return String(n).replace(/\d/g,d=>'٠١٢٣٤٥٦٧٨٩'[+d]);}
const WD=['الأحد','الإثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'];
const MO=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
function fmtDate(iso){const d=new Date(iso+'T00:00:00');
  return WD[d.getDay()]+' '+toAr(d.getDate())+' '+MO[d.getMonth()]+' '+toAr(d.getFullYear());}
function shortDate(iso){const d=new Date(iso+'T00:00:00');return toAr(d.getDate())+' '+MO[d.getMonth()];}
function roundDate(dates,n){
  if(!dates||!dates.length||!n)return null;
  if(n<=dates.length)return dates[n-1];
  const last=new Date(dates[dates.length-1]+'T00:00:00');
  last.setDate(last.getDate()+7*(n-dates.length));   // الجولات الزائدة: أسبوعيًا (يونيو)
  return last.toISOString().slice(0,10);
}
function dayTitle(dayStr,dates){
  const m=String(dayStr).match(/(\d+)/);const n=m?+m[1]:0;
  const fest=/مهرجان/.test(dayStr);
  const base=(fest?'المهرجان ':'الجولة ')+toAr(n);
  const dt=roundDate(dates,n);
  return base+(dt?' — <span class="dt">'+fmtDate(dt)+'</span>':'');
}
function cellHTML(cell,teams){
  const m=cell.match(/^(\d+)\s*ضد\s*(\d+)$/);
  if(m&&teams){const a=teams[+m[1]-1]||('#'+m[1]),b=teams[+m[2]-1]||('#'+m[2]);
    return '<span class="mtch"><b>'+esc(a)+'</b> ضد <b>'+esc(b)+'</b></span>';}
  if(/^استراحة/.test(cell))return '—';
  return esc(cell);
}
function isRestRow(s){return s.cells.some(c=>/^استراحة/.test(c))&&s.cells.every(c=>c===''||/^استراحة/.test(c));}
function renderTemplate(t,teams,dates){
  if(!t)return '';let h='';
  t.days.forEach(day=>{
    h+='<div class="dayttl">'+dayTitle(day.day,dates)+'</div><div class="stbl"><table><tr><th>الوقت</th>'+
      t.pitches.map(p=>'<th>'+esc(p)+'</th>').join('')+'</tr>';
    day.slots.forEach(s=>{
      if(isRestRow(s)){h+='<tr><td class="time">'+esc(s.time)+'</td><td class="rest" colspan="'+t.pitches.length+'">استراحة</td></tr>';return;}
      h+='<tr><td class="time">'+esc(s.time)+'</td>'+s.cells.map(c=>'<td>'+(c?cellHTML(c,teams):'')+'</td>').join('')+'</tr>';
    });
    h+='</table></div>';
  });
  return h;
}
function teamMatches(t,teams,idx){const num=idx+1,out=[];
  t.days.forEach(day=>day.slots.forEach(s=>s.cells.forEach((c,ci)=>{
    const m=c&&c.match(/^(\d+)\s*ضد\s*(\d+)$/);if(!m)return;const a=+m[1],b=+m[2];
    if(a===num||b===num){const opp=a===num?b:a;
      out.push({day:day.day,time:s.time,pitch:t.pitches[ci],opp:teams[opp-1]||('#'+opp)});}
  })));return out;}
function teamMatchesHTML(t,teams,idx,dates){
  const rows=teamMatches(t,teams,idx);
  let h='<div class="stbl"><table><tr><th>الجولة</th><th>التاريخ</th><th>الوقت</th><th>الملعب</th><th>الخصم</th></tr>';
  rows.forEach(r=>{const m=String(r.day).match(/(\d+)/);const n=m?+m[1]:0;const dt=roundDate(dates,n);
    const fest=/مهرجان/.test(r.day);
    h+='<tr><td>'+(fest?'م':'')+toAr(n)+'</td><td class="dt">'+(dt?shortDate(dt):'')+'</td><td class="time">'+esc(r.time)+'</td><td>'+esc(r.pitch)+'</td><td class="mtch"><b>'+esc(r.opp)+'</b></td></tr>';});
  h+='</table></div>';return {html:h,count:rows.length};
}
// ===== الحالة =====
let curAge=-1, tab='groups', curG=0, curT=0, curTeam=null, curRegion='';
function A(){return D.ages[curAge];}
function resetAge(){curG=0;curTeam=null;curRegion='';tab='groups';
  const sz=Object.keys(A().templates).map(Number).sort((a,b)=>a-b);curT=sz.length?sz[0]:0;}
function renderAgebar(){
  let h='<button class="agebtn'+(curAge===-1?' on':'')+'" data-i="-1">📋 ملخص الكل</button>';
  h+=D.ages.map((a,i)=>'<button class="agebtn'+(i===curAge?' on':'')+'" data-i="'+i+'">'+esc(a.label)+'</button>').join('');
  document.getElementById('agebar').innerHTML=h;
  document.querySelectorAll('#agebar .agebtn').forEach(b=>b.onclick=()=>{curAge=+b.dataset.i;if(curAge>=0)resetAge();render();window.scrollTo(0,0);});}
function principlesPanel(){
  if(!PR.length)return '<div class="muted">لا توجد مبادئ.</div>';
  let h='<h3 class="sec">المبادئ الأساسية لبناء الجداول</h3>';
  PR.forEach((p,i)=>{h+='<div class="prin"><div class="pn">'+(i+1)+'</div><div><div class="pt">'+esc(p.p)+'</div>'+
    (p.e?'<div class="pe">'+esc(p.e)+'</div>':'')+'</div></div>';});
  return h;}
// جدول ملخص فئة واحدة مع عمود «ملاعب (التسجيل)» للمقارنة
function summaryTable(a){
  const s=a.summary;if(!s.headers.length)return '<div class="muted">لا يوجد ملخص.</div>';
  const sizePitch={};a.groups.forEach(g=>{if(g.pitches&&!(g.size in sizePitch))sizePitch[g.size]=g.pitches;});
  let h='<div class="stbl"><table><tr>'+s.headers.map(x=>'<th>'+esc(x)+'</th>').join('')+'<th>🏟️ ملاعب (التسجيل)</th></tr>';
  s.rows.forEach(r=>{const n=parseInt(String(r[0]).replace(/[^0-9]/g,''))||0;const rp=sizePitch[n];
    h+='<tr>'+s.headers.map((_,j)=>'<td'+(j===0?' class="time"':'')+'>'+esc(r[j]||'')+'</td>').join('')+
      '<td class="time">'+(rp||'—')+'</td></tr>';});
  h+='</table></div>';return h;}
function overviewPanel(){
  let h='<div class="hint">📊 ملخص الموسم لكل فئة — اضغط اسم الفئة بالأعلى لعرض جداولها.</div>';
  h+='<div class="stbl"><table><tr><th>الفئة</th><th>المجموعات</th><th>الفرق</th>'+
     '<th>عدد المباريات</th><th>عدد المهرجانات</th></tr>';
  let TM=0,TF=0,TG=0,TT=0;
  D.ages.forEach(a=>{
    const gs=a.groups.filter(g=>g.size>=5);
    const grps=gs.length, teams=gs.reduce((s,g)=>s+g.size,0);
    TG+=grps; TT+=teams;
    if(a.braem)TF+=a.festivals; else TM+=a.matches;
    h+='<tr><td class="time">'+esc(a.label)+'</td><td>'+gp(grps)+'</td><td>'+gp(teams)+'</td>'+
       '<td>'+(a.braem?'—':'<b style="color:#ffd166">'+gp(a.matches)+'</b>')+'</td>'+
       '<td>'+(a.braem?'<b style="color:#ffd166">'+gp(a.festivals)+'</b>':'—')+'</td></tr>';
  });
  h+='<tr style="font-weight:800;background:#0d4b32"><td class="time">الإجمالي</td><td>'+gp(TG)+'</td><td>'+gp(TT)+'</td>'+
     '<td>'+gp(TM)+'</td><td>'+gp(TF)+'</td></tr>';
  h+='</table></div>';
  h+='<div class="hint" style="margin-top:10px">⚽ المباريات لفئات تحت ١١–١٤ (دوري داخل كل مجموعة/مجموعة فرعية). 🎪 المهرجانات لفئات البراعم تحت ٥–٩.</div>';
  return h;}
const TABS=[['groups','المجموعات']];
function renderTabs(){document.getElementById('tabs').innerHTML='';}
function groupsPanel(){
  const TARGET=5;
  const all=A().groups;
  // المكتملة = ٥ فرق فأكثر
  const complete=i=>all[i].size>=TARGET;
  const regions=[...new Set(all.filter((g,i)=>complete(i)).map(g=>g.region).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ar'));
  let h='<div class="hint">💡 اختر المنطقة ثم المجموعة لعرض فرقها وجدولها. الفرق المرقّمة مؤقتة (ترتيب التسجيل). تُعرض المجموعات المكتملة (٥ فرق فأكثر) فقط.</div>';
  h+='<div class="sellbl">🗺️ المنطقة</div>';
  h+='<select id="rsel" class="sel"><option value=""'+(curRegion===''?' selected':'')+'>كل المناطق</option>'+
    regions.map(r=>'<option value="'+esc(r)+'"'+(curRegion===r?' selected':'')+'>'+esc(r)+'</option>').join('')+'</select>';
  const idx=all.map((g,i)=>i).filter(i=>complete(i)&&(!curRegion||all[i].region===curRegion));
  if(idx.indexOf(curG)<0){curG=idx.length?idx[0]:-1;curTeam=null;}
  h+='<div class="sellbl">🧩 المجموعة</div>';
  h+='<select id="gsel" class="sel">'+idx.map(i=>'<option value="'+i+'"'+(i===curG?' selected':'')+'>'+
    esc(all[i].group)+' — '+nTeam(all[i].size)+'</option>').join('')+'</select>';
  const g=(curG>=0)?all[curG]:null;
  if(g){
    h+='<h3 class="sec">'+esc(g.group)+' — '+nTeam(g.size)+(g.region?' · '+esc(g.region):'')+'</h3>';
    if(g.tmpl){
      const tmpl=A().templates[String(g.tmpl)];const subs=tmpl.subgroups||[];
      if(subs.length>1){
        h+='<div class="hint">هذه المجموعة مقسّمة إلى '+subs.length+' مجموعات فرعية، تلعب كل واحدة على ملاعبها:</div>';
        subs.forEach(sg=>{h+='<div class="subttl">المجموعة '+sg.label+' — '+nTeam(sg.teams.length)+'</div>'+
          rosterTable(sg.teams,g.teams,g.cities);});
      }else{
        h+='<div class="subttl">فرق المجموعة</div>'+rosterTable(null,g.teams,g.cities);
      }
      h+='<div class="hint">اختر فريقًا لعرض مبارياته فقط، أو «الجدول الكامل» للكل:</div>';
      h+='<select id="tsel" class="sel"><option value="-1"'+(curTeam===null?' selected':'')+'>📋 الجدول الكامل</option>'+
        g.teams.map((t,i)=>{const sl=subLabelOf(subs,i+1);return '<option value="'+i+'"'+(curTeam===i?' selected':'')+'>'+(i+1)+' — '+esc(t)+(sl?' (المجموعة '+sl+')':'')+'</option>';}).join('')+'</select>';
      if(curTeam!==null){const r=teamMatchesHTML(tmpl,g.teams,curTeam,A().dates);const sl=subLabelOf(subs,curTeam+1);
        h+='<h3 class="sec">مباريات '+esc(g.teams[curTeam])+(sl?' (المجموعة '+sl+')':'')+' — '+nMatch(r.count)+'</h3>'+r.html;}
      else h+=renderTemplate(tmpl,g.teams,A().dates);
    }else{
      h+='<div class="subttl">فرق المجموعة</div>'+rosterTable(null,g.teams,g.cities);
      h+='<div class="note">لا يوجد قالب جدول جاهز لعدد '+nTeam(g.size)+' في ملف الجداول بعد — عُرضت قائمة الفرق فقط.</div>';
    }
  }
  return h;
}
function tmplPanel(){
  const sizes=Object.keys(A().templates).map(Number).sort((a,b)=>a-b);
  let h='<div class="hint">💡 قوالب الجداول حسب عدد الفرق (بالأرقام). تُطبَّق على أي مجموعة بنفس العدد.</div>';
  h+='<select id="tmsel" class="sel">'+sizes.map(s=>'<option value="'+s+'"'+(s===curT?' selected':'')+'>'+nTeam(s)+'</option>').join('')+'</select>';
  const t=A().templates[String(curT)];
  if(t){const subs=t.subgroups||[];
    h+='<h3 class="sec">'+esc(t.title)+'</h3>';
    if(subs.length>1)h+='<div class="hint">'+subs.map(s=>'المجموعة '+s.label+': '+s.teams.length+' فرق').join(' · ')+'</div>';
    h+=renderTemplate(t,null,A().dates);}
  return h;
}
function summaryPanel(){
  if(!A().summary.headers.length)return '<div class="muted">لا يوجد ملخص.</div>';
  return '<h3 class="sec">ملخص جداول المجموعات (حسب عدد الفرق)</h3>'+summaryTable(A());
}
function render(){
  renderAgebar();
  const p=document.getElementById('panel');
  if(curAge===-1){document.getElementById('tabs').innerHTML='';p.innerHTML=overviewPanel();return;}
  renderTabs();
  if(curAge===-2){document.getElementById('tabs').innerHTML='';p.innerHTML=principlesPanel();return;}
  p.innerHTML = groupsPanel();
  const rs=document.getElementById('rsel');if(rs)rs.onchange=()=>{curRegion=rs.value;curTeam=null;curG=-1;render();window.scrollTo(0,0);};
  const gs=document.getElementById('gsel');if(gs)gs.onchange=()=>{curG=+gs.value;curTeam=null;render();window.scrollTo(0,0);};
  const ts=document.getElementById('tsel');if(ts)ts.onchange=()=>{const v=+ts.value;curTeam=(v<0?null:v);render();};
}
render();
</script>
</body></html>"""

HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open(BASE + "schedules.html", "w", encoding="utf-8").write(HTML)
print("saved schedules.html", round(len(HTML)/1024), "KB | فئات:", [a["label"] for a in ages],
      "| مجموع القوالب:", sum(len(a["templates"]) for a in ages))
