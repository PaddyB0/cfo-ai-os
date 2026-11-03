# Workflow template

<!-- cfo-os:template begin body -->
Copy this file to begin a new workflow. Name the copy for the job in plain English, put it in the folder for how often it runs, and fill in every heading. Keep the headings exactly as they are, so every workflow reads the same way.

## Trigger

When this workflow runs: a date in `01 Context/Calendar.md`, an event such as a new forecast cycle being loaded, or a request from a named person.

## Inputs

What the workflow needs, and where each input comes from: metrics from the connector by role, files in the period `Inputs/` folder, earlier outputs, and the memory files to read.

## Steps

1. Number every step.
2. One action per step, in the order it is done.
3. Say which scenario, cycle and period each figure comes from.
4. Say where each working file is saved.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.

Add checks that are particular to this workflow below these four.

## Output

What is produced, in which template from `02 Rules and style/Templates/`, and who it goes to.

## Where it is filed

The folder for drafts, the folder for the final as sent, the line added to `Log.md`, and the memory lines proposed at session close.
<!-- cfo-os:template end body -->

## Your notes

