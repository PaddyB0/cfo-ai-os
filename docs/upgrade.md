# Upgrade

Upgrading moves a deployed `CFO OS` folder to a newer template version without touching anything the CFO or Claude wrote.

## How it works

Every file in the template has an ownership class (see [folder-map.md](folder-map.md)). `00 System/Template manifest.json` records the template version the folder came from and a hash of every template region as it was last written.

| Class | What upgrade does |
|---|---|
| `system` | Each template region whose text still matches the recorded hash is replaced with the new template's text. A region that someone has edited is left alone; the new text goes into an upgrade report for a person to merge. |
| `context` | Never touched. If the new template adds a heading to a context file, upgrade reports it as a suggestion. |
| `generated` | The metric catalogue is regenerated only when `--catalogue` is given. Test runs are never touched. |
| `client` | Never opened. |

New template files are added. Files the new template no longer has are listed and never deleted.

## Run a dry run

```
cfo-os upgrade --folder "<path>/CFO OS"
```

By default upgrade only reports. It prints:

- each region it would replace;
- each edited region it would leave, with the new template text;
- each new file it would add;
- each file the template has removed;
- each suggested new heading for a context file.

Read it. Nothing in a `client` file should appear; if it does, stop and report a bug.

## Apply

```
cfo-os upgrade --folder "<path>/CFO OS" --apply
```

On apply, upgrade:

- replaces the unedited regions and adds the new files;
- writes the new text of each edited region to `00 System/Upgrade report <yyyy-mm-dd>.md`;
- adds a line to `00 System/Changelog.md`;
- rewrites `Template manifest.json` with the new version and hashes.

To refresh the catalogue at the same time, add `--catalogue metrics.json`.

If `Instructions.md` changed, paste it into the Claude Project again and run `cfo-os pasted --folder "<path>/CFO OS"`. Then run the test questions and file the run.

## Merging edited regions

An edited region stays as the client left it. Open the upgrade report, decide for each region what the text should be, and edit the region in the folder by hand. Then record the merged text as the new baseline:

```
cfo-os upgrade --folder "<path>/CFO OS" --apply --accept-edited
```

`--accept-edited` records the current text of each edited region in the manifest, so the next upgrade treats it as unedited. Use it only after a person has merged the report; otherwise the template's new text is silently dropped.

## Good practice

- Run `cfo-os check` before and after an upgrade.
- Upgrade one version at a time if several have passed; read the root `CHANGELOG.md` for which regions each version changed.
- Keep a copy of the folder before the first apply. OneDrive version history also works.
