# Quarterly accounts

<!-- cfo-os:template begin body -->
## Trigger

The last month of a quarter is closed, and the quarterly accounts are due to the auditor, a lender or the group, as set out in `01 Context/Calendar.md`.

## Inputs

- {{scenario.actuals}} for the quarter and the year to date, by entity and consolidated.
- The month-end close tie-outs for the three months.
- Quarter-end schedules: accruals, prepayments, deferred revenue, fixed assets, provisions, intercompany and debt.
- The auditor's request list for the quarter, if there is one, saved in `Inputs/` as received.
- The previous quarter's accounts.

## Steps

1. Create the quarter folder `05 Periods/<year>/<yyyy-Qn>/` with its four parts, if it does not exist.
2. Build the income statement for the quarter and the year to date, summing flow metrics over the months.
3. Build the balance sheet at the quarter end, reading end-of-period metrics at the last month of the quarter.
4. Agree intercompany balances and eliminations, and show the elimination entries.
5. Check foreign currency translation: which rates were used for the income statement and the balance sheet, and where the difference goes.
6. Tie each line to the trial balance per entity, and list any difference with its reason.
7. Work through the auditor's request list. For each item, record the file supplied, from `Inputs/` or `Outputs/`, and the date.
8. Draft notes for judgemental areas: revenue recognition, provisions, capitalised costs, going concern.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The quarter's figures agree with the sum of the three monthly management accounts, or the difference is explained.

## Output

The quarterly accounts, the tie-out to the trial balance, and the auditor request list with what was supplied.

## Where it is filed

Working papers in `05 Periods/<year>/<yyyy-Qn>/Working/`, the accounts and the request list as sent in `Outputs/`, a line in `Log.md`. Auditor points go to `03 Memory/Open questions.md` with an owner.
<!-- cfo-os:template end body -->

## Your notes

