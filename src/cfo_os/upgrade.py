"""Move a deployed CFO OS folder to this template version without touching what the CFO or
Claude wrote. A dry run unless --apply is passed.

    cfo-os upgrade --folder "<path>/CFO OS" [--apply] [--tiers CFO,VP] [--catalogue metrics.json]
                   [--catalogue-exclude <id>,<id>] [--accept-edited] [--take-template]

- A template region whose text is as the template last wrote it is replaced.
- A region someone edited is left alone; the new text goes into the upgrade report.
- New template files are added. Files the template no longer has are listed, never deleted.
- Context files are never written; headings the new template adds are reported as suggestions.
- Client files are never opened.
- The tiers come from the manifest. --tiers may add a tier, whose files are then added; it
  may not remove one. A tier folder that cannot be seen is warned about and left alone.
- --accept-edited records the template text offered for edited regions as seen, after a
  person has merged the report, so they are not reported again until the template changes.
- --take-template replaces every region whose text differs from the template, on any folder.
  It overwrites edits made inside template regions, and the dry run lists each one.
- A folder set up by hand (the setup prompt's Route B) has no region hashes. Each region equal
  to the template is recorded; one that differs is reported, or replaced with --take-template.
  After --apply its manifest is in the normal form.
- --catalogue regenerates the metric catalogue, leaving out the metric ids the manifest lists
  as catalogue_exclude. --catalogue-exclude sets that list; an empty value clears it.
- A folder on the 0.2 layout is refused; see docs/upgrade.md, "Moving from 0.2".
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
from .common import (CATALOGUE, MANIFEST, TIERS, TemplateError, add_changelog_line, auto_values,
                     digest, find_template, in_tiers, is_empty, load_manifest, load_ownership,
                     load_placeholders, lookup, parse_tiers, read_text, regions, render_value,
                     replace_regions, resolve_values, tier_of, unknown_answers, write_manifest,
                     write_text)
from .deploy import load_answers, region_record, render_template

HAND_REVIEW = "differs from the template; the folder was set up by hand"
EDITED_REVIEW = "edited in the folder; merge by hand"
NEW_REGION_REVIEW = "new region; add it where it belongs"
# Keys only a hand-deployed (or older) manifest carries; the normal form drops them.
DROPPED_KEYS = ("deployed_by_hand", "answers", "instructions_pasted_sha256")


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
    tiers: tuple[str, ...] = ()
    added_tiers: tuple[str, ...] = ()
    unseen_tiers: tuple[str, ...] = ()
    by_hand: bool = False
    overwritten: list[str] = field(default_factory=list)          # "rel#region", edits replaced
    left_out: int = 0                                             # metrics kept out of the catalogue

    def changes(self) -> bool:
        return bool(self.adds or self.rewrites or self.review or self.removed_regions
                    or self.removed_files or self.suggestions or self.catalogue is not None
                    or self.added_tiers or self.by_hand)

    def warnings(self) -> list[str]:
        return [f"the {t} folder could not be seen and was not upgraded; whoever runs the "
                "upgrade may lack access to it" for t in self.unseen_tiers]


def _version(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split(".") if p.isdigit())


def _headings(text: str) -> list[str]:
    return [l.strip() for l in text.replace("\r\n", "\n").split("\n") if l.startswith("#")]


def recorded_values(manifest: dict[str, Any], specs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """The values the folder was deployed with. A hand-deployed folder records its answers, so
    they are resolved the way deploy resolves them."""
    if not manifest.get("deployed_by_hand"):
        return dict(manifest.get("values") or {})
    answers = manifest.get("answers") or {}
    if not isinstance(answers, dict):
        raise TemplateError(f"{MANIFEST}: answers must be a mapping")
    unknown = unknown_answers(answers, specs)
    if unknown:
        raise TemplateError(f"{MANIFEST}: answers has key(s) no placeholder reads: " + ", ".join(unknown))
    values, _missing = resolve_values(answers, specs, auto_values(
        str(manifest.get("deployer", "")), str(manifest.get("deployed", ""))))
    return values


def upgrade_values(manifest: dict[str, Any], answers: dict[str, Any] | None,
                   specs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """The values the folder was deployed with, any new answers on top, defaults for new
    optional placeholders, and this template's version."""
    unknown = unknown_answers(answers or {}, specs)
    if unknown:
        raise TemplateError("answers file has key(s) no placeholder reads (misspelt?): " + ", ".join(unknown))
    recorded = recorded_values(manifest, specs)
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
            values[name] = render_value(name, spec["form"], raw, spec.get("choices"))
        elif name in recorded:
            values[name] = recorded[name]
        elif spec.get("required"):
            missing.append(name)
        else:
            values[name] = render_value(name, spec["form"], spec.get("default", ""),
                                        spec.get("choices"))
    if missing:
        raise TemplateError("the folder has no value for new required placeholder(s) "
                            f"{', '.join(sorted(missing))}; pass --answers with them")
    return values


def upgrade_tiers(manifest: dict[str, Any], requested: str | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(the tiers after the upgrade, the tiers it adds)."""
    have = parse_tiers(manifest.get("tiers") or [TIERS[0]])
    if requested is None:
        return have, ()
    want = parse_tiers(requested)
    dropped = [t for t in have if t not in want]
    if dropped:
        raise TemplateError(f"--tiers may add a tier but not remove one; the folder has "
                            f"{', '.join(have)}, so --tiers must include {', '.join(dropped)}")
    return want, tuple(t for t in want if t not in have)


def plan_upgrade(folder: Path, template: Path, answers: dict[str, Any] | None = None,
                 metrics: dict[str, Any] | None = None, accept_edited: bool = False,
                 today: str | None = None, tiers: str | None = None,
                 take_template: bool = False, catalogue_exclude: str | None = None) -> Plan:
    today = today or date.today().isoformat()
    manifest = load_manifest(folder)
    if catalogue_exclude is not None and metrics is None:
        raise TemplateError("--catalogue-exclude needs --catalogue, the metric list to "
                            "regenerate the catalogue from")
    if _version(manifest.get("template_version", "0")) > _version(__version__):
        raise TemplateError(f"the folder is on {manifest['template_version']}, newer than this "
                            f"template ({__version__}); upgrade never moves a folder back")
    by_hand = bool(manifest.get("deployed_by_hand"))
    in_use, added = upgrade_tiers(manifest, tiers)
    unseen = tuple(t for t in in_use if t not in added and not (folder / t).is_dir())
    ownership = load_ownership()
    specs = load_placeholders()
    values = upgrade_values(manifest, answers, specs)
    files = render_template(template, ownership, specs, values, in_use)
    recorded_files: dict[str, Any] = {} if by_hand else dict(manifest.get("files") or {})
    plan = Plan(tiers=in_use, added_tiers=added, unseen_tiers=unseen, by_hand=by_hand)
    new_files: dict[str, Any] = {}

    for f in files:
        if tier_of(f.rel) in unseen:
            # Not visible to whoever runs this: leave its record as it was.
            if f.rel in recorded_files:
                new_files[f.rel] = recorded_files[f.rel]
            continue
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
                    plan.review.append((f.rel, r.id, NEW_REGION_REVIEW, r.text))
                record[r.id] = {"applied": None,
                                "template": new_hash if accept_edited else seen.get("template")}
                continue
            cur_hash = digest(have[r.id].text)
            if cur_hash == new_hash:
                record[r.id] = {"applied": new_hash, "template": new_hash}
            elif seen.get("applied") == cur_hash or take_template:
                replace[r.id] = r.text
                plan.replaced.append(f"{f.rel}#{r.id}")
                if seen.get("applied") != cur_hash:
                    plan.overwritten.append(f"{f.rel}#{r.id}")
                record[r.id] = {"applied": new_hash, "template": new_hash}
            else:
                if seen.get("template") != new_hash:
                    plan.review.append((f.rel, r.id, HAND_REVIEW if by_hand else EDITED_REVIEW, r.text))
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
    plan.removed_files = sorted(r for r in recorded_files
                                if r not in template_rels and in_tiers(r, in_use)
                                and tier_of(r) not in unseen)
    # Records of files under an unseen tier that the template no longer has are kept as they were.
    for r, rec in recorded_files.items():
        if tier_of(r) in unseen and r not in new_files:
            new_files[r] = rec
    new_files[CATALOGUE] = recorded_files.get(CATALOGUE, {"class": "generated", "regions": {}})
    # The list given now replaces the manifest's. An id the new metric list lacks is refused
    # only when it was typed now, since a recorded metric may since have been deleted.
    left_out = catalogue.parse_exclude(manifest.get("catalogue_exclude") if catalogue_exclude is None
                                       else catalogue_exclude)
    if metrics is not None:
        kept = catalogue.exclude(metrics, left_out, strict=catalogue_exclude is not None)
        plan.catalogue = catalogue.render(kept, today)
        plan.left_out = kept.get("left_out", 0)

    base = {k: v for k, v in manifest.items() if k not in DROPPED_KEYS + ("catalogue_exclude",)}
    plan.manifest = {**base, "template_version": __version__, "upgraded": today,
                     "tiers": list(in_use), "values": values, "files": new_files}
    if left_out:
        plan.manifest["catalogue_exclude"] = left_out
    return plan


def report_text(plan: Plan, old: str, today: str) -> str:
    lines = [f"# Upgrade report {today}", "",
             f"Template {old} to {__version__}. Each section below is template text that was not "
             "applied because the folder's copy was edited, or because it is new and its place "
             "needs a person. Merge what you want, then run the upgrade with --accept-edited.", ""]
    for rel, rid, why, text in plan.review:
        lines += [f"## {rel}: {rid}", "", why[0].upper() + why[1:] + ".", "", "~~~~markdown", text, "~~~~", ""]
    for rel, heads in plan.suggestions:
        lines += [f"## {rel}: suggested sections", "",
                  "The template now has these headings; add them if they apply.", ""]
        lines += [f"- `{h}`" for h in heads] + [""]
    if plan.removed_regions or plan.removed_files:
        lines += ["## No longer in the template", "", "Left in place. Remove by hand if unused.", ""]
        lines += [f"- {x}" for x in plan.removed_regions + plan.removed_files] + [""]
    if plan.unseen_tiers:
        lines += ["## Not upgraded", ""] + [f"- {w[0].upper() + w[1:]}." for w in plan.warnings()] + [""]
    return "\n".join(lines)


def report_path(today: str) -> str:
    return f"Shared/Claude/Upgrade report {today}.md"


def apply_plan(folder: Path, plan: Plan, today: str) -> str | None:
    old = load_manifest(folder).get("template_version", "?")
    if not plan.changes() and old == __version__:
        return None
    for rel, text in plan.adds.items():
        write_text(folder / rel, text)
    for rel, text in plan.rewrites.items():
        write_text(folder / rel, text)
    for d in load_ownership().directories:
        if in_tiers(d, plan.tiers) and (folder / d).parent.is_dir():
            (folder / d).mkdir(exist_ok=True)
    if plan.catalogue is not None:
        write_text(folder / CATALOGUE, plan.catalogue)
    report = None
    if plan.review or plan.suggestions or plan.removed_regions or plan.removed_files:
        report = report_path(today)
        write_text(folder / report, report_text(plan, old, today))
    tail = f" {len(plan.review)} left for review in '{report}'." if plan.review and report else ""
    tiers = f" Tiers added: {', '.join(plan.added_tiers)}." if plan.added_tiers else ""
    add_changelog_line(folder, f"- {today}: upgraded from template {old} to {__version__}; "
                               f"{len(plan.replaced)} regions replaced, {len(plan.adds)} files added."
                               f"{tiers}{tail}")
    write_manifest(folder, plan.manifest)
    return report


def describe(plan: Plan) -> list[str]:
    out = [f"warning  {w}" for w in plan.warnings()]
    if plan.by_hand:
        out.append("note     the folder was set up by hand; its manifest is rewritten in the normal form")
    out += [f"tier     {t} added" for t in plan.added_tiers]
    if plan.added_tiers:
        out.append("note     everyone in the new tier can read Shared, which holds the metric "
                   "catalogue; --catalogue with --catalogue-exclude leaves metrics out of it")
    out += [f"add      {r}" for r in plan.adds]
    out += [f"replace  {r}" + (" (the folder's text differed and is overwritten)"
                               if r in plan.overwritten else "") for r in plan.replaced]
    out += [f"review   {rel}#{rid}: {why}" for rel, rid, why, _ in plan.review]
    out += [f"suggest  {rel}: {', '.join(h)}" for rel, h in plan.suggestions]
    out += [f"removed  {r} (left in place)" for r in plan.removed_regions + plan.removed_files]
    if plan.catalogue is not None:
        out.append(f"regen    {CATALOGUE}"
                   + (f" ({plan.left_out} left out)" if plan.left_out else ""))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os upgrade", description=__doc__.splitlines()[0])
    ap.add_argument("--folder", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--tiers", default=None,
                    help="the tiers after the upgrade, comma separated; may add a tier, never remove one")
    ap.add_argument("--to", default=None, help="refuse unless this template is that version")
    ap.add_argument("--answers", type=Path, default=None, help="values for new placeholders")
    ap.add_argument("--catalogue", type=Path, default=None, help="regenerate the metric catalogue")
    ap.add_argument("--metrics-from", default="auto", choices=("auto", "neutral", "datarails"))
    ap.add_argument("--accept-edited", action="store_true")
    ap.add_argument("--catalogue-exclude", default=None,
                    help="with --catalogue: metric ids to leave out of the shared catalogue, comma "
                         "separated; replaces the list in the manifest, and an empty value clears it")
    ap.add_argument("--take-template", action="store_true",
                    help="replace every region whose text differs from the template, including "
                         "regions edited in the folder")
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
                            args.accept_edited, args.date, args.tiers, args.take_template,
                            args.catalogue_exclude)
        lines = describe(plan)
        if metrics is not None:
            lines += [f"warning  {w}" for w in catalogue.formula_mentions(
                metrics, plan.manifest.get("catalogue_exclude"))]
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
