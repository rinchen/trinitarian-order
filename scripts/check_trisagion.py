#!/usr/bin/env python3
"""Check Italian/English Trisagion parity and required phrases in trisagion.html."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "trisagion.html"

# Official Italian Part 2 uses "grazia" (likely upstream typo); English uses "thanks".
ALLOWED_ITALIAN_GRAZIA = True

REQUIRED_SHORT_EN = [
    "new breath of Your love",
]
FORBIDDEN_EN = [
    "Make it that",
    "persevering coherence",
]


def parse_prayers(html: str) -> dict:
    """Extract prayer blocks with a simpler regex+slice approach for reliability."""
    forms: dict[str, dict[str, dict]] = {}
    for form_id in ("trisagion-short", "trisagion-long"):
        m = re.search(
            rf'<div class="prayer-copy" id="{form_id}">(.*?)</div>\s*</div>\s*<div class="prayer-actions">',
            html,
            re.DOTALL,
        )
        if not m:
            raise ValueError(f"missing prayer-copy #{form_id}")
        block = m.group(1)
        forms[form_id] = {}
        for lang in ("it", "en"):
            pm = re.search(
                rf'<div class="prayer" lang="{lang}" data-lang="([^"]*)">(.*?)</div>\s*(?=<div class="prayer"|$)',
                block,
                re.DOTALL,
            )
            if not pm:
                raise ValueError(f"missing .{form_id} lang={lang}")
            body = pm.group(2)
            text = re.sub(r"<[^>]+>", " ", body)
            text = re.sub(r"\s+", " ", text).strip()
            forms[form_id][lang] = {
                "label": pm.group(1),
                "text": text,
                "body": body,
                "counts": {
                    "v": len(re.findall(r'class="v"', body)),
                    "r": len(re.findall(r'class="r"', body)),
                    "part": len(re.findall(r'class="part"', body)),
                    "note": len(re.findall(r'class="note"', body)),
                    "lection": len(re.findall(r'class="lection"', body)),
                    "vr": len(re.findall(r'class="vr"', body)),
                    "line": len(re.findall(r'class="line"', body)),
                },
            }
    return forms


def check(html_path: Path) -> list[str]:
    html = html_path.read_text(encoding="utf-8")
    errors: list[str] = []

    if 'lang="it"' not in html:
        errors.append('Italian prayer blocks must set lang="it"')

    try:
        forms = parse_prayers(html)
    except ValueError as e:
        return [str(e)]

    for form_id, langs in forms.items():
        it = langs["it"]["counts"]
        en = langs["en"]["counts"]
        for key in ("v", "r", "part", "note", "lection", "vr"):
            if it[key] != en[key]:
                errors.append(f"{form_id}: count mismatch for .{key}: it={it[key]} en={en[key]}")
        # Structure must not collapse to empty
        if it["v"] < 3 or it["part"] < 2:
            errors.append(f"{form_id}: Italian structure too thin (v={it['v']} part={it['part']})")

    short_en = forms["trisagion-short"]["en"]["text"]
    for phrase in REQUIRED_SHORT_EN:
        if phrase not in short_en:
            errors.append(f"short English missing required phrase: {phrase!r}")

    all_en = forms["trisagion-short"]["en"]["text"] + " " + forms["trisagion-long"]["en"]["text"]
    for bad in FORBIDDEN_EN:
        if bad in all_en:
            errors.append(f"English still contains forbidden calque: {bad!r}")

    long_it = forms["trisagion-long"]["it"]["text"]
    if "a Te grazia" in long_it and not ALLOWED_ITALIAN_GRAZIA:
        errors.append('Italian solemn part 2 has "a Te grazia" (unexpected)')
    if "a Te grazia" not in long_it:
        errors.append(
            'Italian solemn form should retain published "a Te grazia" in part 2 '
            "(allowlisted official quirk)"
        )

    # Solemn form should include restored lections
    if forms["trisagion-long"]["it"]["counts"]["lection"] < 8:
        errors.append(
            "solemn Italian lection count too low: "
            f"{forms['trisagion-long']['it']['counts']['lection']}"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args()
    if not args.html.is_file():
        print(f"ERROR: {args.html} not found", file=sys.stderr)
        return 2
    errs = check(args.html)
    if errs:
        print(f"Trisagion check FAILED ({len(errs)}):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("Trisagion check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
