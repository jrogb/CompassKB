"""Shared loading and parsing for CompassKB tooling.

Everything that needs to read the knowledge base -- the validator, the index
builder, the eval runner -- goes through here so they cannot disagree about
what a valid article is.
"""

from __future__ import annotations

import datetime as _dt
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
TAXONOMY_DIR = REPO_ROOT / "taxonomy"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)

REQUIRED_FIELDS = (
    "id",
    "title",
    "category",
    "status",
    "audiences",
    "tags",
    "owner",
    "created",
    "updated",
    "review_after",
    "summary",
)

OPTIONAL_FIELDS = (
    "sources",
    "related",
    "superseded_by",
    "keywords",
)

KNOWN_FIELDS = frozenset(REQUIRED_FIELDS + OPTIONAL_FIELDS)


class KBError(Exception):
    """Raised when the knowledge base is structurally unreadable."""


@dataclass
class Taxonomy:
    categories: dict[str, dict[str, Any]]
    tags: dict[str, dict[str, Any]]
    audiences: dict[str, dict[str, Any]]
    statuses: dict[str, dict[str, Any]]

    @property
    def indexed_statuses(self) -> set[str]:
        return {k for k, v in self.statuses.items() if v.get("indexed")}


@dataclass
class Article:
    path: pathlib.Path
    meta: dict[str, Any]
    body: str
    front_matter_error: str | None = None

    @property
    def rel_path(self) -> str:
        try:
            return self.path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            # Articles loaded from outside the repo (tests, ad-hoc checks).
            return self.path.as_posix()

    @property
    def id(self) -> str:
        value = self.meta.get("id")
        return value if isinstance(value, str) else self.path.stem

    @property
    def dir_category(self) -> str:
        """The category implied by where the file sits on disk."""
        try:
            return self.path.relative_to(CONTENT_DIR).parts[0]
        except ValueError:
            return self.path.parent.name

    @property
    def headings(self) -> list[tuple[int, str]]:
        out: list[tuple[int, str]] = []
        in_fence = False
        for line in self.body.splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
            if m:
                out.append((len(m.group(1)), m.group(2)))
        return out

    @property
    def word_count(self) -> int:
        stripped = re.sub(r"```.*?```", " ", self.body, flags=re.DOTALL)
        return len(stripped.split())


def _load_taxonomy_file(name: str, key: str) -> dict[str, dict[str, Any]]:
    path = TAXONOMY_DIR / name
    if not path.exists():
        raise KBError(f"missing taxonomy file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get(key)
    if not isinstance(entries, list):
        raise KBError(f"{path} must contain a top-level list under '{key}'")
    out: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry:
            raise KBError(f"{path}: every entry needs an 'id' (got {entry!r})")
        if entry["id"] in out:
            raise KBError(f"{path}: duplicate id {entry['id']!r}")
        out[entry["id"]] = entry
    return out


def load_taxonomy() -> Taxonomy:
    return Taxonomy(
        categories=_load_taxonomy_file("categories.yml", "categories"),
        tags=_load_taxonomy_file("tags.yml", "tags"),
        audiences=_load_taxonomy_file("audiences.yml", "audiences"),
        statuses=_load_taxonomy_file("statuses.yml", "statuses"),
    )


def parse_article(path: pathlib.Path) -> Article:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return Article(
            path=path,
            meta={},
            body=text,
            front_matter_error="no YAML front matter (file must open with a '---' line)",
        )
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return Article(
            path=path, meta={}, body=match.group(2),
            front_matter_error=f"front matter is not valid YAML: {exc}",
        )
    if not isinstance(meta, dict):
        return Article(
            path=path, meta={}, body=match.group(2),
            front_matter_error="front matter must be a mapping of fields",
        )
    return Article(path=path, meta=meta, body=match.group(2))


def iter_article_paths(root: pathlib.Path | None = None) -> list[pathlib.Path]:
    base = root or CONTENT_DIR
    if not base.exists():
        return []
    return sorted(p for p in base.rglob("*.md") if not p.name.startswith("_"))


def load_articles(root: pathlib.Path | None = None) -> list[Article]:
    return [parse_article(p) for p in iter_article_paths(root)]


def as_date(value: Any) -> _dt.date | None:
    """Coerce a front-matter date value, which PyYAML may already have typed."""
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def is_slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG_RE.match(value))


@dataclass
class Finding:
    path: str
    message: str
    level: str = "error"
    line: int | None = None

    def format(self) -> str:
        where = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"{self.level.upper():7} {where}: {self.message}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def error(self, path: str, message: str, line: int | None = None) -> None:
        self.findings.append(Finding(path, message, "error", line))

    def warn(self, path: str, message: str, line: int | None = None) -> None:
        self.findings.append(Finding(path, message, "warning", line))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warning"]
