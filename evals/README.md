# Retrieval evals

Each case is a claim: *someone asking this, in these words, should land on that
article.* `scripts/run_evals.py` scores the knowledge base against those claims
with a BM25 lexical baseline.

The baseline is deliberately not the production retriever. It has no embeddings
to paper over a vocabulary gap, so it fails loudly when an article never uses
the words its readers use — which is a content bug, not a ranking bug.

```bash
python3 scripts/run_evals.py                  # summary
python3 scripts/run_evals.py --k 5 --verbose  # every query and its rank
python3 scripts/run_evals.py --min-recall 0.8 # CI gate
```

Add a case for every new article, and add one whenever somebody says "I couldn't
find X" — that is a free, real-world failing test.

Never delete or loosen a failing case to get green. Full guidance:
`.claude/skills/retrieval-eval/SKILL.md`.
