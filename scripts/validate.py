#!/usr/bin/env python3
"""Validate every article in content/ against the taxonomy and conventions.

Usage:
    python3 scripts/validate.py                 # validate the whole KB
    python3 scripts/validate.py content/guides  # validate a subtree or file
    python3 scripts/validate.py --strict        # treat warnings as failures
    python3 scripts/validate.py --today 2026-01-01   # pin "now" for tests

Exit status is 1 if there are errors (or warnings under --strict), else 0.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from kblib import (  # noqa: E402
    CONTENT_DIR,
    KNOWN_FIELDS,
    REPO_ROOT,
    REQUIRED_FIELDS,
    Article,
    KBError,
    Report,
    Taxonomy,
    as_date,
    is_slug,
    load_taxonomy,
    parse_article,
    iter_article_paths,
)

MAX_SUMMARY_WORDS = 40
MIN_SUMMARY_WORDS = 5
STALE_WARN_DAYS = 30

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check_front_matter(article: Article, tax: Taxonomy, report: Report) -> None:
    rel = article.rel_path
    if article.front_matter_error:
        report.error(rel, article.front_matter_error)
        return

    meta = article.meta

    for key in REQUIRED_FIELDS:
        if key not in meta or meta[key] in (None, "", [], {}):
            report.error(rel, f"missing required front-matter field: {key}")

    for key in meta:
        if key not in KNOWN_FIELDS:
            report.warn(
                rel,
                f"unknown front-matter field {key!r} "
                f"(add it to kblib.OPTIONAL_FIELDS if it is real)",
            )

    # id must be a slug and must match the filename, so links stay predictable.
    if "id" in meta:
        if not is_slug(meta["id"]):
            report.error(rel, f"id {meta['id']!r} must be a lowercase-hyphen slug")
        elif meta["id"] != article.path.stem:
            report.error(
                rel, f"id {meta['id']!r} does not match filename {article.path.stem!r}"
            )
    if not is_slug(article.path.stem):
        report.error(rel, f"filename {article.path.name!r} must be a lowercase-hyphen slug")

    # category must agree with the directory, or the KB stops being navigable.
    category = meta.get("category")
    if category is not None:
        if category not in tax.categories:
            report.error(
                rel,
                f"unknown category {category!r} (known: {', '.join(sorted(tax.categories))})",
            )
        elif category != article.dir_category:
            report.error(
                rel,
                f"category {category!r} but file lives in content/{article.dir_category}/",
            )

    status = meta.get("status")
    if status is not None and status not in tax.statuses:
        report.error(
            rel, f"unknown status {status!r} (known: {', '.join(sorted(tax.statuses))})"
        )

    for field_name, vocab in (("tags", tax.tags), ("audiences", tax.audiences)):
        value = meta.get(field_name)
        if value is None:
            continue
        if not isinstance(value, list):
            report.error(rel, f"{field_name} must be a list")
            continue
        if not value:
            report.error(rel, f"{field_name} must not be empty")
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                report.error(rel, f"{field_name} entry {item!r} must be a string")
                continue
            if item in seen:
                report.warn(rel, f"duplicate {field_name} entry {item!r}")
            seen.add(item)
            if item not in vocab:
                report.error(
                    rel,
                    f"unknown {field_name[:-1]} {item!r} "
                    f"-- add it to taxonomy/{field_name}.yml in this commit, or fix the typo",
                )

    if isinstance(meta.get("tags"), list) and len(meta["tags"]) > 6:
        report.warn(
            rel,
            f"{len(meta['tags'])} tags -- more than ~6 usually means the article "
            "covers too much and should be split",
        )

    summary = meta.get("summary")
    if isinstance(summary, str):
        words = len(summary.split())
        if words > MAX_SUMMARY_WORDS:
            report.warn(
                rel,
                f"summary is {words} words; keep it under {MAX_SUMMARY_WORDS} "
                "-- it is the retrieval snippet, not an intro paragraph",
            )
        elif words < MIN_SUMMARY_WORDS:
            report.warn(rel, f"summary is only {words} words; say what the reader gets")
        if summary.strip().startswith(("This article", "This page", "This doc")):
            report.warn(
                rel,
                "summary starts with 'This article...' -- state the subject directly "
                "so the snippet carries meaning on its own",
            )
    elif summary is not None:
        report.error(rel, "summary must be a string")

    if "owner" in meta and not isinstance(meta["owner"], str):
        report.error(rel, "owner must be a string (a person or team who answers for this page)")


def check_dates(article: Article, today: _dt.date, report: Report) -> None:
    rel = article.rel_path
    meta = article.meta
    parsed: dict[str, _dt.date] = {}

    for key in ("created", "updated", "review_after"):
        raw = meta.get(key)
        if raw is None:
            continue
        value = as_date(raw)
        if value is None:
            report.error(rel, f"{key} {raw!r} is not an ISO date (YYYY-MM-DD)")
        else:
            parsed[key] = value

    if "created" in parsed and "updated" in parsed and parsed["updated"] < parsed["created"]:
        report.error(rel, "updated is earlier than created")
    if "updated" in parsed and parsed["updated"] > today:
        report.error(rel, f"updated {parsed['updated']} is in the future")
    if "review_after" in parsed and "updated" in parsed:
        if parsed["review_after"] <= parsed["updated"]:
            report.error(rel, "review_after must be after updated")

    status = meta.get("status")
    review_after = parsed.get("review_after")
    if review_after and status in {"published", "review"}:
        if review_after < today:
            report.warn(
                rel,
                f"review_after {review_after} has passed -- re-verify the content, then "
                "either push the date out or set status: stale",
            )
        elif (review_after - today).days <= STALE_WARN_DAYS:
            report.warn(rel, f"review due in {(review_after - today).days} days ({review_after})")

    if status == "archived" and not meta.get("superseded_by"):
        report.warn(
            rel,
            "archived without superseded_by -- point readers at the replacement, "
            "or say explicitly that there is none",
        )


def check_body(article: Article, report: Report) -> None:
    rel = article.rel_path
    body = article.body

    if not body.strip():
        report.error(rel, "article has no body")
        return

    headings = article.headings
    h1s = [h for h in headings if h[0] == 1]
    if h1s:
        report.error(
            rel,
            f"body contains an H1 ({h1s[0][1]!r}); the title comes from front matter, "
            "so body headings start at H2",
        )

    levels = [lvl for lvl, _ in headings]
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            report.warn(rel, f"heading level jumps from H{prev} to H{cur}")

    if article.word_count < 25 and article.meta.get("status") == "published":
        report.warn(rel, f"only {article.word_count} words but marked published")

    for placeholder in ("TODO", "TKTK", "FIXME", "Lorem ipsum", "<!-- fill "):
        if placeholder.lower() in body.lower() and article.meta.get("status") == "published":
            report.error(rel, f"published article still contains a {placeholder!r} placeholder")

    if body.count("```") % 2 != 0:
        report.error(rel, "unbalanced code fence (odd number of ``` markers)")

    if article.meta.get("category") == "runbooks":
        required = {"symptoms", "diagnosis", "remediation", "escalation"}
        present = {h.strip().lower() for _, h in headings}
        missing = sorted(required - present)
        if missing:
            report.warn(
                rel,
                "runbook is missing section(s): " + ", ".join(missing)
                + " -- see templates/runbook.md",
            )


def check_links(article: Article, known_ids: dict[str, str], report: Report) -> None:
    rel = article.rel_path
    for match in LINK_RE.finditer(article.body):
        target = match.group(1)
        line = article.body[: match.start()].count("\n") + 1

        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue

        path_part = target.split("#", 1)[0]
        if not path_part:
            continue

        resolved = (article.path.parent / path_part).resolve()
        if not resolved.exists():
            report.error(rel, f"broken relative link: {target}", line=line)
        elif resolved.suffix == ".md":
            try:
                rel_to_content = resolved.relative_to(CONTENT_DIR)
            except ValueError:
                continue
            if resolved.stem not in known_ids:
                report.warn(rel, f"link points at an unindexed file: {rel_to_content}", line=line)

    for ref in article.meta.get("related", []) or []:
        if isinstance(ref, str) and ref not in known_ids:
            report.error(rel, f"related: {ref!r} is not an article id in this KB")

    superseded = article.meta.get("superseded_by")
    if isinstance(superseded, str) and superseded not in known_ids:
        report.error(rel, f"superseded_by: {superseded!r} is not an article id in this KB")


def check_collection(articles: list[Article], report: Report) -> dict[str, str]:
    """Cross-article checks. Returns the id -> path map."""
    known: dict[str, str] = {}
    for article in articles:
        if article.front_matter_error:
            continue
        aid = article.id
        if aid in known:
            report.error(article.rel_path, f"duplicate article id {aid!r} (also in {known[aid]})")
        else:
            known[aid] = article.rel_path

    titles: dict[str, str] = {}
    for article in articles:
        title = article.meta.get("title")
        if not isinstance(title, str):
            continue
        key = title.strip().lower()
        if key in titles:
            report.warn(
                article.rel_path,
                f"title {title!r} duplicates {titles[key]} -- two pages answering the "
                "same question is how a KB starts contradicting itself",
            )
        else:
            titles[key] = article.rel_path
    return known


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", type=pathlib.Path,
                        help="files or directories to validate (default: all of content/)")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    parser.add_argument("--today", type=_dt.date.fromisoformat, default=_dt.date.today(),
                        help="override today's date (YYYY-MM-DD), for reproducible test runs")
    parser.add_argument("--quiet", action="store_true", help="only print the summary line")
    args = parser.parse_args(argv)

    try:
        tax = load_taxonomy()
    except KBError as exc:
        print(f"ERROR   taxonomy: {exc}", file=sys.stderr)
        return 2

    # Directories declared in the taxonomy must actually exist.
    report = Report()
    for cid, entry in tax.categories.items():
        directory = REPO_ROOT / entry.get("directory", f"content/{cid}")
        if not directory.is_dir():
            report.error("taxonomy/categories.yml", f"category {cid!r} declares missing directory {directory}")

    # The whole KB is always loaded so cross-references resolve, even when the
    # caller asked about a single file.
    all_articles = [parse_article(p) for p in iter_article_paths()]
    known_ids = check_collection(all_articles, Report() if args.paths else report)

    if args.paths:
        selected: list[Article] = []
        for target in args.paths:
            target = target.resolve()
            if target.is_file():
                selected.append(parse_article(target))
            else:
                selected.extend(parse_article(p) for p in iter_article_paths(target))
    else:
        selected = all_articles

    for article in selected:
        check_front_matter(article, tax, report)
        if not article.front_matter_error:
            check_dates(article, args.today, report)
            check_body(article, report)
            check_links(article, known_ids, report)

    if not args.quiet:
        for finding in sorted(report.findings, key=lambda f: (f.path, f.line or 0, f.level)):
            print(finding.format())

    n_err, n_warn = len(report.errors), len(report.warnings)
    print(f"\nChecked {len(selected)} article(s): {n_err} error(s), {n_warn} warning(s).")

    if n_err:
        return 1
    if args.strict and n_warn:
        print("--strict: failing because of warnings.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
