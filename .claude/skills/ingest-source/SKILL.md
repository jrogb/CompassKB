---
name: ingest-source
description: Bring external material (support tickets, Slack threads, vendor docs, wikis, code comments) into CompassKB as proper articles, including provenance and licensing checks. Use when asked to import, ingest, migrate, or "turn X into a KB article".
---

# Ingesting an external source

Importing is not copying. Source material is evidence; an article is a
maintained claim. The job is to convert one into the other.

## 1. Check before you copy

Stop and ask the user if any of these are true:

- The source is **third-party material under a licence** (vendor docs, a blog,
  Stack Overflow). Link and summarise in your own words; do not paste.
- The source contains **customer data, credentials, internal hostnames, or
  personal information**. These never enter `content/` — not in an example, not
  in a code block, not redacted-by-asterisks.
- The source is **someone's opinion in a thread**, and no owner has confirmed
  it is how the system actually behaves. A Slack message is a lead, not a source.

## 2. Work out what the article is

Raw sources do not map one-to-one onto articles. Read the whole source first,
then decide:

- A support thread usually becomes **one FAQ** (the literal question) plus
  possibly **one guide** (the underlying task).
- A wiki page usually splits: the "what it is" part becomes a `concepts` page,
  the "how to" part a `guides` page. Importing it whole reproduces the mess you
  were asked to clean up.
- A vendor doc usually becomes a **short reference page that links out**, not a
  copy that silently goes stale when the vendor edits theirs.

Prefer fewer, better pages. Five imported stubs are worse than one real article.

## 3. Create it

Use the `new-article` skill's generator, then record provenance in front matter:

```yaml
sources:
  - title: "Support ticket #4821 — key rotation caused 401s"
    url: https://internal.example.com/tickets/4821
    retrieved: 2026-09-22
  - title: "Gateway rate limiting (vendor docs)"
    url: https://vendor.example.com/docs/rate-limits
    retrieved: 2026-09-22
```

`sources` is what lets the next person re-verify instead of re-researching. An
imported article without it is unmaintainable — nobody will know where the
claim came from when it turns out to be wrong.

## 4. Convert claims into checkable statements

For every factual claim carried over, ask: how would a reader falsify this?

- Vague: "keys expire fairly quickly."
- Checkable: "Keys expire 90 days after creation (gateway default, as of 2026-09)."

Anything you could not confirm goes in with an explicit hedge and an owner to
chase, or it does not go in at all. Never launder an uncertain source into a
confident article.

## 5. Set status honestly

Imported content starts `status: draft`, always — even if the source was
authoritative. It has not been reviewed *in this form*. Set `owner` to whoever
can actually answer questions about it, not to yourself if you only transcribed it.

## 6. Close the loop

```bash
python3 scripts/validate.py content/<category>/<slug>.md
python3 scripts/run_evals.py --k 5
```

Then add an eval case in `evals/queries/` using the words the original asker
used — that phrasing is real evidence of how people search for this. See the
`retrieval-eval` skill.
