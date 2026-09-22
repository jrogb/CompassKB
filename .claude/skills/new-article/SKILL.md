---
name: new-article
description: Add a new article to CompassKB with correct front matter, category, and placement, or split/move an existing one. Use when asked to write, draft, add, document, move, split, or retire a page in the knowledge base.
---

# Adding an article

## 1. Pick the category before you write

The category decides the shape of the page, and it must match the directory.

| The reader wants to... | Category | Shape |
|---|---|---|
| understand what something is | `concepts` | Narrative, durable, no steps |
| accomplish a task | `guides` | Goal, ordered steps, definition of done |
| look up a value | `reference` | Tables, complete, scannable |
| fix something that is broken now | `runbooks` | Symptoms → diagnosis → remediation → escalation |
| get one short answer | `faq` | Answer in the first line |

If a draft wants to be two of these, it is two articles. A guide that keeps
explaining is a guide plus a concept page, linked.

## 2. Scaffold it

Never hand-write front matter — the generator validates the taxonomy for you:

```bash
python3 scripts/new_article.py guides rotating-api-keys \
  --title "Rotating API keys" \
  --summary "Rotate a live API key without dropping in-flight requests." \
  --audiences engineer,operator \
  --tags authentication,security \
  --owner platform-team
```

It refuses unknown tags and audiences. If the tag you want does not exist,
decide whether it is really new: if yes, add it to `taxonomy/tags.yml` with a
description in this same commit; if no, use the existing one.

## 3. Write it

- **The summary is the retrieval snippet.** It is what a search result shows and
  what an embedding sees first. Write it as a claim about the subject
  ("API keys rotate without downtime if you overlap them"), not as a description
  of the page ("This article explains..."). The validator warns on the latter.
- **Body headings start at H2.** The H1 comes from `title`. H2 sections are the
  chunk boundary for retrieval, so a section that would make a good standalone
  answer should be its own H2 with a descriptive heading — `## Rotating without
  downtime`, not `## Notes`.
- **Use the reader's words at least once.** If support tickets say "API key
  expired" and the article only says "credential rotation", nobody finds it.
  Add the phrasing to the body, or to a `keywords:` list in front matter.
- **Link with relative paths** (`../guides/other.md`). The validator checks them.
- **Say when something is true as of.** Version numbers and limits date fast.

## 4. Before committing

```bash
python3 scripts/validate.py content/<category>/<slug>.md
```

Then move `status: draft` → `review` when the content is complete. Only a
reviewer sets `published` — see the `content-review` skill.

## Moving or retiring a page

- **Moving categories:** `git mv` the file, update `category:`, then
  `grep -rn "<old-id>" content/ evals/` and fix every reference. The id stays
  the same if the slug does not change.
- **Retiring:** set `status: archived` and `superseded_by: <new-id>`. Do not
  delete the file — inbound links and search history point at it, and the
  validator uses it to catch dangling references.
