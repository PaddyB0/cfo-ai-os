"""Upgrade a deployed folder to a newer template. Fixtures are fictional: a copy of the
template is edited to stand in for the next version."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from .cfo_os_paths import TEMPLATE  # noqa: F401  (puts src on the path)
import cfo_os.upgrade as upgrade
from cfo_os import __version__ as DEPLOYED
from cfo_os.common import CHANGELOG, MANIFEST, load_manifest, read_text, regions, replace_regions
from cfo_os.upgrade import apply_plan, plan_upgrade

WORKFLOW = "04 Workflows/Monthly/Cash runway.md"
CLIENT = "03 Memory/Decisions.md"
CONTEXT = "01 Context/Company.md"


@pytest.fixture
def next_template(tmp_path, template, monkeypatch) -> Path:
    """The template as a pretend 0.2.0: one region changed, one file added, one removed,
    one heading added to a context file."""
    nxt = tmp_path / "next" / "CFO OS"
    shutil.copytree(template, nxt)
    path = nxt / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: body.text + "\nA step added in 0.2.0."}),
                    encoding="utf-8", newline="")
    (nxt / "04 Workflows/Monthly/Payroll review.md").write_text(
        read_text(nxt / "04 Workflows/Monthly/Cash runway.md"), encoding="utf-8", newline="")
    (nxt / "04 Workflows/Ad hoc/Board or investor question.md").unlink()
    ctx = nxt / CONTEXT
    ctx.write_text(read_text(ctx) + "\n## Banking\n", encoding="utf-8", newline="")
    monkeypatch.setattr(upgrade, "__version__", "0.2.0")
    return nxt


def snapshot(folder: Path) -> dict[str, bytes]:
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}


def test_dry_run_writes_nothing(deployed, next_template):
    before = snapshot(deployed)
    plan = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert f"{WORKFLOW}#{regions(read_text(deployed / WORKFLOW))[0].id}" in plan.replaced
    assert snapshot(deployed) == before


def test_unedited_region_is_replaced_and_other_files_are_left(deployed, next_template):
    client_before = (deployed / CLIENT).read_bytes()
    context_before = (deployed / CONTEXT).read_bytes()
    plan = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert "04 Workflows/Monthly/Payroll review.md" in plan.adds
    assert "04 Workflows/Ad hoc/Board or investor question.md" in plan.removed_files
    assert plan.suggestions == [(CONTEXT, ["## Banking"])]
    apply_plan(deployed, plan, "2027-02-01")
    assert "A step added in 0.2.0." in read_text(deployed / WORKFLOW)
    assert (deployed / "04 Workflows/Monthly/Payroll review.md").is_file()
    assert (deployed / "04 Workflows/Ad hoc/Board or investor question.md").is_file()
    assert (deployed / CLIENT).read_bytes() == client_before
    assert (deployed / CONTEXT).read_bytes() == context_before
    assert load_manifest(deployed)["template_version"] == "0.2.0"
    assert f"upgraded from template {DEPLOYED} to 0.2.0" in read_text(deployed / CHANGELOG)
    again = plan_upgrade(deployed, next_template, today="2027-02-02")
    assert not again.replaced and not again.adds and not again.review


def test_edited_region_goes_to_the_report_until_accepted(deployed, next_template):
    path = deployed / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: body.text + "\nOur own step."}),
                    encoding="utf-8", newline="")
    plan = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert [r[:2] for r in plan.review] == [(WORKFLOW, body.id)]
    report = apply_plan(deployed, plan, "2027-02-01")
    assert "Our own step." in read_text(path) and "A step added" not in read_text(path)
    assert "A step added in 0.2.0." in read_text(deployed / report)
    assert plan_upgrade(deployed, next_template, today="2027-02-02").review
    accepted = plan_upgrade(deployed, next_template, accept_edited=True, today="2027-02-02")
    apply_plan(deployed, accepted, "2027-02-02")
    assert not plan_upgrade(deployed, next_template, today="2027-02-03").review


def test_replaced_region_keeps_crlf_line_endings(deployed, next_template):
    path = deployed / WORKFLOW
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-01"), "2027-02-01")
    raw = path.read_bytes()
    assert b"A step added in 0.2.0." in raw and b"\n" not in raw.replace(b"\r\n", b"")


def test_client_files_are_never_opened(deployed, next_template, monkeypatch):
    opened = []
    real = upgrade.read_text

    def spy(p):
        opened.append(Path(p).relative_to(deployed).as_posix() if deployed in Path(p).parents else str(p))
        return real(p)

    monkeypatch.setattr(upgrade, "read_text", spy)
    plan_upgrade(deployed, next_template, today="2027-02-01")
    touched = [o for o in opened if o.startswith(("03 Memory/", "05 Periods/", "06 Projects/",
                                                   "07 Library/", "08 Archive/"))]
    assert touched == [] and "02 Rules and style/Rules.md" not in opened


def test_upgrade_never_moves_a_folder_back(deployed, next_template, monkeypatch):
    monkeypatch.setattr(upgrade, "__version__", "0.0.9")
    with pytest.raises(Exception, match="never moves a folder back"):
        plan_upgrade(deployed, next_template)


def test_manifest_is_rewritten_only_on_apply(deployed, next_template):
    before = (deployed / MANIFEST).read_bytes()
    plan_upgrade(deployed, next_template, today="2027-02-01")
    assert (deployed / MANIFEST).read_bytes() == before


def test_deleted_or_moved_template_files_are_not_brought_back(deployed, next_template):
    (deployed / "03 Memory/Lessons.md").unlink()
    (deployed / "05 Periods/README.md").rename(deployed / "08 Archive/Periods README.md")
    plan = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert "03 Memory/Lessons.md" not in plan.adds and "05 Periods/README.md" not in plan.adds
    apply_plan(deployed, plan, "2027-02-01")
    assert not (deployed / "03 Memory/Lessons.md").exists()


def test_removed_region_is_reported_once(deployed, next_template):
    path = next_template / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(text.replace(f"<!-- cfo-os:template begin {body.id} -->\n", "")
                        .replace(f"<!-- cfo-os:template end {body.id} -->\n", ""),
                    encoding="utf-8", newline="")
    first = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert f"{WORKFLOW}#{body.id}" in first.removed_regions
    apply_plan(deployed, first, "2027-02-01")
    assert plan_upgrade(deployed, next_template, today="2027-02-02").removed_regions == []


def test_applying_with_nothing_to_change_writes_nothing(deployed, next_template):
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-01"), "2027-02-01")
    before = snapshot(deployed)
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-02"), "2027-02-02")
    assert snapshot(deployed) == before
