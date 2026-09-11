# -*- coding: utf-8 -*-
"""يوحّد هوية الصفحات على اللون الأخضر الرسمي للاتحاد (#006C35).
يستبدل ألوان الواجهة الزرقاء فقط، ولا يمسّ ألوان الرسوم/المؤشرات (أخضر/أحمر/باليتة المجموعات).
الاستخدام: python3 theme_unify.py <ملف.html>"""
import sys, os

# أزرق (هوية قديمة) -> أخضر (الهوية الموحّدة) — ألوان واجهة فقط
MAP = {
    "#0b1c30": "#04150e",  # خلفية الصفحة
    "#0a3d62": "#006C35",  # الشريط العلوي / نص التبويب المفعّل
    "#0f2540": "#06281c",  # خلفية الشريط الجانبي (الخريطة)
    "#16314f": "#0d4b32",  # خلفية التبويبات
    "#13294a": "#0f3b28",  # خلفية الحقول/البطاقات
    "#12283f": "#0d3f2d",  # خلفية بطاقات الأرقام
    "#1c3a5e": "#12563a",  # حدود
    "#2a4a6e": "#1c7a52",  # حدود
    "#1b6ca8": "#0d5136",  # الأزرار
    "#2980b9": "#12734f",  # الأزرار عند المرور
}

path = sys.argv[1]
html = open(path, encoding="utf-8").read()
n = 0
for blue, green in MAP.items():
    for variant in (blue, blue.upper(), blue.lower()):
        if variant in html:
            n += html.count(variant)
            html = html.replace(variant, green)
open(path, "w", encoding="utf-8").write(html)
print("وحّدت هوية", os.path.basename(path), "-> استبدال", n, "لونًا")
