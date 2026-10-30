"""Re-render curation_firstpass.md from the (hand-edited) curation_firstpass.csv."""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_curation import OUT, write_review

csv.field_size_limit(sys.maxsize)
with open(OUT / "curation_firstpass.csv", newline="", encoding="utf-8") as f:
    write_review(list(csv.DictReader(f)))
print("wrote", OUT / "curation_firstpass.md")
