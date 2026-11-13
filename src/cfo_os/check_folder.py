"""Check a deployed CFO OS folder against its filing rules.

    cfo-os check --folder "<path>/CFO OS"

Prints one `path: finding` line per problem and exits 1 when there is any: files outside the
places the filing rules allow, names that break the naming rules, OneDrive "-1" and "-2"
duplicates, unfilled placeholders, and a tier folder the manifest's tiers do not list. A tier
folder that is missing is not a finding, since the person running the check may have no
access to it; a note names it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .common import (INSTRUCTIONS, MANIFEST, PLACEHOLDER_RE, IGNORED_NAMES, TIERS, TemplateError,
                     load_manifest, parse_tiers, read_text)

YEAR_RE = re.compile(r"^FY\d{4}$")
PERIOD_RE = re.compile(r"^(?:\d{4}-(?:0[1-9]|1[0-2])|\d{4}-Q[1-4])$")
LOG_RE = re.compile(r"^Log(?: [^/\\]+)?\.md$")
DUPLICATE_RE = re.compile(r"^(?P<stem>.+)-(?P<n>[1-9])(?P<ext>\.[^.]+)?$")
UPGRADE_REPORT_RE = re.compile(r"^Upgrade report .+\.md$")
WORK_PARTS = ("Inputs", "Outputs", "Working")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}

TOP_FILES = {"Read me first.md", "CLAUDE.md"}
SHARED_DIRS = ("Claude", "Library", "Workflows")
CLAUDE_FILES = {"Instructions.md", "Company.md", "Data.md", "Calendar.md", "Rules.md",
                "Metric catalogue.md", "Changelog.md", "Template manifest.json"}
TIER_DIRS = ("Archive", "Memory", "Periods", "Projects")
WORK_HOLDS = "Inputs, Outputs, Working and a log (Log.md or Log <name>.md)"


def _ignored(p: Path) -> bool:
    return p.name in IGNORED_NAMES or p.name.startswith("~$")


def _children(p: Path) -> list[Path]:
    return sorted(c for c in p.iterdir() if not _ignored(c))


class _Checker:
    def __init__(self, folder: Path, tiers: tuple[str, ...] = TIERS) -> None:
        self.folder = folder
        self.tiers = tiers  # the tiers the manifest records
        self.findings: list[str] = []

    def rel(self, p: Path) -> str:
        return p.relative_to(self.folder).as_posix()

    def add(self, p: Path, text: str) -> None:
        self.findings.append(f"{self.rel(p)}: {text}")

    # --- each place in the folder ---

    def top(self) -> None:
        for c in _children(self.folder):
            if c.is_file() and c.name in TOP_FILES:
                continue
            if c.is_dir() and c.name == "Shared":
                self.shared(c)
                continue
            if c.is_dir() and c.name in TIERS:
                if c.name not in self.tiers:
                    wanted = ",".join(t for t in TIERS if t in self.tiers or t == c.name)
                    self.add(c, f"tier folder not in the manifest's tiers ({', '.join(self.tiers)}); "
                                f"add the tier with 'cfo-os upgrade --tiers {wanted} --apply', or "
                                "remove the folder")
                self.tier(c)
                continue
            self.add(c, "not allowed at the top level; the top level holds only Read me first.md, "
                        f"CLAUDE.md, Shared and the tier folders {', '.join(TIERS)}")

    def shared(self, d: Path) -> None:
        for c in _children(d):
            if not c.is_dir() or c.name not in SHARED_DIRS:
                self.add(c, f"not allowed here; Shared holds only {', '.join(SHARED_DIRS)}")
            elif c.name == "Workflows":
                self.workflows(c)
            elif c.name == "Claude":
                self.claude(c)
            # Library: reference documents as received, anything goes.

    def workflows(self, d: Path) -> None:
        for c in _children(d):
            if c.is_file() and c.suffix == ".md":
                continue
            if c.is_dir() and c.name == "Templates":
                for t in _children(c):
                    if (t.is_file() and t.suffix == ".md") or (t.is_dir() and t.name == "Examples"):
                        continue
                    self.add(t, "not allowed here; Templates holds output templates (.md) and Examples")
                continue
            self.add(c, "not allowed here; Workflows holds one .md file per job and Templates")

    def claude(self, d: Path) -> None:
        for c in _children(d):
            if c.is_file() and (c.name in CLAUDE_FILES or UPGRADE_REPORT_RE.match(c.name)):
                continue
            if c.is_dir() and c.name == "Tests":
                for t in _children(c):
                    if (t.is_file() and t.name == "Test questions.md") or (t.is_dir() and t.name == "Runs"):
                        continue
                    self.add(t, "not allowed here; Tests holds Test questions.md and Runs")
                continue
            self.add(c, "not allowed here; Shared/Claude holds the files Claude reads, Tests "
                        "and upgrade reports")

    def tier(self, d: Path) -> None:
        for c in _children(d):
            if c.is_file() and c.name == "Role.md":
                continue
            if not c.is_dir() or c.name not in TIER_DIRS:
                self.add(c, f"not allowed here; a tier folder holds Role.md, {', '.join(TIER_DIRS)}")
            elif c.name == "Memory":
                for m in _children(c):
                    if m.is_file() and (m.name == "Now.md" or LOG_RE.match(m.name)):
                        continue
                    self.add(m, "not allowed here; Memory holds Now.md and Log.md or Log <name>.md")
            elif c.name == "Periods":
                self.periods(c)
            elif c.name == "Projects":
                self.projects(c)
            # Archive: closed years and finished projects, anything goes.

    def periods(self, d: Path) -> None:
        for y in _children(d):
            if y.is_file():
                self.add(y, "files in Periods go inside a period folder")
                continue
            if not YEAR_RE.match(y.name):
                self.add(y, "a year folder is named FYyyyy")
                continue
            # The year folder is also the period folder for annual work.
            for p in _children(y):
                if (p.is_dir() and p.name in WORK_PARTS) or (p.is_file() and LOG_RE.match(p.name)):
                    continue
                if not p.is_dir():
                    self.add(p, "not allowed here; a year folder holds Inputs, Outputs, Working, "
                                "a log and its month and quarter folders")
                elif not PERIOD_RE.match(p.name):
                    self.add(p, "a period folder is named yyyy-mm or yyyy-Qn")
                else:
                    self.work_folder(p, "period", set())

    def projects(self, d: Path) -> None:
        for p in _children(d):
            if p.is_file():
                self.add(p, "files in Projects go inside a project folder")
                continue
            self.work_folder(p, "project", {"Brief.md"})

    def work_folder(self, d: Path, kind: str, extra_files: set[str]) -> None:
        """A period or project folder: Inputs/, Working/, Outputs/, a log and nothing else."""
        for c in _children(d):
            if c.is_dir() and c.name in WORK_PARTS:
                continue
            if c.is_file() and (LOG_RE.match(c.name) or c.name in extra_files):
                continue
            extra = "".join(f", {n}" for n in sorted(extra_files))
            self.add(c, f"not allowed here; a {kind} folder holds only {WORK_HOLDS}{extra}")

    # --- everywhere ---

    def every_file(self) -> None:
        for p in sorted(self.folder.rglob("*")):
            if _ignored(p) or not p.is_file() or self.rel(p) == MANIFEST:
                continue
            m = DUPLICATE_RE.match(p.name)
            if m and (p.parent / f"{m['stem']}{m['ext'] or ''}").exists():
                self.add(p, f"looks like a OneDrive duplicate of {m['stem']}{m['ext'] or ''}; "
                            "compare and keep one (never delete without asking)")
            if p.suffix.lower() in TEXT_SUFFIXES:
                try:
                    text = read_text(p)
                except UnicodeDecodeError:
                    continue
                for name in sorted(set(PLACEHOLDER_RE.findall(text))):
                    self.add(p, f"unfilled placeholder {name}")


def check(folder: Path) -> tuple[list[str], list[str]]:
    """(findings, notes). Notes are information, not failures."""
    manifest = load_manifest(folder)
    notes: list[str] = []
    tiers = parse_tiers(manifest.get("tiers") or [TIERS[0]])
    c = _Checker(folder, tiers)
    c.top()
    c.every_file()
    if not (folder / INSTRUCTIONS).is_file():
        c.findings.append(f"{INSTRUCTIONS}: missing")
    unseen = [t for t in tiers if not (folder / t).is_dir()]
    if unseen:
        notes.append(f"tier folder(s) {', '.join(unseen)} are in the manifest but could not be seen; "
                     "they were not checked (you may have no access to them)")
    return c.findings, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os check", description=__doc__.splitlines()[0])
    ap.add_argument("--folder", type=Path, required=True)
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
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
