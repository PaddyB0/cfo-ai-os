# Deploy

Deploying turns the template, the answers about a company and its metric list into a new `CFO OS` folder. There are two ways.

- **The setup prompt.** A person pastes `SETUP.md` into Claude with the finance connector connected. Claude checks it can write to the chosen location, collects the answers, and writes the folder: with this tool if it can run Python (Route A), or file by file (Route B). Nothing needs installing. A folder written by Route B has a manifest marked `deployed_by_hand`; `cfo-os check` and `cfo-os upgrade` both accept it.
- **The tool**, described below. Use it to deploy from an answers file you keep, to test the template, or when you maintain several folders.

`SETUP.md` is generated from `src/cfo_os/setup_prompt.md`, `placeholders.yaml` and the template by `python run.py prompt --out SETUP.md`. It is a repository command because it reads `examples/metrics.example.json`, which is not packaged. `python run.py prompt --check SETUP.md` fails when the file is stale.

## Install

You need Python 3.11 or later and PyYAML.

```
pip install "git+https://github.com/PaddyB0/cfo-ai-os"
```

That gives a `cfo-os` command. From a clone, `python run.py <command>` works the same way.

## 1. Write the answers file

Copy `examples/answers.example.yaml` and replace every value. The file is a YAML mapping keyed by the placeholder names in `src/cfo_os/placeholders.yaml`: `company.name` is written as

```yaml
company:
  name: Your Company Ltd
```

Each placeholder is one of three forms:

- **text**: a single line.
- **list**: a YAML list of strings, rendered as one "- item" line each.
- **table**: a YAML list of mappings, rendered as a Markdown table with a column for every key in any row.

Required placeholders must have a value; optional ones fall back to their default. Write metric roles as the metric name with its id, for example `Net Revenue (id 101)`. Give each row of `people` a `tier`: `CFO`, `VP`, `Team`, or `none` for someone who only receives outputs.

**Keep your answers file somewhere private.** It holds facts about a real company. Never commit it to this repository or any public one.

## 2. Get the metric list

The metric catalogue is built from the connector's list of metrics, saved as JSON.

- In the neutral format (see `schemas/metrics.schema.json` and `examples/metrics.example.json`), use `--metrics-from neutral`.
- For the Datarails FinanceOS connector, save the connector's own output and use `--metrics-from datarails`. See [connectors/datarails-financeos.md](connectors/datarails-financeos.md).

The default, `auto`, tells the two apart. Keep the metric list private too.

## 3. Deploy

```
cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<path>/CFO OS" --tiers CFO,VP --deployer "Your Name"
```

- `--tiers` names the tier folders to write, comma separated, from `CFO`, `VP` and `Team`. The default is `CFO`, and `CFO` must always be in the list. See [roles.md](roles.md).
- `--deployer "Name"` is recorded in `Read me first.md` and the first line of `Shared/Claude/Changelog.md`.
- `--metrics-from auto|neutral|datarails` says what format the metric list is in.
- `--catalogue-exclude <id>,<id>` leaves metrics out of the shared metric catalogue, which every tier can read. See [roles.md](roles.md), "What Shared shows everyone".

Deploy refuses a target that exists and is not empty, except one holding only `setup check.txt`, the setup prompt's write test, which it removes. It fails, and writes nothing, if a required answer is missing, an answer key is misspelt or the tier list is invalid. To move an existing folder to a newer template, use [upgrade](upgrade.md).

Deploy writes every template file for the chosen tiers with its placeholders filled, creates empty `Periods/` and `Projects/` in each tier folder, generates `Shared/Claude/Metric catalogue.md`, and writes `Shared/Claude/Template manifest.json` with the template version, the tiers and a hash of every template region.

To try it, deploy the fictional example:

```
cfo-os deploy --answers examples/answers.example.yaml --metrics examples/metrics.example.json --target "<scratch path>/CFO OS" --tiers CFO,VP,Team
```

## 4. Check the folder

```
cfo-os check --folder "<path>/CFO OS"
```

It prints one `path: finding` line per problem and exits with 0 when there are none and 1 when there are. It reports files outside the places the filing rules allow, folder names that break the naming rules, OneDrive "-1" and "-2" duplicates, unfilled placeholders and a missing `Instructions.md`. A tier folder in the manifest that the person running the check cannot see is a note, not a finding.

## 5. Set up the Claude Project

1. Create a Claude Project and paste the one line from `Read me first.md` into its instructions. It points Claude at `Shared/Claude/Instructions.md`, so it never needs pasting again.
2. Connect the finance connector, read-only. Each person signs in as themselves.
3. Give Claude access to the folder.
4. Set the folder permissions in [roles.md](roles.md).
5. Run the questions in `Shared/Claude/Tests/Test questions.md` and file the result in `Shared/Claude/Tests/Runs/`.

## Regenerating the catalogue by hand

```
cfo-os catalogue metrics.json --from neutral > "Metric catalogue.md"
```

Move the result into `Shared/Claude/`. `--from datarails` reads the Datarails connector's output. This command does not read the folder: if the manifest lists `catalogue_exclude`, pass the same ids as `--exclude <id>,<id>`, or use `cfo-os upgrade --folder "<path>/CFO OS" --catalogue metrics.json --apply`, which applies the list itself. The catalogue lists every metric with its roll-up, dimensions and description, and ends with a watch list: metrics with no description, metrics with a warning, retired metrics, and calculated metrics over an end-of-period input that sum over time.

## Public-safety scan

```
cfo-os scrub [path]
```

Scans a path (the repository by default) for anything that should not be public: email addresses, links outside an allowed list of hosts, long ids, long numbers outside dates and versions, and placeholders outside the template, examples, docs and the setup prompt. Run it before you share a folder or open a pull request.
