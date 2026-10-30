# pmlove3.github.io

Paul Max Love III's academic site (https://paulmaxlove.com). A Quarto website published to GitHub Pages.

## Commands

```bash
quarto render                          # builds the site into docs/ (gitignored)
python3 -m unittest discover -s tests  # structured-data and page tests; run after a render
npm install && npm run audit           # accessibility audit (axe) on the rendered pages
```

Deployment: `.github/workflows/publish.yml` renders and deploys on every push to `main`. Pushing any other branch does not deploy.

## Conventions

- Pages are `.qmd`. Directories and files starting with `_` or `.` are not rendered, so `_plans/` and `_extensions/` are safe places for non-page files.
- Links between site pages use `../name.html` relative links, not `.qmd` paths.
- The `date:` front-matter field is a last-updated date; bump it when a page changes.
- Set a `description:` on every page you touch. Most `resources/` pages have none, so search engines write their own snippet.
- Never commit the Raindrop export or anything under `_plans/curation/` or `_plans/.venv/` (both are gitignored).

## Current project: Raindrop links to themed resource pages

Read `_plans/2026-10-30-raindrop-resource-pages.md`, starting with the section "Status and how to resume". It has the decisions, the open questions, the PR sequence, and every task with its check.

- One PR per batch, on the branch names listed in the plan's PR sequence. No force-pushes. The repo has no PR template: use **Summary** and **Test plan** sections.
- New theme pages must pass `tests/test_resource_pages.py` once it exists (at least 8 links, an intro of at least 25 words, an annotation on every link, no duplicate or tracked URLs).
- Do not copy Raindrop excerpts verbatim into annotations; write them yourself and claim only what the linked page supports.
- `_plans/tools/` holds the curation scripts. Run them with `_plans/.venv/bin/python -B -I`. After you have edited `curation_firstpass.csv`, never re-run `build_curation.py --force`: it overwrites your edits.
