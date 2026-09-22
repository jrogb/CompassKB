# CompassKB

A curated knowledge base. The deliverable is **Markdown content in `content/`**
that people and retrieval systems can trust. Everything else in this repo exists
to keep that content accurate and findable.

There is no application code here. Do not add a web framework, a database, or a
frontend without being asked.

## Layout

```
content/          The knowledge base. One .md file per article.
  concepts/       What something is
  guides/         How to accomplish a task
  reference/      Values to look up
  runbooks/       What to do when it is broken
  faq/            One question, one answer
taxonomy/         Closed vocabularies: categories, tags, audiences, statuses
templates/        Starting points, used by scripts/new_article.py
scripts/          Validation, indexing, eval tooling (Python 3.11+, PyYAML only)
evals/queries/    Retrieval eval cases -- real queries, expected articles
docs/             Docs about the KB itself: style guide, front-matter schema
tests/            Tests for the tooling in scripts/
dist/             Build output (gitignored)
```

## Skills

Task-specific guidance lives in `.claude/skills/`. Read the relevant one before
starting:

| Doing this | Read |
|---|---|
| Writing, moving, or retiring an article | `new-article` |
| Running checks / debugging a red build | `kb-validate` |
| Committing, branching, opening a PR | `contribute` |
| Importing external material | `ingest-source` |
| Writing or fixing retrieval evals | `retrieval-eval` |
| Chunking, indexing, `build_index.py` | `chunking` |
| Reviewing content or approving a PR | `content-review` |
| Changelog and releases | `release-notes` |

## Commands

```bash
python3 scripts/validate.py              # front matter, taxonomy, links, structure
python3 scripts/validate.py --strict     # warnings fail too (what CI uses)
python3 scripts/build_index.py --stats   # retrieval chunk summary
python3 scripts/run_evals.py --k 5       # can readers find things
python3 -m pytest tests/ -q              # tooling tests

python3 scripts/new_article.py <category> <slug> --title "..." --summary "..."
```

Run `validate.py` before every commit that touches `content/` or `taxonomy/`.

## Conventions that are not negotiable

- **Front matter is mandatory and validated.** Schema in
  `docs/front-matter.md`. Generate it with `new_article.py`; do not hand-write it.
- **The `category` field must match the directory** the file is in.
- **`id` must equal the filename stem**, both lowercase-hyphen slugs. Other
  articles reference articles by id.
- **Tags, audiences, categories and statuses are closed vocabularies.** A new
  term goes into the `taxonomy/` file *in the same commit* as the first article
  that needs it, with a real description. Never add one just to clear an error.
- **Body headings start at H2.** The H1 comes from `title`. H2 sections are the
  retrieval chunk boundary, so each must make sense standing alone.
- **`summary` is the retrieval snippet.** State the subject as a claim. Not
  "This article explains X" — say what is true about X.
- **Never delete an article.** Set `status: archived` with `superseded_by`.
  Inbound links and search history point at it.
- **Only reviewed content gets `status: published`.** Drafts are excluded from
  the retrieval export by design.

## Things that must never enter `content/`

Credentials, API tokens, private keys, internal hostnames, customer data, or
personal information — including inside examples, code blocks, and "redacted"
placeholders that still carry the real shape. Also: third-party documentation
pasted rather than summarised and linked.

If a task seems to require any of these, stop and ask.

## Accuracy over coverage

A wrong article is worse than a missing one, because the reader stops looking.
When a fact cannot be confirmed, either leave it out or mark it explicitly as
unverified with an owner to chase — never state an uncertain claim confidently.
Every article carries an `owner` and a `review_after` date for this reason.
