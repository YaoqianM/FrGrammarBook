#!/usr/bin/env python3
"""Find the page of every heading marker in build/book.pdf -> build/pages.json."""
import json, pathlib, re
from pypdf import PdfReader

root = pathlib.Path(__file__).resolve().parent.parent
reader = PdfReader(root / "build" / "book.pdf")
pages = {}
for i, p in enumerate(reader.pages):
    for m in re.finditer(r"§(s\d+)§", p.extract_text() or ""):
        pages.setdefault(m.group(1), i + 1)
(root / "build" / "pages.json").write_text(json.dumps(pages))
print(f"{len(reader.pages)} pages, {len(pages)} markers located")
