#!/usr/bin/env bash
# Set up a local checkout (macOS or Linux) for the Raindrop resource-pages project. Safe to re-run.
#
#   _plans/tools/setup_local.sh              install what is missing, then verify the site builds
#   _plans/tools/setup_local.sh --check-only report what is missing and change nothing
set -euo pipefail
cd "$(dirname "$0")/../.."

check_only=0
[ "${1:-}" = "--check-only" ] && check_only=1

ok()   { printf '  ok       %s\n' "$1"; }
todo() { printf '  MISSING  %s\n' "$1"; }
info() { printf '  note     %s\n' "$1"; }

echo "== Tools"
command -v git >/dev/null && ok "git $(git --version | cut -d' ' -f3)" || { todo "git"; exit 1; }
command -v python3 >/dev/null && ok "$(python3 --version)" || { todo "python3 (macOS: brew install python)"; exit 1; }

if command -v quarto >/dev/null; then
  ok "quarto $(quarto --version)"
else
  todo "quarto"
  if [ $check_only -eq 0 ]; then
    if command -v brew >/dev/null; then brew install --cask quarto
    else echo "  Install Quarto from https://quarto.org/docs/get-started/ and re-run."; exit 1; fi
  fi
fi

echo "== Python virtual environment for the link tools (_plans/.venv)"
if [ -x _plans/.venv/bin/python ] && _plans/.venv/bin/python -c 'import requests' 2>/dev/null; then
  ok "requests installed in _plans/.venv"
else
  todo "_plans/.venv with requests"
  if [ $check_only -eq 0 ]; then
    python3 -m venv _plans/.venv
    _plans/.venv/bin/python -m pip install --quiet requests
    ok "created _plans/.venv"
  fi
fi

echo "== Node (only needed for the accessibility audit: npm run audit)"
if command -v npm >/dev/null; then
  ok "npm $(npm --version)"
  if [ ! -d node_modules ] && [ $check_only -eq 0 ]; then npm install --no-audit --no-fund >/dev/null && ok "npm install"; fi
else
  info "npm not found; skip unless you want to run the audit (brew install node)"
fi

echo "== Curation data (gitignored, so it only exists on your machine)"
mkdir -p _plans/curation
if [ -f _plans/curation/curation_firstpass.csv ]; then
  ok "_plans/curation/curation_firstpass.csv"
elif [ -f "$HOME/Downloads/curation_firstpass.csv" ]; then
  if [ $check_only -eq 0 ]; then
    cp "$HOME/Downloads/curation_firstpass.csv" _plans/curation/
    ok "copied curation_firstpass.csv from ~/Downloads"
  else
    todo "curation_firstpass.csv (found in ~/Downloads; setup will copy it)"
  fi
else
  todo "curation_firstpass.csv (download from the parking message, or rebuild: see 'Resume' in the plan)"
fi
if [ -n "${RAINDROP_CSV:-}" ] && [ -f "$RAINDROP_CSV" ]; then
  ok "RAINDROP_CSV=$RAINDROP_CSV"
else
  info "RAINDROP_CSV is not set; only needed to rebuild the table: export RAINDROP_CSV=/path/to/export.csv"
fi

if [ $check_only -eq 0 ]; then
  echo "== Verify the site builds and tests pass"
  quarto render >/dev/null 2>&1 && ok "quarto render exits 0" || { todo "quarto render failed; run 'quarto render' to see why"; exit 1; }
  python3 -B -m unittest discover -s tests 2>&1 | tail -3
fi

echo
echo "Next: open this folder with 'claude' and paste the resume prompt from"
echo "      _plans/2026-10-30-raindrop-resource-pages.md (section 'Status and how to resume')."
