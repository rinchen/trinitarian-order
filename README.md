# Trinitarian Order (O.S.S.T.) — website

A static informational website about the **Order of the Most Holy Trinity and of
the Captives (O.S.S.T.)**, hosted on GitHub Pages and built by GitHub Actions.

This site is **not** an official publication of the Order.

Sections:
- **Home** (`index.html`) — overview and navigation.
- **About** (`about.html`) — founding (1198, St. John de Matha & St. Felix de
  Valois; approved by Pope Innocent III), the charism of ransoming captives, and
  the Cross of the Two Colors.
- **Feast Days** (`feast-days.html`) — the Order's proper liturgical calendar,
  from *The Trinitarian Way* handbook.
- **Trisagion** (`trisagion.html`) — English short form from *The Trinitarian
  Way*, modern English longer form used in the USA, plus Italian *Forma normale*
  and *Forma Solenne* from the Curia Generalizia.
- **Join** (`join.html`) — religious vocations and the lay Third Order, with a
  call to action.

## Tech

Static HTML + CSS + a little vanilla JS. No build step, no framework. Mirrors
the sibling `persecutio` project's static-site → GitHub Pages (`gh-pages`) +
PR-preview pattern.

Layout:
```
*.html                 → pages (relative links — works with file:// and Pages)
assets/css/main.css    → shared styles
assets/js/             → site-nav, back-to-top, copy-trisagion
assets/img/            → SVGs + licensed rasters (see SOURCES.md)
scripts/               → stage_site.sh, rewrite_preview_base.py, check_trisagion.py
tests/                 → unittest site integrity
.github/workflows/     → test.yml, pages.yml, preview.yml
```

## Local preview

You can open any page directly in the browser (`file://…/index.html`) — CSS, JS,
and images use relative paths.

Optional HTTP server (useful if you want to mirror the GitHub Pages URL shape):

```bash
# From the repo root:
python3 -m http.server 8000
# open http://localhost:8000/
```

### Verify
1. All 5 pages load with no 404s (favicon SVG + PNG, CSS, JS, photos, SVGs).
   Home banner is cropped to a reasonable height (not full-viewport-tall).
2. Nav links work from every page; the active page is marked `aria-current`.
   At ~375px use the **Menu** toggle — no horizontal scroll.
3. Trisagion: Italian/English readable layout; language tabs on narrow screens;
   per-language Copy buttons; Italian blocks use `lang="it"`.
4. Run checks: `python3 scripts/check_trisagion.py` and
   `python3 -m unittest discover -s tests -v`.

### Tests / CI

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

GitHub Actions `test.yml` runs lint + the same checks on every push/PR.

Linters: **Ruff** (Python), **ESLint** (JS), **Stylelint** (CSS), **HTMLHint** (HTML).

Trisagion notes for checkers/reviewers:
- Italian is authoritative; English is a rendering.
- Official solemn Part 2 keeps published *a Te grazia*; English uses “thanks.”
- Official short antifona on trinitari.org once printed *governo*; this site
  correctly uses *governa*.

## Deployment (GitHub Actions)

- `.github/workflows/pages.yml` stages via `scripts/stage_site.sh` and deploys
  to the `gh-pages` branch on push to `main` (JamesIves/github-pages-deploy-action,
  `.nojekyll`).
- `.github/workflows/preview.yml` publishes sticky PR previews under
  `/trinitarian-order/pr-preview/pr-N/` (same-repo PRs only). Preview HTML/JS
  shares the production `github.io` origin — treat previews as untrusted.

**Path-filter footgun:** `pages.yml` only deploys when listed paths change. Adding
something like `robots.txt` or `CNAME` requires updating both the path filter and
`scripts/stage_site.sh`.

### One-time GitHub setup (after the first `gh-pages` deploy)
1. **Settings → Pages → Build and deployment → Source:** Deploy from a branch →
   `gh-pages` / `/` (not "GitHub Actions", not `main`).
2. **Settings → Actions → General → Workflow permissions:** Read and write.

### Headers / CSP

Pages set a restrictive meta CSP (`form-action 'none'`, no inline styles). GitHub
Pages cannot set custom HTTP headers, so `frame-ancestors` / HSTS /
`X-Content-Type-Options` are not enforceable here. Google Fonts remain a
third-party dependency for now.

## Content attribution

Site code is MIT. The Order's texts (history, feast days, Trisagion) remain the
property of the Order of the Most Holy Trinity and of the Captives and are used
with attribution. See `LICENSE`. Image licenses: `assets/img/SOURCES.md`.
