# Working with a finance connector

A finance data connector lets Claude read figures from a finance system instead of from files. It is fast and current, and it is easy to read wrongly. The connector rules in `Instructions.md` are short; this page explains each one. Guides for particular connectors are in [connectors/](connectors/).

## One scenario and one cycle per query

Finance systems hold several versions of each figure: actuals, one or more budgets, and a forecast that is re-cut each month or quarter. Each re-cut is a cycle, often named for months of actuals plus months of forecast, such as 9+3. If a query does not name the scenario and cycle, the connector picks a default, and the default may not be the one the person means.

So every query names one scenario and, for a forecast, one cycle, and every answer says which it used. Comparing two cycles is two queries, not one.

## Actuals to the reference month, then the current cycle

`Shared/Claude/Data.md` holds the reference month: the last closed month. A full-year view is actuals for every month up to and including it, then the current forecast cycle for every month after it.

Never add actuals and forecast for the same month. Many forecast cycles carry the closed months as well, copied from actuals or as they were forecast. Taking both double counts.

When a month closes and a new cycle is loaded, the reference month and the current cycle in `Data.md` move on together. Claude notices and proposes the update; someone in the `CFO` or `VP` tier accepts it.

## End-of-period metrics are not summed

Some metrics are flows: revenue, costs, cash movement. A quarter is the sum of its three months. Others are balances or counts at a point in time: cash, receivables, headcount, customers. A quarter is the value at its last month. Summing three months of closing cash gives a figure three times too large that means nothing.

The metric catalogue shows each metric's time roll-up. Read it before answering for a quarter or a year. Averages, such as an average headcount, are their own case: say how the average was taken.

A calculated metric built from a balance, such as revenue per head, needs care. If the connector sums it over months, the quarter value is wrong. The catalogue lists such metrics on its watch list.

## Prefer described metrics

A connector may expose many metrics, some old, some duplicates, some built for one report. Prefer a metric that has a description and no warning. If the answer has to use one without a description, say so, because its definition has not been confirmed. Metrics marked retired are not used.

## Slice with filters

To split a figure by entity, department or product, use the connector's dimension filters. Do not fetch every row and add them up in the chat: it is slow, and it is easy to miss rows or count eliminations twice. If the slices do not add up to the total, say why.

## Decline what the data cannot answer

Finance data does not hold everything: pipeline, contracts, headcount by name, the reason behind a journal. When the question needs data the connector does not hold, Claude declines, says what is missing, and names the fallback: a file to ask for, a person to ask, or a document in `Shared/Library`. It does not estimate a figure and present it as data.

`Data.md` lists the known limits. Each new one found goes there, once someone in the `CFO` or `VP` tier says yes.

## Say which sign convention a table uses

Connectors often use natural sign, with revenue positive and costs negative. Board packs often show costs as positive. Both are fine; mixing them is not. Every table says which convention it uses, and `Rules.md` records the company's.

## Test after every change

`Shared/Claude/Tests/Test questions.md` holds questions that exercise each rule. Run them after a deploy, an upgrade, a change to the instructions, or a change in the connected data. File each run in `Shared/Claude/Tests/Runs/`. A failure is either an instruction gap (the data was there; Claude read it wrongly) or a configuration gap (the data, a role or a name is missing or wrong).
