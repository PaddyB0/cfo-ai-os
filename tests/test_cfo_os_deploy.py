"""Deploy and check. Fixtures are fictional."""

from __future__ import annotations

import copy
import json

import pytest

from .cfo_os_paths import EXAMPLES
from cfo_os.check_folder import check
from cfo_os.common import (CATALOGUE, CHANGELOG, MANIFEST, PLACEHOLDER_RE, TemplateError,
                           load_manifest, load_placeholders, parse_tiers, read_text, write_manifest)
from cfo_os.deploy import SETUP_CHECK, deploy


def test_deploy_fills_every_placeholder_and_checks_clean(deployed):
    leftovers = [p for p in deployed.rglob("*.md") if PLACEHOLDER_RE.search(read_text(p))]
    assert not leftovers
    assert check(deployed) == ([], [])


def test_deploy_writes_manifest_changelog_catalogue_and_empty_folders(deployed, answers):
    manifest = json.loads(read_text(deployed / MANIFEST))
    assert manifest["deployed"] == "2027-01-15"
    assert manifest["tiers"] == ["CFO"]
    assert manifest["values"]["company.name"] == answers["company"]["name"]
    assert manifest["files"]["Shared/Claude/Instructions.md"]["regions"]
    assert "instructions_pasted_sha256" not in manifest
    assert "deployed from template" in read_text(deployed / CHANGELOG)
    assert "Watch list" in read_text(deployed / CATALOGUE)
    assert (deployed / "CFO/Periods").is_dir() and (deployed / "CFO/Projects").is_dir()


def test_default_deploy_writes_the_cfo_tier_only(deployed):
    assert (deployed / "CFO/Role.md").is_file() and (deployed / "CFO/Memory/Now.md").is_file()
    assert not (deployed / "VP").exists() and not (deployed / "Team").exists()
    manifest = json.loads(read_text(deployed / MANIFEST))
    assert not [rel for rel in manifest["files"] if rel.startswith(("VP/", "Team/"))]


def test_three_tier_deploy_writes_every_tier_and_checks_clean(deployed_all):
    for tier in ("CFO", "VP", "Team"):
        for rel in ("Role.md", "Memory/Now.md", "Memory/Log.md", "Periods", "Projects"):
            assert (deployed_all / tier / rel).exists(), f"{tier}/{rel}"
    assert json.loads(read_text(deployed_all / MANIFEST))["tiers"] == ["CFO", "VP", "Team"]
    assert check(deployed_all) == ([], [])


def test_files_shared_by_the_tiers_are_identical_except_role(deployed_all):
    cfo = sorted(p.relative_to(deployed_all / "CFO").as_posix()
                 for p in (deployed_all / "CFO").rglob("*") if p.is_file())
    assert "Role.md" in cfo
    for tier in ("VP", "Team"):
        other = sorted(p.relative_to(deployed_all / tier).as_posix()
                       for p in (deployed_all / tier).rglob("*") if p.is_file())
        assert other == cfo
        for rel in cfo:
            same = (deployed_all / "CFO" / rel).read_bytes() == (deployed_all / tier / rel).read_bytes()
            assert same == (rel != "Role.md"), f"{tier}/{rel}"


@pytest.mark.parametrize("value", ["VP", "CFO,Board", "", "CFO,,VP"])
def test_an_invalid_tier_list_fails_before_anything_is_written(tmp_path, template, answers, metrics, value):
    target = tmp_path / "CFO OS"
    with pytest.raises(TemplateError, match="tiers"):
        deploy(template, answers, metrics, target, "d", "2027-01-15", value)
    assert not target.exists()


def test_tier_lists_are_read_in_any_case_and_order():
    assert parse_tiers("team, cfo") == ("CFO", "Team")
    assert parse_tiers(["VP", "CFO", "VP"]) == ("CFO", "VP")


def test_deploy_takes_a_folder_holding_only_the_setup_check(tmp_path, template, answers, metrics):
    target = tmp_path / "CFO OS"
    target.mkdir()
    (target / SETUP_CHECK).write_text("written by the setup prompt", encoding="utf-8")
    deploy(template, answers, metrics, target, "d", "2027-01-15")
    assert not (target / SETUP_CHECK).exists()
    assert check(target) == ([], [])


def test_deploy_refuses_a_folder_that_is_not_empty(tmp_path, template, answers, metrics):
    (tmp_path / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(TemplateError, match="not empty"):
        deploy(template, answers, metrics, tmp_path, "d", "2027-01-15")
    (tmp_path / SETUP_CHECK).write_text("x", encoding="utf-8")
    with pytest.raises(TemplateError, match="not empty"):
        deploy(template, answers, metrics, tmp_path, "d", "2027-01-15")
    assert (tmp_path / SETUP_CHECK).exists()


def test_deploy_names_every_missing_required_answer(tmp_path, template, answers, metrics):
    broken = copy.deepcopy(answers)
    del broken["company"]["name"]
    broken["cfo"]["name"] = ""
    with pytest.raises(TemplateError) as e:
        deploy(template, broken, metrics, tmp_path / "CFO OS", "d", "2027-01-15")
    assert "company.name" in str(e.value) and "cfo.name" in str(e.value)
    assert not (tmp_path / "CFO OS").exists()


def test_deploy_takes_the_datarails_connector_metric_list(tmp_path, template, answers):
    from cfo_os.catalogue import build as catalogue
    raw = [{"id": 101, "name": "Net Revenue", "kind": "BASE", "category": "Revenue",
            "time_aggregation": "SUM", "dimensions": ["Entity", "Region"], "formula": None,
            "description": "Fictional.", "status_info": {"source_warning": None, "error_message": None}},
           {"id": 102, "name": "Cash", "kind": "BASE", "category": "Balance Sheet",
            "time_aggregation": "EOP", "dimensions": ["Entity"], "formula": None,
            "description": None, "status_info": {}}]
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({"metrics": raw}), encoding="utf-8")
    metrics = catalogue.load_metrics(path)
    assert metrics["core_dimensions"] == ["Entity"]
    assert metrics["metrics"][1]["rollup"] == "end_of_period"
    deploy(template, answers, metrics, tmp_path / "CFO OS", "d", "2027-01-15")
    assert "| 102 | Cash | base | end of period |" in read_text(tmp_path / "CFO OS" / CATALOGUE)


def _findings(folder) -> str:
    return "\n".join(check(folder)[0])


def test_check_top_level_and_shared(deployed):
    (deployed / "notes.txt").write_text("stray", encoding="utf-8")
    (deployed / "Board").mkdir()
    (deployed / "Shared/Drafts").mkdir()
    (deployed / "Shared/Workflows/Payroll.xlsx").write_text("x", encoding="utf-8")
    (deployed / "Shared/Workflows/Templates/Examples").mkdir()
    (deployed / "Shared/Workflows/Templates/logo.png").write_text("x", encoding="utf-8")
    (deployed / "Shared/Claude/Notes.md").write_text("x", encoding="utf-8")
    (deployed / "Shared/Claude/Upgrade report 2027-02-01.md").write_text("x", encoding="utf-8")
    (deployed / "Shared/Claude/Tests/Runs").mkdir()
    (deployed / "Shared/Claude/Tests/Runs/2027-01-15.md").write_text("x", encoding="utf-8")
    (deployed / "Shared/Claude/Tests/Other.md").write_text("x", encoding="utf-8")
    (deployed / "Shared/Library").mkdir()
    (deployed / "Shared/Library/Lease.pdf").write_bytes(b"%PDF")
    text = _findings(deployed)
    assert "notes.txt: not allowed at the top level" in text
    assert "Board: not allowed at the top level" in text
    assert "Shared/Drafts: not allowed here; Shared holds only" in text
    assert "Shared/Workflows/Payroll.xlsx: not allowed here" in text
    assert "Shared/Workflows/Templates/logo.png: not allowed here" in text
    assert "Shared/Claude/Notes.md: not allowed here" in text
    assert "Shared/Claude/Tests/Other.md: not allowed here" in text
    for fine in ("Templates/Examples", "Upgrade report", "Runs/", "Library/"):
        assert fine not in text
    assert len(text.splitlines()) == 7


def test_check_tier_periods_and_projects(deployed):
    cfo = deployed / "CFO"
    (cfo / "Notes.md").write_text("x", encoding="utf-8")
    (cfo / "Memory/Ideas.md").write_text("x", encoding="utf-8")
    (cfo / "Memory/Log Priya.md").write_text("x", encoding="utf-8")
    (cfo / "Periods/loose.md").write_text("x", encoding="utf-8")
    (cfo / "Periods/2027").mkdir()
    (cfo / "Periods/FY2027/2027-02/Working").mkdir(parents=True)
    (cfo / "Periods/FY2027/2027-02/draft.md").write_text("x", encoding="utf-8")
    (cfo / "Periods/FY2027/2027-02/Log Tom.md").write_text("x", encoding="utf-8")
    (cfo / "Periods/FY2027/2027-Q1/Outputs").mkdir(parents=True)
    (cfo / "Periods/FY2027/February").mkdir()
    (cfo / "Periods/FY2027/Working").mkdir()
    (cfo / "Periods/FY2027/Log.md").write_text("x", encoding="utf-8")
    (cfo / "Periods/FY2027/notes.md").write_text("x", encoding="utf-8")
    (cfo / "Projects/brief.md").write_text("x", encoding="utf-8")
    (cfo / "Projects/Refinancing/01 Inputs").mkdir(parents=True)
    (cfo / "Projects/Refinancing/Inputs").mkdir()
    (cfo / "Projects/Refinancing/Brief.md").write_text("x", encoding="utf-8")
    (cfo / "Projects/Refinancing/Log.md").write_text("x", encoding="utf-8")
    (cfo / "Archive/FY2025/anything.xlsx").parent.mkdir(parents=True)
    (cfo / "Archive/FY2025/anything.xlsx").write_text("x", encoding="utf-8")
    text = _findings(deployed)
    assert "CFO/Notes.md: not allowed here; a tier folder holds Role.md" in text
    assert "CFO/Memory/Ideas.md: not allowed here; Memory holds" in text
    assert "CFO/Periods/loose.md: files in Periods go inside a period folder" in text
    assert "CFO/Periods/2027: a year folder is named FYyyyy" in text
    assert "CFO/Periods/FY2027/2027-02/draft.md: not allowed here; a period folder holds only" in text
    assert "CFO/Periods/FY2027/February: a period folder is named yyyy-mm or yyyy-Qn" in text
    assert "CFO/Periods/FY2027/notes.md: not allowed here; a year folder holds" in text
    assert "CFO/Projects/brief.md: files in Projects go inside a project folder" in text
    assert "CFO/Projects/Refinancing/01 Inputs: not allowed here; a project folder holds only" in text
    for fine in ("Log Priya", "Log Tom", "2027-Q1", "FY2027/Working", "FY2027/Log.md",
                 "Refinancing/Inputs:", "Refinancing/Brief.md", "Refinancing/Log.md", "CFO/Archive"):
        assert fine not in text, fine
    assert len(text.splitlines()) == 9


def test_check_finds_duplicates_and_unfilled_placeholders(deployed):
    rules = deployed / "Shared/Claude/Rules.md"
    (deployed / "Shared/Claude/Rules-1.md").write_text(read_text(rules), encoding="utf-8")
    (deployed / "CFO/Memory/Now.md").write_text("{" * 2 + "company.name" + "}" * 2, encoding="utf-8")
    text = _findings(deployed)
    assert "Shared/Claude/Rules-1.md: looks like a OneDrive duplicate of Rules.md" in text
    assert "CFO/Memory/Now.md: unfilled placeholder company.name" in text


def test_check_names_missing_instructions(deployed):
    (deployed / "Shared/Claude/Instructions.md").unlink()
    assert "Shared/Claude/Instructions.md: missing" in _findings(deployed)


def test_check_notes_a_tier_folder_it_cannot_see(deployed_all):
    import shutil
    shutil.rmtree(deployed_all / "Team")
    findings, notes = check(deployed_all)
    assert findings == []
    assert len(notes) == 1 and "Team" in notes[0] and "could not be seen" in notes[0]


def test_check_takes_a_hand_deployed_manifest(deployed, answers):
    write_manifest(deployed, {"template": "cfo-ai-os", "template_version": "0.3.0",
                              "deployed": "2027-01-15", "deployer": "Example Deployer",
                              "deployed_by_hand": True, "tiers": ["CFO"], "answers": answers})
    assert check(deployed) == ([], [])


def test_check_refuses_a_folder_that_was_not_deployed(tmp_path):
    with pytest.raises(TemplateError, match="not deployed"):
        check(tmp_path)


def test_check_refuses_the_02_layout_and_points_to_the_move(tmp_path):
    (tmp_path / "00 System").mkdir()
    (tmp_path / "00 System/Template manifest.json").write_text("{}", encoding="utf-8")
    with pytest.raises(TemplateError, match="0.2 layout") as e:
        check(tmp_path)
    assert "Moving from 0.2" in str(e.value)


def test_cli_deploy_and_check_round_trip(tmp_path, capsys):
    from cfo_os.cli import main
    target = tmp_path / "CFO OS"
    assert main(["deploy", "--answers", str(EXAMPLES / "answers.example.yaml"),
                 "--metrics", str(EXAMPLES / "metrics.example.json"),
                 "--target", str(target), "--tiers", "CFO,VP,Team", "--deployer", "Example"]) == 0
    assert main(["check", "--folder", str(target)]) == 0
    assert "no findings" in capsys.readouterr().out
    assert main(["deploy", "--answers", str(EXAMPLES / "answers.example.yaml"),
                 "--metrics", str(EXAMPLES / "metrics.example.json"),
                 "--target", str(tmp_path / "Other"), "--tiers", "VP"]) == 2
    assert not (tmp_path / "Other").exists()


def test_deploy_refuses_misspelt_answer_keys(tmp_path, template, answers, metrics):
    broken = copy.deepcopy(answers)
    broken["company"]["reportng_currency"] = "GBP"
    broken["peeple"] = []
    with pytest.raises(TemplateError) as e:
        deploy(template, broken, metrics, tmp_path / "CFO OS", "d", "2027-01-15")
    assert "company.reportng_currency" in str(e.value) and "peeple" in str(e.value)


def test_bad_metric_list_fails_before_anything_is_written(tmp_path, template, answers, metrics):
    from cfo_os.catalogue.build import validate
    bad = copy.deepcopy(metrics)
    bad["metrics"][0]["name"] = ["not", "text"]
    with pytest.raises(TemplateError, match="name must be text"):
        validate(bad, "x")
    target = tmp_path / "CFO OS"
    with pytest.raises(Exception):
        deploy(template, answers, bad, target, "d", "2027-01-15")
    assert not target.exists() or not any(target.iterdir())


def test_datarails_kinds_missing_rollup_and_processing_status(tmp_path):
    from cfo_os.catalogue import build as catalogue
    raw = {"metrics": [
        {"id": 101, "name": "Plan Input", "kind": "USER", "time_aggregation": "SUM", "dimensions": ["Entity"]},
        {"id": 102, "name": "Driver", "kind": "DRIVER", "time_aggregation": "SUM", "dimensions": ["Entity"]},
        {"id": 103, "name": "Balance", "kind": "BASE", "dimensions": ["Entity"],
         "status_info": {"status": "PROCESSING"}},
    ]}
    path = tmp_path / "m.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    data = catalogue.load_metrics(path, "datarails")
    assert [m["kind"] for m in data["metrics"]] == ["input", "driver", "base"]
    assert data["metrics"][2]["rollup"] == "unknown"
    flagged = "\n".join(catalogue.watch_list(data["metrics"]))
    assert "103 Balance: the connector gives no roll-up" in flagged
    assert "status PROCESSING" in flagged


# --- a tier the manifest does not list ----------------------------------------------------

def test_check_finds_a_tier_folder_the_manifest_does_not_list(deployed):
    (deployed / "VP" / "Memory").mkdir(parents=True)
    (deployed / "VP" / "Role.md").write_text("A role.\n", encoding="utf-8")
    findings, notes = check(deployed)
    assert notes == []
    assert len(findings) == 1 and findings[0].startswith("VP: tier folder not in the manifest's tiers (CFO)")
    assert "--tiers CFO,VP --apply" in findings[0]


def test_check_refuses_a_manifest_tier_that_is_not_a_tier(deployed):
    manifest = load_manifest(deployed)
    write_manifest(deployed, {**manifest, "tiers": ["CFO", "Board"]})
    with pytest.raises(TemplateError, match="'Board' is not a tier"):
        check(deployed)


# --- the tier of a person -----------------------------------------------------------------

def test_deploy_refuses_a_person_whose_tier_is_not_a_tier(tmp_path, template, answers, metrics):
    bad = copy.deepcopy(answers)
    bad["people"][1]["tier"] = "Board"
    with pytest.raises(TemplateError, match="answer people: row 2 has tier 'Board'; it must be one of "
                                            "CFO, VP, Team, none"):
        deploy(template, bad, metrics, tmp_path / "CFO OS", "Example Deployer", "2027-01-15")
    assert not (tmp_path / "CFO OS").exists()


def test_the_tier_choices_are_the_schema_enum():
    from .cfo_os_paths import ROOT
    schema = json.loads((ROOT / "schemas" / "answers.schema.json").read_text(encoding="utf-8"))
    enum = schema["properties"]["people"]["items"]["properties"]["tier"]["enum"]
    assert load_placeholders()["people"]["choices"] == {"tier": enum}


# --- metrics left out of the shared catalogue ---------------------------------------------

def test_deploy_leaves_named_metrics_out_of_the_catalogue_and_records_them(tmp_path, template, answers,
                                                                          metrics):
    target = tmp_path / "CFO OS"
    deploy(template, answers, metrics, target, "Example Deployer", "2027-01-15", "CFO,VP",
           catalogue_exclude="111, 112")
    text = read_text(target / CATALOGUE)
    assert "Headcount" not in text and "Revenue per Head" not in text
    assert "13 metrics." in text
    assert "2 metrics the connector has are left out of this file by choice" in text
    assert load_manifest(target)["catalogue_exclude"] == ["111", "112"]
    assert check(target) == ([], [])


def test_deploy_without_an_exclusion_writes_the_catalogue_and_manifest_as_before(deployed):
    assert "left out" not in read_text(deployed / CATALOGUE)
    assert "catalogue_exclude" not in load_manifest(deployed)


def test_deploy_refuses_to_leave_out_a_metric_the_list_does_not_have(tmp_path, template, answers,
                                                                    metrics):
    with pytest.raises(TemplateError, match="not in the metric list: 999"):
        deploy(template, answers, metrics, tmp_path / "CFO OS", "Example Deployer", "2027-01-15",
               catalogue_exclude="111,999")
    assert not (tmp_path / "CFO OS").exists()


def test_a_kept_formula_that_names_a_metric_left_out_is_warned_about(metrics, tmp_path, capsys):
    from cfo_os.catalogue.build import formula_mentions
    from cfo_os.cli import main
    assert [line.split(":")[0] for line in formula_mentions(metrics, "111")] == ["112 Revenue per Head"]
    assert formula_mentions(metrics, "111,112") == []
    assert main(["deploy", "--answers", str(EXAMPLES / "answers.example.yaml"),
                 "--metrics", str(EXAMPLES / "metrics.example.json"), "--target", str(tmp_path / "CFO OS"),
                 "--deployer", "Example", "--catalogue-exclude", "111"]) == 0
    assert "warning: 112 Revenue per Head: its formula names Headcount" in capsys.readouterr().err
