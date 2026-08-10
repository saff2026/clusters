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
CANON = {"جيزان": "جازان"}
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
C2G, STRUCT = {}, {}
for r in rows[2:]:
    if not r:
        continue
    age = str(r[1]).strip() if r[1] else ""
    city = str(r[2]).strip() if r[2] else ""
    grp = str(r[3]).strip() if r[3] else ""
    if not age or not city or not grp:
        continue
    city = CANON.get(city, city)
    region = REG.get(city, "غير محدد")
    C2G.setdefault(age, {})[city] = grp
    g = STRUCT.setdefault(region, {}).setdefault(age, {}).setdefault(grp, [])
    if city not in g:
        g.append(city)
for rg in STRUCT.values():
    for ag in rg.values():
        for grp in ag:
            ag[grp] = sorted(ag[grp])
M["C2G"], M["STRUCT"] = C2G, STRUCT

# ربط المجموعة -> المكتب/المنطقة من صفحة «المدخلات» (المصدر الرسمي للمكاتب)
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
M["GROFF"], M["GRREG"] = GROFF, GRREG
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
        # المكتب المعتمد = مكتب المجموعة من جدول «المدخلات» (وإلا مكتب التسجيل)
        office = GROFF.get(grp, reg_office)
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

print("تم التحديث من:", XLSX)
print("  تصنيف: مدن=%d مجموعات=%d" % (
    len({c for ag in C2G.values() for c in ag}),
    len({g for ag in C2G.values() for g in ag.values()})))
print("  داشبورد: صفوف=%d مجموع=%d غير مصنّف=%d" % (
    len(rows_out), sum(r["count"] for r in rows_out),
    sum(r["count"] for r in rows_out if r["group"] == "(غير مصنّف)")))
print("  خيار اكسل: 5-9=%d مجموعة | 11-14=%d مجموعة" % (
    len(excel_groups["5-9"]), len(excel_groups["11-14"])))
