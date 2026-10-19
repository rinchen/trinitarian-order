# Trinitarian Order (O.S.S.T.) website

A static informational website about the **Order of the Most Holy Trinity and of
the Captives (O.S.S.T.)**, hosted on GitHub Pages and built by GitHub Actions.

This site is **not** an official publication of the Order.

## Pages

- **Home** (`index.html`): overview, navigation, and current figures.
- **About** (`about.html`): identity, the two ends of the charism, the *tertia
  pars*, the Cross of the Two Colors, the Order and the wider Trinitarian Family,
  and *The Trinitarian Way* English handbook.
- **History** (`history.html`): a dated timeline from the 1193 vision and
  Cerfroid to the present, plus sections on medieval redemptions (including
  Miguel de Cervantes), the 1599 reform, suppression and restoration, the
  United States, and San Tommaso in Formis.
- **Family** (`family.html`): the distinction between the male Order and the
  Trinitarian Family, contemplative nuns, six sister congregations, the Oblates,
  the Hermitesses, and lay Trinitarians.
- **Saints** (`saints.html`): the five canonized saints, selected blesseds,
  patrons and associates, and selected venerables and servants of God.
- **Feast Days** (`feast-days.html`): the Order's proper liturgical calendar,
  with ranks, notes on source discrepancies, a today marker, a print button, and
  a downloadable `.ics` calendar.
- **Trisagion** (`trisagion.html`): what the prayer is, how Trinitarians pray it,
  the English short form, the modern USA longer form, and the Italian *Forma
  normale* and *Forma Solenne*.
- **Join** (`join.html`): priesthood and brotherhood, contemplative nuns, sister
  congregations, the lay Third Order, formation, and questions.
- **Contact** (`contact.html`): Curia, U.S. Province, Third Order, and women's
  vocations, plus how to correct this independent site.
- **Sources** (`sources.html`): editorial policy, official sources, secondary
  works, image credits, and corrections.

`404.html`, `sitemap.xml`, and `robots.txt` are also staged.

## Tech

Static HTML, CSS, and a little vanilla JavaScript. No build step and no
framework. The site mirrors the sibling `persecutio` project's static-site to
GitHub Pages (`gh-pages`) plus PR-preview pattern.

Layout:

```
*.html                  pages (relative links work with file:// and Pages)
404.html                not-found page (noindex)
sitemap.xml             canonical production URLs
robots.txt              crawl policy and sitemap
assets/css/main.css     shared styles, print styles, self-hosted @font-face
assets/js/              site-nav, back-to-top, copy-trisagion,
                        feast-today, print-page
assets/img/             SVGs and licensed rasters (see assets/img/SOURCES.md)
assets/fonts/           self-hosted WOFF2 files and OFL license texts
assets/feast-days.ics   downloadable proper calendar
scripts/                stage_site.sh, rewrite_preview_base.py,
                        check_trisagion.py, regen_favicon.sh
tests/                  unittest site integrity
.github/workflows/      test.yml, pages.yml, preview.yml
```

## Local preview

Open any page directly in the browser (`file:///.../index.html`). CSS, JS,
fonts, and images use relative paths.

Optional HTTP server:

```bash
# From the repo root:
python3 -m http.server 8000
# open http://localhost:8000/
```

### Verify

1. All 10 pages and `404.html` load with no 404s (favicon SVG and PNG, CSS, JS,
   self-hosted fonts, photos, SVGs, ICS).
2. Nav links work from every page; the active page is marked `aria-current`.
   At about 960px and below use the **Menu** toggle. Escape or an outside click
   closes it.
3. Trisagion: four separate forms (EN short, EN modern USA long, IT short, IT
   solemn); readable verse layout; per-form Copy buttons; Italian blocks use
   `lang="it"`; print button works.
4. Feast Days: today's row is highlighted by `feast-today.js`; the ICS file
   downloads.
5. Run checks: `python3 scripts/check_trisagion.py` and
   `python3 -m unittest discover -s tests -v`.

### Tests and CI

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
npm ci
.venv/bin/ruff check scripts tests
.venv/bin/ruff format --check scripts tests
npm run lint
python3 scripts/check_trisagion.py
python3 -m unittest discover -s tests -v
./scripts/stage_site.sh   # writes _site/ (gitignored)
```

GitHub Actions `test.yml` runs lint and the same checks on every push and pull
request.

Linters: **Ruff** (Python), **ESLint** (JS), **Stylelint** (CSS), **HTMLHint**
(HTML).

Trisagion notes for checkers and reviewers:

- English short follows *The Trinitarian Way* structure; English longer is the
  modern USA form (not the 2010 handbook long form). Italian short and solemn
  follow the Curia texts on trinitari.org/devozioni, including the *Forma
  Solenne* Scripture lections.
- English Sanctus uses "God of hosts" (2011 Missal). The 2010 handbook short
  and long forms still print "God of power and might," which remains permitted
  so far as we know. The page documents this in a source note.
- Official solemn Part 2 keeps the published *a Te grazia*; Parts 1 and 3 use
  *grazie*.
- The official short antifona on trinitari.org once printed *governo*; this
  site correctly uses *governa*. Prefer *splendore* over the Curia typo
  *spendore*.
- `check_trisagion.py` is a regression smoke gate (phrases and structure
  floors), not a full concordance with every Curia paragraph.

Favicon PNG: after editing `assets/img/favicon.svg`, run
`./scripts/regen_favicon.sh` (macOS `qlmanage` and `sips`).

## Deployment (GitHub Actions)

- `.github/workflows/pages.yml` stages via `scripts/stage_site.sh` and deploys
  to the `gh-pages` branch on push to `main`
  (JamesIves/github-pages-deploy-action, `.nojekyll`).
- `.github/workflows/preview.yml` publishes sticky PR previews under
  `/trinitarian-order/pr-preview/pr-N/` (same-repo PRs only). Preview HTML and
  JS share the production `github.io` origin; treat previews as untrusted.
  Production canonical and Open Graph URLs are preserved during the preview
  rewrite.

**Path-filter footgun:** `pages.yml` only deploys when listed paths change.
Adding a new root file requires updating both the path filter and
`scripts/stage_site.sh`.

### One-time GitHub setup (after the first `gh-pages` deploy)

1. **Settings > Pages > Build and deployment > Source:** Deploy from a branch >
   `gh-pages` / `/` (not "GitHub Actions", not `main`).
2. **Settings > Actions > General > Workflow permissions:** Read and write.

### Headers and CSP

Pages set a restrictive meta CSP (`form-action 'none'`, `script-src-attr` and
`style-src-attr 'none'`, `frame-src` and `worker-src 'none'`, no inline styles).
GitHub Pages cannot set custom HTTP headers, so `frame-ancestors`, HSTS, and
`X-Content-Type-Options` are not enforceable here.

Fonts are self-hosted under `assets/fonts/`, so the CSP uses `font-src 'self'`
and `style-src 'self'` with no Google Fonts dependency. Open Graph and canonical
URLs use absolute production URLs.

## Content attribution

Site code (templates, scripts, and other authored software) is licensed under
the MIT License. See `LICENSE`.

The textual and devotional content on this site (historical facts, the
liturgical calendar, and the Trinitarian Trisagion) is the property of the Order
of the Most Holy Trinity and of the Captives (O.S.S.T.) and is reproduced here
for informational purposes with attribution. It is not licensed under MIT and
remains under the Order's ownership. This site is informational and is not an
official publication of the Order.

Official sources:

- Order of the Most Holy Trinity, Curia Generalizia: https://www.trinitari.org/
- Trinitarian liturgical calendar: https://www.trinitari.org/calendario-liturgico-feste/
- Trisagion (Devozioni trinitarie): https://www.trinitari.org/devozioni/
- U.S. Province: https://trinitarians.org/
- Third Order: https://www.thirdordertrinitarians.org/

Secondary works and the editorial policy are listed on `sources.html`. Image
licenses are in `assets/img/SOURCES.md`; font licenses are in
`assets/fonts/README.md`.
