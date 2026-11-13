# Upgrade

Upgrading moves a deployed `CFO OS` folder to a newer template version without touching anything people or Claude wrote.

## How it works

Every file in the template has an ownership class (see [folder-map.md](folder-map.md)). `Shared/Claude/Template manifest.json` records the template version the folder came from, its tiers, and a hash of every template region as it was last written.

| Class | What upgrade does |
|---|---|
| `system` | Each template region whose text still matches the recorded hash is replaced with the new template's text. A region someone has edited is left alone; the new text goes into an upgrade report for a person to merge. |
| `context` | Never touched. If the new template adds a heading to a context file, upgrade reports it as a suggestion. |
| `generated` | The metric catalogue is regenerated only when `--catalogue` is given, leaving out the metric ids the manifest lists as `catalogue_exclude`. Test runs are never touched. |
| `client` | Never opened. |

New template files are added. Files the new template no longer has are listed and never deleted. A template file a person has moved or deleted is not brought back.

## Run a dry run

```
cfo-os upgrade --folder "<path>/CFO OS"
```

By default upgrade only reports: each region it would replace, each edited region it would leave with the new template text, each new file, each file the template has removed, and each suggested heading for a context file. Nothing in a `client` file should appear; if it does, stop and report a bug.

## Apply

```
cfo-os upgrade --folder "<path>/CFO OS" --apply
```

On apply, upgrade replaces the unedited regions and adds the new files, writes the new text of each edited region to `Shared/Claude/Upgrade report <yyyy-mm-dd>.md`, adds a line to `Shared/Claude/Changelog.md`, and rewrites the manifest. To refresh the catalogue at the same time, add `--catalogue metrics.json`. Then run the test questions and file the run. The Claude Project's one-line instruction never needs pasting again.

## Merging edited regions

An edited region stays as the team left it. Open the upgrade report, decide for each region what the text should be, and edit the region in the folder by hand. Then record the merged text as the new baseline:

```
cfo-os upgrade --folder "<path>/CFO OS" --apply --accept-edited
```

`--accept-edited` records the template's new text as seen, so the next upgrade does not report the region again. Use it only after a person has merged the report; otherwise the template's new text is silently dropped.

To drop the team's edits instead, pass `--take-template`. It replaces every region whose text differs from the template with the template's text, on any folder. The dry run marks each such region "the folder's text differed and is overwritten". Text outside template regions is never touched.

## Tiers

Tiers come from the manifest. `--tiers` may add one: `cfo-os upgrade --folder "<path>/CFO OS" --tiers CFO,VP --apply` writes the `VP` folder's files as plain adds. It never removes a tier. Set the new folder's access afterwards; see [roles.md](roles.md).

Whoever runs the upgrade works with their own access. A tier folder in the manifest that they cannot see is reported as a warning, left as it is, and its records are kept, so a later upgrade by someone who can see it picks it up.

## A folder set up by hand

The setup prompt's Route B has Claude write the files itself. Its manifest has `deployed_by_hand: true`, the answers and no region hashes. Upgrade resolves the values from those answers as deploy does and compares each region with the template's rendering. An equal region is recorded. A different one is reported as "differs from the template; the folder was set up by hand" and left alone, unless `--take-template` is passed, which replaces it. On `--apply` the manifest is rewritten in the normal form. `--take-template` works the same way on a later run, so a region left alone on the first apply can still be replaced.

## Moving from 0.2

The layout changed in 0.3 and a 0.2 folder cannot be upgraded in place. Upgrade and check refuse a folder that has `00 System/Template manifest.json`. There is no automatic migration. Deploy a new 0.3 folder, then move your own files across by this table and copy any text you added outside template regions.

| 0.2 | 0.3 |
|---|---|
| `START HERE.md` | `Read me first.md` |
| `00 System/Instructions.md` | `Shared/Claude/Instructions.md` |
| `00 System/Folder map.md` | removed; the rules are in the Instructions `filing-rules` region |
| `00 System/Changelog.md` | `Shared/Claude/Changelog.md` |
| `00 System/Template manifest.json` | `Shared/Claude/Template manifest.json` |
| `00 System/Tests/` | `Shared/Claude/Tests/` |
| `00 System/Upgrade report <date>.md` | `Shared/Claude/Upgrade report <date>.md` |
| `01 Context/Company.md`, `People.md`, `Glossary.md` | `Shared/Claude/Company.md` |
| `01 Context/Data.md`, `Calendar.md`, `Metric catalogue.md` | `Shared/Claude/`, same names |
| `02 Rules and style/Rules.md` | `Shared/Claude/Rules.md` |
| `02 Rules and style/Templates/` | `Shared/Workflows/Templates/` |
| `02 Rules and style/Examples/` | `Shared/Workflows/Templates/Examples/` (created when needed) |
| `03 Memory/Key findings.md`, `Open questions.md` | `<tier>/Memory/Now.md` |
| `03 Memory/Decisions.md`, `Lessons.md` | `<tier>/Memory/Log.md` (lines tagged Decision, Lesson, Question, Answer) |
| `04 Workflows/<cadence>/<job>.md` | `Shared/Workflows/<job>.md` |
| `04 Workflows/Every session/Start session.md`, `Close session.md` | removed; folded into the Instructions `start` and `finish` regions |
| `05 Periods/` | `<tier>/Periods/` |
| `06 Projects/` | `<tier>/Projects/`; the brief template is `Shared/Workflows/Templates/Project brief.md` |
| `07 Library/` | `Shared/Library/` |
| `08 Archive/` | `<tier>/Archive/` |

The Claude Project's instructions change too: replace the pasted `Instructions.md` with the one line in `Read me first.md`.

## Good practice

- Run `cfo-os check` before and after an upgrade.
- Upgrade one version at a time if several have passed; read the root `CHANGELOG.md` for which regions each version changed.
- Keep a copy of the folder before the first apply. OneDrive and SharePoint version history also work.
