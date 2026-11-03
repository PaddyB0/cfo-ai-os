"""Deploy and check. Fixtures are fictional."""

from __future__ import annotations

import copy
import json

import pytest

from .cfo_os_paths import EXAMPLES
from cfo_os.check_folder import check, record_pasted
from cfo_os.common import MANIFEST, PLACEHOLDER_RE, TemplateError, read_text
from cfo_os.deploy import deploy


def test_deploy_fills_every_placeholder_and_checks_clean(deployed):
    leftovers = [p for p in deployed.rglob("*.md") if PLACEHOLDER_RE.search(read_text(p))]
    assert not leftovers
    findings, notes = check(deployed)
    assert findings == []
    assert any("never recorded as pasted" in n for n in notes)


def test_deploy_writes_manifest_changelog_catalogue_and_empty_folders(deployed, answers):
    manifest = json.loads(read_text(deployed / MANIFEST))
    assert manifest["deployed"] == "2027-01-15"
    assert manifest["values"]["company.name"] == answers["company"]["name"]
    assert manifest["files"]["00 System/Instructions.md"]["regions"]
    assert "deployed from template" in read_text(deployed / "00 System/Changelog.md")
    assert "Watch list" in read_text(deployed / "01 Context/Metric catalogue.md")
    assert (deployed / "06 Projects/_Project template/Inputs").is_dir()


def test_deploy_refuses_a_folder_that_is_not_empty(tmp_path, template, answers, metrics):
    (tmp_path / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(TemplateError, match="not empty"):
        deploy(template, answers, metrics, tmp_path, "d", "2027-01-15")


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
    assert "| 102 | Cash | base | end of period |" in read_text(tmp_path / "CFO OS/01 Context/Metric catalogue.md")


def test_check_finds_misfiled_misnamed_duplicate_and_unfilled(deployed):
    (deployed / "notes.txt").write_text("stray", encoding="utf-8")
    (deployed / "05 Periods/FY2027/2027-02/Working").mkdir(parents=True)
    (deployed / "05 Periods/FY2027/2027-02/draft.md").write_text("x", encoding="utf-8")
    (deployed / "05 Periods/FY2027/February").mkdir()
    (deployed / "05 Periods/FY2027/Working").mkdir()
    (deployed / "05 Periods/2027").mkdir()
    (deployed / "06 Projects/Budget/01 Inputs").mkdir(parents=True)
    rules = deployed / "02 Rules and style/Rules.md"
    (deployed / "02 Rules and style/Rules-1.md").write_text(read_text(rules), encoding="utf-8")
    (deployed / "03 Memory/Lessons.md").write_text("{" * 2 + "company.name" + "}" * 2, encoding="utf-8")
    findings, _ = check(deployed)
    text = "\n".join(findings)
    assert "notes.txt: not allowed at the top level" in text
    assert "05 Periods/FY2027/2027-02/draft.md: not allowed here" in text
    assert "05 Periods/FY2027/February: a period folder is named" in text
    assert "05 Periods/2027: a year folder is named FYyyyy" in text
    assert "FY2027/Working" not in text
    assert "06 Projects/Budget/01 Inputs: the two-digit prefix" in text
    assert "Rules-1.md: looks like a OneDrive duplicate" in text
    assert "03 Memory/Lessons.md: unfilled placeholder company.name" in text


def test_check_flags_instructions_changed_after_paste(deployed):
    record_pasted(deployed)
    assert check(deployed)[0] == []
    path = deployed / "00 System/Instructions.md"
    path.write_text(read_text(path) + "\nOne more rule.\n", encoding="utf-8")
    assert any("changed since it was last pasted" in f for f in check(deployed)[0])


def test_check_refuses_a_folder_that_was_not_deployed(tmp_path):
    with pytest.raises(TemplateError, match="not deployed"):
        check(tmp_path)


def test_cli_deploy_and_check_round_trip(tmp_path, capsys):
    from cfo_os.cli import main
    target = tmp_path / "CFO OS"
    assert main(["deploy", "--answers", str(EXAMPLES / "answers.example.yaml"),
                 "--metrics", str(EXAMPLES / "metrics.example.json"),
                 "--target", str(target), "--deployer", "Example"]) == 0
    assert main(["pasted", "--folder", str(target)]) == 0
    assert main(["check", "--folder", str(target)]) == 0
    assert "no findings" in capsys.readouterr().out
