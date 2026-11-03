# Deploy

Deploying turns the template, an answers file and a metric list into a new `CFO OS` folder.

## Install

You need Python 3.11 or later and PyYAML.

```
git clone <this repository>
cd cfo-ai-os
pip install .
```

That gives a `cfo-os` command. Without installing, run `python run.py <command>` from the clone instead; every command below works the same way.

## 1. Write the answers file

Copy `examples/answers.example.yaml` and replace every value with your own. The file is a YAML mapping keyed by the placeholder names in `src/cfo_os/placeholders.yaml`: `company.name` is written as

```yaml
company:
  name: Your Company Ltd
```

Each placeholder is one of three forms:

- **text**: a single line.
- **list**: a YAML list of strings, rendered as one "- item" line each.
- **table**: a YAML list of mappings, rendered as a Markdown table whose columns come from the first row.

Required placeholders must have a value; optional ones fall back to their default. Write metric roles as the metric name with its id, for example `Net Revenue (id 101)`, so Claude can find the metric in the catalogue.

**Keep your answers file somewhere private.** It holds facts about a real company. Never commit it to this repository or any public one.

## 2. Get the metric list

The metric catalogue is built from your connector's list of metrics, saved as JSON.

- If the list is already in the neutral format (see `schemas/metrics.schema.json` and `examples/metrics.example.json`), use `--metrics-from neutral`, the default.
- For the Datarails FinanceOS connector, save the connector's own metric-list output and use `--metrics-from datarails`. See [connectors/datarails-financeos.md](connectors/datarails-financeos.md).

Keep the metric list private too.

## 3. Deploy

```
cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<path>/CFO OS" --deployer "Your Name"
```

Options:

- `--deployer "Name"` is recorded in `START HERE.md` and the first line of `00 System/Changelog.md`.
- `--metrics-from neutral|datarails` says what format the metric list is in.

Deploy refuses a target folder that already exists and is not empty. To move an existing folder to a newer template, use [upgrade](upgrade.md). Deploy fails, and writes nothing, if a required answer is missing.

Deploy writes every template file with its placeholders filled, creates the empty `Inputs/`, `Working/` and `Outputs/` folders in the project template, generates `01 Context/Metric catalogue.md`, and writes `00 System/Template manifest.json` with the template version and a hash of every template region.

To try it first, deploy the fictional example:

```
cfo-os deploy --answers examples/answers.example.yaml --metrics examples/metrics.example.json --target "<scratch path>/CFO OS"
```

## 4. Check the folder

```
cfo-os check --folder "<path>/CFO OS"
```

It prints one `path: finding` line per problem and exits with 0 when there are none and 1 when there are. It reports:

- unfilled placeholders;
- files outside the places the folder map allows;
- names that break the naming rule;
- OneDrive "-1" and "-2" duplicates;
- an `Instructions.md` that has changed since it was last recorded as pasted.

## 5. Set up the Claude Project

1. Create a Claude Project and paste the whole of `00 System/Instructions.md` into its instructions.
2. Record the paste:

   ```
   cfo-os pasted --folder "<path>/CFO OS"
   ```

   From then on, `check` reports when `Instructions.md` changes and needs pasting again.
3. Connect the finance connector, read-only.
4. Give Claude access to the folder.
5. Run the questions in `00 System/Tests/Test questions.md` and file the result in `00 System/Tests/Runs/`.

## Regenerating the catalogue by hand

```
cfo-os catalogue metrics.json --from neutral > "Metric catalogue.md"
```

Move the result into `01 Context/`. `--from datarails` reads the Datarails connector's output. The catalogue lists every metric with its roll-up, dimensions and description, and ends with a watch list: metrics with no description, metrics with a warning, retired metrics, and calculated metrics over an end-of-period input that sum over time.

## Public-safety scan

```
cfo-os scrub [path]
```

Scans a path (the repository by default) for anything that should not be public: email addresses, links outside an allowed list of hosts, long ids, long numbers outside dates and versions, and placeholders outside the template, examples and docs. Run it before you share a folder or open a pull request.
