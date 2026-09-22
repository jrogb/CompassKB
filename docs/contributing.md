# Contributing

The short version lives in `.claude/skills/contribute/SKILL.md`; this is the
human-facing copy.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

Python 3.11+. PyYAML and pytest are the only dependencies.

## Making a change

1. Branch from the default branch: `content/…`, `taxonomy/…`, `tooling/…`, `chore/…`.
2. Create or edit the article. Use the generator for new ones:
   ```bash
   python3 scripts/new_article.py <category> <slug> --title "..." --summary "..."
   ```
3. Validate:
   ```bash
   python3 scripts/validate.py --strict
   python3 -m pytest tests/ -q
   ```
4. Add an eval case in `evals/queries/` for any new article, using a phrasing a
   real reader would type. Then `python3 scripts/run_evals.py --k 5`.
5. Commit with a conventional prefix — `docs(guides):`, `taxonomy:`, `tooling:`,
   `chore:`. The subject says what changed for the reader.
6. Open a PR.

## Keep PRs single-purpose

Content and tooling go in separate PRs. A reviewer checking whether the prose is
*true* should not have to read Python to do it.

Taxonomy changes ship with the first article that needs them, never on their own.

## What a PR must say

1. **What changed for the reader** — the new answer, not the diff.
2. **How you know it is true** — a person, a ticket, a command you ran, code you
   read. "Confirmed with the platform team on 2026-09-18" is a source.
3. **What you deliberately left out**, so the reviewer does not report it as a gap.

If the change alters a previously published answer, say so explicitly: someone
acted on the old one.

## Review

Every content PR needs a reviewer who can verify the claims — usually the
`owner` named in the front matter. Reviewers work from
`.claude/skills/content-review/SKILL.md`. Only a reviewer sets
`status: published`.

Approving a page you could not verify is worse than leaving it in draft, because
the status field then vouches for something nobody checked.
