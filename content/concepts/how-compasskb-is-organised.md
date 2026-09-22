---
id: how-compasskb-is-organised
title: How CompassKB is organised
category: concepts
status: published
audiences: [internal, engineer]
tags: [getting-started, data-model]
owner: kb-maintainers
created: 2026-09-22
updated: 2026-09-22
review_after: 2027-03-22
summary: CompassKB sorts every article into one of five categories and validates its metadata against a closed vocabulary.
keywords: ["kb structure", "where do articles live", "what are the categories"]
related: [adding-an-article, which-category-does-this-go-in]
---

Every article in CompassKB belongs to exactly one of five categories, lives in
the directory named after that category, and carries validated metadata. Those
three facts are what let the knowledge base be searched, reviewed, and trusted
rather than just accumulated.

## The five categories

Each category answers a different kind of question, which is why they are
separate rather than one undifferentiated pile of pages.

| Category | The reader wants to | Shape |
|---|---|---|
| `concepts` | understand what something is | Narrative, durable, no steps |
| `guides` | accomplish a task | Goal, ordered steps, definition of done |
| `reference` | look up a value | Tables, complete, scannable |
| `runbooks` | fix something broken right now | Symptoms, diagnosis, remediation, escalation |
| `faq` | get one short answer | Answer in the first line |

The category in an article's front matter must match the directory it sits in.
`scripts/validate.py` fails the build otherwise, because a KB where the metadata
and the filesystem disagree cannot be navigated reliably by either.

## Why the vocabulary is closed

Tags, audiences, categories and statuses are fixed lists in `taxonomy/`. Adding
a term is a deliberate act that happens in the same commit as the first article
needing it.

Free-form tagging decays predictably: `auth`, `authentication` and `login`
accumulate as separate tags, each holding a third of the relevant articles, and
filtering by any of them silently hides the rest. A closed vocabulary trades a
small amount of authoring friction for a filter that keeps working.

## Why articles are archived, not deleted

Retiring an article means setting `status: archived` and `superseded_by`, not
removing the file. Inbound links, bookmarks and search history all point at the
old page, and a reader who lands on a tombstone that names the replacement is
better served than one who gets a 404. Keeping the file also lets the validator
catch references to it elsewhere in the KB.

## What reaches a retrieval index

Only `published` and `stale` articles are exported by `scripts/build_index.py`.
Drafts are excluded by design — an unreviewed answer surfacing in search is
worse than no answer, because the reader stops looking.

Stale articles are exported with a `stale: true` flag rather than withheld: a
dated answer still beats nothing, provided the consumer can see that it is dated.

## Related

- [Adding an article](../guides/adding-an-article.md)
- [Which category does this go in?](../faq/which-category-does-this-go-in.md)
