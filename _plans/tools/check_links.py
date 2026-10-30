"""Check external links in curation_firstpass.csv. Needs open outbound network.

Usage: python3 check_links.py            (fills link_status in working/curation_firstpass.csv)
Statuses: ok | redirect-ok | dead | blocked (403/429/999: bot-blocking, verify by hand) | error
"""
import csv, sys, concurrent.futures as cf
from pathlib import Path
import requests

csv.field_size_limit(sys.maxsize)
CSV_PATH = Path(__file__).resolve().parents[1] / "curation" / "curation_firstpass.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; personal-site-link-check)"}
WAYBACK_API = "https://archive.org/wayback/available"


def check(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code in (403, 405, 429, 501) or r.status_code >= 500:
            r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True, stream=True)
        code = r.status_code
    except requests.RequestException as exc:
        return "error", type(exc).__name__, ""
    if code < 300:
        return ("redirect-ok" if r.history else "ok"), str(code), ""
    if code in (401, 403, 429, 999):
        return "blocked", str(code), ""
    return "dead", str(code), ""


def wayback(url):
    try:
        snap = requests.get(WAYBACK_API, params={"url": url}, timeout=20).json()["archived_snapshots"]
        return snap.get("closest", {}).get("url", "")
    except (requests.RequestException, ValueError, KeyError):
        return ""


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    todo = [r for r in rows if r["decision"] == "keep"]
    with cf.ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda r: check(r["url"]), todo))
    for r, (status, code, _) in zip(todo, results):
        r["link_status"] = f"{status} {code}"
        if status in ("dead", "error"):
            r["link_status"] += " | wayback: " + (wayback(r["url"]) or "none")
    fields = list(rows[0])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    tally = {}
    for r in todo:
        tally[r["link_status"].split()[0]] = tally.get(r["link_status"].split()[0], 0) + 1
    print(tally)


if __name__ == "__main__":
    main()
