# CompassKB

A curated knowledge base: Markdown articles with validated metadata, a closed
taxonomy, and tooling that checks whether readers can actually find what they
need.

The content is the product. The Python in `scripts/` exists only to stop the
content from drifting.

## Quick start

```bash
python3 -m pip install -r requirements.txt

python3 scripts/validate.py          # check everything
python3 scripts/build_index.py --stats
python3 scripts/run_evals.py --k 5
```

Add an article:

```bash
python3 scripts/new_article.py guides rotating-api-keys \
  --title "Rotating API keys" \
  --summary "Rotate a live API key without dropping in-flight requests." \
  --audiences engineer,operator \
  --tags authentication,security \
  --owner platform-team
```

Then write the body, run `python3 scripts/validate.py`, and open a PR.

## How it is organised

| Directory | Contents |
|---|---|
| `content/` | The articles, one directory per category |
| `taxonomy/` | Closed vocabularies: categories, tags, audiences, statuses |
| `templates/` | Article starting points |
| `scripts/` | Validation, indexing, and eval tooling |
| `evals/queries/` | Real queries and the articles that should answer them |
| `docs/` | Front-matter schema, style guide, contributing |
| `tests/` | Tests for the tooling |

Five categories, and the directory an article sits in must match its `category`
field: `concepts`, `guides`, `reference`, `runbooks`, `faq`. What each is for is
described in `taxonomy/categories.yml`.

## The rules that keep it useful

- Every article has front matter, validated against the taxonomy —
  see [`docs/front-matter.md`](docs/front-matter.md).
- Tags and audiences are a **closed** vocabulary. New terms are added
  deliberately, in the same commit as the article that needs them.
- `summary` is what search results show. It states what is true, not what the
  page contains.
- Body headings start at H2 — H2 sections are the retrieval chunk boundary.
- Articles are archived, never deleted.
- Only reviewed content reaches `status: published`, and only published and
  stale content is exported for retrieval.

## Checks

| Command | Checks |
|---|---|
| `scripts/validate.py` | Front matter, taxonomy, dates, structure, links, duplicates |
| `scripts/build_index.py` | The retrieval export builds; `--stats` for chunk sizes |
| `scripts/run_evals.py` | Real queries still reach the right articles |
| `pytest tests/` | The tooling itself |

CI runs all four on every PR (`.github/workflows/checks.yml`), with
`validate.py --strict`.

## Working with Claude Code

`CLAUDE.md` holds the repo's conventions, and `.claude/skills/` holds
task-specific guidance — adding an article, reviewing content, importing an
external source, tuning chunking, cutting a release. A SessionStart hook
(`.claude/hooks/session-start.sh`) installs the dependency and prints the
current state of the KB, including anything past its review date.

## Contributing

See [`docs/contributing.md`](docs/contributing.md) for branches, commits, and
what a PR needs to contain, and [`docs/style-guide.md`](docs/style-guide.md) for
how to write the prose.
