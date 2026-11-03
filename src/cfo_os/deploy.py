"""Deploy a new CFO OS folder: the template, filled from an answers file, plus a metric
catalogue built from the connector's metric list.

    cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<path>/CFO OS"

The target must not exist or must be empty. Moving an existing folder to a newer template
is upgrade's job.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .catalogue import build as catalogue
from .common import (CATALOGUE, MANIFEST, Ownership, TemplateError, add_changelog_line,
                     auto_values, digest, fill, find_template, load_ownership, load_placeholders,
                     placeholders_in, read_text, regions, resolve_values, template_files,
                     write_manifest, write_text)


@dataclass
class Rendered:
    rel: str
    cls: str
    text: str


def load_answers(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise TemplateError(f"{path}: the answers file must be a YAML mapping")
    return data


def render_template(template: Path, ownership: Ownership, specs: dict[str, dict[str, Any]],
                    values: dict[str, str]) -> list[Rendered]:
    """Every template file, classified and filled. Fails on an unknown placeholder or a
    malformed region, so a broken template never reaches a folder."""
    out = []
    for rel in template_files(template):
        cls = ownership.classify(rel)
        text = read_text(template / rel)
        unknown = placeholders_in(text) - set(specs)
        if unknown:
            raise TemplateError(f"{rel}: unknown placeholder(s) {', '.join(sorted(unknown))}")
        regions(text, rel)
        out.append(Rendered(rel, cls, fill(text, values)))
    return out


def region_record(text: str, rel: str) -> dict[str, dict[str, str]]:
    return {r.id: {"applied": digest(r.text), "template": digest(r.text)} for r in regions(text, rel)}


def deploy(template: Path, answers: dict[str, Any], metrics: dict[str, Any], target: Path,
           deployer: str, today: str) -> list[str]:
    """Write the folder. Returns the paths written, relative to the folder."""
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise TemplateError(f"{target}: not empty; deploy writes only a new folder (use upgrade)")
    ownership = load_ownership()
    specs = load_placeholders()
    values, missing = resolve_values(answers, specs, auto_values(deployer, today))
    if missing:
        raise TemplateError("answers file is missing required value(s): " + ", ".join(sorted(missing)))
    files = render_template(template, ownership, specs, values)

    target.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "template": "cfo-ai-os",
        "template_version": __version__,
        "deployed": today,
        "deployer": deployer,
        "upgraded": None,
        "instructions_pasted_sha256": None,
        "values": values,
        "files": {},
    }
    written = []
    for f in files:
        write_text(target / f.rel, f.text)
        manifest["files"][f.rel] = {"class": f.cls, "regions": region_record(f.text, f.rel)}
        written.append(f.rel)
    for d in ownership.directories:
        (target / d).mkdir(parents=True, exist_ok=True)
    write_text(target / CATALOGUE, catalogue.render(metrics, today))
    manifest["files"][CATALOGUE] = {"class": "generated", "regions": {}}
    written.append(CATALOGUE)
    add_changelog_line(target, f"- {today}: deployed from template {__version__} by {deployer}.")
    write_manifest(target, manifest)
    written.append(MANIFEST)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os deploy", description=__doc__.splitlines()[0])
    ap.add_argument("--answers", type=Path, required=True)
    ap.add_argument("--metrics", type=Path, required=True)
    ap.add_argument("--metrics-from", default="auto", choices=("auto", "neutral", "datarails"))
    ap.add_argument("--target", type=Path, required=True)
    ap.add_argument("--deployer", default=None)
    ap.add_argument("--template", default=None, help="the template/CFO OS folder to deploy from")
    ap.add_argument("--date", default=date.today().isoformat(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    try:
        written = deploy(find_template(args.template), load_answers(args.answers),
                         catalogue.load_metrics(args.metrics, args.metrics_from), args.target,
                         args.deployer or getpass.getuser(), args.date)
    except (TemplateError, OSError, ValueError, yaml.YAMLError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"deployed template {__version__} to {args.target}: {len(written)} files")
    print("next: paste '00 System/Instructions.md' into the Claude Project, then run "
          "'cfo-os pasted' and 'cfo-os check' on the folder")
    return 0
