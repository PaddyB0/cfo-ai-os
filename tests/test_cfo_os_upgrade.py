"""Upgrade a deployed folder to a newer template. Fixtures are fictional: a copy of the
template is edited to stand in for the next version."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from .cfo_os_paths import TEMPLATE  # noqa: F401  (puts src on the path)
import cfo_os.upgrade as upgrade
from cfo_os import __version__ as DEPLOYED
from cfo_os.common import (CHANGELOG, MANIFEST, TemplateError, load_manifest, read_text, regions,
                           replace_regions, write_manifest)
from cfo_os.upgrade import HAND_REVIEW, apply_plan, describe, plan_upgrade

WORKFLOW = "Shared/Workflows/Cash runway.md"
ADDED = "Shared/Workflows/Payroll review.md"
DROPPED = "Shared/Workflows/Board or investor question.md"
CLIENT = "CFO/Memory/Log.md"
CONTEXT = "Shared/Claude/Company.md"
# The pretend next release: one minor version past the one deployed.
_major, _minor, _ = DEPLOYED.split(".")
NEXT = f"{_major}.{int(_minor) + 1}.0"


@pytest.fixture
def next_template(tmp_path, template, monkeypatch) -> Path:
    """The template as a pretend next release: one region changed, one file added, one removed,
    one heading added to a context file."""
    nxt = tmp_path / "next" / "CFO OS"
    shutil.copytree(template, nxt)
    path = nxt / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: body.text + "\nA step added in the next release."}),
                    encoding="utf-8", newline="")
    (nxt / ADDED).write_text(read_text(nxt / WORKFLOW), encoding="utf-8", newline="")
    (nxt / DROPPED).unlink()
    ctx = nxt / CONTEXT
    ctx.write_text(read_text(ctx) + "\n## Banking\n", encoding="utf-8", newline="")
    monkeypatch.setattr(upgrade, "__version__", NEXT)
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
    assert ADDED in plan.adds
    assert DROPPED in plan.removed_files
    assert plan.suggestions == [(CONTEXT, ["## Banking"])]
    apply_plan(deployed, plan, "2027-02-01")
    assert "A step added in the next release." in read_text(deployed / WORKFLOW)
    assert (deployed / ADDED).is_file()
    assert (deployed / DROPPED).is_file()
    assert (deployed / CLIENT).read_bytes() == client_before
    assert (deployed / CONTEXT).read_bytes() == context_before
    assert load_manifest(deployed)["template_version"] == NEXT
    assert f"upgraded from template {DEPLOYED} to {NEXT}" in read_text(deployed / CHANGELOG)
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
    assert report == "Shared/Claude/Upgrade report 2027-02-01.md"
    assert "A step added in the next release." in read_text(deployed / report)
    assert plan_upgrade(deployed, next_template, today="2027-02-02").review
    accepted = plan_upgrade(deployed, next_template, accept_edited=True, today="2027-02-02")
    apply_plan(deployed, accepted, "2027-02-02")
    assert not plan_upgrade(deployed, next_template, today="2027-02-03").review


def test_replaced_region_keeps_crlf_line_endings(deployed, next_template):
    path = deployed / WORKFLOW
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-01"), "2027-02-01")
    raw = path.read_bytes()
    assert b"A step added in the next release." in raw and b"\n" not in raw.replace(b"\r\n", b"")


def test_client_files_are_never_opened(deployed, next_template, monkeypatch):
    opened = []
    real = upgrade.read_text

    def spy(p):
        opened.append(Path(p).relative_to(deployed).as_posix() if deployed in Path(p).parents else str(p))
        return real(p)

    monkeypatch.setattr(upgrade, "read_text", spy)
    plan_upgrade(deployed, next_template, today="2027-02-01")
    touched = [o for o in opened if o.startswith(("CFO/Memory/", "CFO/Periods/", "CFO/Projects/",
                                                   "CFO/Archive/", "Shared/Library/"))]
    assert touched == [] and "Shared/Claude/Rules.md" not in opened


def test_upgrade_never_moves_a_folder_back(deployed, next_template, monkeypatch):
    monkeypatch.setattr(upgrade, "__version__", "0.0.9")
    with pytest.raises(Exception, match="never moves a folder back"):
        plan_upgrade(deployed, next_template)


def test_manifest_is_rewritten_only_on_apply(deployed, next_template):
    before = (deployed / MANIFEST).read_bytes()
    plan_upgrade(deployed, next_template, today="2027-02-01")
    assert (deployed / MANIFEST).read_bytes() == before


def test_deleted_or_moved_template_files_are_not_brought_back(deployed, next_template):
    (deployed / "CFO/Memory/Log.md").unlink()
    (deployed / "CFO/Archive").mkdir()
    (deployed / "Shared/Workflows/Budget.md").rename(deployed / "CFO/Archive/Budget.md")
    plan = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert "CFO/Memory/Log.md" not in plan.adds and "Shared/Workflows/Budget.md" not in plan.adds
    apply_plan(deployed, plan, "2027-02-01")
    assert not (deployed / "CFO/Memory/Log.md").exists()
    assert not (deployed / "Shared/Workflows/Budget.md").exists()


def test_removed_region_is_reported_once(deployed, next_template):
    path = next_template / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    markers = (f"cfo-os:template begin {body.id} ", f"cfo-os:template end {body.id} ")
    kept = [l for l in text.splitlines(keepends=True) if not any(m in l for m in markers)]
    path.write_text("".join(kept), encoding="utf-8", newline="")
    first = plan_upgrade(deployed, next_template, today="2027-02-01")
    assert f"{WORKFLOW}#{body.id}" in first.removed_regions
    apply_plan(deployed, first, "2027-02-01")
    assert plan_upgrade(deployed, next_template, today="2027-02-02").removed_regions == []


def test_applying_with_nothing_to_change_writes_nothing(deployed, next_template):
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-01"), "2027-02-01")
    before = snapshot(deployed)
    apply_plan(deployed, plan_upgrade(deployed, next_template, today="2027-02-02"), "2027-02-02")
    assert snapshot(deployed) == before


# --- tiers --------------------------------------------------------------------------------

def test_tiers_adds_a_tier_as_plain_adds(deployed, template):
    plan = plan_upgrade(deployed, template, today="2027-02-01", tiers="CFO,VP")
    assert plan.added_tiers == ("VP",)
    assert sorted(plan.adds) == ["VP/Memory/Log.md", "VP/Memory/Now.md", "VP/Role.md"]
    assert not plan.replaced and not plan.review
    apply_plan(deployed, plan, "2027-02-01")
    assert (deployed / "VP/Periods").is_dir() and (deployed / "VP/Projects").is_dir()
    assert not (deployed / "Team").exists()
    manifest = load_manifest(deployed)
    assert manifest["tiers"] == ["CFO", "VP"] and "VP/Role.md" in manifest["files"]
    assert "Tiers added: VP." in read_text(deployed / CHANGELOG)
    again = plan_upgrade(deployed, template, today="2027-02-02")
    assert again.tiers == ("CFO", "VP") and not again.changes()


def test_tiers_may_not_remove_a_tier(deployed_all, template):
    with pytest.raises(TemplateError, match="not remove one"):
        plan_upgrade(deployed_all, template, tiers="CFO,VP")


def test_the_02_layout_is_refused_with_a_pointer(tmp_path, template):
    (tmp_path / "00 System").mkdir()
    (tmp_path / "00 System/Template manifest.json").write_text("{}", encoding="utf-8")
    with pytest.raises(TemplateError) as e:
        plan_upgrade(tmp_path, template)
    assert "changed in 0.3" in str(e.value) and "docs/upgrade.md" in str(e.value)
    assert "Moving from 0.2" in str(e.value)


def test_a_tier_folder_that_cannot_be_seen_is_warned_about_and_kept(deployed_all, next_template):
    shutil.rmtree(deployed_all / "Team")
    recorded = load_manifest(deployed_all)["files"]["Team/Role.md"]
    plan = plan_upgrade(deployed_all, next_template, today="2027-02-01")
    assert plan.unseen_tiers == ("Team",)
    assert any("Team folder could not be seen" in line for line in describe(plan))
    assert not [r for r in plan.adds if r.startswith("Team/")]
    report = apply_plan(deployed_all, plan, "2027-02-01")
    assert not (deployed_all / "Team").exists()
    manifest = load_manifest(deployed_all)
    assert manifest["tiers"] == ["CFO", "VP", "Team"]
    assert manifest["files"]["Team/Role.md"] == recorded
    assert "Not upgraded" in read_text(deployed_all / report)


# --- folders set up by hand ---------------------------------------------------------------

def _by_hand(folder, answers) -> None:
    write_manifest(folder, {"template": "cfo-ai-os", "template_version": DEPLOYED,
                            "deployed": "2027-01-15", "deployer": "Example Deployer",
                            "deployed_by_hand": True, "tiers": ["CFO"], "answers": answers})


def test_a_folder_set_up_by_hand_upgrades(deployed, template, answers):
    _by_hand(deployed, answers)
    path = deployed / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: body.text + "\nWritten differently by hand."}),
                    encoding="utf-8", newline="")
    (deployed / "Shared/Workflows/Budget.md").unlink()
    before = path.read_bytes()

    plan = plan_upgrade(deployed, template, today="2027-02-01")
    assert plan.by_hand
    assert [r[:3] for r in plan.review] == [(WORKFLOW, body.id, HAND_REVIEW)]
    assert list(plan.adds) == ["Shared/Workflows/Budget.md"]
    assert not plan.replaced
    record = plan.manifest["files"]
    instructions = record["Shared/Claude/Instructions.md"]["regions"]
    assert instructions and all(r["applied"] == r["template"] for r in instructions.values())
    assert record[WORKFLOW]["regions"][body.id]["applied"] is None

    taken = plan_upgrade(deployed, template, today="2027-02-01", take_template=True)
    assert taken.replaced == [f"{WORKFLOW}#{body.id}"] and not taken.review
    apply_plan(deployed, taken, "2027-02-01")
    assert path.read_bytes() != before and "Written differently" not in read_text(path)
    manifest = json.loads(read_text(deployed / MANIFEST))
    assert "deployed_by_hand" not in manifest and "answers" not in manifest
    assert manifest["values"]["company.name"] == answers["company"]["name"]
    assert manifest["values"]["deploy.deployer"] == "Example Deployer"
    assert manifest["files"][WORKFLOW]["regions"][body.id]["applied"] is not None
    assert not plan_upgrade(deployed, template, today="2027-02-02").changes()


def test_a_folder_set_up_by_hand_keeps_its_own_text_without_take_template(deployed, template, answers):
    _by_hand(deployed, answers)
    path = deployed / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: "Our own steps."}), encoding="utf-8", newline="")
    report = apply_plan(deployed, plan_upgrade(deployed, template, today="2027-02-01"), "2027-02-01")
    assert "Our own steps." in read_text(path)
    assert "the folder was set up by hand" in read_text(deployed / report)
    assert "deployed_by_hand" not in load_manifest(deployed)
    assert plan_upgrade(deployed, template, today="2027-02-02").review


# --- --take-template on any folder --------------------------------------------------------

def test_take_template_replaces_an_edited_region_on_a_normal_folder(deployed, next_template):
    path = deployed / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: body.text + "\nOur own step."}),
                    encoding="utf-8", newline="")
    assert plan_upgrade(deployed, next_template, today="2027-02-01").review
    plan = plan_upgrade(deployed, next_template, today="2027-02-01", take_template=True)
    assert not plan.review and plan.overwritten == [f"{WORKFLOW}#{body.id}"]
    assert f"replace  {WORKFLOW}#{body.id} (the folder's text differed and is overwritten)" in describe(plan)
    apply_plan(deployed, plan, "2027-02-01")
    assert "Our own step." not in read_text(path) and "A step added in the next release." in read_text(path)
    assert not plan_upgrade(deployed, next_template, today="2027-02-02").changes()


def test_take_template_still_works_after_a_hand_folder_was_applied_without_it(deployed, template, answers):
    _by_hand(deployed, answers)
    path = deployed / WORKFLOW
    text = read_text(path)
    body = regions(text)[0]
    path.write_text(replace_regions(text, {body.id: "Our own steps."}), encoding="utf-8", newline="")
    apply_plan(deployed, plan_upgrade(deployed, template, today="2027-02-01"), "2027-02-01")
    assert "deployed_by_hand" not in load_manifest(deployed) and "Our own steps." in read_text(path)
    taken = plan_upgrade(deployed, template, today="2027-02-02", take_template=True)
    assert taken.replaced == [f"{WORKFLOW}#{body.id}"] and not taken.review
    apply_plan(deployed, taken, "2027-02-02")
    assert "Our own steps." not in read_text(path)
    assert not plan_upgrade(deployed, template, today="2027-02-03").changes()


# --- metrics left out of the shared catalogue ---------------------------------------------

CATALOGUE = "Shared/Claude/Metric catalogue.md"


def test_regenerating_the_catalogue_keeps_out_the_metrics_the_manifest_lists(deployed, template, metrics):
    write_manifest(deployed, {**load_manifest(deployed), "catalogue_exclude": ["111", "900"]})
    plan = plan_upgrade(deployed, template, metrics=metrics, today="2027-02-01")
    assert plan.left_out == 1 and "Headcount |" not in plan.catalogue
    assert "1 metric the connector has is left out of this file by choice" in plan.catalogue
    assert f"regen    {CATALOGUE} (1 left out)" in describe(plan)
    apply_plan(deployed, plan, "2027-02-01")
    assert "| 111 |" not in read_text(deployed / CATALOGUE)
    assert load_manifest(deployed)["catalogue_exclude"] == ["111", "900"]


def test_catalogue_exclude_on_upgrade_replaces_and_clears_the_recorded_list(deployed, template, metrics):
    plan = plan_upgrade(deployed, template, metrics=metrics, today="2027-02-01", catalogue_exclude="112")
    apply_plan(deployed, plan, "2027-02-01")
    assert load_manifest(deployed)["catalogue_exclude"] == ["112"]
    assert "| 112 |" not in read_text(deployed / CATALOGUE)
    with pytest.raises(TemplateError, match="not in the metric list: 900"):
        plan_upgrade(deployed, template, metrics=metrics, today="2027-02-02", catalogue_exclude="900")
    with pytest.raises(TemplateError, match="needs --catalogue"):
        plan_upgrade(deployed, template, today="2027-02-02", catalogue_exclude="112")
    cleared = plan_upgrade(deployed, template, metrics=metrics, today="2027-02-02", catalogue_exclude="")
    apply_plan(deployed, cleared, "2027-02-02")
    assert "catalogue_exclude" not in load_manifest(deployed)
    assert "| 112 |" in read_text(deployed / CATALOGUE)


def test_a_hand_folder_keeps_its_catalogue_exclusions_through_the_upgrade(deployed, template, answers,
                                                                         metrics):
    _by_hand(deployed, answers)
    write_manifest(deployed, {**load_manifest(deployed), "catalogue_exclude": ["111"]})
    apply_plan(deployed, plan_upgrade(deployed, template, today="2027-02-01"), "2027-02-01")
    assert load_manifest(deployed)["catalogue_exclude"] == ["111"]
    plan = plan_upgrade(deployed, template, metrics=metrics, today="2027-02-02")
    assert plan.left_out == 1


def test_adding_a_tier_notes_that_the_new_tier_reads_the_shared_catalogue(deployed, template):
    lines = describe(plan_upgrade(deployed, template, today="2027-02-01", tiers="CFO,VP"))
    assert any(line.startswith("note     everyone in the new tier can read Shared") for line in lines)
    assert not any("new tier" in line for line in describe(plan_upgrade(deployed, template,
                                                                        today="2027-02-01")))
