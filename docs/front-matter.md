# Front-matter schema

Every file in `content/` opens with a YAML front-matter block. It is validated
by `scripts/validate.py` and consumed by `scripts/build_index.py`, so it is a
contract, not decoration.

Generate it with `python3 scripts/new_article.py` rather than typing it.

## Required fields

| Field | Type | Rules |
|---|---|---|
| `id` | slug | Lowercase letters, digits, hyphens. **Must equal the filename stem.** Other articles reference this. |
| `title` | string | Sentence case. Becomes the H1; the body must not contain one. |
| `category` | enum | One of `taxonomy/categories.yml`. **Must match the directory** the file is in. |
| `status` | enum | One of `taxonomy/statuses.yml`. See the lifecycle below. |
| `audiences` | list | One or more ids from `taxonomy/audiences.yml`. |
| `tags` | list | One or more ids from `taxonomy/tags.yml`. More than ~6 warns — it usually means the article covers too much. |
| `owner` | string | A person or team who can answer questions about this page. Not necessarily the author. |
| `created` | date | ISO `YYYY-MM-DD`. |
| `updated` | date | ISO. Must be ≥ `created` and not in the future. Bump it on every substantive edit. |
| `review_after` | date | ISO, after `updated`. When someone must re-verify the content. |
| `summary` | string | 5–40 words. The retrieval snippet. |

## Optional fields

| Field | Type | Purpose |
|---|---|---|
| `keywords` | list | Extra phrasings readers use that do not fit naturally in the prose. Helps findability without contorting the writing. |
| `related` | list of ids | Neighbouring articles. Every id must exist. |
| `sources` | list | Provenance for imported or researched content: `title`, `url`, `retrieved`. |
| `superseded_by` | id | Required in practice when `status: archived` — points at the replacement. |

Any other field warns. If a new field is genuinely needed, add it to
`OPTIONAL_FIELDS` in `scripts/kblib.py` and document it here in the same commit.

## Writing the summary

It is the search result, the retrieval snippet, and the first thing an embedding
sees. It must carry meaning with no page around it.

- Weak: `This article explains how API key rotation works.`
- Strong: `API keys rotate without downtime if the old and new keys overlap for one request cycle.`

The validator warns on summaries opening with "This article/page/doc".

## Lifecycle

```
draft  ──►  review  ──►  published  ──►  stale  ──►  archived
                            ▲             │
                            └─── re-verified, review_after pushed out
```

| Status | Exported for retrieval? | Meaning |
|---|---|---|
| `draft` | no | Being written. Not trusted. |
| `review` | no | Content complete, awaiting a reviewer. |
| `published` | **yes** | Reviewed and trusted. |
| `stale` | **yes** | Past review or known to have drifted. Exported with a `stale: true` flag, because a dated answer beats none. |
| `archived` | no | Retired. Set `superseded_by`. The file stays. |

Only a reviewer moves an article to `published` — see
`.claude/skills/content-review/SKILL.md`.

## Example

```yaml
---
id: rotating-api-keys
title: Rotating API keys
category: guides
status: published
audiences: [engineer, operator]
tags: [authentication, security]
owner: platform-team
created: 2026-08-01
updated: 2026-09-18
review_after: 2027-03-18
summary: API keys rotate without downtime if old and new overlap for one request cycle.
keywords: ["api key expired", "401 after rotation"]
related: [api-key-lifecycle, troubleshooting-401s]
sources:
  - title: "Gateway auth design doc"
    url: https://internal.example.com/docs/gateway-auth
    retrieved: 2026-09-18
---
```
