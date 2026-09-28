#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني صفحة «حالة سداد وتفعيل حسابات الفرق» (pay.html).
لكل معيار (السداد / تفعيل الحساب): عدد الفرق غير المطابقة وتوزيعها على المناطق،
ومحاكاة: لو أُلغيت هذه الفرق، كم مجموعة تخرج من الاكتمال (أقل من ٦ فرق) وكم فريقًا يُفقد.
المصدر: «بيانات التسجيل» + «عدد الفرق لكل مدينة» + «المدخلات» من نفس الملف.
الاستخدام: python3 build_pay.py <ملف.xlsx>"""
import sys, json, openpyxl
from collections import defaultdict, Counter

BASE = "/home/user/khitba/cluster_analysis/"
XLSX = sys.argv[1] if len(sys.argv) > 1 else BASE + "pay_latest.xlsx"
CANON = {"جيزان": "جازان", "الجوف": "سكاكا", "ابها": "أبها"}
SIFA = {"هواة": "هواة", "اكاديمية": "أكاديمية", "اكاديمة": "أكاديمية",
        "أكاديمية": "أكاديمية", "نادي": "نادي", "نالدي خاص": "نادي"}
TARGET = 6

M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
REG = dict(M["REG"])          # مدينة -> منطقة (اسم رسمي)
REGIONS = M["regions"]

wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

# ========== 1) التصنيف والأساس من «عدد الفرق لكل مدينة» ==========
ws = wb["عدد الفرق لكل مدينة"]
rows = list(ws.iter_rows(values_only=True))
C2G = {}                       # age -> city -> group
base = defaultdict(int)        # (age, grp) -> إجمالي الفرق (الأساس)
grp_cities = defaultdict(set)  # (age, grp) -> {cities}
for r in rows[2:]:
    if not r:
        continue
    age = str(r[1]).strip() if r[1] else ""
    city = str(r[2]).strip() if r[2] else ""
    grp = str(r[3]).strip() if r[3] else ""
    if not age or not city or not grp:
        continue
    city = CANON.get(city, city)
    cnt = int(r[4]) if len(r) > 4 and isinstance(r[4], (int, float)) else 0
    C2G.setdefault(age, {})[city] = grp
    base[(age, grp)] += cnt
    grp_cities[(age, grp)].add(city)

# منطقة كل مجموعة = الغالبة على مدنها (نفس منطق صفحة التقسيم)
def grp_region(age, grp):
    c = Counter(REG.get(ci) for ci in grp_cities[(age, grp)] if REG.get(ci))
    return c.most_common(1)[0][0] if c else "غير محدد"

# ========== 2) بيانات الفرق من «بيانات التسجيل» ==========
ws2 = wb["بيانات التسجيل"]
r2 = list(ws2.iter_rows(values_only=True))
hi = next(i for i, r in enumerate(r2)
          if r and "الصفة" in [str(c).strip() if c else "" for c in r])
H = {str(c).strip(): j for j, c in enumerate(r2[hi]) if c is not None and str(c).strip()}
agecols = [k for k in H if "المشاركة" in k]
PAYCOL = next((k for k in H if "السداد" in k), None)
ACCTCOL = next((k for k in H if "حساب" in k and "تسجيل" in k), None)

def age_of(cn):
    return "تحت " + "".join(ch for ch in cn if ch.isdigit())

ages = sorted({age_of(c) for c in agecols},
              key=lambda x: int("".join(ch for ch in x if ch.isdigit())))

MET = ("pay", "acct", "both")
rm = {k: defaultdict(int) for k in MET}     # (age,grp) -> فرق محذوفة
teams_ct = {k: 0 for k in MET}
entries_ct = {k: 0 for k in MET}
byreg_teams = {k: Counter() for k in MET}
byreg_entries = {k: Counter() for k in MET}
total_teams = 0
total_entries = 0
amateur_teams = 0

for r in r2[hi + 1:]:
    if not r or all(c in (None, "") for c in r):
        continue
    tname = str(r[H["اسم الفريق"]] or "").strip() if "اسم الفريق" in H else ""
    if not tname:
        continue
    city = str(r[H["المدينة"]] or "").strip()
    city = CANON.get(city, city) or "غير محدد"
    region = REG.get(city, "غير محدد")
    raw_sifa = str(r[H["الصفة"]] or "").strip() if "الصفة" in H else ""
    sifa = SIFA.get(raw_sifa, raw_sifa)
    is_amateur = (sifa == "هواة")   # الأندية والأكاديميات تُعتبر مسدِّدة ومفعِّلة الحساب
    pay_raw = str(r[H[PAYCOL]] or "").strip() if PAYCOL else ""
    acct_raw = str(r[H[ACCTCOL]] or "").strip() if ACCTCOL else ""
    unpaid = is_amateur and (("لم يتم" in pay_raw) or ("لم يسدد" in pay_raw))
    not_acct = is_amateur and (acct_raw != "نعم")
    ent = 0
    contrib = []
    for cn in agecols:
        v = r[H[cn]]
        if not isinstance(v, (int, float)) or v <= 0:
            continue
        v = int(v)
        age = age_of(cn)
        grp = (C2G.get(age, {}) or {}).get(city, "(غير مصنّف)")
        ent += v
        contrib.append((age, grp, v))
    total_teams += 1
    total_entries += ent
    if is_amateur:
        amateur_teams += 1
    for metric, flag in (("pay", unpaid), ("acct", not_acct), ("both", unpaid and not_acct)):
        if flag:
            teams_ct[metric] += 1
            entries_ct[metric] += ent
            byreg_teams[metric][region] += 1
            byreg_entries[metric][region] += ent
            for age, grp, v in contrib:
                rm[metric][(age, grp)] += v

# ========== 3) التصدير ==========
groups = {}
for (age, grp), tot in base.items():
    if grp == "(غير مصنّف)":
        continue
    groups[age + "|" + grp] = {"age": age, "group": grp,
                               "region": grp_region(age, grp), "total": tot}

def metric_block(metric):
    removed = {}
    for (age, grp), c in rm[metric].items():
        if grp == "(غير مصنّف)":
            continue
        removed[age + "|" + grp] = c
    return {"teams": teams_ct[metric], "entries": entries_ct[metric],
            "byRegionTeams": dict(byreg_teams[metric]),
            "byRegionEntries": dict(byreg_entries[metric]),
            "removed": removed}

PAY = {"ages": ages, "regions": REGIONS, "target": TARGET,
       "totalTeams": total_teams, "totalEntries": total_entries,
       "amateurTeams": amateur_teams,
       "groups": groups,
       "metrics": {k: metric_block(k) for k in MET}}
json.dump(PAY, open(BASE + "pay_data.json", "w", encoding="utf-8"), ensure_ascii=False)

# ========== 4) بناء الصفحة ==========
HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>حالة سداد وتفعيل حسابات الفرق</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<style>
 *{box-sizing:border-box} body{margin:0;font-family:'Tajawal',sans-serif;background:#0b1c30;color:#e9eef5}
 a{color:#7cc4ff;text-decoration:none}
 .top{background:#0a3d62;padding:14px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;
   position:sticky;top:0;z-index:10;box-shadow:0 2px 10px rgba(0,0,0,.4)}
 .top h1{margin:0;font-size:19px;font-weight:800} .top .sp{flex:1}
 .top .logo{height:46px;width:auto;display:block;flex-shrink:0;filter:brightness(0) invert(1)}
 .wrap{max-width:1400px;margin:0 auto;padding:18px}
 .flt{margin-bottom:14px} .flt .lab{font-size:12px;color:#9fb6d0;margin-bottom:5px;font-weight:700}
 .tabs{display:flex;flex-wrap:wrap;gap:8px}
 .tab{background:#16314f;border:1px solid #2a4a6e;color:#e9eef5;border-radius:20px;padding:7px 18px;
   cursor:pointer;font-family:'Tajawal';font-size:14px;font-weight:700}
 .tab.on{background:#ffd166;color:#0a3d62;border-color:#ffd166}
 select.rgn{padding:8px 12px;border-radius:8px;border:1px solid #2a4a6e;background:#13294a;color:#fff;
   font-family:'Tajawal';font-size:13px;font-weight:700;min-width:200px}
 .simrow{display:flex;align-items:center;gap:12px;background:#12283f;border:1px solid #1c3a5e;
   border-radius:12px;padding:12px 16px;margin:14px 0}
 .switch{position:relative;display:inline-block;width:52px;height:28px;flex-shrink:0}
 .switch input{opacity:0;width:0;height:0}
 .sl{position:absolute;inset:0;background:#2a4a6e;border-radius:28px;transition:.2s;cursor:pointer}
 .sl:before{content:"";position:absolute;height:22px;width:22px;right:3px;top:3px;background:#fff;border-radius:50%;transition:.2s}
 .switch input:checked + .sl{background:#e0483d}
 .switch input:checked + .sl:before{transform:translateX(-24px)}
 .simrow .txt{font-weight:700;font-size:14px} .simrow .sub{color:#9fb6d0;font-size:12px;font-weight:400}
 .simsub{color:#9fb6d0;font-size:12.5px;margin:-4px 0 12px}
 .kpis{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0 18px}
 .kpi{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:16px 20px;flex:1;min-width:170px;text-align:center}
 .kpi .n{font-size:30px;font-weight:800;color:#ffd166;line-height:1.1}
 .kpi .l{font-size:12.5px;color:#9fb6d0;margin-top:4px}
 .kpi.warn .n{color:#ff9a9a} .kpi.bad .n{color:#e0483d} .kpi.good .n{color:#7ee0a0}
 .sec{color:#ffd166;font-weight:800;font-size:16px;margin:22px 2px 10px}
 .card{background:#12283f;border:1px solid #1c3a5e;border-radius:12px;padding:14px 16px;margin:10px 0}
 .rbar{display:flex;align-items:center;gap:10px;margin-bottom:9px;font-size:13px}
 .rbar .rn{width:150px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:700}
 .rbar .track{flex:1;background:#0b1c30;border-radius:6px;height:20px;overflow:hidden}
 .rbar .fill{height:100%;background:linear-gradient(90deg,#c0392b,#e0483d);border-radius:6px;min-width:3px}
 .rbar .v{width:170px;text-align:left;font-weight:800;color:#ffd166;white-space:nowrap}
 table.gt{width:100%;border-collapse:collapse;font-size:13px}
 table.gt th,table.gt td{padding:8px 10px;text-align:right;border-bottom:1px solid #1c3a5e}
 table.gt th{color:#9fb6d0;font-size:12px;font-weight:700;position:sticky;top:74px;background:#0f2136}
 table.gt tr:hover td{background:#16314f}
 .arw{color:#e0483d;font-weight:800} .b4{color:#7ee0a0;font-weight:800} .af{color:#ff9a9a;font-weight:800}
 .stp{font-size:11px;font-weight:800;border-radius:8px;padding:2px 9px;white-space:nowrap}
 .stp.no{background:#3a1c1c;color:#ff9a9a} .stp.ok{background:#123a2b;color:#7ee0a0} .stp.dim{background:#1c2a3e;color:#9fb6d0}
 .pill{display:inline-block;font-size:11px;font-weight:700;color:#9fb6d0;background:#0b1c30;border-radius:6px;padding:1px 8px}
 .muted{color:#9fb6d0;font-size:13px}
 .note{color:#8fdcb4;font-size:12.5px;margin:-4px 0 10px}
</style></head><body>
<div class="top">
 <img class="logo" src="logo.png" alt="الاتحاد السعودي لكرة القدم" onerror="this.remove()">
 <h1>💳 حالة سداد وتفعيل حسابات الفرق</h1>
</div>
<div class="wrap">
 <div class="note" style="background:#12283f;border:1px solid #1c3a5e;border-radius:10px;padding:10px 14px;margin:0 0 14px;line-height:1.9">ℹ️ خاص بـ<b>الهواة</b> فقط (الأندية والأكاديميات تُعتبر مسدِّدة ومفعِّلة).<br>📌 <b>الجهة</b> = المُسجِّل (نادٍ/أكاديمية/هواة)، وقد تُشارك بعدّة <b>فرق</b> في عدّة فئات. <b>الفريق</b> = مشاركة في فئة واحدة، وهو وحدة المجموعة (المطلوب ٦ فرق لكل مجموعة).</div>
 <div class="flt"><div class="lab">اختر الحالة (تُحاكى فورًا: إلغاء هذه الفرق):</div><div class="tabs" id="metT"></div></div>
 <div class="flt"><div class="lab">المنطقة:</div><select class="rgn" id="rgn"></select></div>
 <div class="flt"><div class="lab">عرض المجموعات:</div><div class="tabs" id="statT"></div></div>
 <div class="simsub" id="simsub"></div>
 <div class="kpis" id="kpis"></div>
 <div id="content"></div>
</div>
<script>
const P=__PAY__;
const T=P.target;
const META={pay:{name:'حالة السداد',teamsL:'جهات لم تُسدِّد',bad:'لم يتم السداد'},
            acct:{name:'تفعيل الحساب',teamsL:'جهات لم تُفعِّل الحساب',bad:'لم يُفعّل الحساب'},
            both:{name:'لم يُسدِّد ولم يُفعِّل',teamsL:'جهات لم تُسدِّد ولم تُفعِّل الحساب',bad:'لم يُسدِّد ولم يُفعّل'}};
let curMet='pay', curRegion='الكل', curStat='all';
const STAT=[['all','كل المجموعات'],['drop','ستُلغى (تخرج من الاكتمال)'],['keep','تبقى مكتملة']];

function arCount(n,one,two,few,many){const m=n%100;
  if(n===1)return one; if(n===2)return two;
  if(m>=3&&m<=10)return n+' '+few; return n+' '+many;}
function nTeam(n){return arCount(n,'فريق واحد','فريقان','فرق','فريقًا');}
function nEntity(n){return arCount(n,'جهة واحدة','جهتان','جهات','جهة');}
function nGroup(n){return arCount(n,'مجموعة واحدة','مجموعتان','مجموعات','مجموعة');}

function metTabs(){
  const el=document.getElementById('metT');
  el.innerHTML=Object.keys(META).map(k=>'<button class="tab'+(k===curMet?' on':'')+'" data-k="'+k+'">'+META[k].name+'</button>').join('');
  el.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{curMet=b.dataset.k;render();});
}
function statTabs(){
  const el=document.getElementById('statT');
  el.innerHTML=STAT.map(([k,t])=>'<button class="tab'+(k===curStat?' on':'')+'" data-s="'+k+'">'+t+'</button>').join('');
  el.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{curStat=b.dataset.s;render();});
}
function regionOptions(){
  const regs=P.regions.slice().sort();
  const sel=document.getElementById('rgn');
  if(curRegion!=='الكل'&&!regs.includes(curRegion))curRegion='الكل';
  sel.innerHTML='<option value="الكل">كل المناطق</option>'+regs.map(r=>'<option'+(r===curRegion?' selected':'')+'>'+r+'</option>').join('');
  sel.onchange=()=>{curRegion=sel.value;render();};
}
// المجموعات ضمن المنطقة المختارة
function groupsInScope(){
  return Object.entries(P.groups).filter(([id,g])=>curRegion==='الكل'||g.region===curRegion);
}
function render(){
  metTabs(); statTabs(); regionOptions();
  const m=P.metrics[curMet], meta=META[curMet];

  // توزيع على المناطق (عدد الجهات) + المشاركات (فرق عبر الفئات)
  const brT=m.byRegionTeams, brE=m.byRegionEntries;
  let regList=Object.keys(brT);
  if(curRegion!=='الكل')regList=regList.filter(r=>r===curRegion);
  regList.sort((a,b)=>(brT[b]||0)-(brT[a]||0));
  const teamsSel=regList.reduce((s,r)=>s+(brT[r]||0),0);
  const entSel=regList.reduce((s,r)=>s+(brE[r]||0),0);
  document.getElementById('simsub').textContent='محاكاة فورية: عند إلغاء '+nEntity(teamsSel)+' ('+nTeam(entSel)+' عبر الفئات)، يُعاد حساب اكتمال كل مجموعة (المطلوب '+T+' فرق) — أيّها ستُلغى وأيّها تبقى.';

  // الأثر على كل مجموعة مكتملة ضمن النطاق
  const scope=groupsInScope();
  const impact=[]; let removedFromComplete=0;
  scope.forEach(([id,g])=>{
    if(g.total<T)return;                       // نتعامل مع المكتملة فقط (المصفّرة أصلًا خارج البطولة)
    const rmv=Math.min(m.removed[id]||0,g.total);
    removedFromComplete+=rmv;
    const after=g.total-rmv;
    impact.push({...g,rmv,after,drop:after<T});
  });
  const compBefore=impact.length;
  const dropN=impact.filter(x=>x.drop).length;
  const compAfter=compBefore-dropN;

  // KPIs (بالترتيب: مجموعات ستُلغى ← جهات ← فرق ستُحذف)
  document.getElementById('kpis').innerHTML=
    '<div class="kpi bad"><div class="n">'+dropN+'</div><div class="l">مجموعات ستُلغى (من '+compBefore+' مكتملة)</div></div>'+
    '<div class="kpi warn"><div class="n">'+teamsSel+'</div><div class="l">'+meta.teamsL+' ('+entSel+' فريقًا عبر الفئات)</div></div>'+
    '<div class="kpi bad"><div class="n">'+removedFromComplete+'</div><div class="l">فرق ستُحذف من مجموعات مكتملة (عبر الفئات)</div></div>';

  // ترشيح حسب الحالة
  let rows=impact.slice();
  if(curStat==='drop')rows=rows.filter(x=>x.drop);
  else if(curStat==='keep')rows=rows.filter(x=>!x.drop);
  // ترتيب: الملغاة أولًا (بحسب النقص)، ثم المتأثرة الباقية (بحسب المحذوف)، ثم غير المتأثرة
  rows.sort((a,b)=>(b.drop-a.drop)||(b.drop?(T-b.after)-(T-a.after):b.rmv-a.rmv)||b.rmv-a.rmv);

  let html='';
  const secTitle=curStat==='drop'?'🧩 المجموعات التي ستُلغى':curStat==='keep'?'🧩 المجموعات التي تبقى مكتملة':'🧩 الأثر على كل المجموعات المكتملة';
  html+='<div class="sec">'+secTitle+' ('+nGroup(rows.length)+')</div>';
  if(rows.length===0){
    html+='<div class="card muted">لا توجد مجموعات ضمن هذا النطاق.</div>';
  }else{
    html+='<div class="card" style="padding:4px 8px"><table class="gt"><thead><tr>'+
      '<th>المجموعة</th><th>الفئة</th><th>المنطقة</th><th>قبل</th><th>يُحذف</th><th>بعد</th><th>الحالة</th>'+
      '</tr></thead><tbody>';
    rows.forEach(g=>{
      const st=g.drop?'<span class="stp no">ستُلغى — ناقص '+(T-g.after)+'</span>'
             :(g.rmv>0?'<span class="stp ok">تبقى مكتملة</span>':'<span class="stp dim">دون تغيير</span>');
      html+='<tr><td><b>'+g.group+'</b></td><td><span class="pill">'+g.age+'</span></td>'+
        '<td>'+g.region.replace(/^منطقة /,'')+'</td>'+
        '<td class="b4">'+g.total+'</td><td class="arw">'+(g.rmv>0?'−'+g.rmv:'0')+'</td>'+
        '<td class="'+(g.drop?'af':'b4')+'">'+g.after+'</td><td>'+st+'</td></tr>';
    });
    html+='</tbody></table></div>';
  }

  // قسم التوزيع على المناطق (جهات، مع عدد الفرق عبر الفئات)
  html+='<div class="sec">📍 توزيع '+meta.teamsL+' على المناطق</div>';
  const maxT=Math.max(1,...regList.map(r=>brT[r]||0));
  html+='<div class="card">';
  if(regList.length===0)html+='<div class="muted">لا توجد جهات مطابقة.</div>';
  regList.forEach(r=>{
    const t=brT[r]||0,e=brE[r]||0;
    html+='<div class="rbar"><div class="rn">'+r.replace(/^منطقة /,'')+'</div>'+
      '<div class="track"><div class="fill" style="width:'+(t/maxT*100)+'%"></div></div>'+
      '<div class="v">'+nEntity(t)+'<span style="color:#8fb3cf;font-weight:400"> · '+e+' فريق</span></div></div>';
  });
  html+='</div>';

  document.getElementById('content').innerHTML=html;
}
render();
</script>
</body></html>"""
HTML = HTML.replace("__PAY__", json.dumps(PAY, ensure_ascii=False))
open(BASE + "pay.html", "w", encoding="utf-8").write(HTML)
print("saved pay.html", len(HTML), "bytes")

comp = sum(1 for g in groups.values() if g["total"] >= TARGET)
comp_e = sum(g["total"] for g in groups.values() if g["total"] >= TARGET)
print("فرق =", total_teams, "| مشاركات =", total_entries,
      "| مجموعات =", len(groups), "| مكتملة =", comp, "| مشاركات مكتملة =", comp_e)
for mt in MET:
    b = PAY["metrics"][mt]
    lost = sum(1 for gid, g in groups.items()
               if g["total"] >= TARGET and g["total"] - b["removed"].get(gid, 0) < TARGET)
    lost_e = sum(min(b["removed"].get(gid, 0), g["total"])
                 for gid, g in groups.items() if g["total"] >= TARGET)
    print(mt, "-> فرق:", b["teams"], "مشاركات متأثرة:", b["entries"],
          "| مجموعات تخرج من الاكتمال:", lost, "| مشاركات محذوفة من المكتملة:", lost_e)
