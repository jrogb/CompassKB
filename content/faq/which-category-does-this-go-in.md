---
id: which-category-does-this-go-in
title: Which category does this go in?
category: faq
status: published
audiences: [internal]
tags: [getting-started]
owner: kb-maintainers
created: 2026-09-22
updated: 2026-09-22
review_after: 2027-03-22
summary: Pick the category by what the reader is trying to do, not by the subject matter.
keywords: ["concepts or guides", "is this a runbook", "wrong category"]
related: [how-compasskb-is-organised]
---

**Short answer:** ask what the reader is *doing*, not what the page is *about*.
Two pages on the same subject often belong in different categories.

## The test

- They want to understand something → `concepts`
- They want to get something done → `guides`
- They want to look a value up → `reference`
- Something is broken right now → `runbooks`
- They asked one short question → `faq`

Subject matter never decides this. "API keys" can legitimately produce a concept
page about how they work, a guide to rotating them, a reference page of limits,
and a runbook for when rotation breaks production.

## If it seems like two categories

It is two articles. The usual case is a guide that keeps stopping to explain
itself: split the explanation into a `concepts` page and link to it. The guide
gets shorter and both become easier to find, because each one is now about a
single thing.

## If it seems like none of them

Write it as `concepts` and raise it with the maintainers. A genuinely new
category means a new directory and a taxonomy change, which is a deliberate
decision rather than something to settle inside one PR.

## If it is already in the wrong one

Move it with `git mv`, update the `category` field to match, then check for
references:

```bash
grep -rn "<article-id>" content/ evals/
```

The id stays the same as long as the filename does, so `related:` entries and
eval cases keep working.
