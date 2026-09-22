import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import kblib  # noqa: E402

VALID_FRONT_MATTER = {
    "id": "example",
    "title": "Example",
    "category": "guides",
    "status": "published",
    "audiences": ["engineer"],
    "tags": ["getting-started"],
    "owner": "kb-maintainers",
    "created": "2026-01-01",
    "updated": "2026-01-02",
    "review_after": "2026-07-01",
    "summary": "Example summary that says something true about the subject.",
}

VALID_BODY = """
Opening paragraph that states the answer directly.

## A section

Enough words in this section that the validator does not complain about an
article being too thin to have been published in the first place, which it
does below twenty five words or so.
"""


def render(meta: dict, body: str = VALID_BODY) -> str:
    """Render a front-matter dict plus body into article source text."""
    lines = ["---"]
    for key, value in meta.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(str(v) for v in value)}]")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


@pytest.fixture
def make_article(tmp_path, monkeypatch):
    """Write an article into a temporary content tree and parse it.

    The kblib path globals are redirected at the temp tree so Article.dir_category
    and relative-link resolution behave exactly as they do in the real repo.
    """
    content_dir = tmp_path / "content"
    monkeypatch.setattr(kblib, "CONTENT_DIR", content_dir)
    monkeypatch.setattr(kblib, "REPO_ROOT", tmp_path)

    import validate as validate_mod

    monkeypatch.setattr(validate_mod, "CONTENT_DIR", content_dir)

    def _make(category: str = "guides", slug: str = "example", *, meta=None, body=VALID_BODY,
              overrides=None, remove=()):
        merged = dict(VALID_FRONT_MATTER if meta is None else meta)
        merged.setdefault("id", slug)
        merged["id"] = merged.get("id", slug)
        merged["category"] = merged.get("category", category)
        for key in remove:
            merged.pop(key, None)
        if overrides:
            merged.update(overrides)
        path = content_dir / category / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(merged, body), encoding="utf-8")
        return kblib.parse_article(path)

    return _make
