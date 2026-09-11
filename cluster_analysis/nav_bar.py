# -*- coding: utf-8 -*-
"""شريط تنقّل موحّد لكل صفحات الموقع + مولّد HTML للشريط.
يُستخدم من inject_nav.py (للصفحات العادية) ومن build_full_map.py (داخل الشريط الجانبي)."""

# (المفتاح، النص، الرابط)
NAV_ITEMS = [
    ("home",      "🏠 الرئيسية",          "index.html"),
    ("map",       "🗺️ الخريطة",           "map.html"),
    ("dashboard", "📊 لوحة الفرق",        "dashboard.html"),
    ("split",     "🧩 التقسيم",           "split.html"),
    ("mp",        "⚽ المباريات واللاعبون", "matches.html"),
]

NAV_CSS = (
    ".saffnav{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;align-items:center;"
    "padding:9px 10px;background:#0b3d2e;direction:rtl;"
    "font-family:'Tajawal',-apple-system,'Segoe UI',sans-serif}"
    ".saffnav a{display:inline-flex;align-items:center;gap:5px;background:#0f5138;color:#eafff3;"
    "text-decoration:none;font-weight:700;font-size:13px;padding:7px 14px;border-radius:20px;"
    "border:1px solid #1a6b49;white-space:nowrap;transition:background .15s}"
    ".saffnav a:hover{background:#12734f}"
    ".saffnav a.on{background:#ffd166;color:#06251a;border-color:#ffd166}"
)


def nav_html(active=""):
    links = []
    for key, label, href in NAV_ITEMS:
        cls = "on" if key == active else ""
        links.append('<a class="{c}" href="{h}">{t}</a>'.format(c=cls, h=href, t=label))
    return '<nav class="saffnav">' + "".join(links) + "</nav>"
