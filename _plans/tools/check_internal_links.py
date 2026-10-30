"""Verify every relative href/src in docs/**/*.html resolves to a file in docs/."""
import re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

DOCS = Path(__file__).resolve().parents[2] / "docs"
ATTR = re.compile(r'(?:href|src)="([^"#?][^"]*?)(?:[#?][^"]*)?"')
bad = []
for html in DOCS.rglob("*.html"):
    for ref in ATTR.findall(html.read_text(encoding="utf-8", errors="ignore")):
        if urlparse(ref).scheme or ref.startswith(("//", "mailto:", "tel:", "javascript:", "data:")):
            continue
        target = (DOCS / ref.lstrip("/")) if ref.startswith("/") else (html.parent / unquote(ref))
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            bad.append((str(html.relative_to(DOCS)), ref))
for page, ref in sorted(set(bad)):
    print(f"BROKEN {page}: {ref}")
print("broken:", len(set(bad)))
sys.exit(1 if bad else 0)
