"""The template itself is well formed. Fixtures are fictional."""

from __future__ import annotations

import json
import re

import pytest
import yaml

from .cfo_os_paths import EXAMPLES, ROOT  # noqa: F401  (also puts src on the path)
from cfo_os.common import (load_ownership, load_placeholders, placeholders_in, read_text,
                           regions, template_files)

WORKFLOW_HEADINGS = ["## Trigger", "## Inputs", "## Steps", "## Checks every output carries",
                     "## Output", "## Where it is filed"]


def test_every_template_file_has_one_ownership_class(template):
    ownership = load_ownership()
    for rel in template_files(template):
        assert ownership.classify(rel) in ("system", "context", "generated", "client"), rel


def test_template_names_only_known_placeholders_and_uses_every_answer(template):
    specs = load_placeholders()
    used: set[str] = set()
    for rel in template_files(template):
        names = placeholders_in(read_text(template / rel))
        assert not names - set(specs), f"{rel}: {names - set(specs)}"
        used |= names
    unused = {n for n, s in specs.items() if not s.get("auto")} - used
    assert not unused, f"placeholders no template file uses: {sorted(unused)}"


def test_block_placeholders_sit_alone_on_their_line(template):
    specs = load_placeholders()
    block = {n for n, s in specs.items() if s["form"] in ("list", "table")}
    for rel in template_files(template):
        for n, line in enumerate(read_text(template / rel).splitlines(), 1):
            for name in placeholders_in(line) & block:
                assert line.strip() == "{" * 2 + name + "}" * 2, f"{rel}:{n}"


def test_regions_parse_and_system_files_have_them(template):
    ownership = load_ownership()
    for rel in template_files(template):
        found = regions(read_text(template / rel), rel)
        cls = ownership.classify(rel)
        if cls != "system":
            assert not found, f"{rel}: only system files carry template regions"
        elif rel != "Shared/Claude/Changelog.md":
            assert found, f"{rel}: a system file needs at least one template region"


def _workflows(template):
    folder = template / "Shared" / "Workflows"
    return sorted(p for p in folder.iterdir() if p.is_file() and p.name != "Workflow template.md")


def test_workflows_follow_the_workflow_template(template):
    workflows = _workflows(template)
    assert len(workflows) == 10
    for path in workflows:
        text = read_text(path)
        positions = [text.find(h) for h in WORKFLOW_HEADINGS]
        assert all(p >= 0 for p in positions), f"{path.name}: missing a workflow heading"
        assert positions == sorted(positions), f"{path.name}: workflow headings out of order"


def test_each_workflow_trigger_begins_with_its_cadence(template):
    for path in _workflows(template):
        lines = read_text(path).splitlines()
        after = lines[lines.index("## Trigger") + 1:]
        first = next(line for line in after if line.strip() and not line.startswith("<!--"))
        assert re.match(r"(Monthly|Quarterly|Annual|On request)\.", first), f"{path.name}: {first}"


REMOVED_NAMES = re.compile(r"\b0\d |START HERE|Folder map|Every session|Start session|Close session|"
                           r"Key findings\.md|Decisions\.md|Open questions\.md|Lessons\.md")


def test_no_template_file_names_a_removed_file_or_folder(template):
    for rel in template_files(template):
        for n, line in enumerate(read_text(template / rel).splitlines(), 1):
            assert not REMOVED_NAMES.search(line), f"{rel}:{n}: {line}"


def test_tier_folders_hold_the_same_files(template):
    def files(tier):
        return sorted(p.relative_to(template / tier).as_posix()
                      for p in (template / tier).rglob("*") if p.is_file())
    assert files("CFO") == files("VP") == files("Team") == ["Memory/Log.md", "Memory/Now.md", "Role.md"]


def test_instructions_keep_client_sections_outside_template_regions(template):
    text = read_text(template / "Shared/Claude/Instructions.md")
    inside = "\n".join(r.text for r in regions(text))
    for heading in ("## Key facts", "## How we work", "## Hypotheses", "## Standard analyses"):
        assert heading in text and heading not in inside, heading


def test_no_lock_or_duplicate_files_in_template(template):
    for rel in template_files(template):
        assert not re.search(r"-\d\.\w+$", rel), rel
        assert not rel.split("/")[-1].startswith("~$"), rel


def test_answers_schema_covers_every_placeholder_root():
    schema = json.loads((ROOT / "schemas" / "answers.schema.json").read_text(encoding="utf-8"))
    roots = {n.split(".")[0] for n, s in load_placeholders().items() if not s.get("auto")}
    assert set(schema["properties"]) == roots


def test_examples_validate_against_the_schemas():
    jsonschema = pytest.importorskip("jsonschema")
    answers = yaml.safe_load((EXAMPLES / "answers.example.yaml").read_text(encoding="utf-8"))
    metrics = json.loads((EXAMPLES / "metrics.example.json").read_text(encoding="utf-8"))
    for name, doc in (("answers", answers), ("metrics", metrics)):
        schema = json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(doc, schema)


def test_examples_say_they_are_fictional():
    for p in EXAMPLES.iterdir():
        assert "fictional" in p.read_text(encoding="utf-8")[:200].lower(), p.name
