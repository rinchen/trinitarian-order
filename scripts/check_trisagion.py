#!/usr/bin/env python3
"""Validate Trisagion forms, Sanctus notes, and key Curia phrases in trisagion.html.

This is a smoke / regression gate — not a full concordance with every source page.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "trisagion.html"

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
        "repeated three times",
    ],
    "trisagion-en-long": [
        "Lord God of hosts",
        "Holy God, Holy Mighty One, Holy Immortal One",
        "repeated nine times",
    ],
    "trisagion-it-short": [
        "Dio dell'universo",
        "nuovo soffio del tuo amore",
        "governa",
    ],
    "trisagion-it-long": [
        "Dio dell'universo",
        "a Te grazia",
        "a Te grazie",
        "governa",
        "Gen 1",
        "Ap 4, 11",
        "Fil 2, 11",
        "Rm 8",
        "Tu nostra speranza",
    ],
}

FORBIDDEN_EN = [
    "Make it that",
    "persevering coherence",
    "God of Hosts.",
]

SOLEMN_MIN_LECTIONS = 18


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
        r'<div class="prayer" lang="(it|en)" data-lang="([^"]*)">(.*)',
        block,
        re.DOTALL,
    )
    if not pm:
        raise ValueError(f"missing .prayer inside #{form_id}")
    body = re.sub(r"</div>\s*$", "", pm.group(3)).strip()
    body = re.sub(r"</div>\s*$", "", body).strip()
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\s+", " ", text).strip()
    text_norm = (
        text.replace("\u2019", "'")
        .replace("&rsquo;", "'")
        .replace("&hellip;", "...")
        .replace("&ldquo;", '"')
        .replace("&rdquo;", '"')
    )
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

    for form_id in ("trisagion-en-short", "trisagion-en-long"):
        text = forms[form_id]["text"]
        if re.search(r"Holy,\s*Holy,\s*Holy[^.]{0,80}God of the universe", text, re.I):
            errors.append(f"{form_id}: English Sanctus must not say 'God of the universe'")
        if "God of power and might" in text:
            errors.append(
                f"{form_id}: prayer body should use 'God of hosts'; "
                "keep 'God of power and might' only in the source note"
            )

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

    # Prefer corrected Italian spelling; reject Curia typo in our published text.
    for form_id in ("trisagion-it-short", "trisagion-it-long"):
        text = forms[form_id]["text"]
        if re.search(r"crea e governo l", text):
            errors.append(f"{form_id}: use 'governa' not Curia typo 'governo'")
        if "spendore" in text:
            errors.append(f"{form_id}: use 'splendore' not Curia typo 'spendore'")

    all_en = forms["trisagion-en-short"]["text"] + " " + forms["trisagion-en-long"]["text"]
    for bad in FORBIDDEN_EN:
        if bad in all_en:
            errors.append(f"English still contains forbidden string: {bad!r}")

    long_it = forms["trisagion-it-long"]["text"]
    if "a Te grazia" not in long_it:
        errors.append(
            'Italian solemn form should retain published "a Te grazia" in part 2 '
            "(allowlisted official quirk)"
        )
    # grazia should appear once (part 2); grazie elsewhere
    if long_it.count("a Te grazia") != 1:
        errors.append(
            f"Italian solemn expected exactly one 'a Te grazia' "
            f"(found {long_it.count('a Te grazia')})"
        )

    if forms["trisagion-en-short"]["counts"]["v"] < 3:
        errors.append("English short form too thin")
    if forms["trisagion-en-long"]["counts"]["v"] < 6:
        errors.append("English longer form too thin")
    if forms["trisagion-it-short"]["counts"]["v"] < 4:
        errors.append("Italian short form too thin")
    if forms["trisagion-it-long"]["counts"]["part"] < 5:
        errors.append("Italian solemn form missing expected parts")
    lections = forms["trisagion-it-long"]["counts"]["lection"]
    if lections < SOLEMN_MIN_LECTIONS:
        errors.append(
            "solemn Italian lection count too low "
            f"(need Curia Scripture apparatus): {lections} < {SOLEMN_MIN_LECTIONS}"
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
