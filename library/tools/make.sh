#!/usr/bin/env bash
# Two passes: the second fills the TOC and the index with page numbers.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f build/pages.json
python3 tools/build.py && node tools/render.mjs && python3 tools/locate.py
python3 tools/build.py && node tools/render.mjs && python3 tools/locate.py
cp build/reader.pdf "法语单词有意思_第一册.pdf"
python3 tools/catalogue.py
