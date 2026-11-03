"""Check a deployed CFO OS folder against its filing rules.

    cfo-os check --folder "<path>/CFO OS"
    cfo-os pasted --folder "<path>/CFO OS"

check prints one `path: finding` line per problem and exits 1 when there is any:
unfilled placeholders, files outside the places the folder map allows, names that break the
naming rule, OneDrive "-1" and "-2" duplicates, and an Instructions.md that changed since it
was last recorded as pasted into the Claude Project. pasted records that moment.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .common import (INSTRUCTIONS, MANIFEST, PLACEHOLDER_RE, IGNORED_NAMES, TemplateError,
                     digest, load_manifest, read_text, write_manifest)

YEAR_RE = re.compile(r"^FY\d{4}$")
PERIOD_RE = re.compile(r"^(?:\d{4}-(?:0[1-9]|1[0-2])|\d{4}-Q[1-4])$")
PREFIX_RE = re.compile(r"^\d{2} ")
DUPLICATE_RE = re.compile(r"^(?P<stem>.+)-(?P<n>[1-9])(?P<ext>\.[^.]+)?$")
WORK_PARTS = {"Inputs", "Working", "Outputs"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}


def _ignored(p: Path) -> bool:
    return p.name in IGNORED_NAMES or p.name.startswith("~$")


def _children(p: Path) -> list[Path]:
    return sorted(c for c in p.iterdir() if not _ignored(c))


def _work_folder(folder: Path, d: Path, extra_files: set[str], findings: list[str]) -> None:
    """A period or project folder: Inputs/, Working/, Outputs/, Log.md and nothing else."""
    for c in _children(d):
        rel = c.relative_to(folder).as_posix()
        if c.is_dir() and c.name in WORK_PARTS:
            continue
        if c.is_file() and (c.name == "Log.md" or c.name in extra_files):
            continue
        findings.append(f"{rel}: not allowed here; a {d.parent.name} folder holds only "
                        f"{', '.join(sorted(WORK_PARTS))}, Log.md" +
                        (f", {', '.join(sorted(extra_files))}" if extra_files else ""))


def check(folder: Path) -> tuple[list[str], list[str]]:
    """(findings, notes). Notes are information, not failures."""
    findings: list[str] = []
    notes: list[str] = []
    manifest = load_manifest(folder)
    allowed_top = {rel.split("/")[0] for rel in manifest.get("files", {})}

    for c in _children(folder):
        if c.name not in allowed_top:
            findings.append(f"{c.name}: not allowed at the top level; file it under a numbered folder")

    periods = folder / "05 Periods"
    if periods.is_dir():
        for y in _children(periods):
            rel = y.relative_to(folder).as_posix()
            if y.is_file():
                if y.name != "README.md":
                    findings.append(f"{rel}: files in 05 Periods go inside a period folder")
                continue
            if not YEAR_RE.match(y.name):
                findings.append(f"{rel}: a year folder is named FYyyyy")
                continue
            # The year folder is also the period folder for annual work.
            for p in _children(y):
                prel = p.relative_to(folder).as_posix()
                if (p.is_dir() and p.name in WORK_PARTS) or (p.is_file() and p.name == "Log.md"):
                    continue
                if not p.is_dir():
                    findings.append(f"{prel}: not allowed here; a year folder holds Inputs, "
                                    "Working, Outputs, Log.md and its month and quarter folders")
                elif not PERIOD_RE.match(p.name):
                    findings.append(f"{prel}: a period folder is named yyyy-mm or yyyy-Qn")
                else:
                    _work_folder(folder, p, set(), findings)

    projects = folder / "06 Projects"
    if projects.is_dir():
        for p in _children(projects):
            rel = p.relative_to(folder).as_posix()
            if p.is_file():
                if p.name != "README.md":
                    findings.append(f"{rel}: files in 06 Projects go inside a project folder")
                continue
            _work_folder(folder, p, {"Brief.md"}, findings)

    for p in sorted(folder.rglob("*")):
        if _ignored(p) or p.relative_to(folder).as_posix() == MANIFEST:
            continue
        rel = p.relative_to(folder).as_posix()
        depth = len(p.relative_to(folder).parts)
        if p.is_dir() and depth > 1 and PREFIX_RE.match(p.name):
            findings.append(f"{rel}: the two-digit prefix is for top-level folders only")
        if p.is_file():
            m = DUPLICATE_RE.match(p.name)
            if m and (p.parent / f"{m['stem']}{m['ext'] or ''}").exists():
                findings.append(f"{rel}: looks like a OneDrive duplicate of "
                                f"{m['stem']}{m['ext'] or ''}; compare and keep one (never delete without asking)")
            if p.suffix.lower() in TEXT_SUFFIXES:
                try:
                    text = read_text(p)
                except UnicodeDecodeError:
                    continue
                for name in sorted(set(PLACEHOLDER_RE.findall(text))):
                    findings.append(f"{rel}: unfilled placeholder {name}")

    instructions = folder / INSTRUCTIONS
    pasted = manifest.get("instructions_pasted_sha256")
    if not instructions.is_file():
        findings.append(f"{INSTRUCTIONS}: missing")
    elif pasted is None:
        notes.append(f"{INSTRUCTIONS}: never recorded as pasted; paste it into the Claude Project, then run cfo-os pasted")
    elif digest(read_text(instructions)) != pasted:
        findings.append(f"{INSTRUCTIONS}: changed since it was last pasted; paste it into the Claude Project, then run cfo-os pasted")
    return findings, notes


def record_pasted(folder: Path) -> None:
    manifest = load_manifest(folder)
    manifest["instructions_pasted_sha256"] = digest(read_text(folder / INSTRUCTIONS))
    write_manifest(folder, manifest)


def main(argv: list[str] | None = None, *, pasted: bool = False) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os pasted" if pasted else "cfo-os check",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--folder", type=Path, required=True)
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if pasted:
            record_pasted(args.folder)
            print(f"recorded {INSTRUCTIONS} as pasted")
            return 0
        findings, notes = check(args.folder)
    except (TemplateError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for line in findings:
        print(line)
    for line in notes:
        print(f"note: {line}")
    if not findings:
        print("no findings")
    return 1 if findings else 0
