"""Deploy a new CFO OS folder: the template, filled from an answers file, plus a metric
catalogue built from the connector's metric list.

    cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<path>/CFO OS"
                  [--tiers CFO,VP,Team]

The target must not exist or must be empty. A target holding only `setup check.txt`, the
setup prompt's write test, counts as empty and the file is removed. Moving an existing folder
to a newer template is upgrade's job.

--tiers names the tier folders to write (default CFO; CFO is always included). Files under a
tier folder not named are not written.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import __version__
from .catalogue import build as catalogue
from .common import (CATALOGUE, MANIFEST, TIERS, Ownership, TemplateError, add_changelog_line,
                     auto_values, digest, fill, find_template, in_tiers, load_ownership,
                     load_placeholders, parse_tiers, placeholders_in, read_text, regions,
                     resolve_values, template_files, unknown_answers, write_manifest, write_text)

SETUP_CHECK = "setup check.txt"


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
                    values: dict[str, str], tiers: Iterable[str] = TIERS) -> list[Rendered]:
    """Every template file for the given tiers, classified and filled. Fails on an unknown
    placeholder or a malformed region, so a broken template never reaches a folder."""
    tiers = tuple(tiers)
    out = []
    for rel in template_files(template):
        if not in_tiers(rel, tiers):
            continue
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


def _only_setup_check(target: Path) -> bool:
    children = list(target.iterdir())
    return len(children) == 1 and children[0].name == SETUP_CHECK and children[0].is_file()


def deploy(template: Path, answers: dict[str, Any], metrics: dict[str, Any], target: Path,
           deployer: str, today: str, tiers: str | Iterable[str] = ("CFO",),
           catalogue_exclude: str | Iterable[Any] | None = None) -> list[str]:
    """Write the folder. Returns the paths written, relative to the folder. Metric ids in
    `catalogue_exclude` are left out of the shared catalogue and recorded in the manifest, so
    a later regeneration leaves them out too."""
    tiers = parse_tiers(tiers)
    left_out = catalogue.parse_exclude(catalogue_exclude)
    setup_check = False
    if target.exists():
        if not target.is_dir():
            raise TemplateError(f"{target}: not a folder")
        setup_check = _only_setup_check(target)
        if not setup_check and any(target.iterdir()):
            raise TemplateError(f"{target}: not empty; deploy writes only a new folder (use upgrade)")
    ownership = load_ownership()
    specs = load_placeholders()
    unknown = unknown_answers(answers, specs)
    if unknown:
        raise TemplateError("answers file has key(s) no placeholder reads (misspelt?): " + ", ".join(unknown))
    values, missing = resolve_values(answers, specs, auto_values(deployer, today))
    if missing:
        raise TemplateError("answers file is missing required value(s): " + ", ".join(sorted(missing)))
    # Everything is rendered before the first write, so bad input never leaves a half-built folder.
    files = render_template(template, ownership, specs, values, tiers)
    catalogue_text = catalogue.render(catalogue.exclude(metrics, left_out, strict=True), today)

    if setup_check:
        (target / SETUP_CHECK).unlink()
    target.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "template": "cfo-ai-os",
        "template_version": __version__,
        "deployed": today,
        "deployer": deployer,
        "upgraded": None,
        "tiers": list(tiers),
        "values": values,
        "files": {},
    }
    if left_out:
        manifest["catalogue_exclude"] = left_out
    written = []
    for f in files:
        write_text(target / f.rel, f.text)
        manifest["files"][f.rel] = {"class": f.cls, "regions": region_record(f.text, f.rel)}
        written.append(f.rel)
    for d in ownership.directories:
        if in_tiers(d, tiers):
            (target / d).mkdir(parents=True, exist_ok=True)
    write_text(target / CATALOGUE, catalogue_text)
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
    ap.add_argument("--tiers", default="CFO",
                    help="tier folders to write, comma separated: CFO, VP, Team (default CFO)")
    ap.add_argument("--catalogue-exclude", default=None,
                    help="metric ids to leave out of the shared metric catalogue, comma separated")
    ap.add_argument("--template", default=None, help="the template/CFO OS folder to deploy from")
    ap.add_argument("--date", default=date.today().isoformat(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    try:
        metrics = catalogue.load_metrics(args.metrics, args.metrics_from)
        written = deploy(find_template(args.template), load_answers(args.answers), metrics,
                         args.target, args.deployer or getpass.getuser(), args.date, args.tiers,
                         args.catalogue_exclude)
    except (TemplateError, OSError, ValueError, yaml.YAMLError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for line in catalogue.formula_mentions(metrics, args.catalogue_exclude):
        print(f"warning: {line}", file=sys.stderr)
    print(f"deployed template {__version__} to {args.target}: {len(written)} files")
    print("next: paste the one line from 'Read me first.md' into the Claude Project "
          "instructions, then run 'cfo-os check' on the folder")
    return 0
