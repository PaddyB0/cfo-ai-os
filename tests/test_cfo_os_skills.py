"""The plugin's skills: their scripts compute the right figures and refuse bad input, and the
skills are well formed and packageable. Every figure here is fictional."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import zipfile
from decimal import Decimal

import pytest

from .cfo_os_paths import ROOT, TEMPLATE
from cfo_os.skills import package, skill_dirs, skill_problems

PLUGIN = ROOT / "plugin"
SKILLS = PLUGIN / "skills"
SCRIPTS = {"cash-runway": "runway.py", "variance-analysis": "variance.py", "forecast-accuracy": "accuracy.py"}


def load(skill: str):
    path = SKILLS / skill / "scripts" / SCRIPTS[skill]
    spec = importlib.util.spec_from_file_location(f"cfo_os_skill_{skill.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example(skill: str) -> dict:
    return json.loads((SKILLS / skill / "examples" / "input.example.json").read_text(encoding="utf-8"))


runway, variance, accuracy = load("cash-runway"), load("variance-analysis"), load("forecast-accuracy")


# Cash runway

def test_runway_example():
    r = runway.run(example("cash-runway"))
    assert r["base"]["runway_month"] == "2027-11"
    assert r["base"]["months_covered"] == 7
    assert r["base"]["lowest_balance"] == Decimal(100)
    assert all(t["ties"] for t in r["ties"])
    sens = {s["name"]: s for s in r["sensitivities"]}
    assert sens["Customer receipts 20 a month lower"]["runway_month"] == "2027-10"
    assert round(r["burn"]["months_of_cash"], 2) == Decimal("8.14")


def test_runway_beyond_horizon_reports_the_low():
    r = runway.run({"opening": {"month": "2027-01", "balance": 100},
                    "movements": [{"month": "2027-02", "amount": -10}, {"month": "2027-03", "amount": 5}]})
    assert r["base"]["beyond_horizon"] and r["base"]["runway_month"] is None
    assert r["base"]["lowest_month"] == "2027-02" and r["base"]["months_covered"] == 2
    assert "stays above the floor" in runway.report(r, 0)


def test_runway_floor_breach_in_first_month():
    r = runway.run({"opening": {"month": "2027-12", "balance": 10}, "minimum_cash": 5,
                    "movements": [{"month": "2028-01", "amount": -6}]})
    assert r["base"]["runway_month"] == "2028-01" and r["base"]["months_covered"] == 0


def test_runway_flags_a_forecast_that_does_not_tie():
    doc = example("cash-runway")
    doc["forecast_closing"][1]["balance"] = 900
    bad = [t for t in runway.run(doc)["ties"] if not t["ties"]]
    assert [t["month"] for t in bad] == ["2027-05"]


@pytest.mark.parametrize("movements, message", [
    ([{"month": "2027-02", "amount": 1}, {"month": "2027-04", "amount": 1}], "without a gap"),
    ([{"month": "2027-02", "amount": 1}, {"month": "2027-02", "amount": 1}], "appears twice"),
    ([{"month": "2027-01", "amount": 1}], "not after the opening"),
    ([{"month": "2027-02", "amount": 1, "source": "Forecast A"},
      {"month": "2027-03", "amount": 1, "source": "Forecast B"}], "more than one source"),
    ([{"month": "2027-2", "amount": 1}], "yyyy-mm"),
    ([{"month": "2027-02", "amount": "lots"}], "expected a number"),
])
def test_runway_refuses_bad_movements(movements, message):
    with pytest.raises(runway.InputError, match=message):
        runway.run({"opening": {"month": "2027-01", "balance": 100}, "movements": movements})


def test_runway_opening_below_the_floor_is_a_breach_now():
    r = runway.run({"opening": {"month": "2027-03", "balance": 200}, "minimum_cash": 250,
                    "movements": [{"month": "2027-04", "amount": 100}],
                    "trailing_actual_movements": [{"month": "2027-03", "amount": -50}]})
    assert r["base"]["runway_month"] == "2027-03" and r["base"]["months_covered"] == 0
    assert r["base"]["lowest_month"] == "2027-04"
    assert r["burn"]["months_of_cash"] is None
    assert "already below the floor" in runway.report(r, 0)


@pytest.mark.parametrize("extra, message", [
    ({"trailing_actual_movements": [{"month": "2025-01", "amount": -5}]}, "up to and including"),
    ({"forecast_closing": [{"month": "2027-09", "balance": 1}]}, "outside the forecast months"),
    ({"forecast_closing": [{"month": "2027-02", "balance": 1}, {"month": "2027-02", "balance": 2}]}, "appears twice"),
])
def test_runway_refuses_checks_that_could_not_be_made(extra, message):
    doc = {"opening": {"month": "2027-01", "balance": 100}, "movements": [{"month": "2027-02", "amount": -1}]}
    with pytest.raises(runway.InputError, match=message):
        runway.run({**doc, **extra})


def test_runway_refuses_a_month_with_no_source_beside_named_ones():
    with pytest.raises(runway.InputError, match="more than one source"):
        runway.run({"opening": {"month": "2027-01", "balance": 100},
                    "movements": [{"month": "2027-02", "amount": 1, "source": "Forecast A"},
                                  {"month": "2027-03", "amount": 1}]})


# Variance analysis

def test_variance_example_directions_and_ties():
    r = variance.run(example("variance-analysis"))
    by = {ln["line"]: ln for ln in r["lines"]}
    assert by["Revenue"]["direction"] == "F"
    assert by["Cost of sales"]["direction"] == "A"
    assert by["Payroll"]["direction"] == "F" and not by["Payroll"]["material"]
    assert by["Marketing"]["direction"] == "A" and by["Marketing"]["material"]
    assert by["Headcount"]["direction"] == "F"
    assert all(t["current_ties"] and t["comparator_ties"] for t in r["totals"])


def test_variance_costs_positive_reverses_the_cost_call():
    doc = {"sign_convention": "costs_positive",
           "lines": [{"line": "Revenue", "type": "revenue", "current": 100, "comparator": 90},
                     {"line": "Rent", "type": "cost", "current": 30, "comparator": 20}],
           "totals": [{"line": "Profit", "of": ["Revenue", "Rent"], "current": 70, "comparator": 70}]}
    r = variance.run(doc)
    assert r["lines"][1]["direction"] == "A"
    assert r["totals"][0]["current_ties"] and r["totals"][0]["comparator_ties"]


def test_variance_rejects_a_positive_cost_under_natural_sign():
    with pytest.raises(variance.InputError, match="positive under the natural convention"):
        variance.run({"lines": [{"line": "Rent", "type": "cost", "current": 30, "comparator": -20}]})


def test_variance_reports_a_total_that_does_not_tie():
    doc = example("variance-analysis")
    doc["totals"][1]["current"] = 170
    r = variance.run(doc)
    assert not r["totals"][1]["current_ties"]
    assert "does not tie" in variance.report(r, 0)


def test_variance_zero_comparator_is_not_meaningful():
    r = variance.run({"lines": [{"line": "New line", "type": "revenue", "current": 5, "comparator": 0}]})
    assert r["lines"][0]["ratio"] is None and "n/m" in variance.report(r, 0)


def test_variance_cost_only_total_ties_with_costs_positive():
    r = variance.run({"sign_convention": "costs_positive",
                      "lines": [{"line": "Payroll", "type": "cost", "current": 300, "comparator": 310},
                                {"line": "Marketing", "type": "cost", "current": 95, "comparator": 60}],
                      "totals": [{"line": "Total opex", "of": ["Payroll", "Marketing"], "current": 395,
                                  "comparator": 370, "favourable_when": "lower"}]})
    t = r["totals"][0]
    assert t["current_ties"] and t["comparator_ties"] and t["direction"] == "A"


def test_variance_refuses_a_bad_favourable_when_on_a_total():
    with pytest.raises(variance.InputError, match="favourable_when"):
        variance.run({"lines": [{"line": "A", "type": "revenue", "current": 1, "comparator": 1}],
                      "totals": [{"line": "T", "of": ["A"], "current": 1, "comparator": 1, "favourable_when": "Higher"}]})


@pytest.mark.parametrize("current, comparator, rule, expected", [
    (0, 0, {"absolute": 25, "percent": 10}, False),
    (1, 0, {"absolute": 25, "percent": 10}, False),
    (30, 0, {"absolute": 25, "percent": 10}, True),
    (1, 0, {"percent": 10}, True),
])
def test_variance_materiality_against_a_zero_comparator(current, comparator, rule, expected):
    r = variance.run({"materiality": rule,
                      "lines": [{"line": "New", "type": "revenue", "current": current, "comparator": comparator}]})
    assert r["lines"][0]["material"] is expected


@pytest.mark.parametrize("pvm, message", [
    ({"line": "Missing", "items": [{"current_volume": 1, "current_price": 1, "comparator_volume": 1, "comparator_price": 1}]},
     "not a line in the table"),
    ({"type": "income", "items": [{"current_volume": 1, "current_price": 1, "comparator_volume": 1, "comparator_price": 1}]},
     "revenue or cost"),
])
def test_variance_refuses_a_bridge_it_cannot_place(pvm, message):
    with pytest.raises(variance.InputError, match=message):
        variance.run({"lines": [{"line": "Revenue", "type": "revenue", "current": 1, "comparator": 1}], "pvm": pvm})


def test_pvm_effects_add_up_exactly_and_match_the_share_formula():
    b = variance.run(example("variance-analysis"))["pvm"]
    effects = {e["name"]: e["value"] for e in b["effects"]}
    assert sum(effects.values()) == b["change"] == Decimal(25)
    assert effects["Volume"] == Decimal("-87.5") and effects["Price"] == Decimal(50)
    assert abs(b["residual"]) < Decimal("1e-20")
    assert b["gap_to_line"]["current"] == Decimal(40) and b["gap_to_line"]["comparator"] == 0


def test_pvm_on_a_cost_line_under_natural_sign():
    doc = {"lines": [{"line": "Freight", "type": "cost", "current": -120, "comparator": -100}],
           "pvm": {"line": "Freight", "items": [{"name": "Pallets", "current_volume": 12, "current_price": 10,
                                                 "comparator_volume": 10, "comparator_price": 10}]}}
    b = variance.run(doc)["pvm"]
    effects = {e["name"]: e for e in b["effects"]}
    assert effects["Volume"]["value"] == Decimal(-20) and effects["Volume"]["direction"] == "A"
    assert b["gap_to_line"] == {"current": Decimal(0), "comparator": Decimal(0)}


# Forecast accuracy

def test_accuracy_example():
    r = accuracy.run(example("forecast-accuracy"))
    by = {ln["line"]: ln for ln in r["lines"]}
    rev, cost, cash = by["Revenue"], by["Operating costs"], by["Closing cash"]
    assert rev["accuracy"]["total_error"] == Decimal(62) and rev["accuracy"]["reading"] == "optimistic"
    assert cost["accuracy"]["total_error"] == Decimal(16) and cost["accuracy"]["reading"] == "optimistic"
    assert rev["run_rate"]["step"] and not cost["run_rate"]["step"]
    assert rev["full_year"]["value"] == Decimal(4323)
    assert cash["full_year"]["value"] == Decimal(1100) and cash["full_year"]["basis"].startswith("balance")


def test_accuracy_costs_positive_reads_bias_the_other_way():
    doc = {"reference_month": "2027-02", "sign_convention": "costs_positive",
           "lines": [{"line": "Costs", "type": "cost", "actuals": {"2027-01": 100, "2027-02": 100},
                      "prior_forecast": {"2027-01": 90, "2027-02": 95}}]}
    assert accuracy.run(doc)["lines"][0]["accuracy"]["reading"] == "optimistic"


def test_accuracy_refuses_actuals_after_the_reference_month():
    doc = example("forecast-accuracy")
    doc["lines"][0]["actuals"]["2027-07"] = 1
    with pytest.raises(accuracy.InputError, match="after the reference month"):
        accuracy.run(doc)


def test_accuracy_refuses_a_full_year_month_with_no_source():
    doc = example("forecast-accuracy")
    del doc["lines"][0]["current_forecast"]["2027-09"]
    with pytest.raises(accuracy.InputError, match="no value for 2027-09"):
        accuracy.run(doc)


def test_accuracy_reads_a_balance_at_the_latest_month_whatever_the_order():
    doc = example("forecast-accuracy")
    months = doc["full_year_months"]
    doc["full_year_months"] = months[-1:] + months[:-1]
    cash = accuracy.run(doc)["lines"][2]["full_year"]
    assert cash["value"] == Decimal(1100) and cash["basis"].endswith("2027-12")


def test_accuracy_steady_burn_is_not_a_step():
    doc = {"reference_month": "2027-06", "run_rate_months": 3,
           "lines": [{"line": "Cash", "type": "balance",
                      "actuals": {"2027-03": 400, "2027-04": 350, "2027-05": 300, "2027-06": 250},
                      "current_forecast": {"2027-07": 200, "2027-08": 150, "2027-09": 100}}]}
    rr = accuracy.run(doc)["lines"][0]["run_rate"]
    assert rr["change"] == 0 and not rr["step"]


@pytest.mark.parametrize("window", ["3.5", 3.7, 0, True])
def test_accuracy_refuses_a_bad_run_rate_window(window):
    doc = example("forecast-accuracy")
    doc["run_rate_months"] = window
    with pytest.raises(accuracy.InputError, match="run_rate_months"):
        accuracy.run(doc)


def test_accuracy_refuses_a_positive_cost_under_natural_sign():
    with pytest.raises(accuracy.InputError, match="positive under the natural convention"):
        accuracy.run({"reference_month": "2027-02",
                      "lines": [{"line": "Costs", "type": "cost", "actuals": {"2027-01": 100, "2027-02": 100},
                                 "prior_forecast": {"2027-01": 110, "2027-02": 110}}]})


# Review findings: inputs that must be refused, and totals that must read correctly

@pytest.mark.parametrize("value", ["NaN", "Infinity", "-inf"])
def test_scripts_refuse_non_finite_figures(value):
    with pytest.raises(runway.InputError, match="finite"):
        runway.run({"opening": {"month": "2027-01", "balance": value}, "movements": [{"month": "2027-02", "amount": 1}]})
    with pytest.raises(variance.InputError, match="finite"):
        variance.run({"lines": [{"line": "A", "type": "revenue", "current": value, "comparator": 1}]})
    with pytest.raises(accuracy.InputError, match="finite"):
        accuracy.run({"reference_month": "2027-01", "lines": [{"line": "A", "actuals": {"2027-01": value}}]})


def test_negative_tolerances_and_thresholds_are_refused():
    with pytest.raises(runway.InputError, match="tie_tolerance"):
        runway.run({"opening": {"month": "2027-01", "balance": 1}, "movements": [{"month": "2027-02", "amount": 1}],
                    "tie_tolerance": -1})
    line = [{"line": "A", "type": "revenue", "current": 2, "comparator": 1}]
    with pytest.raises(variance.InputError, match="tie_tolerance"):
        variance.run({"lines": line, "tie_tolerance": -1})
    for key in ("absolute", "percent"):
        with pytest.raises(variance.InputError, match=f"materiality.{key}"):
            variance.run({"lines": line, "materiality": {key: -1}})


def test_pvm_refuses_a_negative_item_volume():
    with pytest.raises(variance.InputError, match="must not be negative"):
        variance.run({"lines": [{"line": "Revenue", "type": "revenue", "current": 1, "comparator": 1}],
                      "pvm": {"items": [{"current_volume": -1, "current_price": 1, "comparator_volume": 2, "comparator_price": 1},
                                        {"current_volume": 3, "current_price": 1, "comparator_volume": 2, "comparator_price": 1}]}})


@pytest.mark.parametrize("convention, sign", [("costs_positive", 1), ("natural", -1)])
def test_a_cost_only_total_reads_like_a_cost(convention, sign):
    r = variance.run({"sign_convention": convention,
                      "lines": [{"line": "Rent", "type": "cost", "current": sign * 30, "comparator": sign * 20},
                                {"line": "Fees", "type": "cost", "current": sign * 10, "comparator": sign * 10}],
                      "totals": [{"line": "Total costs", "of": ["Rent", "Fees"], "current": sign * 40,
                                  "comparator": sign * 30}]})
    assert r["totals"][0]["direction"] == "A" and r["totals"][0]["current_ties"]


def test_costs_positive_total_of_cost_and_other_adds_them():
    r = variance.run({"sign_convention": "costs_positive",
                      "lines": [{"line": "Rent", "type": "cost", "current": 30, "comparator": 30},
                                {"line": "Other expense", "type": "other", "current": 10, "comparator": 10}],
                      "totals": [{"line": "Total", "of": ["Rent", "Other expense"], "current": 40, "comparator": 40}]})
    assert r["totals"][0]["current_ties"] and r["totals"][0]["comparator_ties"]


def test_packager_finds_the_plugin_from_the_clone_root(tmp_path, monkeypatch):
    from cfo_os import skills as packager
    monkeypatch.setattr(packager, "SOURCE_PLUGIN", tmp_path / "site-packages" / "plugin")
    monkeypatch.chdir(ROOT)
    assert packager.main(["--out", str(tmp_path / "zips")]) == 0
    assert sorted(p.name for p in (tmp_path / "zips").iterdir()) == sorted(f"{s}.zip" for s in SCRIPTS)
    monkeypatch.chdir(tmp_path)
    assert packager.main(["--out", str(tmp_path / "none")]) == 2


@pytest.mark.parametrize("skill", sorted(SCRIPTS))
def test_skill_runs_its_script_from_its_own_folder(skill):
    text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    assert f'python "<skill folder>/scripts/{SCRIPTS[skill]}"' in text
    assert f"python scripts/{SCRIPTS[skill]}" not in text


# The skills as a whole

def test_there_are_skills_and_each_has_a_script():
    assert {d.name for d in skill_dirs(PLUGIN)} == set(SCRIPTS)


@pytest.mark.parametrize("skill", sorted(SCRIPTS))
def test_skill_is_well_formed(skill):
    assert skill_problems(SKILLS / skill) == []


@pytest.mark.parametrize("skill", sorted(SCRIPTS))
def test_skill_names_only_paths_the_template_ships(skill):
    text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    for rel in re.findall(r"`(Shared/[^`]+?\.md)`", text):
        assert (TEMPLATE / rel).is_file(), f"{skill}: {rel}"
    for other in re.findall(r"\(use ([a-z-]+)\)", text):
        assert other in SCRIPTS, f"{skill}: names unknown skill {other}"


@pytest.mark.parametrize("skill", sorted(SCRIPTS))
def test_skill_has_no_placeholders_and_a_fictional_example(skill):
    for p in (SKILLS / skill).rglob("*"):
        if p.is_file() and p.suffix in (".md", ".json", ".py"):
            assert "{" * 2 not in p.read_text(encoding="utf-8").replace("{{\"", ""), p
    assert "fictional" in (SKILLS / skill / "examples" / "input.example.json").read_text(encoding="utf-8")[:200].lower()


@pytest.mark.parametrize("skill", sorted(SCRIPTS))
def test_script_runs_from_the_command_line(skill, tmp_path):
    script = SKILLS / skill / "scripts" / SCRIPTS[skill]
    ok = subprocess.run([sys.executable, str(script), str(SKILLS / skill / "examples" / "input.example.json")],
                        capture_output=True, text=True, encoding="utf-8")
    assert ok.returncode == 0 and ok.stdout.startswith("# "), ok.stderr
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    refused = subprocess.run([sys.executable, str(script), str(bad)], capture_output=True, text=True, encoding="utf-8")
    assert refused.returncode == 1 and "input error" in refused.stderr


def test_plugin_and_marketplace_versions_follow_the_package():
    version = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    from cfo_os import __version__
    assert plugin["version"] == version == __version__
    assert market["plugins"][0].get("version", version) == version
    assert [p["name"] for p in market["plugins"]] == [plugin["name"]]
    assert market["plugins"][0]["source"] == "./plugin"


def test_package_is_reproducible_and_upload_shaped(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = package(SKILLS / "cash-runway", tmp_path / "a")
    second = package(SKILLS / "cash-runway", tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()
    names = zipfile.ZipFile(first).namelist()
    assert "cash-runway/SKILL.md" in names and "cash-runway/scripts/runway.py" in names
    assert not any("__pycache__" in n for n in names)
