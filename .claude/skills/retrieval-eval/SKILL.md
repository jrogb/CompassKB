---
name: retrieval-eval
description: Write and run CompassKB retrieval evals — query sets that check whether readers can actually find an article. Use when adding eval cases, when run_evals.py fails, or when someone reports they could not find a page that exists.
---

# Retrieval evals

An eval case is a claim: *someone asking this, in these words, should land on
that article.* The runner scores the KB against those claims with a BM25
lexical baseline (`scripts/run_evals.py`).

The baseline is not the production retriever, and that is the point. It has no
embeddings to paper over vocabulary gaps, so it fails loudly when an article
never uses the words its readers use. That failure is a **content** bug.

## Writing cases

Files live in `evals/queries/*.yml`, grouped by topic:

```yaml
# evals/queries/authentication.yml
description: Queries support and engineers actually use about auth.
cases:
  - query: "my api key stopped working after 90 days"
    expect_article: rotating-api-keys
    note: "Verbatim from ticket #4821 — keep the reader's phrasing, not ours."

  - query: "how do I rotate a key without downtime"
    expect_articles: [rotating-api-keys, api-key-lifecycle]

  - query: "401 unauthorized gateway"
    expect_article: troubleshooting-401s
```

Rules that keep the set honest:

- **Use real phrasings.** Pull them from tickets, search logs, and Slack
  questions. A query you invented tests your own vocabulary, which the article
  already matches — it will pass and prove nothing.
- **Include the wrong words readers use.** If people say "password" when they
  mean "API key", that is a case. Making it pass usually means adding their word
  to the article, which is the correct fix.
- **One claim per case.** `expect_articles` (plural) is for when two pages are
  both legitimately correct, not for hedging.
- **Add a case with every new article**, in the same PR. An article nobody can
  find is not published, whatever its status field says.
- **Add a case whenever someone says "I couldn't find X".** That is a free,
  real-world failing test. Add it failing, then fix the article.

## Running

```bash
python3 scripts/run_evals.py                  # summary
python3 scripts/run_evals.py --k 5 --verbose  # every query and its rank
python3 scripts/run_evals.py --min-recall 0.8 # CI gate
```

Output is `recall@k` (did the right article appear in the top k) and `MRR`
(how high). Falling MRR with steady recall means the right answer is being
crowded out — usually by a near-duplicate page.

## When a case fails

Fix it in this order. Stop at the first one that applies.

1. **The expectation is wrong.** The article the query should find is a
   different one, or does not exist yet. Fix the case, or write the article.
2. **The article does not use the reader's words.** The usual cause. Add the
   phrasing where it belongs — the `summary`, an H2 heading, or the first
   paragraph. If it genuinely does not belong in the prose, add a
   `keywords:` list to front matter.
3. **The article is too broad.** One page covering five topics dilutes every
   term in it. Split it; the sub-articles will each rank better than the parent.
4. **A near-duplicate is outranking it.** Two pages answering one question.
   Merge them and archive the loser with `superseded_by`.

Only after all four: consider whether the chunking is wrong — see the
`chunking` skill.

## Do not

- Do not delete or loosen a failing case to get green. A failing eval is a
  reader who cannot find the answer; deleting it does not help them.
- Do not tune `--k` upward to pass. If the answer is not in the top 5, readers
  are not seeing it.
