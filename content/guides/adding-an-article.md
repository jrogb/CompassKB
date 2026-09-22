---
id: adding-an-article
title: Adding an article to CompassKB
category: guides
status: published
audiences: [internal, engineer]
tags: [getting-started, onboarding]
owner: kb-maintainers
created: 2026-09-22
updated: 2026-09-22
review_after: 2027-03-22
summary: Scaffold an article with new_article.py, write the body, validate it, and hand it to a reviewer.
keywords: ["write a new page", "how do I add docs", "create article"]
related: [how-compasskb-is-organised, which-category-does-this-go-in]
---

You are done when a new article exists in `content/`, `scripts/validate.py`
passes, an eval case covers it, and its status is `review` waiting on a reviewer.

## Before you start

```bash
python3 -m pip install -r requirements.txt
```

Decide the category first — it determines the shape of the page, not just where
the file goes. See [how CompassKB is organised](../concepts/how-compasskb-is-organised.md).

## Scaffold the file

Do not hand-write front matter. The generator validates tags and audiences
against the taxonomy and fills in the dates:

```bash
python3 scripts/new_article.py guides rotating-api-keys \
  --title "Rotating API keys" \
  --summary "API keys rotate without downtime if old and new overlap for one request cycle." \
  --audiences engineer,operator \
  --tags authentication,security \
  --owner platform-team
```

It prints the path it created and refuses to overwrite an existing file. If it
rejects a tag, that tag does not exist yet — decide whether it is genuinely new
before adding it to `taxonomy/tags.yml`.

## Write the body

Three constraints matter more than the rest:

- **Start at H2.** The H1 comes from `title`, and the validator rejects an H1 in
  the body.
- **Make each H2 section stand alone.** Sections are the unit the retrieval
  index chunks on, so a section beginning "this only works if you did the above"
  becomes a useless fragment. Name the precondition.
- **Write the summary as a claim.** It is the search snippet. "API keys expire
  after 90 days" works; "This article explains API keys" does not.

The rest is in [the style guide](../../docs/style-guide.md).

## Validate

```bash
python3 scripts/validate.py content/guides/rotating-api-keys.md
```

The whole KB is loaded even when you name one file, so cross-article links and
`related:` ids resolve. Errors block a merge; warnings need a decision, not
silence.

## Add an eval case

An article nobody can find is not published in any useful sense. Add a case to
the matching file in `evals/queries/`, using words a real reader would type —
from a ticket or a Slack question, not from the article you just wrote:

```yaml
cases:
  - query: "my api key stopped working after 90 days"
    expect_article: rotating-api-keys
```

Then:

```bash
python3 scripts/run_evals.py --k 5
```

A failure here almost always means the article does not use the reader's
vocabulary. Fix the article, not the eval.

## Hand it over

Set `status: review` and open a PR saying what changed for the reader, how you
know it is true, and what you left out. Only a reviewer sets `published`.

## Related

- [How CompassKB is organised](../concepts/how-compasskb-is-organised.md)
- [Contributing](../../docs/contributing.md)
