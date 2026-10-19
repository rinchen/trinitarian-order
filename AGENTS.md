# Agent notes - trinitarian-order

Static 10-page site (HTML/CSS/vanilla JS) plus `404.html` -> GitHub Pages.

- Relative links for pages/assets (works with `file://` and Pages/previews).
- Asset rule: every local `src`/`href` must resolve; see `assets/img/SOURCES.md`.
- Trisagion gate: `python3 scripts/check_trisagion.py` (four forms, Sanctus notes,
  Curia Scripture floors - smoke test, not full concordance).
- Lint: `npm run lint` (ESLint/Stylelint/HTMLHint) + `.venv/bin/ruff check scripts tests`.
- Stage: `./scripts/stage_site.sh` (used by `pages.yml` / `preview.yml`).
- Favicon PNG: `./scripts/regen_favicon.sh` after editing `favicon.svg`.
- Tests: `python3 -m unittest discover -s tests -v`.
- No framework; no inline styles; no em dashes in site copy; CSP in each page head
  (keep all pages identical).
- Not an official Order publication; Order texts are attributed, not MIT.
- Mark sources `Official` or `Secondary`; secondary works are not official.
- New root pages/files need `PAGES` in `tests/test_site_core.py`, the stage
  script, the `pages.yml` path filter, and `sitemap.xml`.
