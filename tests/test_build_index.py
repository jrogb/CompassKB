"""Tests for scripts/build_index.py and scripts/run_evals.py."""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import build_index as B  # noqa: E402
import run_evals as E  # noqa: E402
from kblib import load_articles, load_taxonomy  # noqa: E402


# --- section splitting -------------------------------------------------------

def test_splits_on_h2_headings(make_article):
    body = "Intro line.\n\n## First\n\nAlpha.\n\n## Second\n\nBeta.\n"
    sections = B.split_sections(make_article(body=body))
    assert [h for h, _ in sections] == ["", "First", "Second"]
    assert "Alpha." in sections[1][1]


def test_h3_does_not_start_a_new_chunk(make_article):
    body = "## First\n\nAlpha.\n\n### Sub\n\nBeta.\n"
    sections = B.split_sections(make_article(body=body))
    assert len(sections) == 1
    assert "Beta." in sections[0][1]


def test_headings_inside_code_fences_are_ignored(make_article):
    body = "## First\n\n```markdown\n## not a heading\n```\n\nAlpha.\n"
    sections = B.split_sections(make_article(body=body))
    assert [h for h, _ in sections] == ["First"]


# --- long-section splitting --------------------------------------------------

def test_long_sections_split_on_paragraph_boundaries():
    paragraph = " ".join(["word"] * 100)
    chunks = B.split_long("\n\n".join([paragraph] * 5), max_words=150, overlap_words=0)
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_overlap_carries_words_across_the_seam():
    paragraph = " ".join(f"w{i}" for i in range(100))
    chunks = B.split_long("\n\n".join([paragraph] * 3), max_words=120, overlap_words=10)
    assert len(chunks) > 1
    tail = chunks[0].split()[-10:]
    assert chunks[1].split()[:10] == tail


def test_short_text_is_a_single_chunk():
    assert B.split_long("just a few words", max_words=350, overlap_words=50) == ["just a few words"]


# --- chunk payload -----------------------------------------------------------

def test_every_chunk_is_prefixed_with_title_and_summary(make_article):
    article = make_article(body="## First\n\nAlpha.\n\n## Second\n\nBeta.\n")
    chunks = B.chunk_article(article, max_words=350, overlap_words=50)
    assert len(chunks) == 2
    for chunk in chunks:
        assert chunk["text"].startswith("Example --")
        assert article.meta["summary"] in chunk["text"]


def test_chunk_carries_filter_metadata(make_article):
    chunk = B.chunk_article(make_article(), max_words=350, overlap_words=50)[0]
    assert chunk["article_id"] == "example"
    assert chunk["category"] == "guides"
    assert chunk["tags"] == ["getting-started"]
    assert chunk["status"] == "published"
    assert chunk["stale"] is False
    assert len(chunk["content_hash"]) == 16


def test_chunk_ids_are_unique_within_an_article(make_article):
    article = make_article(body="## A\n\nOne.\n\n## B\n\nTwo.\n\n## C\n\nThree.\n")
    ids = [c["chunk_id"] for c in B.chunk_article(article, 350, 50)]
    assert ids == sorted(set(ids)) and len(ids) == 3


def test_title_change_rehashes_every_chunk(make_article):
    """The title is part of the embedded text, so editing it invalidates the article."""
    body = "## A\n\nOne.\n\n## B\n\nTwo.\n"
    before = B.chunk_article(make_article(body=body), 350, 50)
    after = B.chunk_article(
        make_article(slug="example", overrides={"title": "Renamed"}, body=body), 350, 50)
    assert [c["content_hash"] for c in before] != [c["content_hash"] for c in after]


def test_stale_articles_are_flagged_not_dropped(make_article):
    chunk = B.chunk_article(make_article(overrides={"status": "stale"}), 350, 50)[0]
    assert chunk["stale"] is True


# --- the real export ---------------------------------------------------------

def test_only_indexed_statuses_are_exported(tmp_path):
    out = tmp_path / "index.jsonl"
    assert B.main(["--out", str(out)]) == 0
    chunks = [json.loads(line) for line in out.read_text().splitlines()]
    indexed = load_taxonomy().indexed_statuses
    assert chunks, "the seed content should produce chunks"
    assert {c["status"] for c in chunks} <= indexed


def test_export_covers_every_published_article(tmp_path):
    out = tmp_path / "index.jsonl"
    B.main(["--out", str(out)])
    exported = {json.loads(line)["article_id"] for line in out.read_text().splitlines()}
    expected = {a.id for a in load_articles()
                if not a.front_matter_error
                and a.meta.get("status") in load_taxonomy().indexed_statuses}
    assert exported == expected


# --- eval runner -------------------------------------------------------------

def test_tokenize_drops_stopwords_and_punctuation():
    assert E.tokenize("How do I rotate the API key?") == ["rotate", "api", "key"]


def test_bm25_ranks_the_matching_document_first():
    docs = [E.tokenize(t) for t in (
        "rotating api keys without downtime overlap",
        "billing invoices and payment methods",
        "glossary of terms",
    )]
    ranked = E.BM25(docs).rank(E.tokenize("how do I rotate api keys"))
    assert ranked and ranked[0][0] == 0


def test_bm25_returns_nothing_for_an_unrelated_query():
    docs = [E.tokenize("billing invoices and payment methods")]
    assert E.BM25(docs).rank(E.tokenize("kubernetes scheduler")) == []


def test_committed_eval_cases_are_wellformed():
    cases = E.load_eval_cases()
    assert cases, "evals/queries/ should contain cases"
    known = {a.id for a in load_articles() if not a.front_matter_error}
    for case in cases:
        assert case.get("query"), f"case without a query in {case['file']}"
        expected = case.get("expect_articles") or ([case["expect_article"]]
                                                   if "expect_article" in case else [])
        assert expected, f"case {case['query']!r} declares no expected article"
        for article_id in expected:
            assert article_id in known, \
                f"case {case['query']!r} expects unknown article {article_id!r}"


def test_the_committed_eval_set_passes():
    assert E.main(["--k", "5", "--min-recall", "1.0"]) == 0
