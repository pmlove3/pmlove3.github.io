"""Apply the dead-link policy to curation_firstpass.csv (plan Task 2, step 4). Safe to re-run.

dead + archived copy -> keep, url replaced by the https archive URL, reason "dead link; archived copy"
dead + no archive    -> drop, reason "dead link, no archive"
"""
import csv, re, sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)
CSV_PATH = Path(__file__).resolve().parents[1] / "curation" / "curation_firstpass.csv"

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

swapped = dropped = 0
for r in rows:
    if r["decision"] != "keep" or not r["link_status"].startswith("dead"):
        continue
    match = re.search(r"wayback: (http\S+)", r["link_status"])
    if match:
        r["url"] = match.group(1).replace("http://", "https://", 1)
        r["reason"] = "dead link; archived copy"
        swapped += 1
    else:
        r["decision"], r["reason"] = "drop", "dead link, no archive"
        dropped += 1

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"swapped to archived copy: {swapped} | dropped: {dropped}")
