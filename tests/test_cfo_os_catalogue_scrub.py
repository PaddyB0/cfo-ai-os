"""The catalogue builder and the public-safety scan. Fixtures are fictional."""

from __future__ import annotations

import pytest

from .cfo_os_paths import ROOT
from cfo_os.catalogue.build import render, validate, watch_list
from cfo_os.common import TemplateError
from cfo_os.scrub_check import scan, scan_text


def test_catalogue_groups_by_category_and_flags_the_watch_list(metrics):
    text = render(metrics, "2027-01-15")
    assert text.startswith("# Metric catalogue")
    assert "Do not edit; regenerate." in text
    flagged = "\n".join(watch_list(metrics["metrics"]))
    assert "no description" in flagged
    assert "retired" in flagged
    assert "end-of-period inputs" in flagged


def test_catalogue_rejects_a_bad_metric_list():
    with pytest.raises(TemplateError, match="rollup"):
        validate({"metrics": [{"id": 1, "name": "A", "kind": "base", "rollup": "EOP", "dimensions": []}]}, "x")
    with pytest.raises(TemplateError, match="twice"):
        m = {"id": 1, "name": "A", "kind": "base", "rollup": "sum", "dimensions": []}
        validate({"metrics": [m, dict(m)]}, "x")


# Strings are split where needed so this file passes the scan it tests.
@pytest.mark.parametrize("line, rule", [
    ("write to someone" + "@" + "example.org", "email"),
    ("see https" + "://intranet.example.org/page", "url host not allowed"),
    ("tenant 01ARZ3NDEKTSV4" + "RRFFQ69G5FAV", "ulid"),
    ("id 123e4567-e89b-12d3-" + "a456-426614174000", "uuid"),
    ("revenue was 48213 last month", "number of four or more digits"),
    ("revenue was 48,213 last month", "number of four or more digits"),
    ("Dear " + "{" * 2 + "cfo.name" + "}" * 2, "placeholder outside the template"),
])
def test_scrub_catches(line, rule):
    assert any(f": {rule}:" in f for f in scan_text("README.md", "Plain text.\n" + line))


@pytest.mark.parametrize("line", [
    "Copyright 2026 Patrick Bowyer",
    "Period 2027-03 and close on 2027-03-31",
    "Version 0.1.0 and 3.11",
    "See https://github.com/ and https://support.claude.com/",
    "      - uses: actions/checkout@" + "a" * 40,
])
def test_scrub_allows(line):
    assert scan_text("README.md", "Plain text.\n" + line) == []


def test_scrub_allows_numbers_in_fictional_fixtures():
    assert scan_text("examples/x.yaml", "# Fictional example\nrevenue: 48213\n") == []


def test_the_repository_itself_scrubs_clean():
    assert scan(ROOT) == []


def test_scrub_still_catches_other_hex_on_a_pinned_action_line():
    line = "      - uses: actions/checkout@" + "a" * 40 + "  # " + "b" * 40
    assert any("long hex id" in f for f in scan_text("README.md", "Plain text.\n" + line))
