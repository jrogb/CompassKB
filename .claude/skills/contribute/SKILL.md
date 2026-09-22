---
name: contribute
description: CompassKB's branch, commit, and pull request conventions — how to scope a content change, what a commit message looks like, and what a PR must contain. Use when committing, opening a PR, or deciding how to split work in this repo.
---

# Contributing to CompassKB

## Scope a change the way it will be reviewed

A content PR is reviewed by someone checking whether the words are *true*, which
is slow. Keep PRs small and single-purpose:

- One article, or one tightly related set, per PR.
- A taxonomy change (new tag, new category) ships **with** the first article
  that needs it — never as a speculative standalone PR.
- Tooling changes (`scripts/`, `tests/`) go in their own PR, separate from
  content. Mixing them means a reviewer who cares about prose has to read Python.

## Branches

Branch from the default branch. Name it for the change:

```
content/rotating-api-keys      # new or edited articles
taxonomy/add-webhooks-tag      # vocabulary changes
tooling/stricter-link-check    # scripts, tests, CI
chore/...                      # everything else
```

## Commits

Conventional-commit prefixes, scoped to the area:

```
docs(guides): add rotating API keys walkthrough
docs(runbooks): correct escalation channel for ingest failures
taxonomy: add webhooks tag
tooling: fail validation on unbalanced code fences
chore: update .gitignore
```

Use `docs(...)` for anything under `content/`. The subject line says what
changed for the *reader*, not what you did to the file — "correct escalation
channel", not "update runbook".

If a change alters a published answer (not just wording), say so in the body:

```
docs(reference): correct the rate limit to 100/min

The page said 1000/min, which was the pre-2025 gateway limit. Support has
been quoting the wrong number. Anyone who read this page before today has
bad information.
```

## Before you push

```bash
python3 scripts/validate.py --strict
python3 -m pytest tests/ -q
```

Both are cheap. A red CI run on a content typo wastes a reviewer's round trip.

## Pull requests

The PR body must answer three things, because the reviewer cannot infer them:

1. **What changed for the reader** — the new answer, not the diff.
2. **How you know it is true** — who confirmed it, which ticket, which code
   you read, which command you ran. "Checked with the platform team on
   2026-09-18" is a real source. "Seems right" is not.
3. **What you deliberately left out** — scope you chose not to cover, so the
   reviewer does not report it as a gap.

Anything touching `taxonomy/` needs the reasoning for the vocabulary change in
the PR body: what existing term was insufficient, and why.

Do not open a PR unless it was asked for.
