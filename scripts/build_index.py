#!/usr/bin/env python3
"""Export the knowledge base as retrieval-ready chunks (JSONL).

Only articles whose status is marked `indexed: true` in taxonomy/statuses.yml
are exported -- drafts must never reach a retrieval index.

Chunking is heading-aware: each H2 section becomes a chunk, and oversized
sections are split on paragraph boundaries. Every chunk carries the article's
title and summary as a prefix so an embedding of the chunk still knows what
document it came from.

Usage:
    python3 scripts/build_index.py                     # write dist/index.jsonl
    python3 scripts/build_index.py --out -              # write to stdout
    python3 scripts/build_index.py --max-words 250 --overlap-words 40
    python3 scripts/build_index.py --stats              # summarise, don't write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from kblib import REPO_ROOT, Article, as_date, load_articles, load_taxonomy  # noqa: E402

DEFAULT_MAX_WORDS = 350
DEFAULT_OVERLAP_WORDS = 50


def split_sections(article: Article) -> list[tuple[str, str]]:
    """Split a body into (heading, text) pairs on H2 boundaries."""
    sections: list[tuple[str, list[str]]] = []
    current_heading = ""
    current: list[str] = []
    in_fence = False

    for line in article.body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue
        if not in_fence and re.match(r"^##\s+\S", line):
            if current_heading or any(l.strip() for l in current):
                sections.append((current_heading, current))
            current_heading = line.lstrip("#").strip()
            current = []
            continue
        current.append(line)

    if current_heading or any(l.strip() for l in current):
        sections.append((current_heading, current))

    return [(h, "\n".join(lines).strip()) for h, lines in sections if "\n".join(lines).strip()]


def split_long(text: str, max_words: int, overlap_words: int) -> list[str]:
    """Split an oversized section on paragraph boundaries, with word overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    buf_words = 0

    for para in paragraphs:
        para_words = len(para.split())
        if buf and buf_words + para_words > max_words:
            chunks.append("\n\n".join(buf))
            if overlap_words > 0:
                tail = " ".join("\n\n".join(buf).split()[-overlap_words:])
                buf, buf_words = ([tail] if tail else []), len(tail.split())
            else:
                buf, buf_words = [], 0
        buf.append(para)
        buf_words += para_words

    if buf:
        chunks.append("\n\n".join(buf))
    return chunks or [text]


def chunk_article(article: Article, max_words: int, overlap_words: int) -> list[dict]:
    meta = article.meta
    header = f"{meta.get('title', article.id)} -- {meta.get('summary', '')}".strip(" -")
    chunks: list[dict] = []

    for heading, text in split_sections(article):
        for part in split_long(text, max_words, overlap_words):
            body = f"## {heading}\n\n{part}" if heading else part
            content = f"{header}\n\n{body}"
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
            chunks.append({
                "chunk_id": f"{article.id}#{len(chunks):03d}",
                "content_hash": digest,
                "article_id": article.id,
                "title": meta.get("title"),
                "summary": meta.get("summary"),
                "section": heading or None,
                "category": meta.get("category"),
                "tags": meta.get("tags", []),
                "audiences": meta.get("audiences", []),
                "status": meta.get("status"),
                "owner": meta.get("owner"),
                "updated": str(as_date(meta.get("updated")) or ""),
                "review_after": str(as_date(meta.get("review_after")) or ""),
                "stale": meta.get("status") == "stale",
                "source_path": article.rel_path,
                "word_count": len(part.split()),
                "text": content,
            })
    return chunks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(REPO_ROOT / "dist" / "index.jsonl"),
                        help="output path, or '-' for stdout")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    parser.add_argument("--overlap-words", type=int, default=DEFAULT_OVERLAP_WORDS)
    parser.add_argument("--stats", action="store_true", help="print a summary instead of writing")
    args = parser.parse_args(argv)

    tax = load_taxonomy()
    indexed = tax.indexed_statuses
    articles = [a for a in load_articles() if not a.front_matter_error]
    exported = [a for a in articles if a.meta.get("status") in indexed]
    skipped = len(articles) - len(exported)

    chunks: list[dict] = []
    for article in exported:
        chunks.extend(chunk_article(article, args.max_words, args.overlap_words))

    if args.stats:
        by_cat: dict[str, int] = {}
        for c in chunks:
            by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
        words = [c["word_count"] for c in chunks] or [0]
        print(f"articles exported : {len(exported)} ({skipped} skipped as unindexed)")
        print(f"chunks            : {len(chunks)}")
        print(f"words per chunk   : min {min(words)}, median {sorted(words)[len(words)//2]}, max {max(words)}")
        print(f"stale chunks      : {sum(1 for c in chunks if c['stale'])}")
        for cat, n in sorted(by_cat.items()):
            print(f"  {cat:12} {n}")
        return 0

    payload = "\n".join(json.dumps(c, ensure_ascii=False) for c in chunks)
    if args.out == "-":
        print(payload)
    else:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")
        print(f"Wrote {len(chunks)} chunk(s) from {len(exported)} article(s) to {out_path}")
        if skipped:
            print(f"Skipped {skipped} article(s) whose status is not indexed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
