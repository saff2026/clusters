# -*- coding: utf-8 -*-
"""يبني صفحة الواجهة (index) بأزرار لكل صفحات الموقع."""
import os

CARDS = [
    ("map.html",       "🗺️", "الخريطة",           "محافظات المملكة والمجموعات وقياس المسافات بينها"),
    ("dashboard.html", "📊", "لوحة الفرق",         "أعداد الفرق المسجَّلة حسب الفئة والمنطقة والمكتب والصفة"),
    ("split.html",     "🧩", "تقسيم الفرق",        "تقسيم الفرق على المجموعات ومدى اكتمالها"),
    ("matches.html",   "⚽", "المباريات واللاعبون", "عدد المباريات وعدد اللاعبين لكل مجموعة"),
]

cards_html = "".join(
    '<a class="card" href="{h}"><div class="ic">{i}</div>'
    '<div class="ttl">{t}</div><div class="dsc">{d}</div>'
    '<div class="go">افتح ←</div></a>'.format(h=h, i=i, t=t, d=d)
    for h, i, t, d in CARDS
)

logo_tag = ('<img class="logo" src="logo.png" alt="الاتحاد السعودي لكرة القدم" '
            'onerror="this.remove()">')

HTML = """<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>بطولات الواعدين والبراعم — موسم 26/27</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;font-family:'Tajawal',-apple-system,'Segoe UI',sans-serif;
 background:radial-gradient(1200px 600px at 50% -10%,#0f5138 0%,#083425 45%,#04211730 100%),#05261b;
 color:#eafff3;display:flex;flex-direction:column;align-items:center;padding:34px 16px 48px}
.logo{height:96px;width:auto;margin-bottom:14px;filter:brightness(0) invert(1) drop-shadow(0 4px 12px #0006)}
h1{font-size:26px;font-weight:800;margin:0 0 6px;text-align:center;line-height:1.4}
.sub{font-size:15px;color:#bfe9d4;margin:0 0 30px;text-align:center;font-weight:500}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;
 width:100%;max-width:920px}
.card{background:#0d3f2d;border:1px solid #1c6b49;border-radius:18px;padding:22px 20px;
 text-decoration:none;color:#eafff3;display:flex;flex-direction:column;align-items:flex-start;
 transition:transform .15s,box-shadow .15s,background .15s;box-shadow:0 6px 18px #0003}
.card:hover{transform:translateY(-4px);background:#11523a;box-shadow:0 12px 28px #0005}
.ic{font-size:40px;line-height:1;margin-bottom:12px}
.ttl{font-size:20px;font-weight:800;margin-bottom:6px}
.dsc{font-size:13.5px;color:#bfe9d4;line-height:1.6;flex:1}
.go{margin-top:14px;font-size:13px;font-weight:700;color:#ffd166}
.foot{margin-top:34px;font-size:12px;color:#8fc4ac;text-align:center}
@media(max-width:560px){h1{font-size:21px}.logo{height:74px}}
</style></head><body>
""" + logo_tag + """
<h1>بطولات الواعدين والبراعم — موسم 26/27</h1>
<div class="sub">اختر الصفحة التي تريد عرضها</div>
<div class="grid">""" + cards_html + """</div>
<div class="foot">الاتحاد السعودي لكرة القدم</div>
</body></html>"""

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "landing.html")
open(out, "w", encoding="utf-8").write(HTML)
print("تم بناء صفحة الواجهة:", out)
