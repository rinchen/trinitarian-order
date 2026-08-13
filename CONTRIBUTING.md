# Contributing

Thanks for helping with this informational site about the Trinitarian Order
(O.S.S.T.). It is **not** an official publication of the Order.

## Rules of thumb

1. **Every `<img src>` / local `href` under `/trinitarian-order/` must exist on disk.**
   Prefer adding licensed assets under `assets/img/` and documenting them in
   `assets/img/SOURCES.md`.
2. **Keep absolute `/trinitarian-order/…` URLs** — required for GitHub Pages and
   PR preview rewrites. Do not switch to relative asset paths.
3. **No build step / no framework.** Prefer shared CSS classes over inline
   `style=` (CSP forbids inline styles). Lint with `npm run lint` and Ruff
   before opening a PR.
4. **Trisagion:** Italian is authoritative. After editing `trisagion.html`, run:
   ```bash
   python3 scripts/check_trisagion.py
   python3 -m unittest discover -s tests -v
   ```
5. **Feast days:** add rows to the table in `feast-days.html` with
   `data-label="Date|Feast|Rank"` on every cell. Keep About patrons consistent.
6. **Chrome drift:** header/nav/footer are duplicated across the five HTML
   pages. Mirror CSP, nav, footer `#sources` link, and script tags on all pages.
7. **Deploy list:** new root files must be added to `scripts/stage_site.sh` and
   the path filter in `.github/workflows/pages.yml`.

## Preview locally

See README — serve under `/trinitarian-order/` via a symlink + `python3 -m http.server`.

## Pull requests

Same-repo PRs get sticky previews at `/trinitarian-order/pr-preview/pr-N/`.
Fork PRs cannot write to `gh-pages`. Prefer merge over rebase when updating
someone else’s PR branch.
