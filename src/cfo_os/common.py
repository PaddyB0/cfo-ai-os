"""What deploy, upgrade and check share: finding the template, ownership classes, template
regions and their hashes, placeholder filling, and careful file writes."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import __version__

PACKAGE = Path(__file__).resolve().parent
FOLDER_NAME = "CFO OS"
MANIFEST = "00 System/Template manifest.json"
CHANGELOG = "00 System/Changelog.md"
INSTRUCTIONS = "00 System/Instructions.md"
CATALOGUE = "01 Context/Metric catalogue.md"
CLASSES = ("system", "context", "generated", "client")
IGNORED_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-z_]+(?:\.[a-z_]+)*)\s*\}\}")
BEGIN_RE = re.compile(r"^<!-- cfo-os:template begin ([a-z0-9]+(?:-[a-z0-9]+)*) -->\s*$")
END_RE = re.compile(r"^<!-- cfo-os:template end ([a-z0-9]+(?:-[a-z0-9]+)*) -->\s*$")
MARKER_RE = re.compile(r"^<!-- cfo-os:template (begin|end)\b")


class TemplateError(Exception):
    """A problem with the template, the answers or a folder that stops the command."""


# --- locating the template ---------------------------------------------------------------

def find_template(explicit: str | os.PathLike[str] | None = None) -> Path:
    """The `template/CFO OS` folder: --template, then CFO_OS_TEMPLATE, then the clone this
    package runs from, then the current directory."""
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("CFO_OS_TEMPLATE"):
        candidates.append(Path(os.environ["CFO_OS_TEMPLATE"]))
    candidates += [parent / "template" / FOLDER_NAME for parent in PACKAGE.parents]
    candidates.append(Path.cwd() / "template" / FOLDER_NAME)
    for c in candidates:
        if c.name != FOLDER_NAME and (c / "template" / FOLDER_NAME).is_dir():
            c = c / "template" / FOLDER_NAME
        if (c / "00 System").is_dir():
            return c.resolve()
    raise TemplateError("template folder not found; run from the clone or pass --template")


def template_files(template: Path) -> list[str]:
    """Every file in the template, as a '/'-separated path relative to `CFO OS/`."""
    out = []
    for p in sorted(template.rglob("*")):
        if p.is_file() and p.name not in IGNORED_NAMES:
            out.append(p.relative_to(template).as_posix())
    return out


# --- ownership -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Ownership:
    rules: tuple[tuple[str, str], ...]
    directories: tuple[str, ...]

    def classify(self, rel: str) -> str:
        for pattern, cls in self.rules:
            if fnmatch.fnmatchcase(rel, pattern):
                return cls
        raise TemplateError(f"{rel}: no ownership rule matches")


def load_ownership(path: Path | None = None) -> Ownership:
    data = yaml.safe_load((path or PACKAGE / "ownership.yaml").read_text(encoding="utf-8"))
    rules = []
    for r in data["rules"]:
        if r["class"] not in CLASSES:
            raise TemplateError(f"ownership.yaml: unknown class {r['class']!r}")
        rules.append((r["pattern"], r["class"]))
    return Ownership(tuple(rules), tuple(data.get("directories") or ()))


# --- placeholders --------------------------------------------------------------------------

def load_placeholders(path: Path | None = None) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load((path or PACKAGE / "placeholders.yaml").read_text(encoding="utf-8"))
    for name, spec in data.items():
        if spec.get("form") not in ("text", "list", "table"):
            raise TemplateError(f"placeholders.yaml: {name} has no valid form")
        if spec.get("required") and "default" in spec:
            raise TemplateError(f"placeholders.yaml: {name} is required and has a default")
    return data


def lookup(answers: dict[str, Any], dotted: str) -> Any:
    node: Any = answers
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, (str, list, dict)) and len(value) == 0)


def _cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def render_value(name: str, form: str, value: Any) -> str:
    """One answer as Markdown text."""
    if form == "text":
        if isinstance(value, (list, dict)):
            raise TemplateError(f"answer {name}: expected a single line of text")
        return str(value).strip()
    if form == "list":
        if isinstance(value, str):
            return value.rstrip()
        if not isinstance(value, list):
            raise TemplateError(f"answer {name}: expected a list")
        return "\n".join(f"- {_cell(v)}" for v in value)
    if isinstance(value, str):
        return value.rstrip()
    if not isinstance(value, list) or not all(isinstance(r, dict) for r in value):
        raise TemplateError(f"answer {name}: expected a list of rows")
    columns: list[str] = []
    for row in value:
        for key in row:
            if key not in columns:
                columns.append(key)
    head = [c.replace("_", " ").capitalize() for c in columns]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(columns)]
    for row in value:
        lines.append("| " + " | ".join(_cell(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines)


def unknown_answers(answers: dict[str, Any], specs: dict[str, dict[str, Any]]) -> list[str]:
    """Keys in the answers file that no placeholder reads, such as a misspelt name. Deploy
    refuses them, so a typo never silently drops an answer."""
    known = {n for n, s in specs.items() if not s.get("auto")}
    roots = {n.split(".")[0] for n in known}
    out = []
    for key, value in answers.items():
        if key not in roots:
            out.append(key)
        elif key not in known:
            if not isinstance(value, dict):
                out.append(key)
                continue
            out += [f"{key}.{leaf}" for leaf in value if f"{key}.{leaf}" not in known]
    return sorted(out)


def resolve_values(answers: dict[str, Any], specs: dict[str, dict[str, Any]],
                   auto: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Every placeholder's rendered text, and the required ones the answers leave empty."""
    values: dict[str, str] = {}
    missing: list[str] = []
    for name, spec in specs.items():
        if spec.get("auto"):
            if name in auto:
                values[name] = auto[name]
            continue
        raw = lookup(answers, name)
        if is_empty(raw):
            if spec.get("required"):
                missing.append(name)
                continue
            raw = spec.get("default", "")
        values[name] = render_value(name, spec["form"], raw)
    return values, missing


def placeholders_in(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def fill(text: str, values: dict[str, str]) -> str:
    def sub(m: re.Match[str]) -> str:
        name = m.group(1)
        if name not in values:
            raise TemplateError(f"no value for placeholder {name}")
        return values[name]

    return PLACEHOLDER_RE.sub(sub, text)


def auto_values(deployer: str, date: str, version: str = __version__) -> dict[str, str]:
    return {"deploy.version": version, "deploy.date": date, "deploy.deployer": deployer}


# --- template regions ----------------------------------------------------------------------

@dataclass(frozen=True)
class Region:
    id: str
    begin: int  # index of the begin marker line
    end: int    # index of the end marker line
    text: str   # the lines between the markers, joined with "\n"


def split_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").split("\n")


def regions(text: str, where: str = "") -> list[Region]:
    """The template regions of a file, in order. Malformed markers raise TemplateError."""
    lines = split_lines(text)
    out: list[Region] = []
    open_id: str | None = None
    start = -1
    seen: set[str] = set()
    for i, line in enumerate(lines):
        b, e = BEGIN_RE.match(line), END_RE.match(line)
        if b:
            if open_id is not None:
                raise TemplateError(f"{where}:{i + 1}: region {b.group(1)} opens inside {open_id}")
            if b.group(1) in seen:
                raise TemplateError(f"{where}:{i + 1}: region {b.group(1)} appears twice")
            open_id, start = b.group(1), i
        elif e:
            if e.group(1) != open_id:
                raise TemplateError(f"{where}:{i + 1}: end of {e.group(1)} does not close {open_id}")
            out.append(Region(open_id, start, i, "\n".join(lines[start + 1:i])))
            seen.add(open_id)
            open_id = None
        elif MARKER_RE.match(line):
            raise TemplateError(f"{where}:{i + 1}: malformed region marker")
    if open_id is not None:
        raise TemplateError(f"{where}: region {open_id} is never closed")
    return out


def digest(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def replace_regions(text: str, new_text: dict[str, str]) -> str:
    """`text` with the body of each named region replaced. Keeps the file's line endings."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = split_lines(text)
    for r in sorted(regions(text), key=lambda r: r.begin, reverse=True):
        if r.id in new_text:
            lines[r.begin + 1:r.end] = split_lines(new_text[r.id])
    return newline.join(lines)


# --- files ---------------------------------------------------------------------------------

def read_text(path: Path) -> str:
    """UTF-8 with line endings as they are on disk, so a CRLF file stays CRLF when rewritten."""
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path: Path, text: str, attempts: int = 5) -> None:
    """Write UTF-8 exactly as given (no newline translation), retrying while a sync client
    or an open editor holds a lock on the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(attempts):
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.5 * (attempt + 1))


def load_manifest(folder: Path) -> dict[str, Any]:
    path = folder / MANIFEST
    if not path.is_file():
        raise TemplateError(f"{folder}: no {MANIFEST}; this folder was not deployed from the template")
    return json.loads(read_text(path))


def write_manifest(folder: Path, manifest: dict[str, Any]) -> None:
    write_text(folder / MANIFEST, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def add_changelog_line(folder: Path, line: str) -> None:
    """Put a dated line at the top of the Changelog's entries, newest first."""
    path = folder / CHANGELOG
    text = read_text(path) if path.is_file() else "# Changelog\n\n## Entries\n"
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = split_lines(text)
    heading = next((i for i, l in enumerate(lines) if l.strip() == "## Entries"), None)
    if heading is None:
        while lines and not lines[-1].strip():
            lines.pop()
        lines += ["", "## Entries"]
        heading = len(lines) - 1
    at = heading + 1
    while at < len(lines) and not lines[at].strip():
        at += 1
    rest = lines[at:] or [""]
    write_text(path, newline.join(lines[:heading + 1] + ["", line] + rest))
