#!/usr/bin/env bash
# Build script for Cloudflare Pages.
# Assembles the public dist/ directory from repository root.
set -euo pipefail

OUT="dist"

rm -rf "$OUT"
mkdir -p "$OUT"

# Root assets
cp index.html "$OUT/"
cp manifest.json "$OUT/"
cp service-worker.js "$OUT/"

# Static directories
cp -r icons "$OUT/"
cp -r privacy "$OUT/"

# Cloudflare Pages control files (copied in if they exist at repo root)
[ -f _headers ]   && cp _headers   "$OUT/" || true
[ -f _redirects ] && cp _redirects "$OUT/" || true
[ -f robots.txt ] && cp robots.txt "$OUT/" || true

# Generated sitemap
# Site URL (override with SITE_URL env var when deploying to a custom domain)
SITE_URL="${SITE_URL:-https://reaction-heat-calculator.pages.dev}"

cat > "$OUT/robots.txt" <<EOF
User-agent: *
Allow: /
Sitemap: ${SITE_URL}/sitemap.xml
EOF

BUILD_DATE=$(date -u +%Y-%m-%d)
cat > "$OUT/sitemap.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${SITE_URL}/</loc><lastmod>${BUILD_DATE}</lastmod><priority>1.0</priority></url>
  <url><loc>${SITE_URL}/privacy/</loc><lastmod>${BUILD_DATE}</lastmod><priority>0.5</priority></url>
</urlset>
EOF

echo "Built: $(du -sh "$OUT" | cut -f1) in $OUT/"
ls -la "$OUT"
