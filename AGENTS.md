# AGENTS.md

Instructions for any coding agent working on this repository. `CLAUDE.md` imports this file, so the rules live in one place.

## What this is

A folder template for a CFO who works with Claude and a finance data connector, plus `cfo-os`, the tool that deploys, upgrades and checks a folder. Read `README.md`, then `docs/folder-map.md` and `docs/upgrade.md`.

- `template/CFO OS/`: the folder a CFO receives, with placeholders and template regions.
- `src/cfo_os/`: the tool. `placeholders.yaml` lists every placeholder; `ownership.yaml` gives every template path its class.
- `schemas/`, `examples/`, `tests/`, `docs/`.

## Rules

1. **No real company in anything.** No client name, person, figure, price, product term, entity structure, metric id or calendar date taken from a real business. Examples and fixtures are invented and say so in their first lines.
2. **Roles, not ids.** Template text names a metric or scenario role through a placeholder listed in `placeholders.yaml`. A new placeholder goes into that file and into `schemas/answers.schema.json` in the same change.
3. **Template regions.** In a `system` file, only text between `cfo-os:template begin` and `end` markers belongs to the template; upgrades replace it. Keep markers on their own lines, never nested, with ids unique in the file. Client text stays outside the markers.
4. **Every workflow** follows `04 Workflows/Workflow template.md`: Trigger, Inputs, Steps, Checks every output carries, Output, Where it is filed.
5. **British English**, plain sentences, file names with spaces inside the CFO folder, normal repository names elsewhere.
6. **Python 3.11+, standard library and PyYAML only.** It must run on a locked-down Windows laptop against a OneDrive folder: keep line endings as found, no symlinks, retry on a file lock.
7. **This repository is a mirror.** The maintainer publishes it from a private source that runs extra scans. Pull requests are welcome and are ported back by hand.

## Before you finish

```
python -m pytest -q
python run.py scrub .
python run.py deploy --answers examples/answers.example.yaml --metrics examples/metrics.example.json --target "<scratch>/CFO OS"
python run.py pasted --folder "<scratch>/CFO OS"
python run.py check --folder "<scratch>/CFO OS"
```

All must pass. When a change alters template text, add a line to `CHANGELOG.md` naming the regions it changed.
