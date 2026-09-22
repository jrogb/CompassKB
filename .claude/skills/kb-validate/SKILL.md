---
name: kb-validate
description: Run CompassKB's checks — front-matter/taxonomy validation, link checking, index build, and retrieval evals — and interpret the output. Use before committing content changes, when CI fails on a content check, or when asked to "validate", "check the KB", "run the checks", or "why is the build red".
---

# Running CompassKB's checks

The full local check, in the order CI runs it:

```bash
python3 scripts/validate.py          # front matter, taxonomy, links, structure
python3 scripts/build_index.py       # retrieval export must build
python3 scripts/run_evals.py --k 5   # queries still find their articles
python3 -m pytest tests/ -q          # tooling's own tests
```

`scripts/validate.py` is the one that matters most and the one to run while
editing. It exits 1 on errors, 0 on warnings. Useful flags:

- `python3 scripts/validate.py content/guides/thing.md` — one file, but the
  whole KB is still loaded so cross-article links resolve.
- `--strict` — warnings fail too. This is what CI uses on the default branch.
- `--today 2026-01-01` — pin the date. Use it when a failure depends on a
  review date so you can reproduce it.

## Reading the output

Errors block a merge. Warnings are a judgement call, but do not leave them for
someone else without saying why in the PR.

| Message | What it actually means |
|---|---|
| `id 'x' does not match filename 'y'` | Rename the file, don't edit the id — ids are referenced by `related:` and by the retrieval index. Grep for the old id first. |
| `category 'x' but file lives in content/y/` | Move the file, or fix the field. The directory is the source of truth for navigation. |
| `unknown tag 'x'` | Either a typo or a genuinely new tag. A new tag goes into `taxonomy/tags.yml` **in the same commit** as the article that needs it, with a real description. |
| `broken relative link` | Something moved. Fix the link; don't delete it. |
| `review_after ... has passed` | Actually re-read the article against reality. Pushing the date out without checking is how a KB starts lying. |
| `published article still contains a 'TODO'` | Either finish it or set `status: draft`. |
| `title ... duplicates ...` | Two pages answering one question. Merge them, or sharpen both titles. |

## When a check fails in CI but not locally

CI runs with `--strict` and a real current date, so a review date that passed
since you last ran it will fail there and not here. Reproduce with:

```bash
python3 scripts/validate.py --strict --today "$(date -u +%F)"
```

## Do not

- Do not silence a finding by loosening the validator. If a rule is genuinely
  wrong, change it deliberately in `scripts/validate.py`, update
  `tests/test_validate.py` to cover the new behaviour, and say so in the commit.
- Do not add a tag, audience, category or status to a taxonomy file just to make
  an error go away — that is exactly the drift the closed vocabulary prevents.
