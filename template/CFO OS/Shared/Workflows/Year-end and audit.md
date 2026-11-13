# Year-end and audit

<!-- cfo-os:template begin body -->
## Trigger

Annual. The last month of the fiscal year closes, through to the signing of the audited accounts.

## Inputs

- {{scenario.actuals}} for the full year, by entity and consolidated.
- The four quarterly accounts and their tie-outs.
- Year-end schedules: fixed asset register, provisions, deferred revenue, accruals, debt, tax, leases, share capital.
- The auditor's plan, request list and timetable, saved in `Inputs/` as received.
- Last year's audited accounts from `Shared/Library` or `Archive/` in your tier.

## Steps

1. Create the year folder `Periods/<FYyyyy>/` in your tier with its four parts, if it does not exist.
2. Agree the timetable with the auditor and record it in `Shared/Claude/Calendar.md`, on the CFO's yes.
3. Run the month-end close for the last month, then the year-end adjustments: provisions, impairment checks, deferred tax, accruals for bonuses and audit fees.
4. Build the trial balance per entity and the consolidation, with intercompany eliminated and foreign currency translated.
5. Tie the full-year figures in the connector to the final trial balance. Explain every difference.
6. Prepare the lead schedules for each area on the auditor's list. Record each item supplied, when and to whom.
7. Track the auditor's queries and adjustments. Each proposed adjustment gets a line saying whether it was booked, and why.
8. Draft the statutory accounts notes the auditor will review, from the lead schedules.
9. When the accounts are signed, propose the date as a Decision line for `Memory/Log.md` in your tier, and propose moving the closed year to `Archive/` in your tier under the filing rules.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The full year agrees with the sum of the four quarters, after year-end adjustments that are listed.

## Output

The year-end trial balance and consolidation, the lead schedules, the auditor request and query log, and the draft notes.

## Where it is filed

Working papers in `Periods/<FYyyyy>/Working/` in your tier, items sent to the auditor and the signed accounts in `Outputs/`, a line in its log. The year moves to `Archive/` in your tier once the audit is signed.
<!-- cfo-os:template end body -->

## Your notes

