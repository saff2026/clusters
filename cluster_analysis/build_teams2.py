#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يعيد بناء teams2.json من صفحة «بيانات التسجيل» في ملف إكسل،
بنفس منطق زر التحديث في الداشبورد (المنطقة من REG، المجموعة من C2G).
الاستخدام: python3 build_teams2.py <ملف.xlsx>"""
import sys, json, openpyxl
from collections import defaultdict

XLSX = sys.argv[1] if len(sys.argv) > 1 else \
    "/root/.claude/uploads/96ed5203-3895-59d2-9405-1c6ffc5c13cf/c8e3d1d1-___________________________.xlsx"
BASE = "/home/user/khitba/cluster_analysis/"
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
C2G, REG = M["C2G"], M["REG"]

CANON = {"جيزان": "جازان"}
SIFA = {"هواة": "هواة", "اكاديمية": "أكاديمية", "اكاديمة": "أكاديمية",
        "أكاديمية": "أكاديمية", "نادي": "نادي", "نالدي خاص": "نادي"}

wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws = wb["بيانات التسجيل"]
rows = list(ws.iter_rows(values_only=True))
hi = next(i for i, r in enumerate(rows)
         if r and "الصفة" in [str(c).strip() if c else "" for c in r])
H = {}
for j, c in enumerate(rows[hi]):
    if c is not None and str(c).strip():
        H[str(c).strip()] = j
agecols = [k for k in H if "المشاركة" in k]

agg = defaultdict(int)
ages, sifset = [], set()
for r in rows[hi + 1:]:
    if not r or all(c in (None, "") for c in r):
        continue
    raw = str(r[H["الصفة"]] or "").strip()
    sifa = SIFA.get(raw, raw or "غير محدد")
    city = str(r[H["المدينة"]] or "").strip()
    city = CANON.get(city, city) or "غير محدد"
    for cn in agecols:
        v = r[H[cn]]
        if not isinstance(v, (int, float)) or v <= 0:
            continue
        age = "تحت " + "".join(ch for ch in cn if ch.isdigit())
        grp = (C2G.get(age, {}) or {}).get(city, "(غير مصنّف)")
        region = REG.get(city, "غير محدد")
        agg[(age, city, grp, region, sifa)] += int(v)
        if age not in ages:
            ages.append(age)
        sifset.add(sifa)

rows_out = [{"age": a, "city": c, "group": g, "region": rg, "sifa": s, "count": n}
            for (a, c, g, rg, s), n in agg.items()]
ages.sort(key=lambda x: int("".join(ch for ch in x if ch.isdigit())))
sifas = [s for s in ["هواة", "نادي", "أكاديمية"] if s in sifset]

out = {"rows": rows_out, "ages": ages, "sifas": sifas,
       "regions": M["regions"], "target": 6}
json.dump(out, open(BASE + "teams2.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

total = sum(r["count"] for r in rows_out)
print("صفوف:", len(rows_out), "| مجموع الفِرَق:", total)
from collections import Counter
reg = Counter()
for r in rows_out:
    reg[r["region"]] += r["count"]
for k, v in reg.most_common():
    print(f"  {k}\t{v}")
unmapped = sum(r["count"] for r in rows_out if r["group"] == "(غير مصنّف)")
print("غير مصنّف:", unmapped)
