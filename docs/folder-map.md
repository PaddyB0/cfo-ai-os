# Folder map

The deployed folder is called `CFO OS`. Its filing rules, written for the CFO, are in `template/CFO OS/00 System/Folder map.md`. This page explains the same layout for whoever deploys and maintains the folder, and how each part is treated by the tool.

## Layout

```
CFO OS/
  START HERE.md
  00 System/          Instructions.md, Folder map.md, Changelog.md, Template manifest.json,
                      Tests/Test questions.md, Tests/Runs/
  01 Context/         Company.md, People.md, Data.md, Glossary.md, Calendar.md, Metric catalogue.md
  02 Rules and style/ Rules.md, Templates/, Examples/
  03 Memory/          Key findings.md, Decisions.md, Open questions.md, Lessons.md
  04 Workflows/       Workflow template.md, Every session/, Monthly/, Quarterly/, Annual/, Ad hoc/
  05 Periods/         FYyyyy/ with yyyy-mm/ and yyyy-Qn/ inside
  06 Projects/        one folder per project, copied from _Project template/
  07 Library/         reference documents as received
  08 Archive/         closed years and finished projects
```

`Template manifest.json` and `Metric catalogue.md` are written by `cfo-os deploy`; they are not in the template.

## The eight filing rules, in brief

1. One home per kind of knowledge; elsewhere, links.
2. Recurring work in `05 Periods/<year>/<period>/`; work with an end date that is not a cycle in `06 Projects/<name>/`.
3. Every period and project folder has `Inputs/` (as received, never edited), `Working/`, `Outputs/` (final, as sent) and `Log.md`.
4. Claude reads `00`, `01`, `02` and `07` and never edits them on its own; it writes `03 Memory` at session close on the CFO's yes.
5. Nothing is deleted. A closed year moves to `08 Archive` once its audit is signed. OneDrive "-1" and "-2" duplicates are flagged, never removed.
6. A new workflow begins from `Workflow template.md`. A workflow run the same way three times is a candidate Skill, with its source in `00 System/Skills/`.
7. If work splits into one Claude Project per workflow family, each reads `00` to `03` and its own workflow folder; `03 Memory` stays shared.
8. Two-digit prefixes on top-level folders only; months yyyy-mm, quarters yyyy-Qn, years FYyyyy; everything else plain English.

`cfo-os check` reports files outside the allowed places, names that break rule 8, and OneDrive duplicates.

## Ownership classes

Every path in the template has one class, set in `src/cfo_os/ownership.yaml`. The class decides what deploy and upgrade do with it.

| Class | Paths | Deploy | Upgrade |
|---|---|---|---|
| `system` | `00 System/` (except `Tests/Runs/`), `02 Rules and style/Templates/`, `04 Workflows/`, `START HERE.md` | written | template regions replaced if unedited |
| `context` | `01 Context/` except the catalogue | written with placeholders filled | never touched; new headings reported as suggestions |
| `generated` | `Metric catalogue.md`, `Template manifest.json`, `Tests/Runs/` | written | the catalogue is regenerated only with `--catalogue`; runs never touched |
| `client` | `Rules.md`, `Examples/`, `03 Memory/`, `05` to `08` | headers only | never opened |

## Template regions

A `system` file marks the text the template owns:

```
<!-- cfo-os:template begin connector-rules -->
...text the template owns...
<!-- cfo-os:template end connector-rules -->
```

Region ids are lowercase with hyphens and unique within a file. Markers sit on their own lines and are never nested. Everything outside the markers belongs to the client: the key facts, hypotheses and standard analyses in `Instructions.md`, the "Your notes" section at the end of each workflow and output template, and the "Your own questions" section of the test questions.

Do not delete or rename a marker in a deployed folder. If you want to change template text, edit it inside the markers; the next upgrade will see the edit, leave it alone and report the new text for you to merge.
