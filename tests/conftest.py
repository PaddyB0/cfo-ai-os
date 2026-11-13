"""Shared fixtures. Everything here is fictional: no real company, person or figure."""

from __future__ import annotations

from pathlib import Path

import pytest

from .cfo_os_paths import EXAMPLES, TEMPLATE

from cfo_os.catalogue import build as catalogue  # noqa: E402
from cfo_os.deploy import deploy, load_answers  # noqa: E402


@pytest.fixture
def template() -> Path:
    return TEMPLATE


@pytest.fixture
def answers() -> dict:
    return load_answers(EXAMPLES / "answers.example.yaml")


@pytest.fixture
def metrics() -> dict:
    return catalogue.load_metrics(EXAMPLES / "metrics.example.json")


@pytest.fixture
def deployed(tmp_path, template, answers, metrics) -> Path:
    """A folder deployed from the example, under a path with a space and an accent, the way
    OneDrive and SharePoint folders usually look."""
    target = tmp_path / "Société Finance" / "CFO OS"
    deploy(template, answers, metrics, target, "Example Deployer", "2027-01-15")
    return target


@pytest.fixture
def deployed_all(tmp_path, template, answers, metrics) -> Path:
    """The same, with all three tier folders."""
    target = tmp_path / "Société Finance" / "CFO OS"
    deploy(template, answers, metrics, target, "Example Deployer", "2027-01-15", "CFO,VP,Team")
    return target
