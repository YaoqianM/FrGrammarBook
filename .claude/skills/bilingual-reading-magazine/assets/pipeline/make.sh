#!/usr/bin/env bash
# Full build: pass 1 lays out the book, locate.py reads page numbers, pass 2 prints them.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f build/pages.json
python3 tools/build.py && node tools/render.mjs && python3 tools/locate.py
python3 tools/build.py && node tools/render.mjs && python3 tools/locate.py
cp build/book.pdf The_Spanish_World.pdf
echo "done: The_Spanish_World.pdf"
