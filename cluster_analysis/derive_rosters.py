#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يشتق أرقام الفرق لكل مجموعة (schedule_groups_<key>.json) من صفحة «بيانات التسجيل»
مطابقةً لتقسيم الموقع الحالي. الجهة التي تُشارك بأكثر من فريق في فئة تُكرَّر بلاحقة رقمية.
الاستخدام: python3 derive_rosters.py <ملف_التسجيل.xlsx>"""
import sys, json, openpyxl
from collections import defaultdict

BASE = "/home/user/khitba/cluster_analysis/"
XLSX = sys.argv[1] if len(sys.argv) > 1 else BASE + "pay_latest.xlsx"
CANON = {"جيزان": "جازان", "الجوف": "سكاكا", "ابها": "أبها"}
TARGET = 5   # الحد الأدنى للمجموعة المكتملة

M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
C2G = M["C2G"]
S = json.load(open(BASE + "split_data.json", encoding="utf-8"))
# منطقة كل (فئة، مجموعة) من التقسيم (المصدر المعتمد)
REGION = {}
for a in S["ages"]:
    for g in S["byAge"].get(a, []):
        REGION[(a, g["group"])] = g["region"]

AGEKEY = {"تحت 5": "u5", "تحت 7": "u7", "تحت 9": "u9", "تحت 11": "u11",
          "تحت 12": "u12", "تحت 13": "u13", "تحت 14": "u14"}

wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws = wb["بيانات التسجيل"]
rows = [[("" if c is None else str(c).strip()) for c in r] for r in ws.iter_rows(values_only=True)]
hi = next(i for i, r in enumerate(rows) if "الصفة" in r)
H = {c: j for j, c in enumerate(rows[hi]) if c}
agecols = [k for k in H if "المشاركة" in k]

def age_of(cn):
    return "تحت " + "".join(ch for ch in cn if ch.isdigit())

# groups[age][grp] = list of {name, city}
groups = defaultdict(lambda: defaultdict(list))
for r in rows[hi + 1:]:
    if not r or len(r) <= H["اسم الفريق"]:
        continue
    name = r[H["اسم الفريق"]]
    if not name:
        continue
    city = r[H["المدينة"]] or ""
    city = CANON.get(city, city)
    for cn in agecols:
        v = r[H[cn]]
        try:
            v = int(float(v)) if v not in ("", None) else 0
        except (TypeError, ValueError):
            v = 0
        if v <= 0:
            continue
        age = age_of(cn)
        grp = (C2G.get(age, {}) or {}).get(city)
        if not grp or grp == "(غير مصنّف)":
            continue
        for i in range(v):
            nm = name if i == 0 else name + " (" + str(i + 1) + ")"
            groups[age][grp].append({"name": nm, "city": city})

# كتابة ملف لكل فئة (المجموعات المكتملة: الحجم ≥ الحد الأدنى)
for age, key in AGEKEY.items():
    out = []
    for grp, teams in groups.get(age, {}).items():
        if len(teams) < TARGET:
            continue
        teams.sort(key=lambda t: (t["city"], t["name"]))
        out.append({"group": grp, "region": REGION.get((age, grp), ""), "teams": teams})
    out.sort(key=lambda g: -len(g["teams"]))
    data = {"age": age, "groups": out}
    json.dump(data, open(BASE + "schedule_groups_" + key + ".json", "w", encoding="utf-8"),
              ensure_ascii=False)
    print(key, age, "| مجموعات:", len(out), "| فرق:", sum(len(g["teams"]) for g in out))
