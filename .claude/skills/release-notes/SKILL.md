---
name: release-notes
description: Maintain CompassKB's CHANGELOG and cut a versioned snapshot of the knowledge base. Use when asked to update the changelog, cut a release, tag a version, or summarise what changed in the KB.
---

# Releases and the changelog

A KB release is a **point that downstream consumers can pin to**: the retrieval
index built from a tag, and a record of which answers changed. Consumers care
about changed answers, not edited files.

## CHANGELOG.md

Keep a Changelog format, ISO dates, newest first. Entries are written for a
reader of the KB, not for someone reading the diff.

```markdown
## [Unreleased]

### Changed
- **Rate limits** are now documented as 100/min, not 1000/min. The old figure
  was the pre-2025 gateway limit; anyone who read `reference/rate-limits` before
  2026-09-22 has the wrong number. ([#41](https://github.com/jrogb/CompassKB/pull/41))

### Added
- Runbook for ingest pipeline failures (`runbooks/ingest-failure`).

### Deprecated
- `guides/legacy-key-setup` is archived, superseded by `guides/rotating-api-keys`.
```

Sections: `Added`, `Changed`, `Corrected`, `Deprecated`, `Removed`, `Security`.

`Corrected` is CompassKB's addition and it is the most important one. It means
**the KB previously said something false**. Anything that changes a published
answer goes there, with what the page used to say, so a reader who acted on the
old version knows they need to re-check. Never quietly fold a correction into
`Changed`.

Typo fixes, formatting, and tooling changes do not get changelog entries. If
the reader's answer did not change, it is not a release note.

## Cutting a release

1. Confirm the default branch is green:
   ```bash
   python3 scripts/validate.py --strict
   python3 scripts/run_evals.py --k 5
   python3 -m pytest tests/ -q
   ```
2. Check for content that should not ship: articles past `review_after`, and
   anything stuck in `review`.
   ```bash
   python3 scripts/validate.py --strict 2>&1 | grep -i "review"
   ```
   A stale page is not automatically a blocker — but decide deliberately, and
   note in the release which known-stale pages went out.
3. Move `[Unreleased]` to a version heading with today's date. Versioning is
   date-based (`2026.09.1` — year.month.sequence), because a KB has no API
   surface to version semantically.
4. Build the artefact the release refers to:
   ```bash
   python3 scripts/build_index.py --out dist/index.jsonl
   python3 scripts/build_index.py --stats
   ```
   Record the article and chunk counts in the release notes; a sharp drop
   usually means something was archived or failed to build, and that is worth
   catching before consumers pull it.
5. Commit (`chore: release 2026.09.1`), tag, and push the tag.

Ask before tagging or pushing a tag — a tag is what other systems pin to, and
moving one after the fact breaks them.
