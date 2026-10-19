# Contributing

Thanks for helping with this informational site about the Trinitarian Order
(O.S.S.T.). It is **not** an official publication of the Order.

## Rules of thumb

1. **Every local `<img src>` / `href` must exist on disk.** Prefer adding
   licensed assets under `assets/img/` and documenting them in
   `assets/img/SOURCES.md`.
2. **Use relative URLs** for pages and assets (`assets/...`, `about.html`) so
   `file://`, GitHub Pages, and PR previews all resolve correctly. Canonical and
   Open Graph metadata use absolute production URLs.
3. **No build step and no framework.** Prefer shared CSS classes over inline
   `style=` (CSP forbids inline styles). Lint with `npm run lint` and Ruff
   before opening a PR.
4. **Trisagion:** Keep English short (*The Trinitarian Way*), modern English
   longer (USA, not the 2010 handbook long form), and Italian Curia forms
   distinct. English prayer text uses `God of hosts` (2011 Missal); keep the
   prominent note that the 2010 handbook short and long forms still have `God of
   power and might` and that the wording remains permitted. After editing
   `trisagion.html`, run:

   ```bash
   python3 scripts/check_trisagion.py
   python3 -m unittest discover -s tests -v
   ```

5. **Feast days:** add rows to the table in `feast-days.html` with
   `data-label="Date|Feast|Rank"` on every cell. Add `data-month` and `data-day`
   to the row so the today marker can find it, and update
   `assets/feast-days.ics`. Keep About patrons consistent.
6. **Chrome drift:** header, nav, footer, CSP, and metadata are duplicated across
   the ten HTML pages plus `404.html`. Keep the CSP identical; mirror nav,
   footer links, script tags, and canonical metadata.
7. **Sources:** official Order and Holy See sources are normative. Independent
   academic or reference works must be marked **Secondary** and must not be
   presented as official publications. Add new sources to `sources.html`.
8. **Favicon:** after editing `assets/img/favicon.svg`, run
   `./scripts/regen_favicon.sh`.
9. **Deploy list:** new root files must be added to `scripts/stage_site.sh` and
   the path filter in `.github/workflows/pages.yml`.
10. **No em dashes** in site copy, HTML, CSS, or JS. The unit tests enforce
    this. Use commas, colons, parentheses, or a new sentence.

## Preview locally

Open `index.html` in a browser, or run `python3 -m http.server 8000` from the
repo root.

## Pull requests

Same-repo PRs get sticky previews at `/trinitarian-order/pr-preview/pr-N/`.
Fork PRs cannot write to `gh-pages`. Prefer merge over rebase when updating
someone else's PR branch.
