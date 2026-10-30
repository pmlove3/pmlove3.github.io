"""After pages are written: confirm the approved curation was applied to the site source.

keep rows must appear on exactly one resources page (theme pages or hubs);
drop/hold rows must appear on none.
"""
import csv, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build_curation import key, LINK, REPO, OUT

csv.field_size_limit(sys.maxsize)
rows = list(csv.DictReader(open(OUT / "curation_firstpass.csv", newline="", encoding="utf-8")))

where = {}
for page in sorted((REPO / "resources").rglob("*.qmd")):
    for _, url in LINK.findall(page.read_text(encoding="utf-8")):
        where.setdefault(key(url), set()).add(str(page.relative_to(REPO)))

problems = 0
for r in rows:
    pages = where.get(key(r["url"]), set())
    if r["decision"] == "keep" and len(pages) != 1:
        print(f"KEEP appears on {len(pages)} pages: {r['title'][:60]} -> {sorted(pages)}")
        problems += 1
    if r["decision"] in ("drop", "hold") and pages:
        print(f"{r['decision'].upper()} still present: {r['title'][:60]} -> {sorted(pages)}")
        problems += 1
print("problems:", problems)
sys.exit(1 if problems else 0)
