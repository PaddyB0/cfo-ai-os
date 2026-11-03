# Contributing

Thank you for helping. Please read this first.

## How this repository works

This public repository is a read-only mirror. The source is kept elsewhere and published here, one commit per release.

- **Issues are welcome.** Report a bug, a mistake in the docs, or a workflow most CFOs would want.
- **Pull requests are welcome.** A pull request is not merged here. It is reviewed, ported back to the source by hand, and appears in the next release. You are credited in the changelog unless you ask not to be.

## Style rules

- **British English**, plain short sentences, no marketing tone, no emoji.
- **Roles, not ids.** Template text names a metric or scenario by its role, through a placeholder listed in `src/cfo_os/placeholders.yaml`. Ids belong in a deployed folder's `01 Context/Data.md`, never here. Do not invent a placeholder; propose it in the pull request.
- **No client facts.** Nothing that could identify a real company: names, people, figures, prices, product terms, entity structures, ids or calendar dates. Examples and test fixtures are fictional and say so in their first line.
- **Every workflow follows the template.** Use the headings of `04 Workflows/Workflow template.md`, in order, with the whole body in a `body` region and an empty `## Your notes` section after it.
- **Template regions.** If you change text inside a region, say so in `CHANGELOG.md`, because upgrades replace it in deployed folders.
- File names in the `CFO OS` folder are plain English with spaces. Everything else uses normal repository naming.

## How a change is tested

Before opening a pull request, run from the clone:

```
pip install . pytest
pytest
cfo-os scrub
cfo-os deploy --answers examples/answers.example.yaml --metrics examples/metrics.example.json --target "<scratch path>/CFO OS"
cfo-os check --folder "<scratch path>/CFO OS"
```

All four must pass: the tests, the public-safety scan with no findings, a clean deploy of the fictional example, and a check of the result with no findings.
