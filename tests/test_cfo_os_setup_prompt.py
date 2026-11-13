"""The setup prompt, SETUP.md. Fixtures are fictional."""

from __future__ import annotations

import pytest

from .cfo_os_paths import EXAMPLES, ROOT
from cfo_os import __version__
from cfo_os.common import TemplateError, load_placeholders, read_text, template_files
from cfo_os.setup_prompt import build, main

SETUP = ROOT / "SETUP.md"


@pytest.fixture(scope="module")
def built() -> str:
    from .cfo_os_paths import TEMPLATE
    return build(TEMPLATE, EXAMPLES / "metrics.example.json")


def test_setup_md_is_fresh(built):
    assert SETUP.is_file(), "run: python run.py prompt --out SETUP.md"
    assert read_text(SETUP).replace("\r\n", "\n") == built, "stale; run: python run.py prompt --out SETUP.md"


def test_setup_md_has_no_unfilled_slot(built):
    assert "[[" not in built


def test_setup_md_carries_every_template_file(built, template):
    for rel in template_files(template):
        assert f"\n### File: {rel}\n" in built, rel


def test_setup_md_names_every_required_placeholder(built):
    for name, spec in load_placeholders().items():
        if spec.get("required") and not spec.get("auto"):
            assert f"`{name}`" in built, name


def test_setup_md_names_the_version(built):
    assert f"@v{__version__}" in built and f" is {__version__}" in built


def test_build_is_deterministic(template):
    metrics = EXAMPLES / "metrics.example.json"
    assert build(template, metrics) == build(template, metrics)


def test_an_unknown_slot_fails(tmp_path, template):
    source = tmp_path / "prompt.md"
    source.write_text("Version [[version]], then [[nonsense]].\n", encoding="utf-8")
    with pytest.raises(TemplateError, match="unknown slot"):
        build(template, EXAMPLES / "metrics.example.json", source=source)


def test_a_template_line_starting_with_the_fence_fails(tmp_path, template):
    import shutil
    copy = tmp_path / "CFO OS"
    shutil.copytree(template, copy)
    path = copy / "Shared/Claude/Rules.md"
    path.write_text(read_text(path) + "\n~~~~\n", encoding="utf-8", newline="")
    with pytest.raises(TemplateError, match="starts with ~~~~"):
        build(copy, EXAMPLES / "metrics.example.json")


def test_check_exits_1_when_stale(tmp_path, capsys):
    stale = tmp_path / "SETUP.md"
    stale.write_text("old\n", encoding="utf-8")
    assert main(["--check", str(stale)]) == 1
    assert main(["--out", str(stale)]) == 0
    assert main(["--check", str(stale)]) == 0
    assert "up to date" in capsys.readouterr().out
