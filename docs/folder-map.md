# Folder map

The deployed folder is called `CFO OS`. Its filing rules, written for Claude and the team, are in the `filing-rules` region of `Shared/Claude/Instructions.md`. This page explains the same layout for whoever deploys and maintains the folder, and how the tool treats each part.

## Layout

```
CFO OS/
  Read me first.md       what the folder is, and the one line for the Claude Project
  CLAUDE.md              read by Claude when the folder is opened; points to Instructions
  Shared/
    Workflows/           one file per job, flat; Workflow template.md
      Templates/         output templates and Project brief.md; Examples/ when first needed
    Claude/              Instructions.md, Company.md, Data.md, Calendar.md, Rules.md,
                         Metric catalogue.md, Changelog.md, Template manifest.json,
                         Tests/Test questions.md, Tests/Runs/, Upgrade report <date>.md
    Library/             reference documents as received; when first needed
  CFO/  VP/  Team/       one folder per tier in use, each the same shape
    Role.md
    Memory/              Now.md, Log.md, and Log <name>.md when several people share the tier
    Periods/             FYyyyy/, with yyyy-mm/ and yyyy-Qn/ inside
    Projects/            <name>/, with Brief.md
    Archive/             closed years and finished projects; when first needed
```

`Template manifest.json` and `Metric catalogue.md` are written by `cfo-os deploy`; they are not in the template. `VP/` and `Team/` exist only for the tiers chosen at deploy; see [roles.md](roles.md).

Every period folder (the FY folder itself, a month, a quarter) and every project folder holds `Inputs/` (as received, never edited), `Working/`, `Outputs/` (final, as sent) and a log: `Log.md`, or one `Log <first name>.md` per person.

## What `cfo-os check` enforces

- The top level holds only `Read me first.md`, `CLAUDE.md`, `Shared/` and the tier folders.
- `Shared/` holds `Workflows/`, `Claude/` and `Library/`. `Workflows/` holds `.md` files and `Templates/`. `Claude/` holds its known files, `Tests/` and upgrade reports. Anything goes in `Library/` and `Templates/Examples/`.
- A tier folder holds `Role.md`, `Memory/`, `Periods/`, `Projects/` and `Archive/`. Anything goes in `Archive/`.
- `Periods/` holds `FYyyyy` folders; inside one, the four parts and `yyyy-mm` or `yyyy-Qn` folders, each holding only the four parts. `Projects/<name>/` holds the four parts and `Brief.md`.
- OneDrive "-1" and "-2" duplicates and unfilled placeholders are reported everywhere.

A tier folder that the person running the check cannot see is not a finding; a note names it.

## Ownership classes

Every path in the template has one class, set in `src/cfo_os/ownership.yaml`. The class decides what deploy and upgrade do with it.

| Class | Paths | Deploy | Upgrade |
|---|---|---|---|
| `system` | `Read me first.md`, `CLAUDE.md`, `Shared/Workflows/`, `Shared/Claude/Instructions.md`, `Changelog.md`, `Tests/Test questions.md`, `<tier>/Role.md` | written | template regions replaced if unedited |
| `context` | `Shared/Claude/Company.md`, `Data.md`, `Calendar.md` | written with placeholders filled | never touched; new headings reported as suggestions |
| `generated` | `Metric catalogue.md`, `Template manifest.json`, `Tests/Runs/`, upgrade reports | written by `cfo-os` | the catalogue is regenerated only with `--catalogue`; runs never touched |
| `client` | `Shared/Claude/Rules.md`, `<tier>/Memory/`, and everything people create | headers only | never opened |

## Template regions

A `system` file marks the text the template owns:

```
<!-- cfo-os:template begin connector-rules -->
...text the template owns...
<!-- cfo-os:template end connector-rules -->
```

Region ids are lowercase with hyphens and unique within a file. Markers sit on their own lines and are never nested. Everything outside the markers belongs to the team: the key facts, how we work, hypotheses and standard analyses in `Instructions.md`, the "Your notes" section at the end of each workflow and output template, and the "Your own questions" section of the test questions.

Do not delete or rename a marker in a deployed folder. To change template text, edit it inside the markers; the next upgrade sees the edit, leaves it alone and reports the new text for you to merge.
