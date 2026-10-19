#!/usr/bin/env bash
# Stage public site files into _site/ for GitHub Pages deploy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p _site
cp index.html about.html history.html family.html saints.html feast-days.html trisagion.html join.html contact.html sources.html 404.html LICENSE sitemap.xml robots.txt _site/
cp -R assets _site/
touch _site/.nojekyll
echo "Staged site into _site/"
