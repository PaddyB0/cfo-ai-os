"""Render `Metric catalogue.md` from a neutral metric list (schemas/metrics.schema.json).

The catalogue is generated, never edited by hand. The guidance that goes with it lives in
the folder's Instructions.md and Data.md.

    cfo-os catalogue metrics.json [--from neutral|datarails] [--as-of yyyy-mm-dd]
                     [--exclude <id>,<id>]

The catalogue sits in `Shared`, which every tier can read. --exclude leaves metrics out of
it; deploy and upgrade keep the same list in the folder's manifest as `catalogue_exclude`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from ..common import TemplateError
from .adapters import datarails_mcp

ROLLUPS = ("sum", "end_of_period", "average", "none", "unknown")
KINDS = ("base", "calculated", "input", "driver", "other")
ROLLUP_WORDS = {"sum": "sum", "end_of_period": "end of period", "average": "average", "none": "none",
                "unknown": "unknown"}
TEXT_FIELDS = ("category", "formula", "description", "warning", "error")


def load_metrics(path: Path, source_format: str = "auto") -> dict[str, Any]:
    """Read a metric list and return it in the neutral form, validated."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if source_format == "datarails" or (source_format == "auto" and datarails_mcp.looks_like(data)):
        data = datarails_mcp.convert(data)
    elif source_format not in ("auto", "neutral"):
        raise TemplateError(f"unknown metric list format {source_format!r}")
    validate(data, path.name)
    return data


def validate(data: Any, where: str) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("metrics"), list):
        raise TemplateError(f"{where}: expected an object with a metrics list")
    if not data["metrics"]:
        raise TemplateError(f"{where}: the metric list is empty")
    seen = set()
    for i, m in enumerate(data["metrics"]):
        loc = f"{where}: metrics[{i}]"
        for key in ("id", "name", "kind", "rollup", "dimensions"):
            if key not in m:
                raise TemplateError(f"{loc}: missing {key}")
        if m["kind"] not in KINDS:
            raise TemplateError(f"{loc}: kind {m['kind']!r} is not one of {', '.join(KINDS)}")
        if m["rollup"] not in ROLLUPS:
            raise TemplateError(f"{loc}: rollup {m['rollup']!r} is not one of {', '.join(ROLLUPS)}")
        if not isinstance(m["name"], str) or not m["name"].strip():
            raise TemplateError(f"{loc}: name must be text")
        if isinstance(m["id"], bool) or not isinstance(m["id"], (int, str)):
            raise TemplateError(f"{loc}: id must be a number or text")
        if not isinstance(m["dimensions"], list) or not all(isinstance(d, str) for d in m["dimensions"]):
            raise TemplateError(f"{loc}: dimensions must be a list of names")
        for key in TEXT_FIELDS:
            if m.get(key) is not None and not isinstance(m[key], str):
                raise TemplateError(f"{loc}: {key} must be text or null")
        if str(m["id"]) in seen:
            raise TemplateError(f"{loc}: id {m['id']} appears twice")
        seen.add(str(m["id"]))


def parse_exclude(value: str | Iterable[Any] | None) -> list[str]:
    """Metric ids to leave out, given as text with commas between them or as a list: text, in order, no repeats."""
    if value is None:
        return []
    items = value.split(",") if isinstance(value, str) else list(value)
    out: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out


def exclude(data: dict[str, Any], ids: str | Iterable[Any] | None,
            strict: bool = False) -> dict[str, Any]:
    """The metric list without the given ids, with the number left out as `left_out`. With
    `strict`, an id the list does not have is refused: a mistyped id would otherwise leave the
    metric in a file every tier can read."""
    ids = parse_exclude(ids)
    if not ids:
        return data
    present = {str(m["id"]) for m in data["metrics"]}
    unknown = [i for i in ids if i not in present]
    if strict and unknown:
        raise TemplateError("metric id(s) to leave out of the catalogue are not in the metric "
                            f"list: {', '.join(unknown)}")
    kept = [m for m in data["metrics"] if str(m["id"]) not in ids]
    return {**data, "metrics": kept, "left_out": len(data["metrics"]) - len(kept)}


def formula_mentions(data: dict[str, Any], ids: str | Iterable[Any] | None) -> list[str]:
    """Metrics that stay in the catalogue whose formula names one that is left out. The
    formula still shows that name, so the caller warns about each."""
    ids = parse_exclude(ids)
    names = [m["name"] for m in data["metrics"] if str(m["id"]) in ids]
    out = []
    for m in sorted(data["metrics"], key=_sort_key):
        if str(m["id"]) in ids or not m.get("formula"):
            continue
        named = [n for n in names if f"'{n}'" in m["formula"]]
        if named:
            out.append(f"{m['id']} {m['name']}: its formula names {', '.join(named)}, which the "
                       "catalogue leaves out; leave this metric out too if the name must not be shared")
    return out


def _sort_key(m: dict[str, Any]) -> tuple[int, Any]:
    return (0, m["id"]) if isinstance(m["id"], int) else (1, str(m["id"]))


def _cell(value: Any) -> str:
    return str(value or "").replace("\n", " ").replace("|", "\\|").strip()


def watch_list(metrics: list[dict[str, Any]]) -> list[str]:
    """Things about the metric list Claude should know before using it."""
    by_name = {m["name"]: m for m in metrics}
    ordered = sorted(metrics, key=_sort_key)
    out: list[str] = []
    undocumented = [str(m["id"]) for m in ordered if not m.get("description")]
    if undocumented:
        out.append(f"- {len(undocumented)} metrics have no description, so Claude has only the "
                   f"name to go on: {', '.join(undocumented)}. Prefer a described metric for the "
                   "same question.")
    for m in ordered:
        tag = f"{m['id']} {m['name']}"
        if m["rollup"] == "unknown":
            out.append(f"- {tag}: the connector gives no roll-up. Ask before adding its months together.")
        if "retired" in m["name"].lower():
            out.append(f"- {tag}: retired in name, still listed. Ignore it.")
        if m["kind"] == "calculated" and m.get("formula") and m["rollup"] == "sum":
            eop = [n for n, other in by_name.items()
                   if f"'{n}'" in m["formula"] and other["rollup"] == "end_of_period"]
            if eop:
                out.append(f"- {tag}: calculated from end-of-period inputs ({', '.join(eop)}) "
                           "but rolls up as a sum. Quarter and year values are unverified.")
        if m.get("error"):
            out.append(f"- {tag}: error `{_cell(m['error'])}`.")
        if m.get("warning"):
            out.append(f"- {tag}: source warning `{_cell(m['warning'])}`.")
    return out


def render(data: dict[str, Any], as_of: str) -> str:
    metrics = data["metrics"]
    core = set(data.get("core_dimensions") or [])
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in metrics:
        groups[m.get("category") or "Uncategorised"].append(m)
    lines = [
        "# Metric catalogue",
        "",
        f"Generated by `cfo-os catalogue` from {data.get('source') or 'a metric list'} on "
        f"{as_of}. {len(metrics)} metrics. Do not edit; regenerate.",
        "",
    ]
    if data.get("left_out"):
        n = data["left_out"]
        lines += [f"{n} {'metric' if n == 1 else 'metrics'} the connector has "
                  f"{'is' if n == 1 else 'are'} left out of this file by choice, because everyone "
                  "who can open `Shared` can read it. A metric missing here may still exist in "
                  "the connector.", ""]
    lines += [
        "Read the description before using a metric. Where it is blank, the metric has no "
        "business definition on file; prefer a described metric that covers the same question. "
        "An end-of-period metric gives the last month's value for a quarter or a year; never "
        "add its months together.",
        "",
    ]
    if core:
        lines += [f"Every metric can be sliced by {', '.join(sorted(core))}; the table lists "
                  "only the other dimensions.", ""]
    for cat in sorted(groups):
        lines += [f"## {cat}", "",
                  "| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |",
                  "|---|---|---|---|---|---|---|"]
        for m in sorted(groups[cat], key=_sort_key):
            extra = [d for d in m["dimensions"] if d not in core]
            lines.append(
                f"| {m['id']} | {_cell(m['name'])} | {m['kind']} | {ROLLUP_WORDS[m['rollup']]} "
                f"| {_cell(', '.join(extra)) if extra else 'none'} | {_cell(m.get('formula'))} "
                f"| {_cell(m.get('description'))} |")
        lines.append("")
    lines += ["## Watch list", "", "Computed from the metric list.", ""]
    lines += watch_list(metrics) or ["- Nothing to flag."]
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os catalogue", description=__doc__.splitlines()[0])
    ap.add_argument("metrics", type=Path, help="the metric list, as JSON")
    ap.add_argument("--from", dest="source_format", default="auto",
                    choices=("auto", "neutral", "datarails"))
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--exclude", default=None,
                    help="metric ids to leave out, comma separated; use the folder manifest's "
                         "catalogue_exclude list when regenerating for a deployed folder")
    args = ap.parse_args(argv)
    try:
        full = load_metrics(args.metrics, args.source_format)
        data = exclude(full, args.exclude, strict=True)
        for line in formula_mentions(full, args.exclude):
            print(f"warning: {line}", file=sys.stderr)
    except (TemplateError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(render(data, args.as_of))
    return 0
