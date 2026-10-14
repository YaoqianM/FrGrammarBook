#!/usr/bin/env python3
"""Find the page of every §key§ marker in build/reader.pdf -> build/pages.json.

Uses poppler's pdftotext: pypdf silently drops some bold CJK/Inter runs."""
import json, pathlib, re, subprocess

lib = pathlib.Path(__file__).resolve().parent.parent
text = subprocess.run(["pdftotext", "-layout", str(lib / "build" / "reader.pdf"), "-"],
                      capture_output=True, text=True, check=True).stdout
pages = {}
for i, page in enumerate(text.split("\f")):
    for m in re.finditer(r"§([a-z0-9]+)§", page):
        pages.setdefault(m.group(1), i + 1)
(lib / "build" / "pages.json").write_text(json.dumps(pages))
print(f"{text.count(chr(12))} pages, {len(pages)} markers located")
