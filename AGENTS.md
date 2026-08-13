# Agent notes — trinitarian-order

Static 5-page site (HTML/CSS/vanilla JS) → GitHub Pages.

- Relative links for pages/assets (works with `file://` and Pages/previews).
- Asset rule: every local `src`/`href` must resolve; see `assets/img/SOURCES.md`.
- Trisagion gate: `python3 scripts/check_trisagion.py` (four forms, Sanctus notes,
  Curia Scripture floors — smoke test, not full concordance).
- Lint: `npm run lint` (ESLint/Stylelint/HTMLHint) + `.venv/bin/ruff check scripts tests`.
- Stage: `./scripts/stage_site.sh` (used by `pages.yml` / `preview.yml`).
- Favicon PNG: `./scripts/regen_favicon.sh` after editing `favicon.svg`.
- Tests: `python3 -m unittest discover -s tests -v`.
- No framework; no inline styles; CSP in each page head (keep all five identical).
- Not an official Order publication; Order texts are attributed, not MIT.
