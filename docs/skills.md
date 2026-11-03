# Skills

The repository ships a Claude plugin, `cfo-os`, in `plugin/`. It holds skills for finance work that most CFOs do the same way and that go wrong in the same ways. Each skill does its arithmetic in a bundled Python script, so the same inputs always give the same figures and the checks are never skipped.

| Skill | What it does | Used by |
|---|---|---|
| `cash-runway` | Projects closing cash from an actual opening balance and one forecast cycle, finds the month cash falls below a floor, ties the projection to the forecast's own closing cash, compares with trailing burn and runs sensitivities. | `04 Workflows/Monthly/Cash runway.md` |
| `variance-analysis` | A variance table with favourable or adverse decided from line type and sign convention, materiality, totals tied to their lines, and a price, volume and mix bridge that adds up exactly. | `02 Rules and style/Templates/Variance table.md`, `Forecast critique.md` |
| `forecast-accuracy` | Net error, WAPE and bias of the previous cycle on closed months, steps from run rate in the new cycle, and the full year spliced at the reference month with each month from one source. | `04 Workflows/Monthly/Forecast critique.md` |

A skill works with or without a CFO OS folder. In a folder, it reads the reference month and cycle from `01 Context/Data.md` and the sign convention and materiality from `02 Rules and style/Rules.md`, and the workflow keeps the steps, the checks and the filing. Outside a folder, it asks for what it needs and says what it assumed.

## Installing

The scripts need code execution, which the Claude apps call "Code execution and file creation". Turn it on first.

- **Claude Code or Cowork.** Add this repository as a plugin marketplace and install the plugin:

  ```
  /plugin marketplace add PaddyB0/cfo-ai-os
  /plugin install cfo-os@cfo-ai-os
  ```

- **The Claude apps (desktop and web).** From the root of a clone, package the skills, then upload each zip under Settings, Capabilities, Skills:

  ```
  cfo-os skills --out "<scratch path>/skills"
  ```

  On a Team or Enterprise plan, an owner can provision the zips for the whole organisation instead, so the CFO installs nothing.

After an upgrade of the template, package and upload again. A skill's version is the template version in `plugin/.claude-plugin/plugin.json`.

## When a workflow becomes a skill

A workflow in a deployed folder stays a workflow until it has been run the same way three times. It becomes a candidate skill only if a skill would do something the workflow file cannot:

- a calculation that must come out the same every time, done by a script rather than by Claude;
- a check that is easy to forget and costly to miss, such as a total that does not tie or a month counted twice;
- reliable use without the CFO having to name the workflow.

A skill that would only repeat the workflow's text stays a workflow: the steps would then live in two places. A skill specific to one company is kept in that folder's `00 System/Skills/` and uploaded from there. One that most CFOs would use comes into this repository.

## In this repository

- One folder per skill under `plugin/skills/`, named in lowercase with hyphens, with `SKILL.md`, `scripts/` and `examples/input.example.json`. The example is fictional and says so in its first line.
- Scripts use the Python standard library only, read one JSON file, print Markdown (or JSON with `--json`), and exit 1 with a plain message when the input breaks a rule.
- The description says what the skill does, when to use it, and which nearby requests belong to another skill.
- `SKILL.md` names template files by their path in the `CFO OS` folder. The tests check each path exists.
- `tests/test_cfo_os_skills.py` covers each script's figures and refusals. Add a case for every rule a script enforces.
- Run `claude plugin validate --strict .` and `claude plugin validate --strict plugin` when the manifests change, and the eval suite in `plugin/evals/` when a description changes:

  ```
  claude plugin eval plugin --allow-tools Bash
  ```
