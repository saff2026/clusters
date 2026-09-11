# -*- coding: utf-8 -*-
"""يحقن شريط التنقّل الموحّد في صفحة HTML عادية (بعد <body>).
الاستخدام: python3 inject_nav.py <ملف.html> <المفتاح>"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_bar import NAV_CSS, nav_html

path, active = sys.argv[1], sys.argv[2]
html = open(path, encoding="utf-8").read()

if "saffnav" not in html:
    # حقن التنسيق قبل </head>
    if "</head>" in html:
        html = html.replace("</head>", "<style>" + NAV_CSS + "</style></head>", 1)
    # حقن الشريط بعد أول وسم <body...>
    m = re.search(r"<body[^>]*>", html)
    if m:
        i = m.end()
        html = html[:i] + "\n" + nav_html(active) + "\n" + html[i:]
    open(path, "w", encoding="utf-8").write(html)
    print("حُقن شريط التنقّل في", os.path.basename(path), "(", active, ")")
else:
    print("الشريط موجود مسبقًا في", os.path.basename(path))
