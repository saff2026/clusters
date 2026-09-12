#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة «الجداول» متعددة الفئات (schedules.html) من ملفات JSON.
لكل فئة: schedule_src_<ds>.json (قوالب/ملخص/إعدادات) + schedule_groups_<key>.json (المجموعات→الفرق).
تُولَّد ملفات src عبر extract_schedules.py، والمجموعات عبر derive_rosters (داخل publish)."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__)) + "/"

# (المفتاح، الاسم، ملف القوالب، ملف المجموعات)
AGES = [
    ("u5",  "تحت 5",  "schedule_src_u5.json",     "schedule_groups_u5.json"),
    ("u11", "تحت 11", "schedule_src_u11_12.json", "schedule_groups_u11.json"),
    ("u12", "تحت 12", "schedule_src_u11_12.json", "schedule_groups_u12.json"),
    ("u13", "تحت 13", "schedule_src_u13.json",    "schedule_groups_u13.json"),
    ("u14", "تحت 14", "schedule_src_u14.json",    "schedule_groups_u14.json"),
]

def load(fn):
    return json.load(open(BASE + fn, encoding="utf-8"))

ages = []
for key, label, srcf, grpf in AGES:
    if not (os.path.exists(BASE + srcf) and os.path.exists(BASE + grpf)):
        continue
    src = load(srcf); G = load(grpf)
    templates = src["templates"]
    avail = set(int(k) for k in templates.keys())
    groups = []
    for g in G["groups"]:
        teams = [t["name"] for t in g["teams"]]
        size = len(teams)
        groups.append({"group": g["group"], "region": g.get("region", ""),
                       "teams": teams, "size": size, "tmpl": size if size in avail else None})
    ages.append({"key": key, "label": label, "settings": src["settings"],
                 "summary": src["summary"], "templates": templates, "groups": groups})

DATA = {"ages": ages}

HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>جداول البطولات</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#04150e;color:#eafff3}
.top{background:#006C35;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.top img.logo{height:46px}
.top h1{font-size:19px;margin:0;font-weight:800}
.wrap{max-width:1080px;margin:0 auto;padding:16px}
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
.sel{background:#0d3f2d;color:#eafff3;border:1px solid #1c6b49;border-radius:10px;padding:10px 14px;font-family:'Tajawal';font-weight:700;font-size:14px;min-width:min(300px,100%);max-width:100%;margin-bottom:12px;cursor:pointer}
.sel option{background:#0b2c1f;color:#eafff3}
.roster{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}
.rteam{background:#0d3f2d;border:1px solid #1c6b49;border-radius:8px;padding:5px 10px;font-size:12.5px}
.rteam b{color:#ffd166;margin-left:5px}
.subttl{color:#ffd166;font-weight:800;font-size:14px;margin:12px 0 4px}
h3.sec{color:#ffd166;font-size:15px;margin:16px 0 8px;border-bottom:1px solid #14543a;padding-bottom:5px}
.dayttl{color:#eafff3;font-weight:800;font-size:13px;margin:14px 0 6px;background:#0d4b32;border:1px solid #1c7a52;border-radius:8px;padding:5px 12px;display:inline-block}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin-bottom:6px}
th,td{border:1px solid #14543a;padding:6px 8px;text-align:center}
th{background:#0d4b32;color:#eafff3;font-weight:700} td{background:#0a2418}
td.time{background:#0d3f2d;color:#ffd166;font-weight:700;white-space:nowrap}
td.rest{color:#6f9a86;font-style:italic;background:#08190f}
.mtch b{color:#bfe9d4}
.note{color:#ffcf8a;background:#3a2f00;border:1px solid #ffd16655;border-radius:8px;padding:8px 11px;font-size:12.5px;margin-top:8px}
.muted{color:#8fdcb4;font-size:13px}
.stbl{overflow-x:auto}
.hint{color:#8fdcb4;font-size:12.5px;margin:2px 0 12px}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد" onerror="this.remove()">
 <h1>🗓️ جداول البطولات</h1>
</div>
<div class="wrap">
 <div class="agebar" id="agebar"></div>
 <div class="cards" id="cards"></div>
 <div class="tabs" id="tabs"></div>
 <div class="panel" id="panel"></div>
</div>
<script>
const D=__DATA__;
function gp(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function arCount(n,one,two,few,many){const m=n%100;if(n===1)return one;if(n===2)return two;
  if(m>=3&&m<=10)return gp(n)+' '+few;return gp(n)+' '+many;}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function nMatch(n){return arCount(n,'مباراة واحدة','مباراتان','مباريات','مباراةً');}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function dayNum(d){return String(d).replace(/^\s*اليوم\s*/,'');}
function subLabelOf(subs,num){for(const s of subs){if(s.teams.indexOf(num)>=0)return s.label;}return '';}
function cellHTML(cell,teams){
  const m=cell.match(/^(\d+)\s*ضد\s*(\d+)$/);
  if(m&&teams){const a=teams[+m[1]-1]||('#'+m[1]),b=teams[+m[2]-1]||('#'+m[2]);
    return '<span class="mtch"><b>'+esc(a)+'</b> ضد <b>'+esc(b)+'</b></span>';}
  if(/^استراحة/.test(cell))return '—';
  return esc(cell);
}
function isRestRow(s){return s.cells.some(c=>/^استراحة/.test(c))&&s.cells.every(c=>c===''||/^استراحة/.test(c));}
function renderTemplate(t,teams){
  if(!t)return '';let h='';
  t.days.forEach(day=>{
    h+='<div class="dayttl">'+esc(day.day)+'</div><div class="stbl"><table><tr><th>الوقت</th>'+
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
function teamMatchesHTML(t,teams,idx){
  const rows=teamMatches(t,teams,idx);
  let h='<div class="stbl"><table><tr><th>اليوم</th><th>الوقت</th><th>الملعب</th><th>الخصم</th></tr>';
  rows.forEach(r=>{h+='<tr><td>'+esc(dayNum(r.day))+'</td><td class="time">'+esc(r.time)+'</td><td>'+esc(r.pitch)+'</td><td class="mtch"><b>'+esc(r.opp)+'</b></td></tr>';});
  h+='</table></div>';return {html:h,count:rows.length};
}
// ===== الحالة =====
let curAge=0, tab='groups', curG=0, curT=0, curTeam=null;
function A(){return D.ages[curAge];}
function resetAge(){curG=0;curTeam=null;tab='groups';
  const sz=Object.keys(A().templates).map(Number).sort((a,b)=>a-b);curT=sz.length?sz[0]:0;}
function renderAgebar(){document.getElementById('agebar').innerHTML=D.ages.map((a,i)=>
  '<button class="agebtn'+(i===curAge?' on':'')+'" data-i="'+i+'">'+esc(a.label)+'</button>').join('');
  document.querySelectorAll('#agebar .agebtn').forEach(b=>b.onclick=()=>{curAge=+b.dataset.i;resetAge();render();});}
function renderCards(){document.getElementById('cards').innerHTML=A().settings.map(s=>
  '<div class="card"><div class="l">'+esc(s[0])+'</div><div class="v">'+esc(s[1])+'</div></div>').join('');}
const TABS=[['groups','المجموعات'],['tmpl','قوالب الجداول'],['summary','ملخص البطولات']];
function renderTabs(){document.getElementById('tabs').innerHTML=TABS.map(([k,l])=>
  '<button class="tab'+(k===tab?' on':'')+'" data-k="'+k+'">'+l+'</button>').join('');
  document.querySelectorAll('#tabs .tab').forEach(b=>b.onclick=()=>{tab=b.dataset.k;render();});}
function groupsPanel(){
  const gs2=A().groups;const g=gs2[curG];
  let h='<div class="hint">💡 اختر مجموعة لعرض فرقها وجدولها. الفرق المرقّمة مؤقتة (ترتيب التسجيل).</div>';
  h+='<select id="gsel" class="sel">'+gs2.map((x,i)=>'<option value="'+i+'"'+(i===curG?' selected':'')+'>'+
    esc(x.group)+' — '+nTeam(x.size)+'</option>').join('')+'</select>';
  if(g){
    h+='<h3 class="sec">'+esc(g.group)+' — '+nTeam(g.size)+(g.region?' · '+esc(g.region):'')+'</h3>';
    if(g.tmpl){
      const tmpl=A().templates[String(g.tmpl)];const subs=tmpl.subgroups||[];
      if(subs.length>1){
        h+='<div class="hint">هذه المجموعة مقسّمة إلى '+subs.length+' مجموعات فرعية، تلعب كل واحدة على ملاعبها:</div>';
        subs.forEach(sg=>{h+='<div class="subttl">المجموعة '+sg.label+'</div><div class="roster">'+
          sg.teams.map(n=>'<span class="rteam"><b>'+n+'</b>'+esc(g.teams[n-1]||('#'+n))+'</span>').join('')+'</div>';});
      }
      h+='<div class="hint">اختر فريقًا لعرض مبارياته فقط، أو «الجدول الكامل» للكل:</div>';
      h+='<select id="tsel" class="sel"><option value="-1"'+(curTeam===null?' selected':'')+'>📋 الجدول الكامل</option>'+
        g.teams.map((t,i)=>{const sl=subLabelOf(subs,i+1);return '<option value="'+i+'"'+(curTeam===i?' selected':'')+'>'+(i+1)+' — '+esc(t)+(sl?' (المجموعة '+sl+')':'')+'</option>';}).join('')+'</select>';
      if(curTeam!==null){const r=teamMatchesHTML(tmpl,g.teams,curTeam);const sl=subLabelOf(subs,curTeam+1);
        h+='<h3 class="sec">مباريات '+esc(g.teams[curTeam])+(sl?' (المجموعة '+sl+')':'')+' — '+nMatch(r.count)+'</h3>'+r.html;}
      else h+=renderTemplate(tmpl,g.teams);
    }else{
      h+='<div class="roster">'+g.teams.map((t,i)=>'<span class="rteam"><b>'+(i+1)+'</b>'+esc(t)+'</span>').join('')+'</div>';
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
    h+=renderTemplate(t,null);}
  return h;
}
function summaryPanel(){
  const s=A().summary;if(!s.headers.length)return '<div class="muted">لا يوجد ملخص.</div>';
  let h='<h3 class="sec">ملخص جداول المجموعات</h3><div class="stbl"><table><tr>'+
    s.headers.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr>';
  s.rows.forEach(r=>{h+='<tr>'+s.headers.map((_,j)=>'<td'+(j===0?' class="time"':'')+'>'+esc(r[j]||'')+'</td>').join('')+'</tr>';});
  h+='</table></div>';return h;
}
function render(){
  renderAgebar();renderCards();renderTabs();
  const p=document.getElementById('panel');
  p.innerHTML = tab==='groups'?groupsPanel() : tab==='tmpl'?tmplPanel() : summaryPanel();
  if(tab==='groups'){
    const gs=document.getElementById('gsel');if(gs)gs.onchange=()=>{curG=+gs.value;curTeam=null;render();window.scrollTo(0,0);};
    const ts=document.getElementById('tsel');if(ts)ts.onchange=()=>{const v=+ts.value;curTeam=(v<0?null:v);render();};
  }
  if(tab==='tmpl'){const ms=document.getElementById('tmsel');if(ms)ms.onchange=()=>{curT=+ms.value;render();window.scrollTo(0,0);};}
}
resetAge();render();
</script>
</body></html>"""

HTML = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
open(BASE + "schedules.html", "w", encoding="utf-8").write(HTML)
print("saved schedules.html", round(len(HTML)/1024), "KB | فئات:", [a["label"] for a in ages],
      "| مجموع القوالب:", sum(len(a["templates"]) for a in ages))
