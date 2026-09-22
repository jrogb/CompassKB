---
name: content-review
description: Review a CompassKB article or content PR against the repo's accuracy, structure, and findability checklist, and decide whether it can move to published. Use when asked to review, check, proofread, or approve knowledge base content.
---

# Reviewing CompassKB content

Reviewing content is not proofreading. The question is whether a reader who
follows this page gets the right outcome. Run the mechanical checks first so
review time goes to the part a machine cannot do.

```bash
python3 scripts/validate.py --strict <path>
python3 scripts/run_evals.py --k 5
```

## Accuracy — the part that matters

- **Is every factual claim checkable, and did someone check it?** Limits,
  version numbers, flag names, endpoints, escalation contacts. If the PR does
  not say how the author knows, ask. "It reads plausibly" is not review.
- **Is anything true-but-stale?** A number that was right last year is now a
  wrong answer with a confident tone.
- **Does it contradict another page?** Search before approving:
  `grep -rn "<key term>" content/`. Two pages disagreeing is worse than a gap,
  because the reader cannot tell which to trust. If you find one, the PR must
  fix or archive the other.
- **Are the steps actually runnable in order?** Read a guide as someone with no
  context: are prerequisites stated, are placeholders explained, does a step
  silently assume a permission the reader lacks?
- **Runbooks: would this work at 3am?** No theory before the first action, the
  literal alert text present so it can be grepped, escalation names a channel
  and a person, destructive steps flagged as destructive.

## Safety

Block the PR on any of these:

- Credentials, tokens, keys, internal hostnames, or customer data — including in
  examples and code blocks.
- Personal information about a named individual.
- Third-party text pasted rather than summarised and linked.
- A destructive command without a stated consequence and a way back.

## Structure

- Category matches the shape (see the `new-article` skill's table). A "guide"
  with no steps is a concept page filed wrong.
- Body starts at H2, headings are descriptive, sections stand alone (see the
  `chunking` skill).
- The answer is near the top. If the reader must read three paragraphs of
  background to learn whether the page applies to them, reorder it.

## Findability

- The `summary` states the subject as a claim, not "This article explains...".
- The words readers actually use appear somewhere in the page.
- An eval case exists in `evals/queries/` for this article, using a real
  phrasing. A new article without one is not reviewable as published.
- `related:` links to neighbours, and neighbours link back where it helps.

## Metadata

- `owner` is someone who can answer questions about this page — not the person
  who typed it, if those differ.
- `review_after` is proportionate: months for volatile material, a year for
  durable concepts. A five-year date on a page about a versioned API is a
  promise nobody will keep.
- `updated` reflects this change.

## The verdict

Say which of these you are giving, and why:

- **Publish** — accurate, checked, findable. Set `status: published`.
- **Publish with follow-ups** — correct as far as it goes; file the gaps as
  issues rather than blocking. Name them.
- **Changes needed** — list them as specific edits, not impressions. "Add the
  rate limit value from the gateway config" beats "needs more detail".
- **Wrong shape** — the content is fine but it is two articles, or the wrong
  category. Say what the split should be.

Never approve a page you could not verify. Say plainly which claims you did not
check and who should — an unreviewed claim marked published is worse than a
draft, because the status field is now lying about it.
