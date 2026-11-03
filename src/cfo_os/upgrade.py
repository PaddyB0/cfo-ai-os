"""Move a deployed CFO OS folder to this template version without touching what the CFO or
Claude wrote. A dry run unless --apply is passed.

    cfo-os upgrade --folder "<path>/CFO OS" [--apply] [--catalogue metrics.json] [--accept-edited]

- A template region whose text is as the template last wrote it is replaced.
- A region someone edited is left alone; the new text goes into the upgrade report.
- New template files are added. Files the template no longer has are listed, never deleted.
- Context files are never written; headings the new template adds are reported as suggestions.
- Client files are never opened.
- --accept-edited records the template text offered for edited regions as seen, after a
  person has merged the report, so they are not reported again until the template changes.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .catalogue import build as catalogue
from .common import (CATALOGUE, MANIFEST, TemplateError, add_changelog_line, digest,
                     find_template, is_empty, load_manifest, load_ownership, load_placeholders,
                     lookup, read_text, regions, render_value, replace_regions, unknown_answers,
                     write_manifest, write_text)
from .deploy import load_answers, region_record, render_template


@dataclass
class Plan:
    adds: dict[str, str] = field(default_factory=dict)            # rel -> text
    rewrites: dict[str, str] = field(default_factory=dict)        # rel -> new file text
    replaced: list[str] = field(default_factory=list)             # "rel#region"
    review: list[tuple[str, str, str, str]] = field(default_factory=list)  # rel, id, why, text
    removed_regions: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)
    suggestions: list[tuple[str, list[str]]] = field(default_factory=list)
    catalogue: str | None = None
    manifest: dict[str, Any] = field(default_factory=dict)

    def changes(self) -> bool:
        return bool(self.adds or self.rewrites or self.review or self.removed_regions
                    or self.removed_files or self.suggestions or self.catalogue is not None)


def _version(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split(".") if p.isdigit())


def _headings(text: str) -> list[str]:
    return [l.strip() for l in text.replace("\r\n", "\n").split("\n") if l.startswith("#")]


def upgrade_values(manifest: dict[str, Any], answers: dict[str, Any] | None,
                   specs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """The values the folder was deployed with, any new answers on top, defaults for new
    optional placeholders, and this template's version."""
    unknown = unknown_answers(answers or {}, specs)
    if unknown:
        raise TemplateError("answers file has key(s) no placeholder reads (misspelt?): " + ", ".join(unknown))
    recorded = manifest.get("values") or {}
    auto = {"deploy.version": __version__,
            "deploy.date": recorded.get("deploy.date", manifest.get("deployed", "")),
            "deploy.deployer": recorded.get("deploy.deployer", manifest.get("deployer", ""))}
    values: dict[str, str] = {}
    missing: list[str] = []
    for name, spec in specs.items():
        if spec.get("auto"):
            values[name] = auto[name]
            continue
        raw = lookup(answers or {}, name)
        if not is_empty(raw):
            values[name] = render_value(name, spec["form"], raw)
        elif name in recorded:
            values[name] = recorded[name]
        elif spec.get("required"):
            missing.append(name)
        else:
            values[name] = render_value(name, spec["form"], spec.get("default", ""))
    if missing:
        raise TemplateError("the folder has no value for new required placeholder(s) "
                            f"{', '.join(sorted(missing))}; pass --answers with them")
    return values


def plan_upgrade(folder: Path, template: Path, answers: dict[str, Any] | None = None,
                 metrics: dict[str, Any] | None = None, accept_edited: bool = False,
                 today: str | None = None) -> Plan:
    today = today or date.today().isoformat()
    manifest = load_manifest(folder)
    if _version(manifest.get("template_version", "0")) > _version(__version__):
        raise TemplateError(f"the folder is on {manifest['template_version']}, newer than this "
                            f"template ({__version__}); upgrade never moves a folder back")
    ownership = load_ownership()
    specs = load_placeholders()
    values = upgrade_values(manifest, answers, specs)
    files = render_template(template, ownership, specs, values)
    recorded_files: dict[str, Any] = manifest.get("files", {})
    plan = Plan()
    new_files: dict[str, Any] = {}

    for f in files:
        path = folder / f.rel
        if not path.exists():
            if f.rel in recorded_files:
                # Deployed before and since moved or removed by a person: leave it gone.
                new_files[f.rel] = recorded_files[f.rel]
                continue
            plan.adds[f.rel] = f.text
            new_files[f.rel] = {"class": f.cls, "regions": region_record(f.text, f.rel)}
            continue
        if f.cls == "client":
            new_files[f.rel] = recorded_files.get(f.rel, {"class": "client", "regions": {}})
            continue
        if f.cls == "generated":
            new_files[f.rel] = recorded_files.get(f.rel, {"class": "generated", "regions": {}})
            continue
        current = read_text(path)
        if f.cls == "context":
            record = dict(recorded_files.get(f.rel) or {"class": "context", "regions": {}})
            offered = set(record.get("suggested") or [])
            have = set(_headings(current))
            extra = [h for h in _headings(f.text) if h not in have and h not in offered]
            if extra:
                plan.suggestions.append((f.rel, extra))
                # Remembered, so the same heading is suggested once, not on every upgrade.
                record["suggested"] = sorted(offered | set(extra))
            new_files[f.rel] = record
            continue
        # system: template regions only
        old_record = (recorded_files.get(f.rel) or {}).get("regions", {})
        have = {r.id: r for r in regions(current, f.rel)}
        record: dict[str, dict[str, Any]] = {}
        replace: dict[str, str] = {}
        for r in regions(f.text, f.rel):
            new_hash = digest(r.text)
            seen = old_record.get(r.id) or {}
            if r.id not in have:
                if seen.get("template") != new_hash:
                    plan.review.append((f.rel, r.id, "new region; add it where it belongs", r.text))
                record[r.id] = {"applied": None,
                                "template": new_hash if accept_edited else seen.get("template")}
                continue
            cur_hash = digest(have[r.id].text)
            if cur_hash == new_hash:
                record[r.id] = {"applied": new_hash, "template": new_hash}
            elif seen.get("applied") == cur_hash:
                replace[r.id] = r.text
                plan.replaced.append(f"{f.rel}#{r.id}")
                record[r.id] = {"applied": new_hash, "template": new_hash}
            else:
                if seen.get("template") != new_hash:
                    plan.review.append((f.rel, r.id, "edited in the folder; merge by hand", r.text))
                record[r.id] = {"applied": seen.get("applied"),
                                "template": new_hash if accept_edited else seen.get("template")}
        for rid in have:
            if rid in record:
                continue
            if not (old_record.get(rid) or {}).get("removed"):
                plan.removed_regions.append(f"{f.rel}#{rid}")
            # Remembered as removed, so a later upgrade does not report it again.
            record[rid] = {"applied": None, "template": None, "removed": True}
        if replace:
            plan.rewrites[f.rel] = replace_regions(current, replace)
        new_files[f.rel] = {"class": f.cls, "regions": record}

    template_rels = {f.rel for f in files} | {CATALOGUE, MANIFEST}
    plan.removed_files = sorted(r for r in recorded_files if r not in template_rels)
    new_files[CATALOGUE] = recorded_files.get(CATALOGUE, {"class": "generated", "regions": {}})
    if metrics is not None:
        plan.catalogue = catalogue.render(metrics, today)

    plan.manifest = {**manifest, "template_version": __version__, "upgraded": today,
                     "values": values, "files": new_files}
    return plan


def report_text(plan: Plan, old: str, today: str) -> str:
    lines = [f"# Upgrade report {today}", "",
             f"Template {old} to {__version__}. Each section below is template text that was not "
             "applied because the folder's copy was edited, or because it is new and its place "
             "needs a person. Merge what you want, then run the upgrade with --accept-edited.", ""]
    for rel, rid, why, text in plan.review:
        lines += [f"## {rel}: {rid}", "", why + ".", "", "~~~~markdown", text, "~~~~", ""]
    for rel, heads in plan.suggestions:
        lines += [f"## {rel}: suggested sections", "",
                  "The template now has these headings; add them if they apply.", ""]
        lines += [f"- `{h}`" for h in heads] + [""]
    if plan.removed_regions or plan.removed_files:
        lines += ["## No longer in the template", "", "Left in place. Remove by hand if unused.", ""]
        lines += [f"- {x}" for x in plan.removed_regions + plan.removed_files] + [""]
    return "\n".join(lines)


def apply_plan(folder: Path, plan: Plan, today: str) -> str | None:
    old = load_manifest(folder).get("template_version", "?")
    if not plan.changes() and old == __version__:
        return None
    for rel, text in plan.adds.items():
        write_text(folder / rel, text)
    for rel, text in plan.rewrites.items():
        write_text(folder / rel, text)
    for d in load_ownership().directories:
        if (folder / d).parent.is_dir():
            (folder / d).mkdir(exist_ok=True)
    if plan.catalogue is not None:
        write_text(folder / CATALOGUE, plan.catalogue)
    report = None
    if plan.review or plan.suggestions or plan.removed_regions or plan.removed_files:
        report = f"00 System/Upgrade report {today}.md"
        write_text(folder / report, report_text(plan, old, today))
    tail = f" {len(plan.review)} left for review in '{report}'." if plan.review and report else ""
    add_changelog_line(folder, f"- {today}: upgraded from template {old} to {__version__}; "
                               f"{len(plan.replaced)} regions replaced, {len(plan.adds)} files added.{tail}")
    write_manifest(folder, plan.manifest)
    return report


def describe(plan: Plan) -> list[str]:
    out = [f"add      {r}" for r in plan.adds]
    out += [f"replace  {r}" for r in plan.replaced]
    out += [f"review   {rel}#{rid}: {why}" for rel, rid, why, _ in plan.review]
    out += [f"suggest  {rel}: {', '.join(h)}" for rel, h in plan.suggestions]
    out += [f"removed  {r} (left in place)" for r in plan.removed_regions + plan.removed_files]
    if plan.catalogue is not None:
        out.append(f"regen    {CATALOGUE}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os upgrade", description=__doc__.splitlines()[0])
    ap.add_argument("--folder", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--to", default=None, help="refuse unless this template is that version")
    ap.add_argument("--answers", type=Path, default=None, help="values for new placeholders")
    ap.add_argument("--catalogue", type=Path, default=None, help="regenerate the metric catalogue")
    ap.add_argument("--metrics-from", default="auto", choices=("auto", "neutral", "datarails"))
    ap.add_argument("--accept-edited", action="store_true")
    ap.add_argument("--template", default=None)
    ap.add_argument("--date", default=date.today().isoformat(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if args.to and args.to.lstrip("v") != __version__:
            raise TemplateError(f"this template is {__version__}, not {args.to}; check out that tag")
        answers = load_answers(args.answers) if args.answers else None
        metrics = catalogue.load_metrics(args.catalogue, args.metrics_from) if args.catalogue else None
        plan = plan_upgrade(args.folder, find_template(args.template), answers, metrics,
                            args.accept_edited, args.date)
        lines = describe(plan)
        print("\n".join(lines) if lines else "nothing to change")
        if not args.apply:
            for rel, rid, why, text in plan.review:
                print(f"\n--- {rel}#{rid} ({why}) ---\n{text}")
            print("\ndry run; pass --apply to write")
            return 0
        report = apply_plan(args.folder, plan, args.date)
        print(f"applied; folder now on template {__version__}" + (f"; see '{report}'" if report else ""))
    except (TemplateError, OSError, ValueError, yaml.YAMLError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0
