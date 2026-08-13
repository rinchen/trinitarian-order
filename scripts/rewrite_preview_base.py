#!/usr/bin/env python3
"""Rewrite absolute /trinitarian-order/ paths for PR preview subpaths."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_EXTS = {".html", ".js", ".css", ".svg", ".json", ".xml", ".txt", ".md"}


def rewrite_tree(root: Path, old: str, new: str, exts: set[str] | None = None) -> list[str]:
    """Replace path prefix in text files under root. Returns rewritten paths.

    Skips already-rewritten preview paths so a second pass is idempotent when
    ``old`` is a prefix of ``new`` (e.g. /trinitarian-order/ → …/pr-preview/…).
    """
    import re

    if not old:
        raise ValueError("old path must be non-empty")
    if old == new:
        return []
    allowed = exts or DEFAULT_EXTS
    # Match old only when not already followed by the next segment of new.
    # For old=/trinitarian-order/ and new=/trinitarian-order/pr-preview/pr-N/,
    # skip …/trinitarian-order/pr-preview/…
    escaped = re.escape(old)
    if new.startswith(old):
        rest = new[len(old) :]
        first = rest.split("/", 1)[0]
        if first:
            pattern = re.compile(escaped + r"(?!" + re.escape(first) + r")")
        else:
            pattern = re.compile(escaped)
    else:
        pattern = re.compile(escaped)

    rewritten: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        new_text, n = pattern.subn(new, text)
        if n == 0:
            continue
        path.write_text(new_text, encoding="utf-8")
        rewritten.append(str(path.relative_to(root)))
    return rewritten


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("_site"))
    parser.add_argument("--old", default="/trinitarian-order/")
    parser.add_argument(
        "--new", required=True, help="Replacement prefix, e.g. /trinitarian-order/pr-preview/pr-1/"
    )
    args = parser.parse_args()
    for rel in rewrite_tree(args.root, args.old, args.new):
        print(f"rewrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
