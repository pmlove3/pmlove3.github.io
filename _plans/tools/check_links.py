"""Check external links for `keep` rows in curation_firstpass.csv. Needs outbound network.

Usage: python3 check_links.py [--workers 4] [--include-github]

Statuses written to the link_status column:
  ok / redirect-ok   reachable (2xx, possibly after redirects)
  dead               HTTP 404/410 on a GET retry, or the hostname does not resolve
  blocked            reachable but refuses scripts (401/403/418/429/999, other 4xx): treat as alive
  unreachable        connection errors/timeouts on every attempt: could be the site or the network
                     you run this from; verify by hand before dropping
  unverified-github  github.com rows are skipped unless --include-github (some sandboxes deny it)
Only `dead` rows get a Wayback lookup, so a live page is never swapped for an archive copy.
"""
import csv, sys, time, concurrent.futures as cf
from pathlib import Path
import requests

csv.field_size_limit(sys.maxsize)
CSV_PATH = Path(__file__).resolve().parents[1] / "curation" / "curation_firstpass.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; personal-site-link-check)"}
WAYBACK_API = "https://archive.org/wayback/available"
ATTEMPTS = 3


def classify(code):
    if code < 300:
        return None  # decided by caller (ok vs redirect-ok)
    if code in (404, 410):
        return "dead"
    return "blocked"


def check(url):
    last_error = ""
    for attempt in range(ATTEMPTS):
        try:
            r = requests.head(url, headers=HEADERS, timeout=20, allow_redirects=True)
            if r.status_code >= 400:  # many servers mishandle HEAD; confirm with GET
                r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True, stream=True)
            code = r.status_code
            verdict = classify(code) or ("redirect-ok" if r.history else "ok")
            return verdict, str(code)
        except requests.exceptions.SSLError as exc:
            last_error = "SSLError"
        except requests.exceptions.ConnectionError as exc:
            last_error = "ConnectionError"
            text = str(exc)
            if "Name or service not known" in text or "NameResolutionError" in text or "nodename nor servname" in text:
                return "dead", "DNS"
        except requests.exceptions.Timeout:
            last_error = "Timeout"
        except requests.RequestException as exc:
            last_error = type(exc).__name__
        time.sleep(2 * (attempt + 1))
    return "unreachable", last_error


def wayback(url):
    try:
        snap = requests.get(WAYBACK_API, params={"url": url}, timeout=25).json()["archived_snapshots"]
        return snap.get("closest", {}).get("url", "")
    except (requests.RequestException, ValueError, KeyError):
        return ""


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    include_github = "--include-github" in sys.argv
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    todo = []
    for r in rows:
        r["link_status"] = ""
        if r["decision"] != "keep":
            continue
        if r["domain"] == "github.com" and not include_github:
            r["link_status"] = "unverified-github"
        else:
            todo.append(r)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda r: check(r["url"]), todo))
    for r, (status, detail) in zip(todo, results):
        r["link_status"] = f"{status} {detail}"
        if status == "dead":
            r["link_status"] += " | wayback: " + (wayback(r["url"]) or "none")
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tally = {}
    for r in rows:
        if r["decision"] == "keep":
            key = r["link_status"].split()[0]
            tally[key] = tally.get(key, 0) + 1
    print(tally)


if __name__ == "__main__":
    main()
