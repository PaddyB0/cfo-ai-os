"""Build the setup prompt, `SETUP.md`: one self-contained file a person pastes into Claude to
set up a CFO OS folder, with every template file in it.

    cfo-os prompt [--out SETUP.md | --check SETUP.md]

It fills the `[[slot]]`s of `setup_prompt.md` (shipped with this package) from the template,
`placeholders.yaml` and the fictional example metric list. The output has no dates in it, so
the same repository always gives the same file. --check exits 1 when the file on disk is not
what this repository builds.

This is a repository command, like scrub: it reads `examples/metrics.example.json` from the
clone, which is not packaged.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .catalogue import build as catalogue
from .common import (CATALOGUE, MANIFEST, PACKAGE, TemplateError, find_template, load_placeholders,
                     read_text, template_files, tier_of)

SOURCE = PACKAGE / "setup_prompt.md"
SLOT_RE = re.compile(r"\[\[([a-z_]+)\]\]")
FENCE = "~~~~"
EXAMPLE_DATE = "2027-01-15"  # fixed and fictional, so the output never changes by day


def _cell(text: Any) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _default(spec: dict[str, Any]) -> str:
    return "`" + " ".join(str(spec.get("default", "")).split()) + "`"


def _table(head: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def questions(specs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """The three question tables: connector, person and optional person answers."""
    connector, person, optional = [], [], []
    for name, spec in specs.items():
        if spec.get("auto"):
            continue
        source = spec.get("source")
        if source not in ("connector", "person"):
            raise TemplateError(f"placeholders.yaml: {name} has no source (connector or person)")
        meaning = _cell(spec.get("meaning", ""))
        if source == "connector":
            if not spec.get("required"):
                meaning += f" Optional; default {_default(spec)}."
            connector.append([f"`{name}`", meaning, spec["form"]])
        elif spec.get("required"):
            person.append([f"`{name}`", meaning, spec["form"]])
        else:
            optional.append([f"`{name}`", meaning, spec["form"], _default(spec)])
    return {
        "questions_connector": _table(["Name", "What it is", "Form"], connector),
        "questions_person": _table(["Name", "What it is", "Form"], person),
        "questions_optional": _table(["Name", "What it is", "Form", "Default"], optional),
    }


def file_list(template: Path) -> str:
    rels = sorted(template_files(template) + [CATALOGUE, MANIFEST])
    out = []
    for rel in rels:
        tier = tier_of(rel)
        out.append(f"- `{rel}`" + (f" ({tier} tier only)" if tier else ""))
    return "\n".join(out)


def catalogue_example(metrics_path: Path) -> str:
    text = catalogue.render(catalogue.load_metrics(metrics_path), EXAMPLE_DATE).rstrip("\n")
    return f"{FENCE}markdown\n{text}\n{FENCE}"


def manifest_example(version: str) -> str:
    example = {
        "template": "cfo-ai-os",
        "template_version": version,
        "deployed": EXAMPLE_DATE,
        "deployer": "Alex Example",
        "deployed_by_hand": True,
        "tiers": ["CFO", "VP"],
        "answers": {
            "company": {"name": "Example Instruments Ltd", "reporting_currency": "GBP"},
            "cfo": {"name": "Alex Example", "title": "CFO"},
            "people": [{"name": "Alex Example", "role": "CFO", "tier": "CFO", "receives": "Everything"}],
        },
    }
    body = json.dumps(example, indent=2, ensure_ascii=False)
    return ("A fictional example. It shows the shape, not every answer.\n\n"
            f"{FENCE}json\n{body}\n{FENCE}\n\n"
            "`answers` holds every answer from step 1, required and optional, under its nested "
            "key, the same way `company.name` sits as `name` under `company`. A list answer is "
            "a JSON list of strings. A table answer is a JSON list of objects whose keys are "
            "lower case with `_` for a space. Leave out the three `deploy` values, which the "
            "fields above already hold. Write `deployed_by_hand` as `true` and do not add "
            "`values` or `files`. If metrics were left out of the catalogue in step 1.5, add "
            "`catalogue_exclude` next to `tiers`: a JSON list of their ids, each as a string. "
            "The tool reads it when the catalogue is next regenerated.")


def payload(template: Path) -> str:
    parts = []
    for rel in template_files(template):
        text = read_text(template / rel).replace("\r\n", "\n")
        for n, line in enumerate(text.split("\n"), 1):
            if line.startswith(FENCE):
                raise TemplateError(f"{rel}:{n}: a line starts with {FENCE}, which would end its "
                                    "block in the setup prompt")
        parts.append(f"### File: {rel}\n\n{FENCE}markdown\n{text.rstrip(chr(10))}\n{FENCE}")
    return "\n\n".join(parts)


def build(template: Path, metrics_path: Path, version: str = __version__,
          source: Path = SOURCE) -> str:
    """The setup prompt. Fails on an unknown slot or one left unfilled."""
    specs = load_placeholders()
    slots = {"version": version, **questions(specs), "file_list": file_list(template),
             "catalogue_example": catalogue_example(metrics_path),
             "manifest_example": manifest_example(version), "payload": payload(template)}
    text = read_text(source).replace("\r\n", "\n")
    unknown = sorted(set(SLOT_RE.findall(text)) - set(slots))
    if unknown:
        raise TemplateError(f"{source.name}: unknown slot(s) {', '.join(unknown)}")
    # One pass, so text placed in a slot is never itself read as a slot.
    out = SLOT_RE.sub(lambda m: slots[m.group(1)], text)
    if "[[" in out:
        line = next(l for l in out.split("\n") if "[[" in l)
        raise TemplateError(f"the setup prompt still holds '[[' after filling: {line.strip()}")
    return out if out.endswith("\n") else out + "\n"


def default_metrics(template: Path) -> Path:
    path = template.parent.parent / "examples" / "metrics.example.json"
    if not path.is_file():
        raise TemplateError(f"{path}: not found; run cfo-os prompt from a clone of the repository")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os prompt", description=__doc__.splitlines()[0])
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--out", type=Path, default=None, help="write the prompt to this file")
    group.add_argument("--check", type=Path, default=None,
                       help="exit 1 if this file is not what the repository builds")
    ap.add_argument("--template", default=None, help="the template/CFO OS folder")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        template = find_template(args.template)
        text = build(template, default_metrics(template))
        if args.check:
            on_disk = read_text(args.check).replace("\r\n", "\n") if args.check.is_file() else None
            if on_disk != text:
                print(f"{args.check}: stale; run cfo-os prompt --out {args.check}", file=sys.stderr)
                return 1
            print(f"{args.check}: up to date")
            return 0
        if args.out:
            with open(args.out, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"wrote {args.out}: {len(text)} characters")
            return 0
        sys.stdout.write(text)
    except (TemplateError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0
