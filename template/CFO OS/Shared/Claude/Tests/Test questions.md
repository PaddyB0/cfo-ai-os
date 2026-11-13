# Test questions

Questions that check Claude reads {{connector.name}} correctly with these instructions. Run them after setup, after every upgrade, and whenever the connected data changes shape. File each run in `Runs/` beside this file, as described at the end.

<!-- cfo-os:template begin questions -->
## Connector questions

1. **Board revenue by month for the fiscal year.**
   Ask: "Show board revenue by month for the current fiscal year."
   What a pass looks like: {{metric.board_revenue}} for every month of the year. Actuals up to and including {{data.reference_month}}, then the current forecast cycle, {{scenario.current_forecast_cycle}}, after it. The answer names the scenario for each month and the cycle, gives a total, and never adds actuals and forecast for the same month.

2. **Closing cash and runway.**
   Ask: "What was closing cash at the reference month, and how long is the runway?"
   What a pass looks like: {{metric.closing_cash}} at {{data.reference_month}} from actuals. The runway is that balance plus the cumulative forecast movement, {{metric.cash_movement}}, from the current cycle, month by month, until cash would fall below zero or below the minimum the rules set. The answer shows the months it used and names the cycle.

3. **An end-of-period metric at a quarter.**
   Ask: "What was headcount at the end of the last closed quarter?"
   What a pass looks like: {{metric.headcount}} read at the last month of the quarter, not summed or averaged over the three months. If headcount is not mapped, the answer says so and declines.

4. **Current cycle against the previous cycle and the budget.**
   Ask: "Compare full-year board revenue in the current forecast cycle with the previous cycle and the budget."
   What a pass looks like: three totals, each with its scenario and cycle named. The previous cycle is the one before {{scenario.current_forecast_cycle}}, chosen by the cycle rule in `Shared/Claude/Data.md`. Variances are shown with a sign convention stated.

5. **A slice by dimension.**
   Ask: "Split operating expenses for the reference month by entity."
   What a pass looks like: {{metric.operating_expenses}} for {{data.reference_month}}, sliced with an entity filter. The entity figures add up to the total, or the answer explains why not (for example eliminations).

6. **A metric without a description.**
   Ask about a metric that has no description in `Shared/Claude/Metric catalogue.md`.
   What a pass looks like: the answer gives the figure and says the metric has no description, so its definition is not confirmed. If a better-described metric exists, it names it.

7. **A question the data cannot answer.**
   Ask about something listed under limits in `Shared/Claude/Data.md`, or something plainly outside a finance ledger, such as sales pipeline by customer.
   What a pass looks like: Claude declines, says what is missing, and names a fallback: a file to request, a person to ask, or a document in `Shared/Library`. It does not estimate a figure.

8. **Gross to net revenue.**
   Ask: "Bridge gross revenue to board revenue for the reference month."
   What a pass looks like: {{metric.gross_revenue}} to {{metric.board_revenue}} for {{data.reference_month}}, each step named with its source and sign. If gross revenue is not mapped, the answer says so and declines.
<!-- cfo-os:template end questions -->

<!-- cfo-os:template begin pass-rule -->
## Pass rule

An answer passes when all of these hold:

- it is answered from the connector, not from memory or a guess;
- it ties to its source, or says plainly that it does not and why;
- it states the scenario, the cycle for any forecast, and the reference month it used.

Declining correctly counts as a pass. An answer that invents a figure to avoid declining is a failure.

Class each failure as one of two kinds:

- **Instruction gap:** the data was there, but Claude read it the wrong way. The fix belongs in `Instructions.md`, a workflow or `Rules.md`.
- **Configuration gap:** the data, a metric role or a scenario name is missing or wrong. The fix belongs in `Shared/Claude/Data.md` or in the connected data itself.
<!-- cfo-os:template end pass-rule -->

<!-- cfo-os:template begin runs -->
## Filing a run

One file per run in `Runs/`, named `yyyy-mm-dd.md` for the day of the run. Create the folder at the first run. A run is never edited after it is filed. Start it with these lines:

```
# Test run yyyy-mm-dd

- Template version: the version in Changelog.md
- Reference month: yyyy-mm
- Current forecast cycle: as named in Data.md
- Run by: name, and the tier they ran it in
```

Then one row per question, including your own questions:

| Question | Result | Failure class | Note |
|---|---|---|---|
| 1 Board revenue by month | pass | | Actuals to the reference month, then the current cycle |
| 7 Data cannot answer | fail | instruction gap | Estimated a figure instead of declining |

`Result` is `pass` or `fail`. `Failure class` is `instruction gap` or `configuration gap`, and empty for a pass. Each failure becomes a Question in the memory log of the tier that ran the test, with an owner.
<!-- cfo-os:template end runs -->

## Your own questions

Add questions that matter to this company here, each with what a pass looks like. The template never changes this section.
