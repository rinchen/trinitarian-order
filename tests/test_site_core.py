#!/usr/bin/env python3
"""Site integrity tests: assets, chrome, nav, feasts, trisagion, stage."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "about.html", "feast-days.html", "trisagion.html", "join.html"]
NAV_HREFS = ["index.html", "about.html", "feast-days.html", "trisagion.html", "join.html"]
CSP_REQUIRED = [
    "default-src 'self'",
    "script-src 'self'",
    "script-src-attr 'none'",
    "style-src 'self' https://fonts.googleapis.com",
    "style-src-attr 'none'",
    "font-src https://fonts.gstatic.com",
    "img-src 'self'",
    "object-src 'none'",
    "frame-src 'none'",
    "worker-src 'none'",
    "form-action 'none'",
]


def _local_refs(html: str) -> list[str]:
    refs = []
    for m in re.finditer(r'(?:src|href)="([^"]+)"', html):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "mailto:", "#")):
            continue
        refs.append(ref.split("#", 1)[0].split("?", 1)[0])
    return refs


def _csp_content(html: str) -> str:
    m = re.search(
        r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"',
        html,
    )
    if not m:
        raise AssertionError("missing CSP meta")
    return m.group(1)


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
            self.assertNotIn(
                "/trinitarian-order/",
                html,
                f"{name} still has absolute /trinitarian-order/ paths",
            )
        self.assertEqual(missing, [], "broken local asset refs:\n" + "\n".join(missing))

    def test_relative_url_hygiene(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            for ref in _local_refs(html):
                self.assertFalse(
                    ref.startswith("/"),
                    f"{name}: local ref must be relative, got {ref!r}",
                )
                self.assertNotIn("github.io", ref, f"{name}: {ref}")

    def test_shared_chrome(self):
        required_snippets = [
            'aria-label="Primary"',
            'id="nav-toggle"',
            'id="site-nav"',
            "about.html#sources",
            "site-nav.js",
            "back-to-top.js",
            "apple-touch-icon",
            'href="assets/img/favicon.svg"',
            'href="assets/img/favicon-32x32.png"',
        ]
        csps = []
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            for snip in required_snippets:
                self.assertIn(snip, html, f"{name} missing {snip!r}")
            self.assertNotIn("X-Content-Type-Options", html, name)
            self.assertNotIn("frame-ancestors", html, name)
            self.assertNotIn("style=", html, f"{name} still has inline style=")
            for m in re.finditer(r"<a\b[^>]*target=\"_blank\"[^>]*>", html):
                tag = m.group(0)
                self.assertIn("noopener", tag, f"{name}: {tag}")
                self.assertIn("noreferrer", tag, f"{name}: {tag}")
            csp = _csp_content(html)
            csps.append(csp)
            for token in CSP_REQUIRED:
                self.assertIn(token, csp, f"{name} CSP missing {token!r}")
            self.assertNotIn("data:", csp, f"{name} CSP still allows data: images")
        self.assertEqual(len(set(csps)), 1, "CSP must be identical on all pages")

    def test_favicon_files(self):
        self.assertTrue((ROOT / "assets/img/favicon.svg").is_file())
        self.assertTrue((ROOT / "assets/img/favicon-32x32.png").is_file())

    def test_cross_svg_colors(self):
        for rel in ("assets/img/trinitarian-cross.svg", "assets/img/favicon.svg"):
            svg = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn('fill="#aa0000"', svg, rel)
            self.assertIn('fill="#003380"', svg, rel)
            # Red vertical should follow blue horizontal so it paints on top.
            self.assertLess(svg.find("#003380"), svg.find("#aa0000"), rel)

    def test_aria_current_targets_self(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(html.count('aria-current="page"'), 1, name)
            m = re.search(r'<a href="([^"]+)"[^>]*aria-current="page"', html)
            if not m:
                m = re.search(r'aria-current="page"[^>]*href="([^"]+)"', html)
            self.assertIsNotNone(m, name)
            self.assertEqual(m.group(1), name, name)

    def test_nav_link_set(self):
        for name in PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            nav_m = re.search(
                r'<nav class="site-nav" id="site-nav"[^>]*>(.*?)</nav>',
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(nav_m, name)
            hrefs = re.findall(r'href="([^"]+)"', nav_m.group(1))
            self.assertEqual(hrefs, NAV_HREFS, name)

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
        preview = (ROOT / ".github" / "workflows" / "preview.yml").read_text(encoding="utf-8")
        self.assertIn("rewrite_preview_base.py", preview)
        self.assertIn("--old", preview)
        self.assertIn("pr-preview/pr-", preview)

    def test_stage_site_payload(self):
        site = ROOT / "_site"
        before = site.exists()
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "stage_site.sh")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        try:
            for name in PAGES:
                self.assertTrue((site / name).is_file(), name)
            self.assertTrue((site / "LICENSE").is_file())
            self.assertTrue((site / ".nojekyll").is_file())
            self.assertTrue((site / "assets/css/main.css").is_file())
            self.assertTrue((site / "assets/js/site-nav.js").is_file())
            self.assertTrue((site / "assets/img/favicon.svg").is_file())
            self.assertTrue((site / "assets/img/trinitarian-cross.svg").is_file())
        finally:
            if not before and site.exists():
                shutil.rmtree(site, ignore_errors=True)

    def test_sources_md_parity(self):
        sources = (ROOT / "assets/img/SOURCES.md").read_text(encoding="utf-8")
        img_dir = ROOT / "assets" / "img"
        files = [
            p.name
            for p in img_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg"}
        ]
        for name in files:
            self.assertIn(f"`{name}`", sources, f"SOURCES.md missing {name}")
        for m in re.finditer(r"`([^`]+)`", sources):
            name = m.group(1)
            if not name.endswith((".svg", ".png", ".jpg", ".jpeg")):
                continue
            self.assertTrue((img_dir / name).is_file(), f"SOURCES lists missing {name}")


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

    def test_source_note_and_labels(self):
        html = (ROOT / "trisagion.html").read_text(encoding="utf-8")
        self.assertIn('class="source-note"', html)
        self.assertIn("Modern (USA)", html)
        self.assertIn("Forma Solenne (Curia)", html)
        self.assertIn("governa", html)
        self.assertNotIn("crea e governo", html)


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
