#!/usr/bin/env bash
# Rasterize assets/img/favicon.svg → favicon-32x32.png (macOS qlmanage + sips).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SVG="$ROOT/assets/img/favicon.svg"
OUT="$ROOT/assets/img/favicon-32x32.png"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [[ ! -f "$SVG" ]]; then
  echo "ERROR: missing $SVG" >&2
  exit 1
fi

if ! command -v qlmanage >/dev/null || ! command -v sips >/dev/null; then
  echo "ERROR: qlmanage and sips required (macOS)" >&2
  exit 1
fi

qlmanage -t -s 32 -o "$TMP" "$SVG" >/dev/null
PNG="$(find "$TMP" -name 'favicon*' -type f | head -n 1)"
if [[ -z "$PNG" ]]; then
  echo "ERROR: qlmanage did not produce a PNG" >&2
  exit 1
fi
sips -z 32 32 "$PNG" --out "$OUT" >/dev/null
echo "Wrote $OUT"
