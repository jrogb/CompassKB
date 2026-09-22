#!/usr/bin/env python3
"""Create a new article from a template with valid front matter already filled in.

Usage:
    python3 scripts/new_article.py guides rotating-api-keys \
        --title "Rotating API keys" \
        --audiences engineer,operator \
        --tags authentication,security \
        --owner "platform-team" \
        --summary "Rotate a live API key without dropping requests."

Defaults: status draft, created/updated today, review_after in 180 days.
Prints the path it wrote. Refuses to overwrite an existing file.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from kblib import CONTENT_DIR, REPO_ROOT, is_slug, load_taxonomy  # noqa: E402

DEFAULT_REVIEW_DAYS = 180
TEMPLATES = REPO_ROOT / "templates"

TEMPLATE_FOR_CATEGORY = {
    "runbooks": "runbook.md",
    "faq": "faq.md",
    "reference": "reference.md",
}


def csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    tax = load_taxonomy()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("category", choices=sorted(tax.categories))
    parser.add_argument("slug", help="lowercase-hyphen id; becomes the filename")
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", default="", help="one sentence; this is the retrieval snippet")
    parser.add_argument("--audiences", type=csv_list, default=["engineer"])
    parser.add_argument("--tags", type=csv_list, default=[])
    parser.add_argument("--owner", default="unassigned")
    parser.add_argument("--review-days", type=int, default=DEFAULT_REVIEW_DAYS)
    parser.add_argument("--today", type=_dt.date.fromisoformat, default=_dt.date.today())
    args = parser.parse_args(argv)

    if not is_slug(args.slug):
        parser.error(f"slug {args.slug!r} must be lowercase letters, digits and hyphens")

    unknown_aud = [a for a in args.audiences if a not in tax.audiences]
    unknown_tags = [t for t in args.tags if t not in tax.tags]
    if unknown_aud:
        parser.error(f"unknown audience(s): {', '.join(unknown_aud)} "
                     f"(known: {', '.join(sorted(tax.audiences))})")
    if unknown_tags:
        parser.error(f"unknown tag(s): {', '.join(unknown_tags)} -- add them to "
                     f"taxonomy/tags.yml in this commit, or pick from: "
                     f"{', '.join(sorted(tax.tags))}")

    target = CONTENT_DIR / args.category / f"{args.slug}.md"
    if target.exists():
        print(f"refusing to overwrite existing article: {target}", file=sys.stderr)
        return 1

    template_name = TEMPLATE_FOR_CATEGORY.get(args.category, "article.md")
    template_path = TEMPLATES / template_name
    if not template_path.exists():
        template_path = TEMPLATES / "article.md"

    body = template_path.read_text(encoding="utf-8")
    if body.startswith("---"):
        # Templates carry example front matter; drop it and write a real one.
        body = body.split("\n---\n", 2)[-1]

    created = args.today
    review_after = created + _dt.timedelta(days=args.review_days)

    def yaml_list(items: list[str]) -> str:
        return "[" + ", ".join(items) + "]" if items else "[]"

    front = "\n".join([
        "---",
        f"id: {args.slug}",
        f"title: {args.title!r}" if ":" in args.title else f"title: {args.title}",
        f"category: {args.category}",
        "status: draft",
        f"audiences: {yaml_list(args.audiences)}",
        f"tags: {yaml_list(args.tags)}",
        f"owner: {args.owner}",
        f"created: {created}",
        f"updated: {created}",
        f"review_after: {review_after}",
        f"summary: {args.summary or 'TODO: one sentence -- what does the reader get?'}",
        "---",
        "",
    ])

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(front + "\n" + body.lstrip("\n"), encoding="utf-8")
    print(target.relative_to(REPO_ROOT))
    print("\nNext: fill the body, then run `python3 scripts/validate.py`, "
          "then set status to review.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
