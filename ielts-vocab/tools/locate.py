#!/usr/bin/env python3
"""Find the page of every hidden §marker§ in build/volN.pdf -> build/volN.pages.json."""
import json, pathlib, re, sys
from pypdf import PdfReader

root = pathlib.Path(__file__).resolve().parent.parent
v = sys.argv[1]
reader = PdfReader(root / "build" / f"vol{v}.pdf")
pages = {}
for i, p in enumerate(reader.pages):
    for m in re.finditer(r"§([a-z]\w*)§", (p.extract_text() or "").replace("\n", "")):
        pages.setdefault(m.group(1), i + 1)
(root / "build" / f"vol{v}.pages.json").write_text(json.dumps(pages))
print(f"vol{v}: {len(reader.pages)} pages, {len(pages)} markers located")
