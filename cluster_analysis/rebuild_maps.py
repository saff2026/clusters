#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يعيد بناء C2G وSTRUCT في _maps.json من صفحة «عدد الفرق لكل مدينة» في الإكسل،
مع الإبقاء على REG (المدينة→المنطقة) وقائمة المناطق كما هي."""
import sys, json, openpyxl

XLSX = sys.argv[1] if len(sys.argv) > 1 else \
    "/root/.claude/uploads/96ed5203-3895-59d2-9405-1c6ffc5c13cf/c8e3d1d1-___________________________.xlsx"
BASE = "/home/user/khitba/cluster_analysis/"
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
REG = M["REG"]
CANON = {"جيزان": "جازان"}

wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws = wb["عدد الفرق لكل مدينة"]
rows = list(ws.iter_rows(values_only=True))

C2G = {}      # age -> city -> group
STRUCT = {}   # region -> age -> group -> [cities]
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

# ترتيب المدن داخل كل مجموعة
for rg in STRUCT.values():
    for ag in rg.values():
        for grp in ag:
            ag[grp] = sorted(ag[grp])

M["C2G"] = C2G
M["STRUCT"] = STRUCT
json.dump(M, open(BASE + "_maps.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

nages = len(C2G)
ngroups = len({g for ag in C2G.values() for g in ag.values()})
print("فئات:", nages, "| مجموعات فريدة:", ngroups,
      "| مدن مصنّفة:", len({c for ag in C2G.values() for c in ag}))
print("مناطق في STRUCT:", len(STRUCT))
