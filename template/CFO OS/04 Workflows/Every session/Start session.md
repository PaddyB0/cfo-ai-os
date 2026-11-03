# Start session

<!-- cfo-os:template begin body -->
## Trigger

The first message of every chat, or the CFO saying "start a session".

## Inputs

- `01 Context/`, all files, including `Data.md` for the reference month and the current forecast cycle.
- `02 Rules and style/Rules.md`.
- `03 Memory/`: `Key findings.md`, the newest lines of `Decisions.md` and `Lessons.md`, and every unanswered line in `Open questions.md`.
- The workflow file for the task, if the CFO named one.
- The `Log.md` of the current period or project, if there is one.
- `01 Context/Calendar.md` for what is due next.

## Steps

1. Read the inputs above, in the reading order in the instructions.
2. Check that {{connector.name}} answers. If it does not, say so and work only from files until it does.
3. Check that the reference month in `Data.md`, {{data.reference_month}} at deploy, is still the last closed month. If a later month looks closed in the connector, say so and propose the update; do not change `Data.md` yourself.
4. Find the period or project folder for the task. If it does not exist, propose its name under the naming rule, and create it with `Inputs/`, `Working/`, `Outputs/` and `Log.md` once the CFO agrees.
5. Look for OneDrive duplicates, files ending in "-1" or "-2", in the folders you will use. List any you find.
6. Tell the CFO, in a few lines: what you read, the reference month and cycle you will use, the open questions that touch this task, anything due soon from the calendar, and any duplicates found.
7. Ask what to do first if the task is not yet clear. Otherwise begin the workflow.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.

## Output

A short opening note in the chat. No file is written at the start of a session, except a new period or project folder the CFO has agreed to.

## Where it is filed

Nowhere. The note stays in the chat. What matters from it is carried into the session close.
<!-- cfo-os:template end body -->

## Your notes

