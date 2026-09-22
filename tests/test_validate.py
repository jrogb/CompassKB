"""Tests for scripts/validate.py.

These pin the rules the skills and CLAUDE.md promise. If a rule genuinely needs
to change, change it here in the same commit so the change is deliberate.
"""

import datetime as dt
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import validate as V  # noqa: E402
from kblib import Report, load_taxonomy  # noqa: E402

TODAY = dt.date(2026, 6, 1)


@pytest.fixture(scope="module")
def tax():
    return load_taxonomy()


def messages(report):
    return " | ".join(f.message for f in report.findings)


def run_front_matter(article, tax):
    report = Report()
    V.check_front_matter(article, tax, report)
    return report


# --- the real repo -----------------------------------------------------------

def test_real_content_validates_strictly():
    """The committed knowledge base passes its own strict check."""
    assert V.main(["--strict", "--quiet", "--today", "2026-09-22"]) == 0


def test_taxonomy_loads(tax):
    assert set(tax.categories) == {"concepts", "guides", "reference", "runbooks", "faq"}
    assert tax.indexed_statuses == {"published", "stale"}


# --- front matter ------------------------------------------------------------

def test_valid_article_has_no_findings(make_article, tax):
    assert run_front_matter(make_article(), tax).findings == []


def test_missing_required_field_is_an_error(make_article, tax):
    report = run_front_matter(make_article(remove=["owner"]), tax)
    assert report.errors and "owner" in messages(report)


def test_id_must_match_filename(make_article, tax):
    report = run_front_matter(make_article(slug="example", overrides={"id": "different"}), tax)
    assert any("does not match filename" in f.message for f in report.errors)


def test_category_must_match_directory(make_article, tax):
    report = run_front_matter(make_article(category="guides", overrides={"category": "concepts"}), tax)
    assert any("file lives in content/guides/" in f.message for f in report.errors)


def test_unknown_tag_is_an_error(make_article, tax):
    report = run_front_matter(make_article(overrides={"tags": ["not-a-real-tag"]}), tax)
    assert any("unknown tag" in f.message for f in report.errors)


def test_unknown_audience_is_an_error(make_article, tax):
    report = run_front_matter(make_article(overrides={"audiences": ["martians"]}), tax)
    assert any("unknown audience" in f.message for f in report.errors)


def test_unknown_status_is_an_error(make_article, tax):
    report = run_front_matter(make_article(overrides={"status": "finished"}), tax)
    assert any("unknown status" in f.message for f in report.errors)


def test_unknown_field_warns_but_does_not_block(make_article, tax):
    report = run_front_matter(make_article(overrides={"colour": "blue"}), tax)
    assert not report.errors
    assert any("unknown front-matter field" in f.message for f in report.warnings)


def test_self_referential_summary_warns(make_article, tax):
    report = run_front_matter(
        make_article(overrides={"summary": "This article explains how the thing works."}), tax)
    assert any("This article" in f.message for f in report.warnings)


def test_malformed_front_matter_is_reported(tmp_path):
    from kblib import parse_article
    path = tmp_path / "broken.md"
    path.write_text("no front matter here\n", encoding="utf-8")
    assert "no YAML front matter" in parse_article(path).front_matter_error


# --- dates -------------------------------------------------------------------

def test_updated_before_created_is_an_error(make_article):
    report = Report()
    V.check_dates(make_article(overrides={"created": "2026-05-01", "updated": "2026-04-01"}),
                  TODAY, report)
    assert any("earlier than created" in f.message for f in report.errors)


def test_future_updated_is_an_error(make_article):
    report = Report()
    V.check_dates(make_article(overrides={"updated": "2027-01-01",
                                          "review_after": "2027-06-01"}), TODAY, report)
    assert any("in the future" in f.message for f in report.errors)


def test_passed_review_date_warns(make_article):
    report = Report()
    V.check_dates(make_article(overrides={"review_after": "2026-02-01"}), TODAY, report)
    assert not report.errors
    assert any("has passed" in f.message for f in report.warnings)


def test_archived_without_replacement_warns(make_article):
    report = Report()
    V.check_dates(make_article(overrides={"status": "archived"}), TODAY, report)
    assert any("superseded_by" in f.message for f in report.warnings)


def test_non_iso_date_is_an_error(make_article):
    report = Report()
    V.check_dates(make_article(overrides={"updated": "01/02/2026"}), TODAY, report)
    assert any("is not an ISO date" in f.message for f in report.errors)


# --- body --------------------------------------------------------------------

def test_h1_in_body_is_an_error(make_article):
    report = Report()
    V.check_body(make_article(body="# A title\n\nSome words here to pad it out.\n"), report)
    assert any("body contains an H1" in f.message for f in report.errors)


def test_placeholder_in_published_article_is_an_error(make_article):
    report = Report()
    V.check_body(make_article(body="## Section\n\nTODO: write this properly.\n"), report)
    assert any("placeholder" in f.message for f in report.errors)


def test_unbalanced_code_fence_is_an_error(make_article):
    body = "## Section\n\n```bash\necho hello\n\nMore prose that never closes the fence.\n"
    report = Report()
    V.check_body(make_article(body=body), report)
    assert any("unbalanced code fence" in f.message for f in report.errors)


def test_h1_inside_a_code_fence_is_ignored(make_article):
    body = "## Section\n\n```markdown\n# not a real heading\n```\n\nEnough trailing prose here.\n"
    report = Report()
    V.check_body(make_article(body=body), report)
    assert not report.errors


def test_runbook_missing_sections_warns(make_article):
    article = make_article(category="runbooks", slug="thing",
                           overrides={"category": "runbooks", "audiences": ["operator"],
                                      "tags": ["incident"]},
                           body="## Symptoms\n\nThe thing is broken and here is what you see.\n")
    report = Report()
    V.check_body(article, report)
    assert any("missing section" in f.message for f in report.warnings)


# --- links and cross-references ----------------------------------------------

def test_broken_relative_link_is_an_error(make_article):
    body = "## Section\n\nSee [the other page](../guides/nope.md) for detail here.\n"
    report = Report()
    V.check_links(make_article(body=body), {}, report)
    assert any("broken relative link" in f.message for f in report.errors)


def test_external_links_are_not_checked(make_article):
    body = "## Section\n\nSee [the vendor](https://example.com/docs) for detail here.\n"
    report = Report()
    V.check_links(make_article(body=body), {}, report)
    assert report.findings == []


def test_related_must_reference_a_real_article(make_article):
    report = Report()
    V.check_links(make_article(overrides={"related": ["ghost-article"]}), {}, report)
    assert any("not an article id" in f.message for f in report.errors)


def test_duplicate_ids_are_reported(make_article):
    a = make_article(category="guides", slug="dupe", overrides={"id": "dupe"})
    b = make_article(category="concepts", slug="dupe",
                     overrides={"id": "dupe", "category": "concepts"})
    report = Report()
    V.check_collection([a, b], report)
    assert any("duplicate article id" in f.message for f in report.errors)


def test_duplicate_titles_warn(make_article):
    a = make_article(category="guides", slug="one", overrides={"id": "one", "title": "Same"})
    b = make_article(category="guides", slug="two", overrides={"id": "two", "title": "same"})
    report = Report()
    V.check_collection([a, b], report)
    assert any("duplicates" in f.message for f in report.warnings)
