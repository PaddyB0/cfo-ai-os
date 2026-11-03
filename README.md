# cfo-ai-os

A folder template that lets Claude work as a finance analyst for a CFO, reading figures from a finance data connector and keeping its memory in plain Markdown files.

A personal project by Patrick Bowyer. Not an official Datarails product and not supported by Datarails. Datarails and FinanceOS are trademarks of their owner.

## What it is

- **A folder, `CFO OS`.** Plain Markdown files the CFO keeps in OneDrive, SharePoint or any synced folder: instructions for a Claude Project, the company's context and rules, output templates, workflows for the regular finance cycle, and a memory that Claude proposes and the CFO accepts. The CFO never needs to see this repository.
- **A small tool, `cfo-os`.** It deploys the folder from an answers file, upgrades a deployed folder to a newer template without touching what the CFO or Claude wrote, checks a folder against its filing rules, and builds a metric catalogue from the connector's metric list.
- **Skills, `cfo-os`.** A Claude plugin with skills for cash runway, variance analysis (with a price, volume and mix bridge) and forecast accuracy. Each does its arithmetic in a bundled script, so the same inputs always give the same figures. They work with or without the folder. See [Skills](docs/skills.md).
- **Docs** on the memory model and on reading figures from a finance connector without the usual mistakes.

## Who it is for

A CFO, finance lead or adviser who uses Claude with a read-only finance data connector and wants the work to be repeatable: the same rules, the same workflows, and a memory that survives from one chat to the next. It is connector-neutral; the first connector guide is for the Datarails FinanceOS connector.

## Deploy in five steps

1. Install Python 3.11 or later, clone this repository and run `pip install .` (or use `python run.py <command>` from the clone).
2. Copy `examples/answers.example.yaml`, fill it with your company's facts, and keep it somewhere private.
3. Save your connector's metric list as JSON. See [the connector guide](docs/connectors/datarails-financeos.md).
4. Deploy:

   ```
   cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<path>/CFO OS" --deployer "Your Name"
   ```

5. Paste `00 System/Instructions.md` into a Claude Project, run `cfo-os pasted --folder "<path>/CFO OS"`, connect the connector read-only, and run the test questions in `00 System/Tests/`.

Try it first with the fictional example: `examples/answers.example.yaml` and `examples/metrics.example.json`.

## Install the skills

In Claude Code or Cowork:

```
/plugin marketplace add PaddyB0/cfo-ai-os
/plugin install cfo-os@cfo-ai-os
```

In the Claude desktop or web app, run `cfo-os skills --out "<path>/skills"` from the clone's root and upload each zip under Settings, Capabilities, Skills, with code execution turned on.

## Upgrade in two steps

1. Dry run, and read what would change:

   ```
   cfo-os upgrade --folder "<path>/CFO OS"
   ```

2. Apply:

   ```
   cfo-os upgrade --folder "<path>/CFO OS" --apply
   ```

Only unedited template regions are replaced. Edited regions are reported for a person to merge, and files the CFO or Claude wrote are never opened.

## Docs

- [Memory model](docs/memory-model.md): one home per kind of knowledge, who writes what, the session close.
- [Working with a connector](docs/working-with-a-connector.md): scenarios and cycles, end-of-period metrics, declining what the data cannot answer.
- [Connector guide: Datarails FinanceOS](docs/connectors/datarails-financeos.md)
- [Folder map](docs/folder-map.md): the layout, the filing rules, ownership classes and template regions.
- [Deploy](docs/deploy.md), [Upgrade](docs/upgrade.md), [Writing a workflow](docs/writing-a-workflow.md), [Skills](docs/skills.md)

## Licence

Apache-2.0. See `LICENSE` and `NOTICE`. Contributions: see `CONTRIBUTING.md`. Security and data leaks: see `SECURITY.md`.
