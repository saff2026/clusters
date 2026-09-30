#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني رُوسترات الجداول (schedule_groups_<key>.json) من التوزيع الرسمي للفرق على
المجموعات الفرعية الموجود أسفل جداول «عدد الفرق» في ملفات الجداول
(«توزيع الفرق على مجموعة X — تحت N»). يأخذ المدينة من ملف التسجيل بمطابقة الاسم."""
import re, json, openpyxl

BASE = "/home/user/khitba/cluster_analysis/"
CANON = {"جيزان": "جازان", "الجوف": "سكاكا", "ابها": "أبها"}
TARGET = 5
# (الملف، الفئة الافتراضية إن لم تُذكر في العنوان)
FILES = [("sched_new_u5.xlsx", "تحت 5"), ("sched_new_u7_9.xlsx", None),
         ("sched_new_u11_12.xlsx", None), ("sched_new_u13.xlsx", "تحت 13"),
         ("sched_new_u14.xlsx", "تحت 14")]
AGEKEY = {"تحت 5": "u5", "تحت 7": "u7", "تحت 9": "u9", "تحت 11": "u11",
          "تحت 12": "u12", "تحت 13": "u13", "تحت 14": "u14"}

def norm(s):
    return re.sub(r"\s*\(\d+\)\s*$", "", str(s)).strip()

# منطقة كل مجموعة من التقسيم
S = json.load(open(BASE + "split_data.json", encoding="utf-8"))
REGION = {}
for a in S["ages"]:
    for g in S["byAge"].get(a, []):
        REGION[(a, g["group"])] = g["region"]

# خريطة الاسم->المدينة لكل (فئة، مجموعة) من التسجيل
M = json.load(open(BASE + "_maps.json", encoding="utf-8"))
C2G = M["C2G"]
wb0 = openpyxl.load_workbook(BASE + "pay_latest.xlsx", read_only=True, data_only=True)
ws = wb0["بيانات التسجيل"]
rows = [[("" if c is None else str(c).strip()) for c in r] for r in ws.iter_rows(values_only=True)]
hi = next(i for i, r in enumerate(rows) if "الصفة" in r)
H = {c: j for j, c in enumerate(rows[hi]) if c}
agecols = [k for k in H if "المشاركة" in k]
name2city = {}   # (age, group, normname) -> city
reg_roster = {}  # (age, group) -> [{name, city}]  (احتياطي بترتيب المدينة/الاسم)
from collections import defaultdict
_reg = defaultdict(list)
for r in rows[hi + 1:]:
    if not r or len(r) <= H["اسم الفريق"] or not r[H["اسم الفريق"]]:
        continue
    nm = r[H["اسم الفريق"]]; city = CANON.get(r[H["المدينة"]] or "", r[H["المدينة"]] or "")
    for cn in agecols:
        v = r[H[cn]]
        try:
            v = int(float(v)) if v not in ("", None) else 0
        except (TypeError, ValueError):
            v = 0
        if v <= 0:
            continue
        age = "تحت " + "".join(ch for ch in cn if ch.isdigit())
        grp = (C2G.get(age, {}) or {}).get(city)
        if grp:
            name2city[(age, grp, norm(nm))] = city
            for i in range(v):
                _reg[(age, grp)].append({"name": nm if i == 0 else nm + " (" + str(i + 1) + ")", "city": city})
for k, lst in _reg.items():
    lst.sort(key=lambda t: (t["city"], t["name"]))
    reg_roster[k] = lst

# ---- استخراج التوزيع الرسمي ----
dist = {}   # (age, group) -> {num: name}
for fn, defage in FILES:
    wb = openpyxl.load_workbook(BASE + fn, read_only=True, data_only=True)
    for sn in wb.sheetnames:
        if not re.match(r"^\d+\s*(فريقًا|فريق|فرق)", sn):
            continue
        rws = [[("" if c is None else str(c).strip()) for c in r] for r in wb[sn].iter_rows(values_only=True)]
        cur = None
        i = 0
        while i < len(rws):
            r = rws[i]
            title = next((c for c in r if c.startswith("توزيع الفرق على")), None)
            if title:
                m = re.search(r"على\s+(مجموعة\s+.+?)\s*—", title)
                if m:
                    grp = re.sub(r"\s*\(.*?\)\s*", " ", m.group(1)).strip()   # أزل المدن بين قوسين
                    am = re.search(r"تحت\s*(\d+)", title)
                    age = ("تحت " + am.group(1)) if am else defage
                    cur = (age, grp) if age else None
                else:
                    cur = None
                i += 1; continue
            blocks = [j for j, c in enumerate(r) if c.startswith("المجموعة") and "(الفرق" in c]
            if blocks and cur:
                k = i + 1
                while k < len(rws):
                    rr = rws[k]; got = False
                    for nc in blocks:
                        num = rr[nc - 1] if nc - 1 < len(rr) else ""
                        nm = rr[nc] if nc < len(rr) else ""
                        if num.isdigit() and nm:
                            dist.setdefault(cur, {})[int(num)] = nm; got = True
                    if not got:
                        break
                    k += 1
                i = k; continue
            i += 1

# ---- بناء الرُوسترات: التوزيع الرسمي حيث وُجد، وإلا ترتيب التسجيل ----
by_key = {}   # key -> {age, groups:[...]}
official = 0
allkeys = set(reg_roster) | set(dist)
for (age, grp) in allkeys:
    key = AGEKEY.get(age)
    if not key:
        continue
    if (age, grp) in dist:                       # التوزيع الرسمي
        numname = dist[(age, grp)]
        teams = [{"name": numname[n], "city": name2city.get((age, grp, norm(numname[n])), "")}
                 for n in sorted(numname)]
        official += 1
    else:                                        # احتياطي: ترتيب التسجيل
        teams = list(reg_roster[(age, grp)])
    by_key.setdefault(key, {"age": age, "groups": []})
    by_key[key]["groups"].append({"group": grp, "region": REGION.get((age, grp), ""), "teams": teams})
print("مجموعات بتوزيع رسمي:", official, "| مجموعات احتياطية:", len(allkeys) - official)

for key in ["u5", "u7", "u9", "u11", "u12", "u13", "u14"]:
    d = by_key.get(key, {"age": {v: k for k, v in AGEKEY.items()}[key], "groups": []})
    d["groups"].sort(key=lambda g: -len(g["teams"]))
    json.dump(d, open(BASE + "schedule_groups_%s.json" % key, "w", encoding="utf-8"), ensure_ascii=False)
    tot = sum(len(g["teams"]) for g in d["groups"])
    nocity = sum(1 for g in d["groups"] for t in g["teams"] if not t["city"])
    print(key, d["age"], "| مجموعات:", len(d["groups"]), "| فرق:", tot, "| بدون مدينة:", nocity)
