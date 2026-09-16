#!/usr/bin/env bash
# يبني كل الصفحات وينشرها على فرع main داخل clusters/ ليتحدّث الرابط:
#   https://saff2026.github.io/clusters/clusters/            (الواجهة — أزرار كل الصفحات)
#   https://saff2026.github.io/clusters/clusters/map.html    (الخريطة)
# ملاحظة: صفحة «لوحة الفرق» (dashboard) مجمّدة بطلب المستخدم — لا تُبنى ولا تُنشر من هنا.
set -e
cd /home/user/khitba
python3 cluster_analysis/build_full_map.py >/dev/null
python3 cluster_analysis/build_matches.py >/dev/null
python3 cluster_analysis/build_players.py >/dev/null
python3 cluster_analysis/build_split.py >/dev/null
python3 cluster_analysis/build_schedules.py >/dev/null
python3 cluster_analysis/build_landing.py >/dev/null
# حقن شريط التنقّل الموحّد في الصفحات العادية (الخريطة تحمل الشريط من مولّدها)
python3 cluster_analysis/inject_nav.py cluster_analysis/matches.html mp >/dev/null
python3 cluster_analysis/inject_nav.py cluster_analysis/players.html mp >/dev/null
python3 cluster_analysis/inject_nav.py cluster_analysis/split.html split >/dev/null
python3 cluster_analysis/inject_nav.py cluster_analysis/schedules.html schedules >/dev/null
# توحيد الهوية على الأخضر الرسمي (تحويل صفحات الهوية الزرقاء)
python3 cluster_analysis/theme_unify.py cluster_analysis/split.html >/dev/null
python3 cluster_analysis/theme_unify.py cluster_analysis/governorates_map.html >/dev/null

# النسخ المحلية + docs/ : index = الواجهة، map.html = الخريطة (لوحة الفرق مجمّدة — لا تُنسخ)
cp cluster_analysis/landing.html cluster_analysis/index.html
cp cluster_analysis/landing.html docs/index.html
cp cluster_analysis/governorates_map.html cluster_analysis/map.html
cp cluster_analysis/governorates_map.html docs/map.html
cp cluster_analysis/matches.html docs/matches.html
cp cluster_analysis/players.html docs/players.html
cp cluster_analysis/split.html docs/split.html
cp cluster_analysis/schedules.html docs/schedules.html

# تجهيز نسخ للنشر على main
cp cluster_analysis/landing.html /tmp/_pub_landing.html
cp cluster_analysis/governorates_map.html /tmp/_pub_map.html
cp cluster_analysis/matches.html /tmp/_pub_matches.html
cp cluster_analysis/players.html /tmp/_pub_players.html
cp cluster_analysis/split.html /tmp/_pub_split.html
cp cluster_analysis/schedules.html /tmp/_pub_schedules.html
if [ -f cluster_analysis/logo.png ]; then
  cp cluster_analysis/logo.png docs/logo.png
  cp cluster_analysis/logo.png /tmp/_pub_logo.png
fi
DEV=$(git rev-parse --abbrev-ref HEAD)
git add -A && git commit -q -m "Update site: landing page + unified nav + locked Excel option" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01SbBJEs6uTpJ66VfDZ59Deq" || true
git push -u origin "$DEV" >/dev/null 2>&1 || true
git fetch origin main >/dev/null 2>&1
git checkout main >/dev/null 2>&1
git pull origin main >/dev/null 2>&1 || true
mkdir -p clusters
cp /tmp/_pub_landing.html clusters/index.html
cp /tmp/_pub_map.html clusters/map.html
cp /tmp/_pub_matches.html clusters/matches.html
cp /tmp/_pub_players.html clusters/players.html
cp /tmp/_pub_split.html clusters/split.html
cp /tmp/_pub_schedules.html clusters/schedules.html
[ -f /tmp/_pub_logo.png ] && cp /tmp/_pub_logo.png clusters/logo.png && git add clusters/logo.png
# لوحة الفرق (clusters/dashboard.html + dashboard_view.html) مجمّدة — لا تُنسخ ولا تُضاف
git add clusters/index.html clusters/map.html clusters/matches.html clusters/players.html clusters/split.html clusters/schedules.html
git commit -q -m "Update published site: landing + nav + locked Excel option" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01SbBJEs6uTpJ66VfDZ59Deq" || true
git push origin main >/dev/null 2>&1
git checkout "$DEV" >/dev/null 2>&1
echo "نُشر: https://saff2026.github.io/clusters/clusters/ (الواجهة) و /map.html — لوحة الفرق مجمّدة"
