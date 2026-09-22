#!/usr/bin/env bash
# SessionStart hook for CompassKB.
#
# Makes sure a session can actually run the repo's checks, then prints a short
# state-of-the-KB summary so the model does not have to rediscover it.
#
# Anything on stdout is added to the session context. Keep it short and factual.
# Never fail the session: a broken hook must not block someone editing Markdown,
# so every step degrades to a printed warning.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || exit 0

PY="${PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "CompassKB: python3 not found -- scripts/validate.py and the other checks cannot run."
  exit 0
fi

# PyYAML is the only dependency. Install it quietly if it is missing.
if ! "$PY" -c "import yaml" >/dev/null 2>&1; then
  echo "CompassKB: installing PyYAML (the only dependency)..."
  if ! "$PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt >/dev/null 2>&1; then
    echo "CompassKB: could not install PyYAML automatically."
    echo "  Run: $PY -m pip install -r requirements.txt"
    exit 0
  fi
fi

echo "CompassKB -- docs/content knowledge base."
echo "Checks: $PY scripts/validate.py [--strict] | build_index.py | run_evals.py | pytest tests/"

# Article counts by category, straight from the files.
"$PY" - <<'PYEOF' 2>/dev/null || echo "  (could not read content/ -- run scripts/validate.py for detail)"
import sys, pathlib
sys.path.insert(0, "scripts")
try:
    from kblib import load_articles, load_taxonomy
except Exception as exc:                      # tooling not importable yet
    print(f"  tooling not importable: {exc}")
    raise SystemExit(0)

try:
    tax = load_taxonomy()
    articles = [a for a in load_articles() if not a.front_matter_error]
except Exception as exc:
    print(f"  could not load the KB: {exc}")
    raise SystemExit(0)

if not articles:
    print("  content/ is empty -- see .claude/skills/new-article/SKILL.md to add the first article.")
    raise SystemExit(0)

by_status: dict[str, int] = {}
by_cat: dict[str, int] = {}
for a in articles:
    by_status[str(a.meta.get("status"))] = by_status.get(str(a.meta.get("status")), 0) + 1
    by_cat[str(a.meta.get("category"))] = by_cat.get(str(a.meta.get("category")), 0) + 1

print(f"  {len(articles)} article(s): " + ", ".join(f"{n} {k}" for k, n in sorted(by_cat.items())))
print("  status: " + ", ".join(f"{n} {k}" for k, n in sorted(by_status.items())))

import datetime as dt
from kblib import as_date
today = dt.date.today()
overdue = [
    a.id for a in articles
    if a.meta.get("status") in {"published", "review"}
    and (d := as_date(a.meta.get("review_after"))) and d < today
]
if overdue:
    shown = ", ".join(sorted(overdue)[:5])
    more = f" (+{len(overdue) - 5} more)" if len(overdue) > 5 else ""
    print(f"  {len(overdue)} article(s) past review_after: {shown}{more}")
PYEOF

# A dirty tree at session start usually means an interrupted edit; worth saying.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  changed="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$changed" != "0" ]; then
    echo "  working tree has $changed uncommitted change(s) on $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  fi
fi

exit 0
