# Month-end close

<!-- cfo-os:template begin body -->
## Trigger

The first working day after a month ends, through to the close date in `01 Context/Calendar.md`.

## Inputs

- The close checklist from last month's `Log.md`, if there is one.
- Trial balances or ledger extracts per entity, saved in the month's `Inputs/` folder as received.
- Bank statements, the payroll report, and the accruals and prepayments schedules.
- {{scenario.actuals}} from {{connector.name}} once the month is loaded.

## Steps

1. Create the month folder `05 Periods/<year>/<yyyy-mm>/` with `Inputs/`, `Working/`, `Outputs/` and `Log.md`, if it does not exist.
2. Track the checklist: bank reconciliations, sales and purchase cut-off, payroll posted, accruals and prepayments, fixed assets and depreciation, intercompany agreed, VAT or sales tax, and revaluation of foreign currency balances. Record each item as done, open or not needed, with who did it.
3. Check that intercompany balances agree between entities, and list the ones that do not.
4. When the month is loaded in the connector, tie the connector's figures to the trial balance per entity for revenue, cost and closing cash. Record any difference.
5. Check the balance sheet: closing cash in the connector against the bank reconciliation, and any balance that moved more than materiality without an explanation.
6. Flag journals posted after the close date and anything reclassified from an earlier month.
7. When the CFO confirms the month is closed, propose the update to the reference month in `01 Context/Data.md`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.

## Output

The close checklist with status, the tie-out of the connector to the trial balance, and a list of open items with owners.

## Where it is filed

Working papers in the month's `Working/`, the signed-off checklist and tie-out in `Outputs/`, a line in `Log.md`. Open items go to `03 Memory/Open questions.md` at session close.
<!-- cfo-os:template end body -->

## Your notes

