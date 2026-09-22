#!/usr/bin/env python3
"""Score the knowledge base against the retrieval eval set.

This runs a BM25 lexical baseline over the chunks that build_index.py produces.
It is deliberately NOT the production retriever: its job is to catch content
problems -- an article nobody can find because it never uses the words readers
use -- before they reach a real index. A query that fails here is usually a
wording problem in the article, not a ranking problem in the retriever.

Usage:
    python3 scripts/run_evals.py                  # score every eval file
    python3 scripts/run_evals.py --k 5 --verbose  # show per-query results
    python3 scripts/run_evals.py --min-recall 0.8 # fail below a threshold
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys
from collections import Counter

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from build_index import chunk_article  # noqa: E402
from kblib import REPO_ROOT, load_articles, load_taxonomy  # noqa: E402

EVAL_DIR = REPO_ROOT / "evals" / "queries"
TOKEN_RE = re.compile(r"[a-z0-9]+")

K1, B = 1.5, 0.75

STOPWORDS = frozenset("""
a an and are as at be but by can do does for from how i if in into is it its
me my of on or our so than that the their them then there these they this to
was we what when where which who why will with you your
""".split())


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 1]


class BM25:
    def __init__(self, docs: list[list[str]]):
        self.docs = docs
        self.lengths = [len(d) for d in docs]
        self.avg_len = (sum(self.lengths) / len(docs)) if docs else 0.0
        self.freqs = [Counter(d) for d in docs]
        df = Counter()
        for d in docs:
            df.update(set(d))
        n = len(docs)
        self.idf = {
            term: math.log(1 + (n - count + 0.5) / (count + 0.5))
            for term, count in df.items()
        }

    def score(self, query: list[str], index: int) -> float:
        freq = self.freqs[index]
        length = self.lengths[index] or 1
        total = 0.0
        for term in query:
            if term not in freq:
                continue
            tf = freq[term]
            denom = tf + K1 * (1 - B + B * length / (self.avg_len or 1))
            total += self.idf.get(term, 0.0) * (tf * (K1 + 1)) / denom
        return total

    def rank(self, query: list[str]) -> list[tuple[int, float]]:
        scored = [(i, self.score(query, i)) for i in range(len(self.docs))]
        scored = [(i, s) for i, s in scored if s > 0]
        return sorted(scored, key=lambda x: -x[1])


def load_eval_cases() -> list[dict]:
    cases: list[dict] = []
    if not EVAL_DIR.exists():
        return cases
    for path in sorted(EVAL_DIR.glob("*.yml")) + sorted(EVAL_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for case in data.get("cases", []):
            case.setdefault("file", path.name)
            cases.append(case)
    return cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--k", type=int, default=5, help="rank cutoff for recall@k (default 5)")
    parser.add_argument("--verbose", action="store_true", help="print every query, not just failures")
    parser.add_argument("--min-recall", type=float, default=None,
                        help="exit non-zero if recall@k falls below this (0-1)")
    args = parser.parse_args(argv)

    cases = load_eval_cases()
    if not cases:
        print(f"No eval cases found in {EVAL_DIR.relative_to(REPO_ROOT)}/. "
              "Add a .yml file with a top-level 'cases:' list.")
        return 0

    tax = load_taxonomy()
    indexed = tax.indexed_statuses
    articles = [a for a in load_articles()
                if not a.front_matter_error and a.meta.get("status") in indexed]
    if not articles:
        print("No indexed articles to search. Publish something first.")
        return 0

    chunks: list[dict] = []
    for article in articles:
        chunks.extend(chunk_article(article, max_words=350, overlap_words=50))

    bm25 = BM25([tokenize(c["text"]) for c in chunks])

    hits = 0
    reciprocal_total = 0.0
    failures: list[str] = []

    for case in cases:
        query = case.get("query", "")
        expected = case.get("expect_articles") or ([case["expect_article"]] if "expect_article" in case else [])
        expected_set = set(expected)
        ranked = bm25.rank(tokenize(query))

        seen_articles: list[str] = []
        for idx, _score in ranked:
            aid = chunks[idx]["article_id"]
            if aid not in seen_articles:
                seen_articles.append(aid)
            if len(seen_articles) >= args.k:
                break

        top_k = seen_articles[: args.k]
        matched = expected_set & set(top_k)
        rank_of_first = next((i + 1 for i, a in enumerate(top_k) if a in expected_set), None)

        if matched:
            hits += 1
            reciprocal_total += 1 / rank_of_first if rank_of_first else 0.0
            if args.verbose:
                print(f"PASS  [{rank_of_first}] {query!r} -> {', '.join(sorted(matched))}")
        else:
            got = ", ".join(top_k) or "(nothing matched)"
            line = f"FAIL  {query!r}\n        expected: {', '.join(sorted(expected_set)) or '(none declared)'}\n        got:      {got}"
            failures.append(line)
            print(line)

    total = len(cases)
    recall = hits / total if total else 0.0
    mrr = reciprocal_total / total if total else 0.0
    print(f"\n{total} quer(ies): recall@{args.k} = {recall:.2f} ({hits}/{total}), MRR = {mrr:.2f}")

    if failures:
        print("\nA failure usually means the article does not use the reader's words. "
              "Fix it in the article (summary, headings, a 'keywords' field) before "
              "touching retrieval settings.")

    if args.min_recall is not None and recall < args.min_recall:
        print(f"recall@{args.k} {recall:.2f} is below --min-recall {args.min_recall:.2f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
