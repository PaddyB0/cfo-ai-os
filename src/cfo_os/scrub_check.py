"""The generic public-safety scan for this repository. It needs no private input, so it runs
in public CI and before every release.

    cfo-os scrub [path]

It reports, as `path:line: rule: text`:
- email addresses;
- URLs on hosts outside ALLOWED_HOSTS;
- long ids: ULIDs, UUIDs and hex strings of 32 characters or more (pinned action SHAs in
  workflow files excepted);
- numbers of four or more digits, other than years, dates and versions, in files whose first
  lines do not say they are fictional;
- placeholders outside template/, examples/, docs/, tests/ and the placeholder list.

Exit codes: 0 clean, 1 findings, 2 usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_HOSTS = {
    "github.com", "docs.github.com", "www.apache.org", "docs.python.org", "www.python.org",
    "pypi.org", "keepachangelog.com", "semver.org", "support.claude.com", "docs.claude.com",
    "www.anthropic.com", "claude.ai", "www.datarails.com", "support.datarails.com",
    "mcp.datarails.com", "json-schema.org",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "build", "dist", ".tox"}
PLACEHOLDER_ROOTS = ("template/", "examples/", "docs/", "tests/", "src/cfo_os/placeholders.yaml")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://([^/\s)>\]\"'`]+)")
ULID_RE = re.compile(r"\b[0-9A-HJKMNP-TV-Z]{26}\b")
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
HEX_RE = re.compile(r"\b[0-9a-fA-F]{32,}\b")
PINNED_ACTION_RE = re.compile(r"uses:\s*[\w.-]+/[\w./-]+@[0-9a-f]{40}\b")
NUMBER_RE = re.compile(r"(?<![\w.,-])\d{1,3}(?:,\d{3})+(?![\w.]\d)|(?<![\w.,-])\d{4,}(?![\w,]|\.\d)")
DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}(?:-\d{2})?(?!\d)")
# Not a GitHub Actions expression, which is "$" followed by the same braces.
PLACEHOLDER_RE = re.compile(r"(?<!\$)\{\{\s*[a-z_]+(?:\.[a-z_]+)*\s*\}\}")
FICTIONAL_RE = re.compile(r"fictional", re.I)


def is_year(token: str) -> bool:
    return len(token) == 4 and 1900 <= int(token) <= 2099


def scan_text(rel: str, text: str) -> list[str]:
    findings: list[str] = []
    fictional = bool(FICTIONAL_RE.search(text[:400]))
    placeholders_ok = rel.startswith(PLACEHOLDER_ROOTS)
    for n, line in enumerate(text.splitlines(), 1):
        def hit(rule: str, token: str) -> None:
            findings.append(f"{rel}:{n}: {rule}: {token}")

        for m in EMAIL_RE.finditer(line):
            hit("email", m.group(0))
        for m in URL_RE.finditer(line):
            host = m.group(1).split("@")[-1].split(":")[0].lower().rstrip(".")
            if host not in ALLOWED_HOSTS:
                hit("url host not allowed", host)
        for m in ULID_RE.finditer(line):
            hit("ulid", m.group(0))
        for m in UUID_RE.finditer(line):
            hit("uuid", m.group(0))
        if not PINNED_ACTION_RE.search(line):
            for m in HEX_RE.finditer(line):
                hit("long hex id", m.group(0))
        if not fictional:
            bare = DATE_RE.sub(" ", line)
            for m in NUMBER_RE.finditer(bare):
                if not is_year(m.group(0)):
                    hit("number of four or more digits", m.group(0))
        if not placeholders_ok:
            for m in PLACEHOLDER_RE.finditer(line):
                hit("placeholder outside the template", m.group(0))
    return findings


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if any(part.endswith(".egg-info") for part in p.relative_to(root).parts):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        findings += scan_text(p.relative_to(root).as_posix(), text)
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cfo-os scrub", description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    if not args.path.is_dir():
        print(f"error: {args.path} is not a directory", file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    findings = scan(args.path)
    for f in findings:
        print(f)
    print(f"scrub: {len(findings)} finding(s)")
    return 1 if findings else 0
