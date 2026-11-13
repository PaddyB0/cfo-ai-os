# Writing a workflow

A workflow file tells Claude how a recurring job is done, step by step, so it is done the same way each time. Every workflow follows `Shared/Workflows/Workflow template.md`, with the same headings in the same order.

## The headings

- **Trigger.** When the workflow runs. The first sentence is its cadence, `Monthly.`, `Quarterly.`, `Annual.` or `On request.`, because all workflows sit in one flat folder. Then the date in the calendar, the event such as a new forecast cycle, or the request.
- **Inputs.** What it needs and where each input comes from. Name metrics by role (board revenue, closing cash) and scenarios by role (actuals, budget, current forecast cycle), not by id. The ids live in `Shared/Claude/Data.md`, so a workflow keeps working when a metric is replaced.
- **Steps.** Numbered, one action each, in order. Say which scenario, cycle and period each figure comes from, and where each file is saved.
- **Checks every output carries.** Always these four, then any that are particular to the workflow:
  - each figure ties to its source, or the output says it does not and why;
  - the scenario and, for a forecast, the cycle are stated;
  - each figure has a source;
  - the sign convention is named for every table.
- **Output.** What is produced, in which template, and for whom.
- **Where it is filed.** The period or project folder in your tier for drafts and finals, the log line, and the memory lines proposed when the work is done.

## In a deployed folder

1. Copy `Workflow template.md` into `Shared/Workflows/` and name it in plain English. Start its Trigger with the cadence.
2. Write it outside any template region: delete the region markers in your copy, because the whole file is yours. The template never changes a file it did not ship.
3. Run it once with Claude, then correct it. Lessons from the run go in `Memory/Log.md` in your tier as Lesson lines; changes to the steps go in the file. Only someone in the `CFO` or `VP` tier can accept a change to `Shared`.
4. A workflow run the same way three times is a candidate Claude Skill. Keep its source in `Shared/Library/`.

To change a workflow the template ships, add your notes in its "Your notes" section, or edit inside its region and merge the upgrade report when the template changes.

## In this repository

A workflow comes into the template only when it is generic: most finance teams have the same job, and nothing in it would let a reader recognise a company. Industry-specific analyses stay in the client's folder.

- Wrap the whole body, below the H1, in one region named `body`, and end the file with an empty `## Your notes` section after the end marker.
- Use only placeholders listed in `src/cfo_os/placeholders.yaml`.
- Add the file to the root `CHANGELOG.md`.
- Run the tests, `cfo-os scrub`, deploy the example and run `cfo-os check` on the result. See `CONTRIBUTING.md`.
