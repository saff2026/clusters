#!/usr/bin/env bash
# يبني الخريطة والداشبورد وينشرهما على فرع main داخل clusters/ ليتحدّث الرابط:
#   https://saff2026.github.io/clusters/clusters/  (الخريطة)
#   https://saff2026.github.io/clusters/clusters/dashboard.html  (لوحة الفرق)
set -e
cd /home/user/khitba
python3 cluster_analysis/build_full_map.py >/dev/null
python3 cluster_analysis/build_dashboard.py >/dev/null
cp cluster_analysis/governorates_map.html cluster_analysis/index.html
cp cluster_analysis/governorates_map.html docs/index.html
cp cluster_analysis/dashboard.html docs/dashboard.html
cp cluster_analysis/dashboard_view.html docs/dashboard_view.html
cp cluster_analysis/governorates_map.html /tmp/_pub_map.html
cp cluster_analysis/dashboard.html /tmp/_pub_dash.html
cp cluster_analysis/dashboard_view.html /tmp/_pub_dashv.html
if [ -f cluster_analysis/logo.png ]; then
  cp cluster_analysis/logo.png docs/logo.png
  cp cluster_analysis/logo.png /tmp/_pub_logo.png
fi
DEV=$(git rev-parse --abbrev-ref HEAD)
git add -A && git commit -q -m "Update map + dashboard build" || true
git push -u origin "$DEV" >/dev/null 2>&1 || true
git fetch origin main >/dev/null 2>&1
git checkout main >/dev/null 2>&1
git pull origin main >/dev/null 2>&1 || true
mkdir -p clusters
cp /tmp/_pub_map.html clusters/index.html
cp /tmp/_pub_dash.html clusters/dashboard.html
cp /tmp/_pub_dashv.html clusters/dashboard_view.html
[ -f /tmp/_pub_logo.png ] && cp /tmp/_pub_logo.png clusters/logo.png && git add clusters/logo.png
git add clusters/index.html clusters/dashboard.html clusters/dashboard_view.html
git commit -q -m "Update published clusters map + dashboard" || true
git push origin main >/dev/null 2>&1
git checkout "$DEV" >/dev/null 2>&1
echo "نُشر: https://saff2026.github.io/clusters/clusters/ و /dashboard.html"
