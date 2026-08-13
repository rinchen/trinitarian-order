#!/usr/bin/env python3
"""Validate Trisagion forms and required Sanctus phrases in trisagion.html."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "trisagion.html"

# Official Italian Part 2 uses "grazia" (upstream Curia wording); keep it.
ALLOWED_ITALIAN_GRAZIA = True

FORM_IDS = (
    "trisagion-en-short",
    "trisagion-en-long",
    "trisagion-it-short",
    "trisagion-it-long",
)

REQUIRED_PHRASES = {
    "trisagion-en-short": [
        "God of hosts",
        "Hail, Daughter of God the Father",
    ],
    "trisagion-en-long": [
        "Lord God of hosts",
        "Holy God, Holy Mighty One, Holy Immortal One",
    ],
    "trisagion-it-short": [
        "Dio dell",
        "nuovo soffio del tuo amore",
    ],
    "trisagion-it-long": [
        "Dio dell",
        "a Te grazia",
    ],
}

FORBIDDEN_EN = [
    "Make it that",
    "persevering coherence",
    "God of Hosts.",  # prefer lowercase "hosts" as in Modern Long photo
]


def extract_prayer(html: str, form_id: str) -> dict:
    marker = f'id="{form_id}"'
    start = html.find(marker)
    if start < 0:
        raise ValueError(f"missing prayer-copy #{form_id}")
    actions = html.find('<div class="prayer-actions">', start)
    if actions < 0:
        raise ValueError(f"missing prayer-actions after #{form_id}")
    block = html[start:actions]
    pm = re.search(
        rf'<div class="prayer" lang="(it|en)" data-lang="([^"]*)">(.*)',
        block,
        re.DOTALL,
    )
    if not pm:
        raise ValueError(f"missing .prayer inside #{form_id}")
    # Trim trailing closing divs of .prayer / .prayer-copy
    body = re.sub(r"</div>\s*$", "", pm.group(3)).strip()
    body = re.sub(r"</div>\s*$", "", body).strip()
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\s+", " ", text).strip()
    # Normalize curly apostrophe for phrase checks
    text_norm = text.replace("\u2019", "'").replace("&rsquo;", "'")
    return {
        "lang": pm.group(1),
        "label": pm.group(2),
        "text": text_norm,
        "body": body,
        "counts": {
            "v": len(re.findall(r'class="v"', body)),
            "r": len(re.findall(r'class="r"', body)),
            "part": len(re.findall(r'class="part"', body)),
            "note": len(re.findall(r'class="note"', body)),
            "lection": len(re.findall(r'class="lection"', body)),
            "vr": len(re.findall(r'class="vr"', body)),
        },
    }


def check(html_path: Path) -> list[str]:
    html = html_path.read_text(encoding="utf-8")
    errors: list[str] = []

    if 'lang="it"' not in html:
        errors.append('Italian prayer blocks must set lang="it"')

    forms: dict[str, dict] = {}
    for form_id in FORM_IDS:
        try:
            forms[form_id] = extract_prayer(html, form_id)
        except ValueError as e:
            errors.append(str(e))
            return errors

    expected_lang = {
        "trisagion-en-short": "en",
        "trisagion-en-long": "en",
        "trisagion-it-short": "it",
        "trisagion-it-long": "it",
    }
    for form_id, lang in expected_lang.items():
        if forms[form_id]["lang"] != lang:
            errors.append(f"{form_id}: expected lang={lang}, got {forms[form_id]['lang']}")

    for form_id, phrases in REQUIRED_PHRASES.items():
        text = forms[form_id]["text"]
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{form_id}: missing required phrase: {phrase!r}")

    # English must not calque Italian "Dio dell'universo" as Sanctus.
    for form_id in ("trisagion-en-short", "trisagion-en-long"):
        text = forms[form_id]["text"]
        if re.search(r"Holy,\s*Holy,\s*Holy[^.]{0,80}God of the universe", text, re.I):
            errors.append(f"{form_id}: English Sanctus must not say 'God of the universe'")
        # Printed prayer text should use post-2011 Missal "hosts", not 2010 handbook alone.
        if "God of power and might" in text:
            errors.append(
                f"{form_id}: prayer body should use 'God of hosts'; "
                "keep 'God of power and might' only in the source note"
            )

    # Page must prominently document the 2010 handbook alternative.
    if "God of power and might" not in html:
        errors.append("page must note 2010 handbook wording 'God of power and might'")
    if "2010" not in html or "2011" not in html:
        errors.append("page must note 2010 Trinitarian Way vs 2011 Missal Sanctus change")
    if "Both its short and long" not in html:
        errors.append(
            "page must note that 2010 Trinitarian Way short and long forms "
            "used 'God of power and might'"
        )
    if "not</strong> the long form printed" not in html and "not the long form printed" not in html:
        errors.append(
            "page must state the modern USA longer form is not the "
            "Trinitarian Way handbook long form"
        )
    if "USA" not in html:
        errors.append("page must attribute the modern English longer form to USA use")

    all_en = forms["trisagion-en-short"]["text"] + " " + forms["trisagion-en-long"]["text"]
    for bad in FORBIDDEN_EN:
        if bad in all_en:
            errors.append(f"English still contains forbidden string: {bad!r}")

    long_it = forms["trisagion-it-long"]["text"]
    if "a Te grazia" in long_it and not ALLOWED_ITALIAN_GRAZIA:
        errors.append('Italian solemn part 2 has "a Te grazia" (unexpected)')
    if "a Te grazia" not in long_it:
        errors.append(
            'Italian solemn form should retain published "a Te grazia" in part 2 '
            "(allowlisted official quirk)"
        )

    # Basic structure floors
    if forms["trisagion-en-short"]["counts"]["v"] < 3:
        errors.append("English short form too thin")
    if forms["trisagion-en-long"]["counts"]["v"] < 6:
        errors.append("English longer form too thin")
    if forms["trisagion-it-short"]["counts"]["v"] < 4:
        errors.append("Italian short form too thin")
    if forms["trisagion-it-long"]["counts"]["part"] < 5:
        errors.append("Italian solemn form missing expected parts")
    if forms["trisagion-it-long"]["counts"]["lection"] < 3:
        errors.append(
            "solemn Italian lection count too low: "
            f"{forms['trisagion-it-long']['counts']['lection']}"
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
