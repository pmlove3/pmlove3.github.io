"""Build the first-pass curation table for the Raindrop -> resource pages project.

Reads the Raindrop export (kept outside the repo), the existing hub pages, and writes
working/curation_firstpass.csv plus working/curation_firstpass.md for review.
"""
import csv, os, re, sys
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode

csv.field_size_limit(sys.maxsize)

REPO = Path(__file__).resolve().parents[2]
SRC = Path(os.environ["RAINDROP_CSV"])  # the full Raindrop export; keep it outside the repo
OUT = REPO / "_plans" / "curation"      # working files, gitignored
FOLDERS = {"R-Stuff", "Stata", "stats"}

# Sections of the current hubs whose links move into theme pages.
HUB_SECTIONS = {
    "resources/r.qmd": ("## External Resources", None),
    "resources/stata.qmd": ("## Learning Stata Resources", "## File Management"),
}

TRACKING = re.compile(r"^(utm_|fbclid|gclid|mc_|ref$|ref_src)")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
WAYBACK = re.compile(r"^https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.+)$")


def clean_url(url):
    p = urlparse(url.strip())
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k)]
    return p._replace(query=urlencode(q)).geturl()


def key(url):
    """Dedupe key: host without www, path without trailing slash, query; wayback unwrapped."""
    m = WAYBACK.match(url)
    if m:
        url = m.group(1)
    p = urlparse(url)
    return (p.netloc.lower().removeprefix("www.") + p.path.rstrip("/") +
            ("?" + p.query if p.query else "") + ("#" + p.fragment if p.fragment else ""))


DROP_RULES = [  # (regex on lowercase "title url", reason)
    (r"consent\.youtube\.com", "duplicate consent-wall URL"),
    (r"rtweet|graphtweets|twitter", "depends on the retired Twitter API"),
    (r"pushbullet|pushoverr|pocketapi", "personal notification tooling"),
    (r"stackoverflow\.com/questions", "single Q&A thread"),
    (r"securityaffairs\.com", "news item, not a resource"),
    (r"jetbrains\.com", "typeface, off-topic"),
    (r"developer\.ft\.com|ftrtools|news-r/ft", "paywalled API"),
    (r"safaribooksonline\.com", "paywalled/dead host"),
    (r"tryr\.codeschool\.com", "retired course platform"),
    (r"selenium-python\.readthedocs", "Python, off-topic"),
    (r"kb\.iu\.edu/search", "search-results page"),
    (r"prooffreaderplus", "off-topic blog post"),
    (r"rstudio server on google compute|rstudio server amazon machine|rstudio on aws", "outdated hosting guide"),
    (r"python is superior to r", "off-topic opinion"),
    (r"mining sent email", "off-topic"),
]
HOLD_RULES = [  # instructor-oriented candidates, held back pending your call
    (r"gradetools", "grading tool"),
    (r"datadrivencv", "CV tooling"),
    (r"course sequence", "course-design post"),
    (r"free workshop on deep learning", "dated event post"),
    (r"ocrug/presentations", "pedagogical slide decks"),
    (r"campus\.datacamp\.com", "login-gated course"),
    (r"statisticalhorizons\.com", "paid seminar"),
]

THEMES = [  # first match wins on lowercase "title tags url"
    ("r-text-analysis", r"tidytext|quanteda|topic ?model|topicmodels|\blda\b|ldavis|tf-idf|text mining|text analy|textclean|readtext|concordanc|word frequency|textreuse|hunspell|cld3|\bstm\b|strex|stringr|regex|regular expression|rebus|snowball|tm\.plugin|jstor|sentiment|blei|movie scripts|sherlock|shinyconc|filesstrings|widyr|spelling|unrtf|abbyy|youtubecaption|essurvey"),
    ("r-political-economic-data", r"eurostat|ameco|ropengov|convergeu|central bank|statistical data warehouse|essurvey|scraep|srf data|european"),
    ("r-web-scraping-apis", r"selenium|rvest|scrap|\bpolite\b|wayback|\bapi\b|httr|\bcurl\b|new york times|nytimes|json|xml2|web technologies|beautifulsoup|crminer|selectorgadget|keyring|password"),
    ("r-networks-surveys", r"igraph|ggraph|statnet|ergm|tergm|rsiena|network analysis|conjoint|discourse network|sigmajs|survey|mosaic|mplot|probability|machine learning|data mining|caret|catboost|tidymodels|keras|knn|cluster"),
    ("r-shiny-dashboards", r"shiny|flexdashboard|plumber|rhandsontable|htmlwidgets|dashboard"),
    ("git-github-for-r", r"\bgit\b|github quick|happy git|happygitwithr|version control"),
    ("r-markdown-reports", r"markdown|rmarkdown|bookdown|knitr|pandoc|citation|citr|bibliograph|pagedown|thesis|tinytex|ctan|texreg|officer|\bspin\b|reproducible report|literate|rmd|refmanager|knitcitations|grateful|compiling reports"),
    ("r-data-visualization", r"ggplot|\bgg[a-z]+|plotly|highchart|leaflet|palette|colour|color|graph gallery|visualiz|chart|\bmaps?\b|osmdata|heat|lattice|rcharts|infographic|venn|globe4r|tufte|rcolorbrewer|tangram|formattable"),
    ("rstudio-positron-workflow", r"rstudio|positron|vscode|vs code|radian|nvim|emacs|\bess\b|shortcut|lintr|styler|style guide|\bhere\b|reprex|working director|renv|\bpak\b|docker|rocker|cheatsheet|best coding|code structure|command palette|colaboratory|jupyter|ubuntu|\bami\b|compute engine|\baws\b|addin|rsthemes|datapasta|litr-project|remedy|hippie|structuring|posit"),
    ("r-data-wrangling-tables", r"tidyverse|dplyr|purrr|janitor|naniar|visdat|lubridate|\bdates?\b|data\.table|fread|vroom|clean|\btables?\b|\bgt\b|database|tidy data|readr|excel|writexl|modifylist|transpose|functionals|\bfs\b|dirdf|easycsv|anytime|repurrrsive|validate|pipes|rename|variable"),
    ("learning-r", r"introduction|intro\b|tutorial|cookbook|r for|learn|course|r4ds|advanced r|book|programming|ucla|translating stata|fundamentals|knowledger|beginner|first r|r treasures|stephen pettigrew|polsci"),
]


def theme_for(row):
    if row["folder"] in ("Stata", "(hub) stata"):
        return "learning-stata"
    text = " ".join([row["title"], row["tags"], row["url"]]).lower()
    if row["folder"] == "stats" and "r-stuff" not in row["tags"].lower():
        return "statistics-hub"
    for name, pattern in THEMES:
        if re.search(pattern, text):
            return name
    return "unassigned"


def hub_rows():
    rows = []
    for rel, (start, end) in HUB_SECTIONS.items():
        text = (REPO / rel).read_text(encoding="utf-8")
        i = text.index(start)
        j = text.index(end, i) if end else len(text)
        for title, url in LINK.findall(text[i:j]):
            rows.append({"id": "", "title": title.strip(), "url": url, "folder": "(hub) " + Path(rel).stem,
                         "tags": "", "created": "", "excerpt": "", "note": ""})
    return rows


def write_review(rows, dupes=None):
    """Write curation_firstpass.md: one table per theme, for review."""
    by_theme = {}
    for r in rows:
        by_theme.setdefault(r["theme"], []).append(r)
    note = f"; {dupes} duplicates removed" if dupes is not None else ""
    lines = [f"# Curation review ({len(rows)} links{note})\n"]
    for theme in sorted(by_theme):
        group = by_theme[theme]
        kept = sum(1 for r in group if r["decision"] == "keep")
        lines.append(f"\n## {theme} — {kept} keep / {len(group) - kept} drop or hold\n")
        lines.append("| decision | title | domain | source | link | reason |\n|---|---|---|---|---|---|")
        for r in sorted(group, key=lambda r: (r["decision"], r["title"].lower())):
            title = r["title"].replace("|", "/")
            status = (r.get("link_status") or "").split(" | ")[0]
            lines.append(f"| {r['decision']} | {title} | {r['domain']} | {r['source']} | {status} | {r['reason']} |")
    (OUT / "curation_firstpass.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "curation_firstpass.csv").exists() and "--force" not in sys.argv:
        sys.exit("curation_firstpass.csv already exists and may hold your edits; pass --force to rebuild it")
    with open(SRC, newline="", encoding="utf-8-sig") as f:
        raindrop = [r for r in csv.DictReader(f) if r["folder"] in FOLDERS]

    seen, out, dupes = {}, [], 0
    for r in hub_rows() + raindrop:  # hub rows first so they win dedupe
        r["url"] = clean_url(r["url"])
        k = key(r["url"])
        if k in seen:
            dupes += 1
            continue
        seen[k] = True
        hay = (r["title"] + " " + r["url"]).lower()
        decision, reason = "keep", ""
        for pattern, why in DROP_RULES:
            if re.search(pattern, hay):
                decision, reason = "drop", why
                break
        else:
            for pattern, why in HOLD_RULES:
                if re.search(pattern, hay):
                    decision, reason = "hold", why
                    break
        out.append({
            "decision": decision, "reason": reason, "theme": theme_for(r),
            "source": r["folder"], "title": r["title"][:120], "url": r["url"],
            "domain": urlparse(r["url"]).netloc.removeprefix("www."),
            "tags": r["tags"], "excerpt": (r["excerpt"] or "")[:300].replace("\n", " "),
            "note": (r["note"] or "")[:300].replace("\n", " "),
            "link_status": "",  # filled by check_links.py
        })

    fields = list(out[0])
    with open(OUT / "curation_firstpass.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    write_review(out, dupes)

    by_theme = {}
    for r in out:
        by_theme.setdefault(r["theme"], []).append(r)
    print(f"rows={len(out)} dupes_removed={dupes}")
    for theme in sorted(by_theme):
        rows = by_theme[theme]
        print(f"{theme:28} keep={sum(1 for r in rows if r['decision']=='keep'):3} "
              f"drop={sum(1 for r in rows if r['decision']=='drop'):3} hold={sum(1 for r in rows if r['decision']=='hold'):3}")


if __name__ == "__main__":
    main()
