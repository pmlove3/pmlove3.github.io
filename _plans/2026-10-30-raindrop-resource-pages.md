# Raindrop → Themed Resource Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superjawn:subagent-driven-development (recommended) or superjawn:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the useful links in the Raindrop folders `R-Stuff`, `Stata` and `stats` into annotated, themed Quarto pages that branch from the existing R, Stata and Statistics hubs, so the site gains crawlable, non-thin content without changing how it is built or deployed.

**Architecture:** Each hub (`resources/r.qmd`, `resources/stata.qmd`) keeps its setup content and gains a Quarto listing that auto-renders cards for its child pages (`resources/r/*.qmd`, `resources/stata/*.qmd`). Raindrop stays the archive; a script produces a first-pass curation table (theme / keep / drop / hold per link), the owner approves it, and pages are then written from the approved rows with a one-line annotation per link. A small unit test guards against thin pages.

**Tech Stack:** Quarto 1.10.x (project is `type: website`, output `docs/`), Python 3 stdlib plus `requests` for the link check, `unittest` (existing `tests/` convention), Playwright + axe-core (existing `npm run audit`), GitHub Actions deploy on push to `main` (unchanged).

---

## 0. Decisions needed from you

Please approve, or change, each of these before implementation starts.

| # | Decision | Recommendation |
|---|---|---|
| D1 | **Network access for the link check.** This session's network policy blocks third-party hosts (`CONNECT … 403`), so I can neither check links nor read the pages I annotate. | **A:** raise the environment's *Network access* level for the session ([steps](https://code.claude.com/docs/en/cloud-environments#network-access)). **B:** you run `check_links.py` on your machine and send back the CSV (Task 2). **C:** skip the check and accept some dead links. I recommend A. |
| D2 | **Move, don't duplicate.** Tutorial/book sections currently on `r.qmd` and `stata.qmd` move into the new theme pages. Hub URLs stay the same, so the course pages that link to them keep working. | Move (avoids duplicate-content and keeps hubs focused on setup). |
| D3 | **Page list.** See §2. Stata is **one** page, not two as I first suggested: only about 4 reporting links exist, which would be a thin page. `stats` is mostly noise (2 R items, a letter-frequency blog post, a search-results page) and folds into the Statistics hub. A new R theme appeared in the data: **political & economic data packages** (`eurostat`, `ameco`, ECB, `rOpenGov`, `essurvey`). | Approve the list; any theme with fewer than 8 kept links folds into its hub or a sibling page. |
| D4 | **Where the plan and tooling live.** `_plans/` is committed (plan + scripts). `_plans/curation/` (your per-link decisions) is gitignored. The underscore keeps Quarto from rendering any of it. | As stated. |
| D5 | **Commit cadence.** One commit per task on `claude/website-resources-wiki-omw6e8`. No pull request unless you ask. | As stated. |
| D6 | **Held-back (instructor-only) links.** First-pass flags: `gradetools`, `datadrivencv`, the "Course sequence" post, the "Free workshop on Deep Learning" post. I cannot tell what else is instructor-only from titles. | You mark any others at the Task 3 review. |

## 1. What I measured (so the expected outputs below are real)

| Fact | Value |
|---|---|
| Raindrop export | 21,019 bookmarks, ~100 folders. Only `R-Stuff` (325), `Stata` (24), `stats` (8) are in scope. The CSV stays **outside** the repo (`$RAINDROP_CSV`). |
| First-pass table | **387 rows** = 357 Raindrop rows + the links currently on the hubs' tutorial sections, minus **20 duplicates**. 359 `keep`, 28 `drop`/`hold` before any manual review. |
| Baseline render | `quarto render` exits 0, 44 pages, ~33 s, 59 HTML files in `docs/`. |
| Baseline tests | `python3 -m unittest discover -s tests` → `Ran 18 tests … OK`. |
| Baseline audit | `npm run audit` → `✅ Accessibility audit passed with 0 violations!` (4 files). |
| Baseline internal links | `python3 _plans/tools/check_internal_links.py` → `broken: 0`. |
| Listing prototype | A hub listing with `contents: "r/*.qmd"`, `fields: [title, description]`, `sort: "order"` renders child cards with titles, descriptions and links as **static HTML**, ordered by a custom `order:` front-matter field. Verified in a scratch copy of the site. |
| Quarto availability | Not preinstalled; `pip install quarto-cli` gave 1.10.20. CI uses `quarto-actions/setup@v2` (unpinned), so CI may use a newer version. |
| Existing meta descriptions | **None of the 14 existing `resources/*.html` pages has a `<meta name="description">`**, because their `.qmd` files have no `description:` field (news pages do). Quarto emits the tag as `<meta name="description" content="…">` when the field is set. The four pages this plan edits (`r`, `stata`, `statistics`, `index`) get one; the other ten are a cheap follow-up (out of scope). |
| Deploy | `.github/workflows/publish.yml` runs only on push to `main`. Pushing the feature branch does **not** deploy; live-site checks happen after you merge. |

First-pass theme sizes (keep rows, upper bounds before pruning, including hub-origin links):

| Theme (slug) | Keep | Notes |
|---|---:|---|
| `learning-stata` | 33 | 20 already on the hub; ~13 new |
| `r-text-analysis` | 53 | likely split: tutorials vs packages |
| `r-markdown-reports` | 45 | |
| `rstudio-positron-workflow` | 36 | |
| `r-data-visualization` | 36 | |
| `r-data-wrangling-tables` | 28 | |
| `r-web-scraping-apis` | 27 | |
| `unassigned` | 26 | judgment calls, resolved in Task 3 |
| `r-networks-surveys` | 25 | |
| `learning-r` | 22 | |
| `r-shiny-dashboards` | 10 | |
| `git-github-for-r` | 7 | below 8 → folds into workflow unless it grows |
| `r-political-economic-data` | 7 | below 8 → check after Task 3 |
| `statistics-hub` | 4 | goes on `statistics.qmd` |

## 2. File structure

```
_plans/                                   # Quarto ignores underscore dirs
  2026-10-30-raindrop-resource-pages.md   # this plan (committed)
  tools/                                  # committed
    build_curation.py                     # CSV + hubs → curation_firstpass.csv / .md   (exists, tested)
    render_review.py                      # re-render .md from the edited CSV           (exists, tested)
    check_links.py                        # fill link_status; needs open network        (exists, compiles)
    verify_curation_applied.py            # approved decisions vs. site source          (exists, tested)
    check_internal_links.py               # broken relative links in docs/              (exists, tested)
  curation/                               # gitignored: per-link decisions

resources/
  r.qmd                       MODIFY  keep install/online/publishing/videos/handouts; drop External Resources; add intro + listing
  r/                          CREATE  one .qmd per approved R theme (candidates below)
    learning-r.qmd
    rstudio-positron-workflow.qmd
    r-markdown-reports.qmd
    r-data-visualization.qmd
    r-data-wrangling-tables.qmd
    r-text-analysis.qmd
    r-web-scraping-apis.qmd
    r-networks-surveys.qmd
    r-political-economic-data.qmd
    r-shiny-dashboards.qmd
    git-github-for-r.qmd      (only if ≥ 8 kept links; otherwise a section of the workflow page)
  stata.qmd                   MODIFY  move Learning Stata Resources out; add intro + listing
  stata/learning-stata.qmd    CREATE
  statistics.qmd              MODIFY  add intro and the 3 kept `stats` links
  index.qmd                   MODIFY  add a listing of all guides

tests/test_resource_pages.py  CREATE  guard against thin / unannotated pages
tests/audit.js                MODIFY  audit the new hub and one page per section
.gitignore                    MODIFY  ignore /_plans/curation/
```

## 3. Page conventions (apply to every new page)

**Thin-page rules** (enforced by `tests/test_resource_pages.py`): a `description`; an intro paragraph of at least 25 words before the first heading or list; at least 8 links; every link line carries an annotation of at least 20 characters; no duplicate URLs on a page; no tracking parameters.

**Annotation rules** (the SEO value of these pages is the text around the links):

1. One sentence, at most ~25 words, plain and factual. No "great", "amazing", "must-read".
2. **Never copy Raindrop excerpts verbatim.** They are the source site's own text; use them only as input.
3. **Claim only what the title, excerpt, URL, or well-known facts support.** I cannot read the live pages in this environment (D1). Anything I am unsure of gets a minimal descriptive annotation and goes on a "please verify" list in the batch review message.
4. **Preserve existing hub annotations**, such as "Good Starting Place", "Free Access with Github Student Developer Pack", "NYU Login Required".
5. One level only: no nested sub-bullets under a link (the test checks each link line).
6. Wayback replacements (Task 2) are marked "(archived copy)".

**Template.** Bullet form for tutorials, books and videos; table form for package-heavy sections.

```markdown
---
title: "Learning R"
description: "Free books, courses, and tutorials for learning R, with notes on where to start."
date: "2026-10-30"
order: 1
categories: [r, learning]
---

Two to four sentences: who the page is for, what is collected here, and how to use it
(for example, "start with the first section, then pick a topic guide").

## Start here

- [R for Data Science (2e)](https://r4ds.hadley.nz/) — Free online book that walks through importing, tidying, transforming, visualizing, and communicating data with the tidyverse.

## Packages

| Package | What it does |
|---|---|
| [janitor](https://github.com/sfirke/janitor) | Cleans messy column names and finds duplicate rows in data frames |

## Related on this site

- [R setup and installation](../r.html)
```

- `order:` sets card order on the hub (prototype-verified). `categories:` is unused today but keeps a tag listing possible later.
- Links from pages in `resources/r/` or `resources/stata/` to other site pages use `../name.html`, matching the site's existing `.html` link style.
- `date` is the last-updated date, as on the existing hubs.

**Hub listing block** (front matter, then the body placeholder div):

```yaml
listing:
  id: r-guides
  contents: "r/*.qmd"
  type: default
  fields: [title, description]
  sort: "order"
  max-description-length: 250
```

```markdown
## Guides

::: {#r-guides}
:::
```

**Commit trailers** (append to every commit message):

```
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KbGrmPbEkJ5aQUPvSNGiom
```

## 4. Tasks

### Task 1: Housekeeping — ignore working data, commit plan and tooling

**Files:**
- Modify: `.gitignore`
- Create (already on disk): `_plans/2026-10-30-raindrop-resource-pages.md`, `_plans/tools/*.py`

**Check:** `git status` shows the plan and tools as new, `_plans/curation/` absent from it, and a render does not publish `_plans`.

- [ ] **Step 1: Add the ignore rule**

Append this line to `.gitignore`:

```
/_plans/curation/
```

- [ ] **Step 2: Confirm git sees what it should**

Run: `git status --short`
Expected: `M .gitignore` and `?? _plans/` (and nothing under `_plans/curation/` once you run `git add _plans && git status --short`: it lists only the plan and `tools/` files).

- [ ] **Step 3: Confirm Quarto ignores `_plans`**

Run: `quarto render >/dev/null 2>&1; echo "exit=$?"; test ! -e docs/_plans && echo "not published"`
Expected: `exit=0` then `not published`.

- [ ] **Step 4: Commit**

```bash
git add .gitignore _plans/2026-10-30-raindrop-resource-pages.md _plans/tools
git commit -m "docs: add Raindrop resource-pages plan and curation tooling"
```

(Append the trailers from §3.)

### Task 2: Link check (gate D1)

**Files:**
- Uses: `_plans/tools/build_curation.py`, `_plans/tools/check_links.py`
- Writes: `_plans/curation/curation_firstpass.csv` (`link_status` column)

**Check:** the tally printed by `check_links.py` sums to the number of `keep` rows (359 on the first pass), and every `dead`/`error` row has a Wayback result or `none`.

- [ ] **Step 1: Confirm the network path you chose in D1**

- Option A: run `curl -sS -o /dev/null -w '%{http_code}\n' --max-time 20 https://r4ds.hadley.nz/`. Expected: `200`. (Today it fails with `CONNECT tunnel failed, response 403`.)
- Option B: on your machine, from a checkout of the branch:
  `RAINDROP_CSV=/path/to/your-export.csv python3 _plans/tools/build_curation.py`, then `pip install requests && python3 _plans/tools/check_links.py`, then send me `_plans/curation/curation_firstpass.csv`. I place it at the same path and continue.
- Option C: skip to Task 3; `link_status` stays empty.

- [ ] **Step 2: Build the first-pass table (skip if it already exists)**

Run: `RAINDROP_CSV=<path to your export> python3 -I _plans/tools/build_curation.py`
Expected first line: `rows=387 dupes_removed=20`. If the CSV exists the script refuses and tells you to pass `--force`; do **not** force once Task 3 edits have begun.

- [ ] **Step 3: Run the check (Option A)**

Run: `python3 _plans/tools/check_links.py`
Expected: one line like `{'ok': …, 'redirect-ok': …, 'blocked': …, 'dead': …, 'error': …}` whose values sum to 359. Takes a few minutes (16 threads, 20 s timeout).

- [ ] **Step 4: Apply the dead-link policy in the CSV**

| `link_status` | Action |
|---|---|
| `ok`, `redirect-ok` | keep as is |
| `blocked` (401/403/429/999) | keep; this is bot-blocking (common on Medium, Towards Data Science, Stack Overflow). Spot-check by hand ≤ 10 |
| `dead` / `error` **with** a Wayback URL | keep, replace `url` with the snapshot, annotate "(archived copy)" |
| `dead` / `error` **without** a Wayback URL | set `decision` to `drop`, `reason` to `dead link` |

- [ ] **Step 5: Commit**

Nothing to commit: `_plans/curation/` is gitignored. Mark the task done in the session notes.

### Task 3: Curation review (gate: you approve the table)

**Files:**
- Edit: `_plans/curation/curation_firstpass.csv` (columns `decision`, `reason`, `theme`)
- Regenerate: `_plans/curation/curation_firstpass.md` via `render_review.py`

**Check:** `python3 -I _plans/tools/render_review.py` succeeds and the `.md` shows, per theme, ≥ 8 `keep` rows for every theme that will become a page.

- [ ] **Step 1: Resolve `unassigned` and mis-themed rows**

For each `unassigned` row, set `theme` to one of the §2 slugs, `learning-stata`, `statistics-hub`, or `hub-only` (stays on a hub, not on a theme page). Known cases to settle: `convergEU`, `eurostat`, `ameco`, ECB data warehouse, `rOpenGov` → `r-political-economic-data`; `scholar`, `datapasta` → workflow; `rdrr.io` → `learning-r`; `dagitty` → `hub-only` or `drop`.

- [ ] **Step 2: Apply your hold-back list (D6)**

Set `decision=hold`, `reason=instructor` for the four flagged rows plus anything you name.

- [ ] **Step 3: Prune for quality and size**

Target 8–40 kept links per page. For `r-text-analysis` (53), either prune niche single-purpose repos or split into `r-text-analysis` (tutorials/books) and `r-text-analysis-packages`. Set `decision=drop`, `reason` stated, for the rest.

- [ ] **Step 4: Fold small themes**

Any theme with fewer than 8 `keep` rows has its `theme` reassigned: `git-github-for-r` → `rstudio-positron-workflow`; `r-political-economic-data` → `r-data-wrangling-tables` (unless it reaches 8); `statistics-hub` stays (it is not a theme page).

- [ ] **Step 5: Regenerate the review view and hand it to you**

Run: `python3 -I _plans/tools/render_review.py`
Expected: `wrote …/_plans/curation/curation_firstpass.md`. I send you that path; **implementation of Tasks 5–7 starts only after you approve it.**

### Task 4: Guard test (write first, fails first)

**Files:**
- Create: `tests/test_resource_pages.py`

**Check:** `python3 -m unittest tests.test_resource_pages -v` fails today for the right reason, and passes after Task 5. Cheapest faithful evidence: the thin-page rules *are* the project's main acceptance criterion, and a source-level test runs in milliseconds with no render.

- [ ] **Step 1: Create the test**

```python
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_DIRS = [ROOT / "resources" / "r", ROOT / "resources" / "stata"]

MIN_LINKS = 8
MIN_INTRO_WORDS = 25
MIN_ANNOTATION_CHARS = 20

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
TRACKING = re.compile(r"[?&](utm_[a-z]+|fbclid|gclid)=")
BLOCK_START = ("#", "-", "*", "|", ":", "`")


def theme_pages():
    return sorted(path for directory in THEME_DIRS for path in directory.glob("*.qmd"))


def parse(path):
    match = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise AssertionError(f"{path.name}: missing YAML front matter")
    return match.group(1), match.group(2)


def intro_words(body):
    intro = []
    for line in body.strip().splitlines():
        if line.strip().startswith(BLOCK_START):
            break
        intro.append(line)
    return len(re.findall(r"\w+", " ".join(intro)))


def link_lines(body):
    return [line for line in body.splitlines()
            if line.strip().startswith(("-", "*", "|")) and LINK.search(line)]


def annotation(line):
    rest = LINK.sub("", line).replace("|", " ")
    return " ".join(rest.strip(" -*—–\t").split())


class ResourceThemePageTests(unittest.TestCase):
    def test_theme_pages_exist(self):
        self.assertTrue(theme_pages(), "no theme pages found under resources/r or resources/stata")

    def test_pages_have_description_and_intro(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                front, body = parse(path)
                self.assertRegex(front, r"(?m)^description:\s*\S", "missing description")
                self.assertGreaterEqual(intro_words(body), MIN_INTRO_WORDS, "intro paragraph too short")

    def test_pages_are_not_thin(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                self.assertGreaterEqual(len(LINK.findall(body)), MIN_LINKS, "fewer than 8 links")

    def test_every_link_is_annotated(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                bare = [line.strip()[:80] for line in link_lines(body)
                        if len(annotation(line)) < MIN_ANNOTATION_CHARS]
                self.assertEqual(bare, [], "links without an annotation")

    def test_no_duplicate_or_tracked_urls(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                urls = [url for _, url in LINK.findall(body)]
                self.assertEqual(len(urls), len(set(urls)), "duplicate URL on page")
                self.assertEqual([u for u in urls if TRACKING.search(u)], [], "tracking parameters in URL")


if __name__ == "__main__":
    unittest.main()
```

(This exact file was validated against a passing and a failing fixture: the failing fixture trips all five rules, and an empty directory trips only `test_theme_pages_exist`.)

- [ ] **Step 2: Run it and confirm the right failure**

Run: `python3 -m unittest tests.test_resource_pages 2>&1 | tail -6`
Expected: `FAILED (failures=1)` with `AssertionError: [] is not true : no theme pages found under resources/r or resources/stata`.

- [ ] **Step 3: Do not commit yet**

Committing a red test would break `python3 -m unittest discover -s tests`. It is committed together with the first pages in Task 5.

### Task 5: Stata page, Stata hub, Statistics hub (the pattern task)

**Files:**
- Create: `resources/stata/learning-stata.qmd`
- Modify: `resources/stata.qmd`
- Modify: `resources/statistics.qmd`
- Commit with: `tests/test_resource_pages.py`, `.gitignore` already done

**Check:** `python3 -m unittest discover -s tests` → all pass (18 existing + 5 new), `quarto render` exits 0, and `verify_curation_applied.py` reports no problems for Stata rows.

- [ ] **Step 1: Write `resources/stata/learning-stata.qmd`**

Front matter: `title: "Learning Stata"`, a unique `description` (≤ 160 characters), `date: "2026-10-30"`, `order: 1`, `categories: [stata, learning]`. Content comes from the approved `learning-stata` rows, laid out as:

1. Intro (≥ 25 words): who it is for (students in NYUAD methods courses), how it is organised, how it relates to the hub's software-access notes.
2. `## Start here`: 3 picks, proposed from the current hub's own "Websites" order (Princeton Online Stata Tutorial, UCLA Stata Learning Modules, Stata Corp's learning-resources page) and confirmed by you at the review.
3. `## Tutorials and course notes`
4. `## Writing good do-files`: includes the Paris School of Economics do-file guide, Arizona do-file templates, SSC "Stata for Researchers: Do Files", the Stata Coding Guide.
5. `## Video`
6. `## Books and manuals`: keeps the Bittmann book entry and its "ebook can be accessed from the Library website" note.
7. `## Tables and reports`: estout, dyndoc, the Reporting Reference Manual (about four links; stays a section, not a page).
8. `## Cheatsheets and reference`
9. `## Related on this site`: `../stata.html`, `../statistics.html`, `../r.html` (with the "Translating Stata to R" link going on the R Learning page, not here).

Every link line follows §3.

- [ ] **Step 2: Run the guard test; fix until green**

Run: `python3 -m unittest tests.test_resource_pages -v 2>&1 | tail -12`
Expected: `Ran 5 tests … OK`.

- [ ] **Step 3: Edit the Stata hub**

Run this once from the repo root to cut the moved section:

```python
from pathlib import Path

p = Path("resources/stata.qmd")
s = p.read_text(encoding="utf-8")
start = s.index("## Learning Stata Resources")
end = s.index("## File Management")
s = s[:start] + s[end:]
s = s.replace(
    'title: "STATA"\ndate: "2025-04-17"\n---\n',
    '''title: "STATA"
description: "Stata software access, working habits, and a guide to tutorials, videos, books, and do-file practice for students in NYU Abu Dhabi methods courses."
date: "2026-10-30"
listing:
  id: stata-guides
  contents: "stata/*.qmd"
  type: default
  fields: [title, description]
  sort: "order"
  max-description-length: 250
---

Software access, working habits, and reference notes for using Stata in NYUAD courses. Tutorials, videos, books, and do-file guidance are collected in the guide below.

## Guides

::: {#stata-guides}
:::

''',
    1,
)
p.write_text(s, encoding="utf-8")
```

Expected: `git diff --stat resources/stata.qmd` shows the Learning section removed and the listing added; `NYUAD Software Downloads`, `File Management`, `Datasets`, `Miscellaneous`, `Important Lessons on Stata` and `Math and Programming Operators` are untouched.

- [ ] **Step 4: Edit `resources/statistics.qmd`**

Add an intro paragraph (≥ 25 words) and annotate the existing three links plus the three kept `stats` links (LibreTexts *Introductory Statistics*, MathsIsFun combinations and permutations, UNC *A Primer in Probability*). Bump `date` to `2026-10-30`, and add a `description:` (≤ 160 characters) since the page has none today. Do not move the file.

- [ ] **Step 5: Render and run all checks**

```bash
quarto render 2>&1 | grep -iE "warn|error" ; echo "render exit=${PIPESTATUS[0]}"
python3 -m unittest discover -s tests 2>&1 | tail -3
python3 -I _plans/tools/check_internal_links.py | tail -1
python3 -I _plans/tools/verify_curation_applied.py | grep -iE "stata|statistics" | head
```

Expected: `render exit=0`; `Ran 23 tests … OK`; `broken: 0`; the verifier prints no line for Stata or `stats` rows (R rows are still reported until Task 6).

- [ ] **Step 6: Look at it**

Check `docs/resources/stata.html` contains the "Guides" card with the description text (`grep -c "Learning Stata" docs/resources/stata.html` ≥ 1) and that the hub no longer holds the moved links: `grep -c "princeton.edu/~otorres" docs/resources/stata.html` → `0`, and the same URL appears once in `docs/resources/stata/learning-stata.html`.

- [ ] **Step 7: Review gate: send you the diff and a "please verify" list. Commit after you approve**

```bash
git add tests/test_resource_pages.py resources/stata.qmd resources/stata resources/statistics.qmd
git commit -m "feat(resources): add Learning Stata guide and annotate Statistics hub"
```

### Task 6: R hub and R theme pages (three review batches)

**Files per batch:** the `resources/r/*.qmd` pages listed below; `resources/r.qmd` is edited in Batch A (listing) and again in Batch C (removal of the moved section, once every moved link has a home).

**Check (every batch):** `python3 -m unittest discover -s tests` passes; `quarto render` exits 0; `check_internal_links.py` prints `broken: 0`; `verify_curation_applied.py` shows no problem for rows in this batch's themes.

**Batch A: `learning-r`, `rstudio-positron-workflow` (+ `git-github-for-r` only if it kept ≥ 8)**

- [ ] **Step 1: Write the pages from the approved rows** following §3. `learning-r` Start-here picks: *An Introduction to R* (carry the hub's "Good Starting Place" note), *R for Data Science (2e)*, *R Cookbook*. Include **Translating Stata to R** with a pointer to `../stata.html`. The Datacamp / GitHub Student Developer Pack entries move here and keep their hub annotations.
- [ ] **Step 2: Add the listing to `resources/r.qmd`** (front matter block from §3 with `id: r-guides`, `contents: "r/*.qmd"`; intro paragraph of ≥ 25 words, e.g. "Installation notes, ways to run R online, and publishing setup for R and RStudio or Positron. Topic guides for learning R, workflow, visualization, text analysis, and more are listed below."; `## Guides` div placed before `## Installation`; bump `date` to `2026-10-30`; add a `description:` of ≤ 160 characters, e.g. "Install R, RStudio, or Positron, run R online, and publish documents, plus guides to learning R, text analysis, visualization, and reproducible research."). Leave the `## External Resources` section in place for now.
- [ ] **Step 3: Run the Task 6 checks.** Expected: the verifier will report the moved hub links as "KEEP appears on 2 pages" (hub + new page) until Batch C removes them; that is expected here. Confirm the only such lines are for links you have moved.
- [ ] **Step 4: Review gate.** Send you the rendered page text and the "please verify" list. Commit after approval:

```bash
git add resources/r resources/r.qmd
git commit -m "feat(resources): add Learning R and R workflow guides"
```

**Batch B: `r-markdown-reports`, `r-data-visualization`, `r-data-wrangling-tables`**

- [ ] **Step 1: Write the pages.** `r-markdown-reports` links to `../tinytex.html` and carries the hub's RMarkdown notes (Pandoc Markdown note, *Definitive Guide* → *Cookbook* progression). `r-data-visualization` links to `../gis.html` for maps. Package-heavy sections use the table form.
- [ ] **Step 2: Run the Task 6 checks.**
- [ ] **Step 3: Review gate, then commit:**

```bash
git add resources/r
git commit -m "feat(resources): add R Markdown, visualization, and data wrangling guides"
```

**Batch C: `r-text-analysis` (and the packages split if chosen), `r-web-scraping-apis`, `r-networks-surveys`, `r-political-economic-data` (if ≥ 8) , `r-shiny-dashboards`**

- [ ] **Step 1: Write the pages.** The hub's *Regular Expressions* links go to `r-text-analysis`. `r-political-economic-data` links to `../data.html`.
- [ ] **Step 2: Remove the moved section from `resources/r.qmd`**, only after the verifier is clean:

```python
from pathlib import Path

p = Path("resources/r.qmd")
s = p.read_text(encoding="utf-8")
s = s[: s.index("## External Resources")].rstrip() + "\n"
p.write_text(s, encoding="utf-8")
```

Expected: `git diff --stat resources/r.qmd` shows only deletions of the External Resources block; `Installation`, `Using R Online`, `Publishing`, `Videos` and `Handouts` are unchanged.
- [ ] **Step 3: Run the Task 6 checks, plus the full curation verification:**

Run: `python3 -I _plans/tools/verify_curation_applied.py`
Expected: `problems: 0`. Every `keep` row appears on exactly one page; every `drop`/`hold` row on none.
- [ ] **Step 4: Review gate, then commit:**

```bash
git add resources/r resources/r.qmd
git commit -m "feat(resources): add R text analysis, scraping, networks, and Shiny guides; move hub links"
```

### Task 7: Resources index lists every guide

**Files:**
- Modify: `resources/index.qmd`

**Check:** `docs/resources/index.html` contains a card linking to every page under `resources/r/` and `resources/stata/`.

- [ ] **Step 1: Replace the front matter and add the listing above the existing headings**

New head of the file (everything below `## Guides` is the existing content, unchanged):

```markdown
---
title: "Resources"
description: "Guides and links for students and researchers: R, Stata, statistics, data and GIS, writing tools, and research software."
date: "2026-10-30"
listing:
  id: guides
  contents:
    - "r/*.qmd"
    - "stata/*.qmd"
  type: default
  fields: [title, description]
  sort: "title"
  max-description-length: 200
---

## Guides

::: {#guides}
:::

## Statistics
```

Note: the prototype verified a single glob; the two-glob list is the one thing here not yet verified. If Quarto rejects it, use two listings (`id: r-guides-index`, `id: stata-guides-index`) instead.

- [ ] **Step 2: Render and count cards**

Run: `quarto render >/dev/null 2>&1; for f in $(cd docs/resources && ls r/*.html stata/*.html); do grep -q "resources/$f" docs/resources/index.html || echo "MISSING $f"; done; echo done`
Expected: only `done`.

- [ ] **Step 3: Commit**

```bash
git add resources/index.qmd
git commit -m "feat(resources): list all guides on the Resources index"
```

### Task 8: Accessibility audit coverage

**Files:**
- Modify: `tests/audit.js` (the `files` array, near the top of `runAudit`)

**Check:** `npm run audit` still reports `0 violations` with the new pages included. Baseline is 0 on the existing four files, so any new violation comes from this work.

- [ ] **Step 1: Extend the array**

Replace

```js
const files = ['index.html', 'cv.html', 'colophon.html', '404.html'];
```

with

```js
const files = [
    'index.html', 'cv.html', 'colophon.html', '404.html',
    'resources/index.html', 'resources/r.html', 'resources/stata.html',
    'resources/r/learning-r.html', 'resources/stata/learning-stata.html',
];
```

- [ ] **Step 2: Run it**

Run: `quarto render >/dev/null 2>&1 && npm run audit 2>&1 | tail -8`
Expected: `✅ Accessibility audit passed with 0 violations!`. If axe flags the listing cards or the package tables (for example a table without a header row, or low-contrast card text), fix the page or `styles.css` and rerun.

- [ ] **Step 3: Commit**

```bash
git add tests/audit.js
git commit -m "test: include resource hubs and guides in accessibility audit"
```

### Task 9: Final verification and push

**Files:** none changed unless a check fails.

**Check:** everything below passes in one pass from a clean render.

- [ ] **Step 1: Clean render and the full suite**

```bash
rm -rf docs .quarto && quarto render 2>&1 | grep -iE "warn|error"; echo "render exit=${PIPESTATUS[0]}"
python3 -m unittest discover -s tests 2>&1 | tail -3
npm run audit 2>&1 | tail -2
python3 -I _plans/tools/check_internal_links.py | tail -1
python3 -I _plans/tools/verify_curation_applied.py | tail -1
```

Expected, in order: `render exit=0`; `Ran 23 tests … OK`; `✅ Accessibility audit passed with 0 violations!`; `broken: 0`; `problems: 0`.

- [ ] **Step 2: SEO spot-checks on the built output**

```bash
grep -L '<meta name="description"' docs/resources/r/*.html docs/resources/stata/*.html docs/resources/r.html docs/resources/stata.html docs/resources/statistics.html docs/resources/index.html; echo "(empty above = all have a description)"
grep -c "resources/r/learning-r.html" docs/sitemap.xml
test ! -e docs/_plans && echo "plans not published"
```

Expected: no filenames listed; the sitemap count is `1`; `plans not published`. (If `docs/sitemap.xml` is absent, `site-url` generation is off and the sitemap check is reported to you as not applicable rather than skipped silently.)

- [ ] **Step 3: Inbound links still work**

Run: `grep -rhoE "resources/(r|stata|statistics|data|gis)\.html" teaching | sort -u | while read p; do test -e "docs/$p" && echo "ok $p" || echo "MISSING $p"; done`
Expected: every line starts with `ok`.

- [ ] **Step 4: Push the branch**

```bash
git push -u origin claude/website-resources-wiki-omw6e8
```

Expected: branch updated. No pull request is opened (D5). On retry for network failure only: wait 2 s, 4 s, 8 s, 16 s.

- [ ] **Step 5: Report**

I report what changed, the measured results above, the unverified annotations, and one thing I cannot verify from here: the live site and its indexing, because the workflow deploys only from `main`. After you merge, the Action runs and the pages appear at `https://paulmaxlove.com/resources/…`.

## 5. Self-review

**Spec coverage**

| Your requirement | Where it is met |
|---|---|
| Themed pages branching from the R / Stata hubs, not a flat link dump | §2 structure; Tasks 5–6; hub listings |
| Start with Stata, stats, R-stuff folders | Scope of `build_curation.py` (`FOLDERS`); Tasks 5, 6 |
| Don't take everything; hold back instructor-only links | `HOLD_RULES`, D6, Task 3 Step 2, verifier checks `hold` rows are absent |
| Worry about thin pages / SEO | §3 rules, Task 4 guard test, static-HTML listing (prototype-verified), Task 9 SEO checks |
| Simple deployment as now | No workflow or `_quarto.yml` change; render + push-to-`main` unchanged |
| Not full Obsidian yet | Pages are plain `.qmd` with `categories:` so a later vault or tag listing stays cheap |
| Raindrop stays a source | Export read-only, CSV kept out of repo; nothing written back |
| ~400 links → change strategy | Curation (359 keep before pruning, targeting roughly a third to half published), link check, per-link annotation |

**Placeholder scan.** The only deliberately content-dependent steps are the page bodies in Tasks 5–6. They cannot be written before the Task 3 approval and the D1 decision, so each states its source (approved CSV rows), exact structure, and acceptance checks instead of inventing links. The guard test and verifier enforce the structure. No `TBD` or "handle edge cases" steps remain.

**Consistency.** Slugs in §1, §2, Task 3 and Task 6 match; `order`/`sort` and listing `id`s match the prototype; script names and paths match the files in `_plans/tools/`.

**Known risks**

1. **Annotation accuracy** without reading live pages (D1). Mitigated by rule 3 and the per-batch "please verify" list.
2. **Quarto version drift.** Local 1.10.20 vs. unpinned CI. Listings are long-standing Quarto features, but the first post-merge Action run is the real test.
3. **Two-glob listing** on the Resources index is untested (Task 7 has a fallback).
4. **Thin text-analysis page risk reversed:** 53 candidate links may make that page too long; Task 3 Step 3 handles it by pruning or splitting.
5. **Rollback.** Each task is one commit; `git revert` of a batch restores the hubs. Hub URLs never change.

**Out of scope (possible follow-ups with the same tooling):** the other Raindrop folders (`GIS` 53, `Data Sources` 27, `Research / Tools` 40, `Writing` 13, `Computer Science` 90, …), per-tag pages, an Obsidian vault, a scheduled dead-link check.

---

**Plan complete and saved to `_plans/2026-10-30-raindrop-resource-pages.md`. Once you have decided D1–D6, two execution options:**

1. **Subagent-Driven (recommended):** a fresh subagent per task with review between tasks.
2. **Inline Execution:** run the tasks in this session with checkpoints at each gate.
