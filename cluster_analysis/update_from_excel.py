#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تحديث شامل من ملف إكسل واحد:
  1) يعيد بناء التصنيف C2G/STRUCT في _maps.json (من صفحة «عدد الفرق لكل مدينة»).
  2) يعيد بناء بيانات الداشبورد teams2.json (من صفحة «بيانات التسجيل»).
  3) يبني excel_groups.json لخيار الخريطة «اكسل» (لكل فئة: 5-9 و 11-14).
الاستخدام: python3 update_from_excel.py <ملف.xlsx>
بعدها: bash publish.sh  لإعادة البناء والنشر.
"""
import sys, json, openpyxl
from collections import defaultdict, Counter

BASE = "/home/user/khitba/cluster_analysis/"
XLSX = sys.argv[1] if len(sys.argv) > 1 else BASE + "latest.xlsx"
CANON = {"جيزان": "جازان", "الجوف": "سكاكا"}
# التجاوزات اليدوية أُلغيت: الاتحاد ضبط التصنيف داخل الإكسل نفسه (مجموعة الخبر/الرس ودمج عنيزة).
GRP_OVERRIDE = {}
GRP_MERGE = {}
SIFA = {"هواة": "هواة", "اكاديمية": "أكاديمية", "اكاديمة": "أكاديمية",
        "أكاديمية": "أكاديمية", "نادي": "نادي", "نالدي خاص": "نادي"}
AGES_59 = ["تحت 5", "تحت 7", "تحت 9"]
AGES_1114 = ["تحت 11", "تحت 12", "تحت 13", "تحت 14"]

M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
REG = M["REG"]
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

# ========== 1) التصنيف من «عدد الفرق لكل مدينة» ==========
ws = wb["عدد الفرق لكل مدينة"]
rows = list(ws.iter_rows(values_only=True))
C2G = {}
recs = []  # (age, city, grp)
recs_cnt = []  # (age, city, grp, count) — لصفحة «تقسيم الفرق على المجموعات»
for r in rows[2:]:
    if not r:
        continue
    age = str(r[1]).strip() if r[1] else ""
    city = str(r[2]).strip() if r[2] else ""
    grp = str(r[3]).strip() if r[3] else ""
    if not age or not city or not grp:
        continue
    city = CANON.get(city, city)
    grp = GRP_OVERRIDE.get((age, city), grp)
    grp = GRP_MERGE.get(grp, grp)
    cnt = int(r[4]) if len(r) > 4 and isinstance(r[4], (int, float)) else 0
    C2G.setdefault(age, {})[city] = grp
    recs.append((age, city, grp))
    recs_cnt.append((age, city, grp, cnt))

# ربط المجموعة -> المكتب/المنطقة من صفحة «المدخلات» (المصدر الرسمي)
GROFF, GRREG = {}, {}
if "المدخلات" in wb.sheetnames:
    wi = list(wb["المدخلات"].iter_rows(values_only=True))
    for r in wi[2:]:
        if not r or len(r) < 9:
            continue
        g = str(r[6]).strip() if r[6] else ""
        reg = str(r[7]).strip() if r[7] else ""
        off = str(r[8]).strip() if r[8] else ""
        if g and off:
            GROFF[g] = off
        if g and reg:
            GRREG[g] = reg

# تطبيع أسماء المناطق المختصرة (من المدخلات) إلى الأسماء المعتمدة في REG
REGNORM = {}
for canon in M["regions"]:
    for short in set(GRREG.values()):
        if short and short in canon:
            REGNORM[short] = canon

# معالجة ذاتية: أي مدينة مصنّفة لكنها غير موجودة في REG تأخذ منطقة مجموعتها
for age, city, grp in recs:
    if city not in REG and grp in GRREG:
        REG[city] = REGNORM.get(GRREG[grp], GRREG[grp])

# بناء STRUCT بعد معالجة المناطق
STRUCT = {}
for age, city, grp in recs:
    region = REG.get(city, "غير محدد")
    g = STRUCT.setdefault(region, {}).setdefault(age, {}).setdefault(grp, [])
    if city not in g:
        g.append(city)
for rg in STRUCT.values():
    for ag in rg.values():
        for grp in ag:
            ag[grp] = sorted(ag[grp])
M["C2G"], M["STRUCT"] = C2G, STRUCT
M["GROFF"], M["GRREG"], M["REG"] = GROFF, GRREG, REG
json.dump(M, open(BASE + "_maps.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ========== 2) بيانات الداشبورد من «بيانات التسجيل» ==========
ws2 = wb["بيانات التسجيل"]
r2 = list(ws2.iter_rows(values_only=True))
hi = next(i for i, r in enumerate(r2)
         if r and "الصفة" in [str(c).strip() if c else "" for c in r])
H = {str(c).strip(): j for j, c in enumerate(r2[hi]) if c is not None and str(c).strip()}
agecols = [k for k in H if "المشاركة" in k]
OFF_COL = "مكتب الوزارة"
agg = defaultdict(int)
ages, sifset, offset = [], set(), set()
for r in r2[hi + 1:]:
    if not r or all(c in (None, "") for c in r):
        continue
    raw = str(r[H["الصفة"]] or "").strip()
    sifa = SIFA.get(raw, raw or "غير محدد")
    city = str(r[H["المدينة"]] or "").strip()
    city = CANON.get(city, city) or "غير محدد"
    reg_office = str(r[H[OFF_COL]] or "").strip() if OFF_COL in H and r[H[OFF_COL]] is not None else ""
    for cn in agecols:
        v = r[H[cn]]
        if not isinstance(v, (int, float)) or v <= 0:
            continue
        age = "تحت " + "".join(ch for ch in cn if ch.isdigit())
        grp = (C2G.get(age, {}) or {}).get(city, "(غير مصنّف)")
        region = REG.get(city, "غير محدد")
        # المكتب المعتمد = مكتب التسجيل (كما أدخله المسجِّل)
        office = reg_office
        agg[(age, city, grp, region, sifa, office)] += int(v)
        if age not in ages:
            ages.append(age)
        sifset.add(sifa)
        if office:
            offset.add(office)
rows_out = [{"age": a, "city": c, "group": g, "region": rg, "sifa": s, "office": o, "count": n}
            for (a, c, g, rg, s, o), n in agg.items()]
ages.sort(key=lambda x: int("".join(ch for ch in x if ch.isdigit())))
teams = {"rows": rows_out, "ages": ages,
         "sifas": [s for s in ["هواة", "نادي", "أكاديمية"] if s in sifset],
         "offices": sorted(offset), "regions": M["regions"], "target": 6}
json.dump(teams, open(BASE + "teams2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ========== 3) خيار الخريطة «اكسل» (تجميع المدن لكل فئة) ==========
def scheme_groups(age_list):
    # مدينة -> مجموعة (ثابتة داخل المخطط)، ثم عكسها إلى مجموعة -> مدن
    c2g = {}
    for a in age_list:
        for c, g in (C2G.get(a) or {}).items():
            c2g[c] = g
    g2c = defaultdict(list)
    for c, g in c2g.items():
        g2c[g].append(c)
    out = []
    for g, cities in g2c.items():
        cities = sorted(cities)
        region = Counter(REG.get(c, "غير محدد") for c in cities).most_common(1)[0][0]
        out.append([region, g, cities])
    out.sort(key=lambda x: x[1])
    return out

excel_groups = {"5-9": scheme_groups(AGES_59), "11-14": scheme_groups(AGES_1114)}
json.dump(excel_groups, open(BASE + "excel_groups.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# ========== 4) عدد المباريات واللاعبين لكل (فئة، مجموعة) — بالاعتماد على رؤوس الأعمدة ==========
def sheet_headers(sheet_name):
    """يعيد (الصفوف، خريطة الرأس اسم→فهرس، فهرس صف الرأس) بالاعتماد على أسماء الأعمدة
    حتى لا تتأثر القراءة عند تغيّر ترتيب الأعمدة في الإكسل."""
    rws = list(wb[sheet_name].iter_rows(values_only=True))
    hidx = None
    for i, rr in enumerate(rws):
        vals = [str(c).strip() if c else "" for c in rr]
        if "المجموعة" in vals and "الفئة" in vals:
            hidx = i
            break
    if hidx is None:
        return rws, {}, 0
    hmap = {}
    for j, c in enumerate(rws[hidx]):
        key = str(c).strip() if c is not None else ""
        if key and key not in hmap:
            hmap[key] = j
    return rws, hmap, hidx

def cell_num(r, idx):
    return int(r[idx]) if idx is not None and idx < len(r) and isinstance(r[idx], (int, float)) else 0

def cell_str(r, idx):
    return str(r[idx]).strip() if idx is not None and idx < len(r) and r[idx] else ""

matches_data = {}
if "عدد المباريات" in wb.sheetnames:
    rws, h, hidx = sheet_headers("عدد المباريات")
    ca, cg, cn = h.get("الفئة"), h.get("المجموعة"), h.get("عدد الفرق")
    cm = next((h[k] for k in h if "مباريات" in k), None)
    for r in rws[hidx + 1:]:
        if not r:
            continue
        age, grp = cell_str(r, ca), cell_str(r, cg)
        if age and grp:
            matches_data[age + "|" + grp] = {"n": cell_num(r, cn), "m": cell_num(r, cm)}
json.dump(matches_data, open(BASE + "matches_data.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# ========== 5) عدد اللاعبين لكل (فئة، مجموعة) — من صفحة «عدد اللاعبين» ==========
players_data = {}
if "عدد اللاعبين" in wb.sheetnames:
    rws, h, hidx = sheet_headers("عدد اللاعبين")
    ca, cg, cn = h.get("الفئة"), h.get("المجموعة"), h.get("عدد الفرق")
    cp = next((h[k] for k in h if "لاعب" in k), None)
    for r in rws[hidx + 1:]:
        if not r:
            continue
        age, grp = cell_str(r, ca), cell_str(r, cg)
        if age and grp:
            players_data[age + "|" + grp] = {"n": cell_num(r, cn), "p": cell_num(r, cp)}
json.dump(players_data, open(BASE + "players_data.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# ========== 6) تقسيم الفرق على المجموعات — من «عدد الفرق لكل مدينة» ==========
# لكل (فئة، مجموعة): منطقتها، ومدنها مع عدد الفرق في كل مدينة، والإجمالي.
def grp_region(grp):
    r = GRREG.get(grp, "")
    return REGNORM.get(r, r) or "غير محدد"

split_map = {}  # (age, grp) -> {region, cities:{city:cnt}}
ages_seen = []
for age, city, grp, cnt in recs_cnt:
    d = split_map.setdefault((age, grp), {"region": grp_region(grp), "cities": {}})
    d["cities"][city] = d["cities"].get(city, 0) + cnt
    if age not in ages_seen:
        ages_seen.append(age)
ages_seen.sort(key=lambda x: int("".join(ch for ch in x if ch.isdigit()) or 0))

# منطقة المجموعة = المنطقة الغالبة لمدنها (المصدر الأدق)؛ ولا نتركها «غير محدد» أبدًا إن أمكن
for (age, grp), d in split_map.items():
    cc = Counter(REG.get(c, "غير محدد") for c in d["cities"])
    cc.pop("غير محدد", None)
    if cc and (d["region"] == "غير محدد" or d["region"] not in cc):
        d["region"] = cc.most_common(1)[0][0]

split_byAge = {}
for (age, grp), d in split_map.items():
    cities = sorted(d["cities"].items(), key=lambda kv: (-kv[1], kv[0]))
    split_byAge.setdefault(age, []).append({
        "group": grp, "region": d["region"],
        "total": sum(d["cities"].values()),
        "cities": [{"city": c, "n": n} for c, n in cities]})
for age in split_byAge:
    split_byAge[age].sort(key=lambda x: -x["total"])
split_data = {"ages": ages_seen, "target": teams.get("target", 6),
              "regions": M["regions"], "byAge": split_byAge}
json.dump(split_data, open(BASE + "split_data.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

print("تم التحديث من:", XLSX)
print("  تصنيف: مدن=%d مجموعات=%d" % (
    len({c for ag in C2G.values() for c in ag}),
    len({g for ag in C2G.values() for g in ag.values()})))
print("  داشبورد: صفوف=%d مجموع=%d غير مصنّف=%d" % (
    len(rows_out), sum(r["count"] for r in rows_out),
    sum(r["count"] for r in rows_out if r["group"] == "(غير مصنّف)")))
print("  خيار اكسل: 5-9=%d مجموعة | 11-14=%d مجموعة" % (
    len(excel_groups["5-9"]), len(excel_groups["11-14"])))
