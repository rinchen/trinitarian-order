#!/usr/bin/env python3
"""Site integrity tests: assets, chrome, nav, feasts, trisagion parity."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "about.html", "feast-days.html", "trisagion.html", "join.html"]


def _local_refs(html: str) -> list[str]:
    refs = []
    for m in re.finditer(r'(?:src|href)="([^"]+)"', html):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "mailto:", "#")):
            continue
        refs.append(ref.split("#", 1)[0].split("?", 1)[0])
    return refs


class TestSiteCore(unittest.TestCase):
    def test_pages_exist(self):
        for name in PAGES:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_local_assets_resolve(self):
        missing = []
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            for ref in _local_refs(html):
                if not ref:
                    continue
                path = (ROOT / ref).resolve()
                try:
                    path.relative_to(ROOT.resolve())
                except ValueError:
                    missing.append(f"{name}: escapes root via {ref}")
                    continue
                if not path.is_file():
                    missing.append(f"{name}: {ref}")
            # Prefer relative URLs so file:// and Pages/previews all work.
            self.assertNotIn(
                "/trinitarian-order/",
                html,
                f"{name} still has absolute /trinitarian-order/ paths",
            )
        self.assertEqual(missing, [], "broken local asset refs:\n" + "\n".join(missing))

    def test_shared_chrome(self):
        required_snippets = [
            'aria-label="Primary"',
            'id="nav-toggle"',
            'id="site-nav"',
            "form-action 'none'",
            "about.html#sources",
            "site-nav.js",
            "back-to-top.js",
            "apple-touch-icon",
        ]
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            for snip in required_snippets:
                self.assertIn(snip, html, f"{name} missing {snip!r}")
            self.assertNotIn("X-Content-Type-Options", html, name)
            self.assertNotIn("frame-ancestors", html, name)
            self.assertNotIn("style=", html, f"{name} still has inline style=")

    def test_aria_current_once(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(html.count('aria-current="page"'), 1, name)

    def test_feast_includes_nov6(self):
        html = (ROOT / "feast-days.html").read_text(encoding="utf-8")
        self.assertIn("November 6", html)
        self.assertIn("Mariano of St. Joseph", html)

    def test_workflows_stage_same_pages(self):
        stage = (ROOT / "scripts" / "stage_site.sh").read_text(encoding="utf-8")
        for name in PAGES:
            self.assertIn(name, stage)
        for wf in ("pages.yml", "preview.yml"):
            text = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            self.assertIn("stage_site.sh", text, wf)


class TestTrisagion(unittest.TestCase):
    def test_check_script_passes(self):
        script = ROOT / "scripts" / "check_trisagion.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_sanctus_variants_present(self):
        html = (ROOT / "trisagion.html").read_text(encoding="utf-8")
        self.assertNotIn("Make it that", html)
        self.assertNotIn("persevering coherence", html)
        self.assertIn("God of hosts", html)
        self.assertIn("Lord God of hosts", html)
        self.assertIn("God of power and might", html)  # 2010 handbook note
        self.assertIn("2010", html)
        self.assertIn("2011", html)
        self.assertIn("USA", html)
        self.assertIn("Modern (USA)", html)
        self.assertIn("Dio dell", html)
        self.assertIn('class="source-note"', html)
        # English Sanctus must not calque Italian "Dio dell'universo"
        self.assertNotRegex(
            html,
            r"Holy,\s*Holy,\s*Holy[^.]{0,80}God of the universe",
        )


class TestPreviewRewrite(unittest.TestCase):
    def test_rewrite_preview_base(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from rewrite_preview_base import rewrite_tree  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<a href="/trinitarian-order/about.html">x</a>', encoding="utf-8"
            )
            (root / "assets").mkdir()
            (root / "assets" / "x.js").write_text(
                'var u="/trinitarian-order/assets/js/x.js";', encoding="utf-8"
            )
            rewritten = rewrite_tree(
                root, "/trinitarian-order/", "/trinitarian-order/pr-preview/pr-9/"
            )
            self.assertEqual(sorted(rewritten), ["assets/x.js", "index.html"])
            self.assertIn(
                "/trinitarian-order/pr-preview/pr-9/about.html",
                (root / "index.html").read_text(encoding="utf-8"),
            )
            # Idempotent / no double rewrite if old prefix gone
            rewritten2 = rewrite_tree(
                root, "/trinitarian-order/", "/trinitarian-order/pr-preview/pr-9/"
            )
            self.assertEqual(rewritten2, [])
            self.assertNotIn(
                "/trinitarian-order/pr-preview/pr-9/pr-preview/",
                (root / "index.html").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
