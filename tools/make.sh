#!/usr/bin/env bash
# Two passes: the second fills the table of contents with page numbers.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f build/pages.json
python3 tools/build.py && node tools/render.mjs && python3 tools/locate.py
python3 tools/build.py && node tools/render.mjs
cp build/book.pdf "French_Grammar_TCF_Canada_B2.pdf"
python3 tools/locate.py
