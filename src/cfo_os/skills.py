"""Package the plugin's skills as zip files for upload in Claude's settings.

    cfo-os skills --out <folder> [--plugin <path>]

Writes one <name>.zip per skill in the plugin's skills/ folder, each holding a <name>/ folder with SKILL.md
at its top, which is the shape the Claude apps accept under Settings, Capabilities, Skills.
The plugin is found next to the source tree (run from a clone), then in plugin/ under the
current folder (installed with pip, run from the clone's root), or wherever --plugin points.
The zips are reproducible: the same skill always gives the same bytes.

Exit codes: 0 written, 1 a skill is malformed, 2 usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

import yaml

SOURCE_PLUGIN = Path(__file__).resolve().parents[2] / "plugin"
SKIP_DIRS = {"__pycache__", ".pytest_cache"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
MAX_DESCRIPTION = 2 ** 10  # the Claude apps refuse a longer skill description


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise ValueError(f"{skill_md}: no YAML frontmatter")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{skill_md}: frontmatter is not a mapping")
    return data


def skill_problems(skill_dir: Path) -> list[str]:
    """What stops a skill folder from being a valid, uploadable skill."""
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [f"{skill_dir.name}: no SKILL.md"]
    try:
        meta = frontmatter(md)
    except (ValueError, yaml.YAMLError) as e:
        return [str(e)]
    problems = []
    name, desc = meta.get("name"), meta.get("description")
    if name != skill_dir.name:
        problems.append(f"{skill_dir.name}: name {name!r} differs from the folder name")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
        problems.append(f"{skill_dir.name}: name must be lowercase words joined by hyphens, at most 64 characters")
    if not isinstance(desc, str) or not desc.strip():
        problems.append(f"{skill_dir.name}: no description")
    elif len(desc) > MAX_DESCRIPTION:
        problems.append(f"{skill_dir.name}: description is {len(desc)} characters; the limit is {MAX_DESCRIPTION}")
    elif "<" in desc or ">" in desc:
        problems.append(f"{skill_dir.name}: description must not contain angle brackets")
    return problems


def skill_dirs(plugin: Path) -> list[Path]:
    root = plugin / "skills"
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []


def find_plugin(explicit: Path | None) -> Path | None:
    candidates = [explicit] if explicit else [SOURCE_PLUGIN, Path.cwd() / "plugin"]
    return next((c for c in candidates if skill_dirs(c)), None)


def package(skill_dir: Path, out: Path) -> Path:
    target = out / f"{skill_dir.name}.zip"
    files = sorted(p for p in skill_dir.rglob("*")
                   if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(skill_dir).parts))
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo(f"{skill_dir.name}/{p.relative_to(skill_dir).as_posix()}", FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os skills", description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True, help="folder to write the zip files into")
    ap.add_argument("--plugin", type=Path, help="the plugin folder (default: plugin/ in the clone)")
    args = ap.parse_args(argv)
    plugin = find_plugin(args.plugin)
    if plugin is None:
        where = args.plugin or "the source tree or plugin/ under the current folder"
        print(f"error: no skills found in {where}; run from the clone's root or pass --plugin <clone>/plugin",
              file=sys.stderr)
        return 2
    dirs = skill_dirs(plugin)
    problems = [p for d in dirs for p in skill_problems(d)]
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    for d in dirs:
        print(package(d, args.out))
    return 0
