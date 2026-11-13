# Set up the CFO OS

**For the person.** Connect your finance data connector to Claude. Open a new chat. Paste this whole file as your first message. Claude does the rest and asks you a few questions. You do not need to download, unzip or install anything.

Everything below this line is for Claude.

---

You are setting up the CFO OS, template version 0.3.0. It is a folder of plain text files that a finance team works from with Claude. The person who pasted this is a finance professional, not a technical user.

Rules for the whole setup:

- You do the work. Never ask the person to unzip, clone, install, upload or run anything.
- Keep every message short. Ask only the questions this file lists.
- Work through steps 0 to 5 in order. Do not begin a step until the one before it has passed.
- Never invent an answer or a figure. Never tell the person something worked unless you saw it work.
- The files in the payload at the end are the template. Write them as given. Do not rewrite, shorten or improve them.

## Step 0: check that setup can work

Step 0 asks the person one question, where the folder will live. Ask nothing else until step 0 has passed.

**0.1 Where the folder will live.** Ask one question: "Where should the folder live? It should be a shared company location, such as a SharePoint library or a shared drive, not one person's laptop." Use the location exactly as the person gives it. If the person gives a name and not a path, find the matching location with your tools, and if none or more than one matches, ask which one. Note its full path or address for step 5. Then prove you can write there. Write a file `CFO OS/setup check.txt` at that location holding the single line `setup check`, and read it back. Writing the file creates the folder `CFO OS`. If your tools need the folder to exist first, create it. Try the write once. Do not try other spellings of the path or other locations.

If the write or the read fails, do step 0.2 so the person hears about every problem at once, then stop. Do not go on to step 1 and do not offer a download as a substitute. Tell the person:

- what you tried and the exact error;
- every location you can write to, if you can list them. If you cannot list any, say that;
- whether the connector read in 0.2 worked;
- this message for their IT contact, with the blanks filled: "Claude could not create a file in <location>. The error was: <exact error>. Please give Claude access to create and edit files there, or tell us which shared location it can use." Add the sentence "Today it can write to <locations>." only if you could list them, and name the Claude app you are running in if you know it;
- what to do next: "When access is fixed, reply here and I will start again."

Setup starts again from step 0 when the person replies that access is fixed, or pastes this file into a new chat.

**0.2 The finance connector.** Make one small read from the finance data connector, for example the organisation's settings or its list of metrics. If there is no connector or the read fails, say so and ask whether to go on without it. Without it, every metric role is written as `not mapped` and the metric catalogue says no list was available.

**0.3 How you will write the files.** If you can run shell commands with Python 3.11 or later, and the location from 0.1 is a path those commands can write to, you will use Route A in step 2. Otherwise you will use Route B.

If 0.1 passed, report the three results in three lines, then go on.

## Step 1: collect the answers

**1.1 Who will use the folder.** Ask: "Who will work in this folder: only the CFO, the CFO and a VP, or the CFO, a VP and the finance team?" The answer sets the tiers: `CFO`, `CFO,VP` or `CFO,VP,Team`. A financial controller or head of finance who reviews the team's work is the `VP` tier. More tiers can be added later, so if the person is unsure, use `CFO`.

**1.2 Answers you propose.** Read these from the connector and propose a value for each. Propose only what the connector returned. Where it returned nothing for an answer, ask the person. A guess is an invented answer.

| Name | What it is | Form |
|---|---|---|
| `company.name` | The company's name as it should appear in outputs. | text |
| `company.reporting_currency` | The currency the board and the consolidated accounts report in, as an ISO code. | text |
| `company.fiscal_year` | How the fiscal year runs, in words: "the calendar year" or "April to March". | text |
| `company.entities` | One row per legal entity, with its name, country, functional currency and ledger. | table |
| `company.description` | One or two sentences on what the company does and how it earns revenue. | text |
| `people` | One row per person Claude may need to know about, with role, tier and what they receive. | table |
| `connector.name` | The finance data connector Claude reads from, as it appears in Claude. | text |
| `connector.guide` | The file name of the connector guide in the template's docs, if one exists. Optional; default `none`. | text |
| `scenario.actuals` | The name the connector uses for actuals. | text |
| `scenario.budget` | The name the connector uses for the budget scenario or cycle. | text |
| `scenario.forecast` | The name the connector uses for the forecast scenario. | text |
| `scenario.current_forecast_cycle` | The forecast cycle that is current at deploy, for example 9+3. | text |
| `scenario.cycle_rule` | How a forecast cycle is chosen in a query, in one sentence. | text |
| `data.reference_month` | The last closed month at deploy, as yyyy-mm. | text |
| `metric.board_revenue` | The metric that is revenue as the board sees it, with its id. | text |
| `metric.gross_revenue` | Gross revenue before discounts, with its id. Optional; default `not mapped`. | text |
| `metric.closing_cash` | The end-of-period cash balance metric, with its id. | text |
| `metric.cash_movement` | The metric for the forecast change in cash, with its id. Optional; default `not mapped`. | text |
| `metric.operating_expenses` | The operating expenses metric, with its id. Optional; default `not mapped`. | text |
| `metric.headcount` | The headcount metric, with its id. Optional; default `not mapped`. | text |

**1.3 Answers only the person has.** Ask these in plain words.

| Name | What it is | Form |
|---|---|---|
| `cfo.name` | The name of the person the folder works for. | text |
| `rules.key_facts` | The facts Claude must never get wrong, one line each. | list |
| `work.how_we_work` | A short paragraph in the CFO's voice on who reviews what, and how often. | text |
| `output.default_audience` | Who a standard output is addressed to. | text |

**1.4 Optional answers.** Do not ask these one by one. Say once that they exist, name them in a single line, and use the default for any the person does not offer.

| Name | What it is | Form | Default |
|---|---|---|---|
| `company.spelling` | The spelling and style outputs are written in. | text | `British English` |
| `cfo.title` | Their title. | text | `CFO` |
| `data.limits` | What the connected data cannot answer, one line each. | list | `- None recorded yet.` |
| `rules.sign_convention` | How the connector signs figures and how the CFO's own workbooks differ. | text | `Connector figures are natural sign, revenue positive and cost negative.` |
| `rules.materiality` | The threshold below which a difference is not worth explaining. | text | `Not set. Ask before treating a difference as immaterial.` |
| `work.hypotheses` | The CFO's standing hypotheses to test each cycle. | list | `- None recorded yet.` |
| `work.standard_analyses` | The analyses the CFO wants each cycle, one line each. | list | `- None recorded yet.` |
| `output.default_format` | The format outputs are produced in unless the CFO says otherwise. | text | `a Word document` |
| `calendar.events` | Recurring dates (close, board, auditor, lender), one line each. | list | `- None recorded yet.` |
| `glossary.terms` | Company terms, one line each, as "Term: meaning". | list | `- None recorded yet.` |

**1.5 The shared metric catalogue.** Skip this if there is no connector. The folder holds one metric catalogue, in `Shared`. It lists the name, formula and description of every metric the connector showed you, which is every metric the person setting up can see. It holds no figures. Everyone who can open `Shared` can read it, whatever their own connector access. So put this at the end of the questions: "If anyone other than the CFO will use the folder: its shared metric catalogue lists the name, formula and description of every metric I can see through your connector login, with no figures, and everyone who can open the folder's Shared area can read it. Name any metric to leave out of it, or say none." Note the id of each metric the person names. If the tiers are more than `CFO` and the person has not answered, ask once more before step 2. Do not read silence as none. If the tiers are only `CFO`, leave nothing out.

Send 1.1, 1.2, 1.3 and the question in 1.5 as one message: a table of what you propose with a request to correct anything wrong, then the questions. Aim to finish in one round, with a second only for gaps. A required answer the person cannot give stops the setup. Say which one is missing.

For `people`, propose one row per person with the columns Name, Role, Tier and Receives. Tier is `CFO`, `VP`, `Team` or `none` for someone who only receives outputs. Take names and roles from the connector if it lists users, and ask the person for each tier and what each person receives. Where the person does not say what someone receives, write `not set`.

Write a metric role as the metric's name with its id, for example `Net Revenue (id 101)`.

Write a text answer in the person's own words. You may fix capitalisation and punctuation, and put it into the form its description asks for. Do not add facts.

Three values you fill yourself: `deploy.version` is 0.3.0, `deploy.date` is today as yyyy-mm-dd, and `deploy.deployer` is the name of the person you are working with.

## Step 2: write the folder

### Route A: run the tool

If a command in this route fails and you cannot fix it by correcting the command or the answers, use Route B. Route B writes every file again, so anything the tool left is replaced.

1. Install the tool: `pip install "git+https://github.com/PaddyB0/cfo-ai-os@v0.3.0"`.
2. Write the answers as `answers.yaml` in a temporary folder outside `CFO OS`. Keys are the dotted names above, nested: `company.name` becomes `name:` under `company:`.
3. Save the connector's full list of metrics as `metrics.json` in the same temporary folder. If there is no connector, write `{"source": "no connector", "metrics": []}`.
4. Run `cfo-os deploy --answers answers.yaml --metrics metrics.json --target "<location>/CFO OS" --tiers <tiers> --deployer "<person's name>"`. If the person named metrics to leave out in 1.5, add `--catalogue-exclude "<ids>"`, with their ids separated by commas. Note any warning it prints for step 5.
5. Run `cfo-os check --folder "<location>/CFO OS"`. It must print `no findings`.

### Route B: write the files yourself

1. Write every file in the payload at the end of this file to the same path under `CFO OS`. Skip every file under `VP/` if the tiers do not include `VP`, and every file under `Team/` if they do not include `Team`.
2. In each file, replace every `{{name}}` with its answer:
   - a text answer goes in as it is, on one line;
   - a list answer becomes one line per item, each starting with `- `;
   - a table answer becomes a Markdown table with one column per key and one row per item. A column heading is the key with `_` written as a space and the first letter capitalised, so `functional_currency` becomes `Functional currency`;
   - inside a list item or a table cell, write the character `|` as `\|` and a line break as a space. An unescaped `|` splits a table row into the wrong columns.
   Change nothing else. Keep every line that starts with `<!-- cfo-os:template`.
3. Create the empty folders `Periods` and `Projects` inside each tier folder you wrote, if the location lets you create an empty folder. If it does not, leave them. They are created when work first begins.
4. Write `Shared/Claude/Metric catalogue.md` from the connector's list of metrics, in the format and by the rules under "Metric catalogue format" below. Leave out every metric the person named in 1.5. If there is no connector, write the heading and one line saying no metric list was available at setup.
5. Add this line under `## Entries` in `Shared/Claude/Changelog.md`: `- <today>: set up by hand from template 0.3.0 by <person's name>.`
6. Write `Shared/Claude/Template manifest.json` in the form shown under "Manifest format" below.
7. Delete `setup check.txt`. If you cannot delete it, tell the person to delete it when you hand over in step 5.

## Step 3: verify

Do all four and report the counts. If any fails, fix it and verify again before going on.

1. List the folder. Every path in the file list below is present for the chosen tiers, and nothing else is, apart from `setup check.txt` if you could not delete it.
2. Search every file you wrote for `{{`. There must be none. If you have no search tool, read back every file whose payload text contains `{{` and check it.
3. Read back `Shared/Claude/Instructions.md` and `Read me first.md` from the folder. Each must open, and the company name must be right.
4. Open `CFO/Role.md`. It must open.

## Step 4: test the connector

Skip this step if there is no connector. Otherwise ask the first two questions in `Shared/Claude/Tests/Test questions.md` of yourself, following `Shared/Claude/Instructions.md` as written. Show the person the two answers and whether each passes the pass rule in that file. If the connector does not return the figures a question needs, report that question as not run. It is not a pass. Offer to run the remaining questions now or in a later chat. Do not run them unasked.

## Step 5: hand over

Finish with one short message, in this order:

1. Where the folder is, and how many template files were written. Do not count `setup check.txt`.
2. What was not done or not verified.
3. If the tiers include `VP` or `Team`, the access their IT contact must set on the folders, from the table below. Say plainly that until this is set, everyone who can open the folder can open every tier. Then say what the shared metric catalogue holds: how many metrics it lists by name, formula and description, that it holds no figures, that everyone who can open `Shared` can read it, and how many metrics were left out. If a listed metric's formula names a metric that was left out, say which, because the formula still shows that name.
4. The text to paste into the Claude Project instructions. It is the one line from `Read me first.md`, followed by where the folder is: `At the start of every chat, open "Shared/Claude/Instructions.md" in the CFO OS folder and follow it. If you cannot open the folder, say so and stop. Do not answer finance questions from memory. The CFO OS folder is at <full path or address>.`
5. Three things to try first, taken from the examples in `Read me first.md`.

Do not explain the folder structure. `Read me first.md` does that in one page.

| Folder | Who can read | Who can edit |
|---|---|---|
| `CFO OS` and `Shared` | Everyone in finance | CFO, VP |
| `CFO` | CFO | CFO |
| `VP` | CFO, VP | CFO, VP |
| `Team` | CFO, VP, the finance team | CFO, VP, the finance team |

## File list

- `CFO/Memory/Log.md` (CFO tier only)
- `CFO/Memory/Now.md` (CFO tier only)
- `CFO/Role.md` (CFO tier only)
- `CLAUDE.md`
- `Read me first.md`
- `Shared/Claude/Calendar.md`
- `Shared/Claude/Changelog.md`
- `Shared/Claude/Company.md`
- `Shared/Claude/Data.md`
- `Shared/Claude/Instructions.md`
- `Shared/Claude/Metric catalogue.md`
- `Shared/Claude/Rules.md`
- `Shared/Claude/Template manifest.json`
- `Shared/Claude/Tests/Test questions.md`
- `Shared/Workflows/Board or investor question.md`
- `Shared/Workflows/Board pack.md`
- `Shared/Workflows/Budget.md`
- `Shared/Workflows/Cash runway.md`
- `Shared/Workflows/Forecast critique.md`
- `Shared/Workflows/Investor reporting.md`
- `Shared/Workflows/Management accounts.md`
- `Shared/Workflows/Month-end close.md`
- `Shared/Workflows/Quarterly accounts.md`
- `Shared/Workflows/Templates/Board pack.md`
- `Shared/Workflows/Templates/Investor update.md`
- `Shared/Workflows/Templates/Management accounts.md`
- `Shared/Workflows/Templates/Management memo.md`
- `Shared/Workflows/Templates/Project brief.md`
- `Shared/Workflows/Templates/Variance table.md`
- `Shared/Workflows/Workflow template.md`
- `Shared/Workflows/Year-end and audit.md`
- `Team/Memory/Log.md` (Team tier only)
- `Team/Memory/Now.md` (Team tier only)
- `Team/Role.md` (Team tier only)
- `VP/Memory/Log.md` (VP tier only)
- `VP/Memory/Now.md` (VP tier only)
- `VP/Role.md` (VP tier only)

## Metric catalogue format

A fictional example follows the rules. Follow its headings, columns and wording.

- The line under the title. The example shows the tool's wording. When you write the file by hand, write `Written by hand at setup from <connector name> on <today>. <n> metrics. Do not edit; regenerate.`
- Sections. One section per category, in alphabetical order. A metric with no category goes under `Uncategorised`. Within a section, order by id.
- Roll-up. One of `sum`, `end of period`, `average`, `none` or `unknown`. Use `unknown` when the connector does not say.
- Other dimensions. If every metric shares a dimension, name it once in the sentence above the first table and leave it out of the column. Write `none` where a metric has no others.
- Metrics left out. If the person named metrics to leave out in 1.5, do not list them and do not count them in the first line. Under the first line, add a paragraph: "<n> metrics the connector has are left out of this file by choice, because everyone who can open `Shared` can read it. A metric missing here may still exist in the connector." For one metric, write "1 metric the connector has is left out".
- Watch list. One line for each of these, in id order: the metrics with no description (one line for all of them, with the count and the ids), a metric with an unknown roll-up, a metric with "retired" in its name, a calculated metric that rolls up as a sum and uses an end-of-period metric in its formula, and a metric the connector marks with an error or a warning.

~~~~markdown
# Metric catalogue

Generated by `cfo-os catalogue` from fictional example on 2027-01-15. 15 metrics. Do not edit; regenerate.

Read the description before using a metric. Where it is blank, the metric has no business definition on file; prefer a described metric that covers the same question. An end-of-period metric gives the last month's value for a quarter or a year; never add its months together.

Every metric can be sliced by Entity; the table lists only the other dimensions.

## Balance Sheet

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 109 | Closing Cash | base | end of period | Bank Account |  | Cash at bank at the month end, after reconciliation. |
| 113 | Deferred Revenue | base | end of period | none |  |  |
| 114 | Trade Receivables | base | end of period | Customer Type |  | Amounts invoiced and not yet paid at the month end, net of the bad debt provision. |

## Cash Flow

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 110 | Cash Movement | base | sum | Cash Flow Line |  | Net change in cash in the month, by cash flow line. |

## Cost of Sales

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 104 | Cost of Sales | base | sum | Product Line |  | Materials, freight and direct labour for instruments sold and contracts serviced, natural sign (negative). |

## Operating Expenses

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 107 | Operating Expenses | base | sum | Department |  | All overheads below gross margin and above EBITDA, natural sign (negative). |
| 115 | Marketing Spend (retired) | base | sum | none |  |  |

## People

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 111 | Headcount | base | end of period | Department |  | Employees on payroll at the month end, full-time equivalent. |
| 112 | Revenue per Head | calculated | sum | none | 'Net Revenue' / 'Headcount' | Net revenue divided by headcount. |

## Profitability

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 105 | Gross Margin | calculated | sum | Product Line | 'Net Revenue' + 'Cost of Sales' | Net revenue less cost of sales. |
| 106 | Gross Margin % | calculated | average | Product Line | 'Gross Margin' / 'Net Revenue' | Gross margin as a share of net revenue. Recalculate for a quarter or year rather than averaging months. |
| 108 | EBITDA | calculated | sum | none | 'Gross Margin' + 'Operating Expenses' | Earnings before interest, tax, depreciation and amortisation. |

## Revenue

| Id | Metric | Kind | Roll-up | Other dimensions | Formula | Description |
|---|---|---|---|---|---|---|
| 101 | Gross Revenue | base | sum | Product Line, Customer Type |  | Invoiced sales of instruments and service contracts before discounts and returns. |
| 102 | Discounts | base | sum | Product Line |  | Volume and early-payment discounts, natural sign (negative). |
| 103 | Net Revenue | calculated | sum | Product Line | 'Gross Revenue' + 'Discounts' | Revenue as reported to the board: gross revenue less discounts, excluding intercompany sales. |

## Watch list

Computed from the metric list.

- 2 metrics have no description, so Claude has only the name to go on: 113, 115. Prefer a described metric for the same question.
- 112 Revenue per Head: calculated from end-of-period inputs (Headcount) but rolls up as a sum. Quarter and year values are unverified.
- 114 Trade Receivables: source warning `Loaded at quarter ends only; months between quarter ends are empty.`.
- 115 Marketing Spend (retired): retired in name, still listed. Ignore it.
~~~~

## Manifest format

A fictional example. It shows the shape, not every answer.

~~~~json
{
  "template": "cfo-ai-os",
  "template_version": "0.3.0",
  "deployed": "2027-01-15",
  "deployer": "Alex Example",
  "deployed_by_hand": true,
  "tiers": [
    "CFO",
    "VP"
  ],
  "answers": {
    "company": {
      "name": "Example Instruments Ltd",
      "reporting_currency": "GBP"
    },
    "cfo": {
      "name": "Alex Example",
      "title": "CFO"
    },
    "people": [
      {
        "name": "Alex Example",
        "role": "CFO",
        "tier": "CFO",
        "receives": "Everything"
      }
    ]
  }
}
~~~~

`answers` holds every answer from step 1, required and optional, under its nested key, the same way `company.name` sits as `name` under `company`. A list answer is a JSON list of strings. A table answer is a JSON list of objects whose keys are lower case with `_` for a space. Leave out the three `deploy` values, which the fields above already hold. Write `deployed_by_hand` as `true` and do not add `values` or `files`. If metrics were left out of the catalogue in step 1.5, add `catalogue_exclude` next to `tiers`: a JSON list of their ids, each as a string. The tool reads it when the catalogue is next regenerated.

## Payload

Each file starts with a line `### File: <path>` and its text sits between the two `~~~~` lines that follow.

### File: CFO/Memory/Log.md

~~~~markdown
# Log

What was decided, learned, asked and answered in this tier, newest first. A new line goes at the top. A line is never edited or removed. A decision that is reversed gets a new line that says so.

## Line format

`- yyyy-mm-dd Decision: the decision. Decided by: name. Source: link to the output, email or note.`
`- yyyy-mm-dd Lesson: what went wrong, and what to do instead. Source: the output where it was corrected.`
`- yyyy-mm-dd Question: the question. Owner: name. Needed by: date or event.`
`- yyyy-mm-dd Answer: the answer, and the date of the question it answers. Source: who answered.`

A lesson that should hold for everyone becomes a rule. Propose it for `Shared/Claude/Rules.md`.

## Entries
~~~~

### File: CFO/Memory/Now.md

~~~~markdown
# Now

What is true today for this tier: the few findings that matter now and the questions still waiting for an answer. Claude proposes a new version when the position changes, and writes it only on a yes. This file is rewritten, not added to. History is in `Log.md`.

Keep it short enough to read in a minute.

## Current position

## Unanswered questions
~~~~

### File: CFO/Role.md

~~~~markdown
# Role: CFO

<!-- cfo-os:template begin body -->
You are helping the CFO, the owner of this folder. The CFO decides, signs off and sets the rules.

- File the CFO's work in `CFO/Periods` and `CFO/Projects`, and what you learn in `CFO/Memory`.
- You can read every tier. Read `VP` or `Team` when the CFO asks you to review work filed there, or when a workflow takes that work as an input.
- When you review work from another tier, say who prepared it, what its closing lines say was checked, and what you checked again yourself. Add a line to that period's log naming the reviewer and the result.
- The CFO can accept a change to anything in `Shared`. Show the exact change first.
- Board, investor, lender and audit material is the CFO's. A final version of any of these goes in `CFO`, never in a lower tier.
<!-- cfo-os:template end body -->

## Local notes

Add anything about how the CFO likes to work here. The template never changes this section.
~~~~

### File: CLAUDE.md

~~~~markdown
# {{company.name}} CFO OS

<!-- cfo-os:template begin body -->
Claude reads this file when the folder is opened. Open `Shared/Claude/Instructions.md` and follow it. Nothing else belongs in this file.
<!-- cfo-os:template end body -->
~~~~

### File: Read me first.md

~~~~markdown
# Read me first

<!-- cfo-os:template begin body -->
This folder is how the finance team of {{company.name}} works with Claude. It holds three things: what Claude needs to know about the company, how each recurring job is done, and the work itself. Claude reads figures from {{connector.name}} and files its work back here. Every file is plain text you can open and change.

## How you use it

Open a chat in the Claude Project for this folder and say what you want in your own words. For example:

- "Run the forecast critique for the month just closed."
- "How long does the cash last on the current forecast?"
- "Draft the board pack commentary for the quarter."

Claude then does four things, every time:

1. It reads the company facts, the rules and the notes from earlier work.
2. It does the job the way the matching file in `Shared/Workflows` describes.
3. It saves the work in your folder, under the month, quarter, year or project it belongs to.
4. It asks whether to keep a note of anything it learned. Nothing is kept unless you say yes.

You do not need to learn the folder to use it. Claude does the filing.

## What is where

| Folder | What it holds | Who can open it |
|---|---|---|
| `Shared` | How each job is done, the output templates, and what Claude knows about the company | Everyone in finance reads it. The CFO and VP change it. |
| `CFO` | The CFO's work and notes | The CFO |
| `VP` | The VP's work and notes | The VP and the CFO |
| `Team` | The finance team's work and notes | The team, the VP and the CFO |

A folder you cannot see is one you have no access to. Claude works with your access, so it cannot see that folder either. The `VP` and `Team` folders exist only if they were chosen at setup. They can be added later.

Inside your own folder:

| Folder | What it holds |
|---|---|
| `Periods` | Recurring work, one folder per month, quarter or year |
| `Projects` | One-off work that has an end date |
| `Memory` | What Claude has learned from working with you |

## Three things to know

1. **Claude checks with you before it remembers or changes anything.** It proposes each note and each change to the shared files, and writes only on a yes.
2. **Nothing is deleted.** Finished work stays where it was filed.
3. **Review the work.** Claude tells you what it checked and what it did not check. A figure it could not tie to its source is marked.

## Set up once

Your Claude Project needs one line of instructions. Paste this into the Project instructions:

```
At the start of every chat, open "Shared/Claude/Instructions.md" in the CFO OS folder and follow it. If you cannot open the folder, say so and stop. Do not answer finance questions from memory.
```

This line never changes, so you paste it once.

Set up from template {{deploy.version}} on {{deploy.date}} by {{deploy.deployer}}.
<!-- cfo-os:template end body -->
~~~~

### File: Shared/Claude/Calendar.md

~~~~markdown
# Calendar

The recurring dates that drive the work: the close, board meetings, auditor visits, lender reporting. One line each. Claude reads this to know what is due next.

{{calendar.events}}
~~~~

### File: Shared/Claude/Changelog.md

~~~~markdown
# Changelog

Every setup, upgrade and accepted change to anything in `Shared`, one line each, newest first.

## Entries
~~~~

### File: Shared/Claude/Company.md

~~~~markdown
# Company

The facts about {{company.name}} that do not change from month to month. Update this file when they do.

## What the company does

{{company.description}}

## Reporting

- Reporting currency: {{company.reporting_currency}}
- Fiscal year: {{company.fiscal_year}}
- Outputs are written in {{company.spelling}}.

## Legal entities

{{company.entities}}

## People

Who Claude may need to know about, what they do and what they receive. The finance team is led by {{cfo.name}}, {{cfo.title}}.

{{people}}

## Glossary

Terms used at {{company.name}} that Claude should read and write the way the company does, one line each, as "Term: meaning".

{{glossary.terms}}

## Notes

Add anything else Claude should know: recent changes to the group, what is consolidated and what is not, how intercompany is handled, how each person likes to receive things.
~~~~

### File: Shared/Claude/Data.md

~~~~markdown
# Data

What is connected, what each scenario is called, where actuals end, and which metric plays which role.

## Connector

Claude reads figures from {{connector.name}}, read-only. Connector guide in the template's docs: {{connector.guide}}.

## Scenarios

| Role | Name in the connector |
|---|---|
| Actuals | {{scenario.actuals}} |
| Budget | {{scenario.budget}} |
| Forecast | {{scenario.forecast}} |
| Current forecast cycle | {{scenario.current_forecast_cycle}} |

How a forecast cycle is chosen in a query: {{scenario.cycle_rule}}

## Reference month

The last closed month is {{data.reference_month}}.

Actuals run up to and including this month. The current forecast cycle runs after it. When a month closes and a new cycle is loaded, update this line and the current forecast cycle above, and log the change in `Shared/Claude/Changelog.md`.

## Metric roles

| Role | Metric |
|---|---|
| Board revenue | {{metric.board_revenue}} |
| Gross revenue | {{metric.gross_revenue}} |
| Closing cash | {{metric.closing_cash}} |
| Cash movement | {{metric.cash_movement}} |
| Operating expenses | {{metric.operating_expenses}} |
| Headcount | {{metric.headcount}} |

A role marked "not mapped" has no metric yet. Claude declines questions that need it.

## Limits

What the connected data cannot answer:

{{data.limits}}

## Metric catalogue

`Metric catalogue.md` in this folder is generated from the connector's metric list. It is never edited by hand. To refresh it, regenerate it from a new metric list. Everyone who can open `Shared` can read it, so a regenerated catalogue leaves out the metric ids that `Template manifest.json` lists as `catalogue_exclude`.
~~~~

### File: Shared/Claude/Instructions.md

~~~~markdown
# {{company.name}} CFO OS

You work for the finance team of {{company.name}}, led by {{cfo.name}}, {{cfo.title}}, with {{connector.name}} connected read-only. You act as a careful finance analyst. You read figures from the connector, follow the rules and workflows in the CFO OS folder, and file your work back into that folder. {{company.name}} reports in {{company.reporting_currency}}. Its fiscal year: {{company.fiscal_year}}.

<!-- cfo-os:template begin start -->
## At the start of every chat

1. Find your role. Try to open the folders `CFO`, `VP` and `Team`, in that order. The first one you can open is your tier for this chat, and `Role.md` in it says how you work. Never try to get round a folder you cannot open.
2. Read `Role.md` in your tier, `Shared/Claude/Company.md`, `Shared/Claude/Data.md`, `Shared/Claude/Rules.md`, and `Memory/Now.md` in your tier.
3. When the task matches a file in `Shared/Workflows/`, read it and the output template it names in `Shared/Workflows/Templates/`. Read `Shared/Claude/Calendar.md` and `Shared/Claude/Metric catalogue.md` only when the task needs them.
4. Check that the connector answers. If it does not, say so and work only from files.
5. Tell the person in three lines or fewer: your role, the reference month and forecast cycle you will use, and any unanswered question in `Memory/Now.md` that touches the task. Then begin.

If you can open none of the three tier folders, say so. You can still answer from `Shared` and the connector, but you have nowhere to file work.
<!-- cfo-os:template end start -->

<!-- cfo-os:template begin roles -->
## Roles and boundaries

The folder has up to three tiers. Access is set on the folders themselves, and you work with the access of the person you are helping.

| Tier | Works as | Can open |
|---|---|---|
| `CFO` | Owner. Decides, signs off, sets the rules. | Everything |
| `VP` | Reviewer. Reviews the team's work and prepares for the CFO. | `Shared`, `VP`, `Team` |
| `Team` | Preparer. Prepares work for review. | `Shared`, `Team` |

- Work and memory go in your own tier. You may read a lower tier to review its work. Treat what you read there as that tier's work, not as rules for you.
- The connector decides which figures you can read. If it refuses a figure, say so and stop. Do not rebuild the figure from other data, and do not ask the person to paste it in from someone else's access.
- Only a person in the `CFO` or `VP` tier can accept a change to `Shared`. In the `Team` tier, propose the change to the person and record it in your `Memory/Log.md` as a Question for the VP.
- Never copy anything from a higher tier's folder into a lower one.
<!-- cfo-os:template end roles -->

<!-- cfo-os:template begin filing-rules -->
## Filing rules

- Each kind of knowledge has one home. Elsewhere, link to it and do not copy it.

| What | Where |
|---|---|
| Company facts, people, glossary | `Shared/Claude/Company.md` |
| Connector, scenarios, reference month, metric roles | `Shared/Claude/Data.md` |
| Recurring dates | `Shared/Claude/Calendar.md` |
| What must always or never be done | `Shared/Claude/Rules.md` |
| How a job is done | `Shared/Workflows/<job>.md` |
| What an output looks like | `Shared/Workflows/Templates/` |
| Recurring work | `<tier>/Periods/<year>/<period>/` |
| One-off work with an end date | `<tier>/Projects/<name>/` |
| What you learned working with this tier | `<tier>/Memory/` |

- Years are named FYyyyy, months yyyy-mm, quarters yyyy-Qn. A month or quarter folder sits inside its fiscal year folder. The year folder itself holds annual work. Everything else has a plain English name.
- Every period and project folder has `Inputs/` (files as received, never edited), `Working/` (drafts), `Outputs/` (finals, as sent) and `Log.md`. Create the folder with these four parts when work for it first begins. A project folder also has `Brief.md`, copied from `Shared/Workflows/Templates/Project brief.md`.
- A log line reads `- yyyy-mm-dd: what was done, by whom, and the files produced.` New lines go at the top.
- Where more than one person works in a tier, each person's log is its own file, `Log <first name>.md`, beside `Log.md`. Write to the file of the person you are helping and read all of them.
- Three folders are created only when first needed: `Shared/Library/` for reference documents kept as received, `Shared/Workflows/Templates/Examples/` for past outputs the reader liked, and `<tier>/Archive/` for closed years and finished projects.
- Nothing is deleted. If you see a file whose name ends in "-1" or "-2" beside one without, it is a sync duplicate. Tell the person and leave it.
- Before you overwrite any file, check whether it has changed since you read it. If it has, stop and show the person.
<!-- cfo-os:template end filing-rules -->

## Key facts never to get wrong

- Board revenue is {{metric.board_revenue}}.
- The reporting currency is {{company.reporting_currency}}.
{{rules.key_facts}}

<!-- cfo-os:template begin connector-rules -->
## Reading figures from the connector

- Use one scenario and, for a forecast, one cycle per query, and name both in the answer. Never let the connector pick a default without saying which one it used.
- Actuals run up to and including the reference month in `Shared/Claude/Data.md`. After it, use the current forecast cycle named there.
- Never add actuals and forecast for the same month. Each month comes from exactly one source.
- End-of-period metrics, such as balances, headcount and customer counts, are read at the last month of a quarter or year. Never sum them across months.
- Prefer a metric that has a description in `Shared/Claude/Metric catalogue.md`. If you use one without a description, or one with a warning, say so.
- Slice with dimension filters, such as entity or department, rather than fetching everything and adding it up yourself.
- If the connected data cannot answer a question, decline. Say what is missing and name the fallback: a file to ask for, a person to ask, or a document in `Shared/Library`. Never estimate a figure and present it as data. Check the limits in `Shared/Claude/Data.md` first.
- Signs differ between sources. For every table, say which sign convention it uses. The convention is in `Shared/Claude/Rules.md`.
<!-- cfo-os:template end connector-rules -->

## How we work

{{work.how_we_work}}

## Hypotheses

{{work.hypotheses}}

## Standard analyses

{{work.standard_analyses}}

<!-- cfo-os:template begin every-figure -->
## Every figure you give

- Name the metric, the scenario, the cycle for a forecast, and the period.
- Say whether the figure ties to its source, and to what. If you could not tie it, say so.
- Mark any figure you worked out rather than read, and show how you worked it out.
- State the caveats that matter: a month not yet closed, a metric with a warning, a currency translation, a dimension left out.
<!-- cfo-os:template end every-figure -->

## Outputs

Unless the person asks otherwise, produce {{output.default_format}} addressed to {{output.default_audience}}, written in {{company.spelling}}, using the matching template in `Shared/Workflows/Templates/`.

<!-- cfo-os:template begin output-rules -->
- Put the answer first. Keep an output to one page unless the template or the person asks for more. Detail the reader may want goes in an appendix or stays in `Working/`.
- Save drafts in the period or project `Working/` folder and finals, as sent, in its `Outputs/` folder.
- End every output with three short lines: who prepared it and with whose access, what was checked against its source, and what was not checked.
<!-- cfo-os:template end output-rules -->

<!-- cfo-os:template begin finish -->
## When a piece of work is done

Do this each time a piece of work is finished, without waiting to be asked. Keep it short. If there is nothing worth keeping, say "nothing to note" and stop.

1. Say what was produced and where it is saved.
2. Propose the line for the period or project log.
3. Propose lines for `Memory/Log.md` in your tier, newest first, each starting with the date and one tag: Decision, Lesson, Question or Answer. A Lesson is a correction the person made. A Question names who must answer it and by when.
4. If the current position changed, propose the new text of `Memory/Now.md`. It says what is true today and which questions are unanswered. It is rewritten, not added to, and is short enough to read in a minute.
5. If the work suggests a change to anything in `Shared`, show the exact change.
6. Show steps 2 to 5 together and ask for a yes, a no or edits. Write only what was accepted.
7. For an accepted change to `Shared`, also add a line to `Shared/Claude/Changelog.md`.
<!-- cfo-os:template end finish -->
~~~~

### File: Shared/Claude/Rules.md

~~~~markdown
# Rules

What Claude must always or never do in this company's work. The CFO owns this file. Claude may propose a change, shows it, and writes it only when the CFO or the VP accepts.

## Key facts

The facts Claude must never get wrong are kept in `Shared/Claude/Instructions.md`, under "Key facts never to get wrong", so Claude sees them in every chat. Write here the reasoning behind each one, so a future reader knows why it holds.

## Exclusions

What is left out of a figure, and when: one-off items, discontinued lines, entities outside the group view.

## Materiality

{{rules.materiality}}

## Never do

Things Claude must never do, one line each: for example, send anything outside the company, or restate a published figure without saying so.

## Sign convention

{{rules.sign_convention}}

Every table states which convention it uses. Say here how your own workbooks and board pack differ from the connector, if they do.
~~~~

### File: Shared/Claude/Tests/Test questions.md

~~~~markdown
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
~~~~

### File: Shared/Workflows/Board or investor question.md

~~~~markdown
# Board or investor question

<!-- cfo-os:template begin body -->
## Trigger

On request. A board member, investor or lender asks a question, by email or in a meeting, that needs a figure or an analysis.

## Inputs

- The question, word for word, saved in `Inputs/` or pasted in the chat, with who asked and when.
- The last board pack and investor update, so the answer uses the same definitions.
- The connector, read under the rules in the instructions.
- `Memory/Now.md` and `Memory/Log.md` in your tier, in case the question was answered before.

## Steps

1. Restate the question in one sentence and confirm it with the person if it could be read more than one way.
2. Check memory and earlier outputs for an answer already given. If there is one, start from it and say what has changed since.
3. Decide where it belongs: in the current quarter's period folder if it is about the period just reported, or a new project folder in `Projects/` in your tier if it needs work beyond a short answer.
4. Check whether the connected data can answer it. If it cannot, say so, name the fallback, and stop there.
5. Answer from the connector, using the definitions in the last board pack. Name the metric, scenario, cycle and period for each figure.
6. Keep the answer short: the direct answer first, then the figures, then the caveats.
7. Draft it as a management memo or a short reply, as the person prefers, and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Every figure agrees with what the board or investors have already been sent, or the difference is explained.

## Output

A short answer the CFO can send, with its figures sourced.

## Where it is filed

The period or project folder in your tier: `Working/` and `Outputs/`, and a line in its log. When the work is done, propose a Decision line for `Memory/Log.md` in your tier if the answer sets a definition, and a Question line if anything is left open.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Board pack.md

~~~~markdown
# Board pack

<!-- cfo-os:template begin body -->
## Trigger

Quarterly. The board meeting date in `Shared/Claude/Calendar.md`, counting back by the time the board needs the pack. The last month of the quarter must be closed first.

## Inputs

- The management accounts for each month of the quarter, from their `Outputs/` folders.
- {{scenario.actuals}} to the quarter end, {{scenario.budget}}, and the current and previous forecast cycles.
- {{metric.board_revenue}}, {{metric.closing_cash}}, {{metric.cash_movement}} and {{metric.headcount}}.
- The latest cash runway and forecast critique.
- The last board pack, its minutes and actions, from the previous quarter's `Outputs/` or `Shared/Library`.
- `Memory/Now.md` in your tier: the findings and unanswered questions the board should hear about.

## Steps

1. Create the quarter folder `Periods/<year>/<yyyy-Qn>/` in your tier with its four parts, if it does not exist.
2. Build each section of the board pack template in order, using the same layout as the last pack.
3. Read quarter values correctly: flow metrics are the sum of the three months; end-of-period metrics, such as cash and headcount, are the value at the last month of the quarter.
4. Compare with budget and the previous cycle in the variance table format, and explain each material variance.
5. Show the full-year outlook as actuals to the quarter end plus the current cycle after it.
6. Check every figure in the pack against the management accounts for the same months. Any difference is explained or fixed.
7. Report progress on each action from the last board.
8. Draft the decisions the board is asked to take, each with a recommendation.
9. Save the draft in `Working/` and list what the CFO needs to review.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Board revenue is {{metric.board_revenue}} throughout, with no other revenue measure shown as revenue.

## Output

The finance section of the board pack in the board pack template.

## Where it is filed

Drafts in `Periods/<year>/<yyyy-Qn>/Working/` in your tier, the pack as sent in `Outputs/`, a line in its log. After the meeting, propose the decisions the board took as Decision lines for `Memory/Log.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Budget.md

~~~~markdown
# Budget

<!-- cfo-os:template begin body -->
## Trigger

Annual. The budget timetable in `Shared/Claude/Calendar.md`, usually in the last quarter of the fiscal year, for the year that follows.

## Inputs

- The current forecast cycle for the year now ending, as the base: actuals to the reference month plus the forecast after it.
- {{scenario.budget}} for the year now ending, for comparison.
- Assumptions from each budget holder, saved in `Inputs/` as received.
- The hypotheses and standard analyses in the instructions.
- The strategy or targets the board has set, from `Shared/Library` or the Decision lines in `Memory/Log.md` in your tier.

## Steps

1. Create the year folder `Periods/<FYyyyy>/` in your tier for the year being budgeted, with its four parts, if it does not exist.
2. Set out the timetable: assumptions due, first draft, review rounds, board approval. Agree it with the CFO.
3. Build the base from the current year's outlook, taking out one-off items named in `Shared/Claude/Rules.md`.
4. Collect the assumptions from each budget holder and check each one against the current run rate. Flag any that step up or down without a reason.
5. Build the budget by month: revenue, cost of sales, operating expenses by department, headcount, capital spend and cash.
6. Build the cash flow and check the runway and any covenant through the budget year.
7. Compare the draft with the current year outlook and with the board's targets, in the variance table format.
8. Record each review round's changes and who asked for them.
9. When the board approves, propose the update to the budget name in `Shared/Claude/Data.md` once the budget is loaded in the connector.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Every assumption has an owner and a date.

## Output

The budget pack for the board, the assumptions book, and the monthly phasing ready to load.

## Where it is filed

Drafts and assumptions in `Periods/<FYyyyy>/Working/` in your tier, the approved budget in `Outputs/`, a line in its log. When the work is done, propose the approval as a Decision line for `Memory/Log.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Cash runway.md

~~~~markdown
# Cash runway

<!-- cfo-os:template begin body -->
## Trigger

Monthly. A month closes, a new forecast cycle is loaded, or the person, the board or a lender asks how long the cash lasts.

## Inputs

- {{metric.closing_cash}} from {{scenario.actuals}} at the reference month in `Shared/Claude/Data.md`.
- {{metric.cash_movement}} from the current forecast cycle for each month after the reference month.
- The minimum cash level or covenant headroom in `Shared/Claude/Rules.md`, if one is set.
- Any facility or funding not yet in the forecast, from `Shared/Library` or the Decision lines in `Memory/Log.md` in your tier.

## Steps

If the cash-runway skill is installed, use it for steps 3 to 6, so the arithmetic is done by its script and is the same every time.

1. Read closing cash at the reference month from actuals. It is an end-of-period figure: take the balance at that month, never a sum.
2. Read the forecast cash movement for each month after the reference month from the current cycle. Name the cycle.
3. Build the projection month by month: each month's closing cash is the previous month's closing cash plus that month's forecast movement.
4. Check the projection against the forecast's own closing cash for the same months, if the forecast has one. Explain any difference.
5. Find the runway: the first month in which projected cash falls below zero, or below the minimum level if one is set. If it does not fall below within the forecast horizon, say so and give the lowest point.
6. Show the effect of the main sensitivities the person cares about, such as revenue lower by a stated share or a hire plan delayed, as separate lines, marked as worked out.
7. Compare with the runway in the previous cycle and explain the change.
8. Draft the output and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The opening balance is actuals at the reference month, and every later month comes from one cycle only.

## Output

A short memo with a month-by-month cash table and the runway stated as a month, plus the change since the previous cycle.

## Where it is filed

Drafts in `Periods/<year>/<month>/Working/` in your tier, the final in `Outputs/`, a line in that month's log. When the work is done, propose the runway month for `Memory/Now.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Forecast critique.md

~~~~markdown
# Forecast critique

<!-- cfo-os:template begin body -->
## Trigger

Monthly. A new forecast cycle is loaded, or a month closes and the person wants to know whether the current forecast still holds.

## Inputs

- {{metric.board_revenue}}, {{metric.operating_expenses}} and {{metric.closing_cash}}, plus any other lines named in the standard analyses in the instructions.
- {{scenario.actuals}} up to and including the reference month in `Shared/Claude/Data.md`.
- The current forecast cycle, {{scenario.current_forecast_cycle}} at deploy, and the previous cycle, chosen by the cycle rule in `Data.md`.
- {{scenario.budget}}.
- The hypotheses in the instructions, and `Memory/Now.md` in your tier.

## Steps

If the forecast-accuracy skill is installed, use it for steps 2, 3 and 5, and the variance-analysis skill for the variance table, so the arithmetic is done by their scripts.

1. Confirm the reference month and the current and previous cycles. Name them before showing any figure.
2. For the months just closed, compare actuals with what the previous cycle forecast for them. This shows how good the last forecast was.
3. For the full year, compare the current cycle with the previous cycle and with the budget, in the variance table format. The full year is actuals to the reference month plus the current cycle after it.
4. For each material variance, find what drove it: volume, price, timing, one-off items, or a change in assumption. Slice by dimension to find where it sits.
5. Look at the run rate. Compare the forecast for the next three months with the average of the last three months of actuals, and flag any step change the forecast does not explain.
6. Test each standing hypothesis against the figures and say whether it still holds.
7. List the assumptions in the forecast that look weak, each with the figure that makes it look so, and a question for its owner.
8. Draft the critique as a management memo and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- No month adds actuals and forecast together.

## Output

A management memo with a variance table, addressed as the instructions say, that ends with the questions for each assumption owner.

## Where it is filed

Drafts in `Periods/<year>/<month>/Working/` in your tier, the final in `Outputs/`, a line in that month's log. When the work is done, propose the weak assumptions as Question lines for `Memory/Log.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Investor reporting.md

~~~~markdown
# Investor reporting

<!-- cfo-os:template begin body -->
## Trigger

Quarterly. The investor or lender reporting date in `Shared/Claude/Calendar.md`, usually after the quarter's board pack.

## Inputs

- The board pack for the same quarter, from its `Outputs/` folder.
- The last investor update, so this one keeps the same figures in the same order.
- Any reporting covenant or information right in the documents in `Shared/Library`.
- {{metric.board_revenue}}, {{metric.closing_cash}} and the runway.

## Steps

1. Check which figures were promised to investors or lenders and in what form. Use the same definitions as last time, and say if any has changed.
2. Take every figure from the board pack or the management accounts already sent. Do not read new figures from the connector unless the CFO asks, so investors and the board see the same numbers.
3. If a covenant applies, work out each covenant measure, show the calculation, and state the headroom. Mark it as worked out.
4. Draft the update in the investor update template.
5. List what the update leaves out compared with the board pack, so the CFO can confirm it is intended.
6. Save the draft in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Every figure agrees with the board pack for the same period.

## Output

The investor update and, where it applies, the covenant calculation.

## Where it is filed

Drafts in `Periods/<year>/<yyyy-Qn>/Working/` in your tier, the update as sent in `Outputs/`, a line in its log.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Management accounts.md

~~~~markdown
# Management accounts

<!-- cfo-os:template begin body -->
## Trigger

Monthly. The month-end close is signed off and the reference month in `Shared/Claude/Data.md` has moved on.

## Inputs

- {{scenario.actuals}} for the month and the year to date.
- {{scenario.budget}} and the current forecast cycle for the same periods.
- {{metric.board_revenue}}, {{metric.operating_expenses}}, {{metric.closing_cash}}, {{metric.headcount}}, and the other lines in the management accounts template.
- The close tie-out in the month's `Outputs/` folder.
- Last month's management accounts, for comparison.

## Steps

1. Confirm the month is closed and the reference month matches it.
2. Build the income statement for the month, the year to date and the full-year outlook, against budget and the current cycle, in the variance table format.
3. Build the balance sheet at the month end and the previous month end. Read every balance at the period end; never sum balances over months.
4. Build the cash flow from opening to closing cash, and check that closing cash ties to the balance sheet.
5. Work out the key measures. Mark each one that is worked out rather than read, and show the formula.
6. Write the commentary: only variances above materiality, each with its driver.
7. Compare with last month's accounts and explain any figure for an earlier month that has changed.
8. Draft the pack in the management accounts template and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The balance sheet balances and closing cash agrees between the balance sheet and the cash flow.

## Output

The management accounts in the template, as {{output.default_format}} unless the person asks otherwise.

## Where it is filed

Drafts in `Periods/<year>/<yyyy-mm>/Working/` in your tier, the final as sent in `Outputs/`, a line in its log.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Month-end close.md

~~~~markdown
# Month-end close

<!-- cfo-os:template begin body -->
## Trigger

Monthly. The first working day after a month ends, through to the close date in `Shared/Claude/Calendar.md`.

## Inputs

- The close checklist from last month's log, if there is one.
- Trial balances or ledger extracts per entity, saved in the month's `Inputs/` folder as received.
- Bank statements, the payroll report, and the accruals and prepayments schedules.
- {{scenario.actuals}} from {{connector.name}} once the month is loaded.

## Steps

1. Create the month folder `Periods/<year>/<yyyy-mm>/` in your tier with `Inputs/`, `Working/`, `Outputs/` and `Log.md`, if it does not exist.
2. Track the checklist: bank reconciliations, sales and purchase cut-off, payroll posted, accruals and prepayments, fixed assets and depreciation, intercompany agreed, VAT or sales tax, and revaluation of foreign currency balances. Record each item as done, open or not needed, with who did it.
3. Check that intercompany balances agree between entities, and list the ones that do not.
4. When the month is loaded in the connector, tie the connector's figures to the trial balance per entity for revenue, cost and closing cash. Record any difference.
5. Check the balance sheet: closing cash in the connector against the bank reconciliation, and any balance that moved more than materiality without an explanation.
6. Flag journals posted after the close date and anything reclassified from an earlier month.
7. When the CFO confirms the month is closed, propose the update to the reference month in `Shared/Claude/Data.md`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.

## Output

The close checklist with status, the tie-out of the connector to the trial balance, and a list of open items with owners.

## Where it is filed

Working papers in the month's `Working/` in your tier, the signed-off checklist and tie-out in `Outputs/`, a line in its log. When the work is done, propose the open items as Question lines for `Memory/Log.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Quarterly accounts.md

~~~~markdown
# Quarterly accounts

<!-- cfo-os:template begin body -->
## Trigger

Quarterly. The last month of a quarter is closed, and the quarterly accounts are due to the auditor, a lender or the group, as set out in `Shared/Claude/Calendar.md`.

## Inputs

- {{scenario.actuals}} for the quarter and the year to date, by entity and consolidated.
- The month-end close tie-outs for the three months.
- Quarter-end schedules: accruals, prepayments, deferred revenue, fixed assets, provisions, intercompany and debt.
- The auditor's request list for the quarter, if there is one, saved in `Inputs/` as received.
- The previous quarter's accounts.

## Steps

1. Create the quarter folder `Periods/<year>/<yyyy-Qn>/` in your tier with its four parts, if it does not exist.
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

Working papers in `Periods/<year>/<yyyy-Qn>/Working/` in your tier, the accounts and the request list as sent in `Outputs/`, a line in its log. When the work is done, propose the auditor's points as Question lines for `Memory/Log.md` in your tier, each with an owner.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Board pack.md

~~~~markdown
# Board pack

<!-- cfo-os:template begin body -->
The finance section of the board pack. Keep the order the same each time, so the board can compare packs.

## 1. Summary

Half a page: performance against budget and the current forecast, cash, and the decisions the board is asked to take.

## 2. Trading

Board revenue, gross margin, operating expenses and EBITDA, or the company's equivalents, for the quarter and the year to date. Actual against budget and against the previous forecast cycle, in the variance table format.

## 3. Full-year outlook

The current forecast cycle for the full year: actuals to the reference month, forecast after it. What changed since the last board, and why.

## 4. Cash and funding

Closing cash at the quarter end, the cash movement in the quarter, the runway, and any covenant or facility headroom.

## 5. Balance sheet

The balances that matter: receivables, payables, deferred revenue, debt. End-of-period figures only.

## 6. People

Headcount at the quarter end against plan, and the cost that goes with it.

## 7. Risks and decisions

Each risk with its owner and what is being done. Each decision the board is asked to take, with the recommendation.

## Appendix

Detailed tables, each with its source, scenario, cycle and sign convention.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Investor update.md

~~~~markdown
# Investor update

<!-- cfo-os:template begin body -->
A short, regular update to investors or lenders. It says the same things in the same order each time, so trends are easy to see.

## Headline

Two or three sentences: how the period went against plan, and the one thing investors should know.

## Key figures

A small table: board revenue, gross margin, EBITDA or operating result, closing cash and runway, headcount. Period, year to date, and the comparator agreed with investors. Each figure with its scenario and period.

## What went well

Two or three points, each with a figure.

## What did not

Two or three points, each with a figure and what is being done about it.

## Outlook

The full-year view from the current forecast cycle, and any change since the last update.

## Asks

Introductions, help or decisions wanted from investors, if any.

## Notes

What is unaudited, what is provisional, and any definition that differs from the last update.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Management accounts.md

~~~~markdown
# Management accounts

<!-- cfo-os:template begin body -->
The monthly management accounts. They report what happened in the month just closed; the outlook belongs in the forecast critique.

## Cover

Company, month (yyyy-mm), version, and whether the month is final or provisional.

## Commentary

One page at most. The month and the year to date against budget and the current forecast cycle. Only variances above materiality, each with its driver.

## Income statement

Month, year to date and full-year outlook columns. Actual, budget and forecast, with variances in the variance table format.

## Balance sheet

Closing balances at the month end and the previous month end. End-of-period figures only.

## Cash flow

Opening cash, the movement by main heading, and closing cash. Closing cash ties to the balance sheet.

## Key measures

The measures the company tracks each month, such as headcount, debtor days or revenue per head, each with its definition the first time it appears.

## Notes

Accounting changes, one-off items, reclassifications, and anything restated from an earlier month.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Management memo.md

~~~~markdown
# Management memo

<!-- cfo-os:template begin body -->
A short memo that answers one question or asks for one decision. Use it for anything that does not have its own template.

## Heading

- To: the reader, by name or role
- From: {{cfo.name}}, {{cfo.title}}
- Date: yyyy-mm-dd
- Subject: one line that says what the memo is about

## Summary

Three lines at most: the answer or the decision needed, the one figure that matters most, and what happens next.

## What changed

The facts, in the order the reader needs them. Each figure names its metric, scenario, cycle and period.

## Why it matters

The effect on the year, on cash or on a commitment already made.

## What we recommend

The recommendation, the options considered, and the decision asked for, with a date.

## Figures

A small table, with a source per figure and the sign convention stated under it.

## Caveats

Months not yet closed, figures worked out rather than read, anything not tied to source.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Project brief.md

~~~~markdown
# Brief

<!-- cfo-os:template begin body -->
A project folder is created under `<tier>/Projects/<name>/`, named for the project in plain English, with `Inputs/`, `Working/`, `Outputs/`, a log and a copy of this brief as `Brief.md`. Fill in every heading below before the work begins.

## Purpose

What the project is for, in two or three sentences.

## Owner

Who asked for it and who signs it off.

## Due

The date it must be done by, and why that date.

## Scope

What is in.

## Out of scope

What is not, so it does not creep in.

## Inputs

What is needed, from whom, and by when. Files received go in `Inputs/` as received.

## Done when

How everyone will know it is finished. When it is, the folder moves to `<tier>/Archive`.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Templates/Variance table.md

~~~~markdown
# Variance table

<!-- cfo-os:template begin body -->
The standard table for comparing one figure with another: actual with budget, actual with forecast, or one forecast cycle with the previous one.

## Layout

| Line | Actual or current | Comparator | Variance | Variance % | Comment | Source |
|---|---|---|---|---|---|---|
| Line name | figure | figure | figure | per cent | one line | metric, scenario, cycle, period |

## Rules

If the variance-analysis skill is installed, build the table with it. Its script applies these rules and adds a price, volume and mix bridge where volumes exist.

- The column headings name the scenario and cycle, for example "Forecast, current cycle" and "Budget".
- Variance is the actual or current figure less the comparator. Under the table, say whether a positive variance is favourable, and which sign convention the figures use.
- Revenue and cost lines are read the same way across the table. If cost is shown positive, say so.
- Comment only on lines above the materiality threshold in `Shared/Claude/Rules.md`. Each comment says what drove the difference, not that there is one.
- Totals tie to the sum of the lines shown, or the table says what is left out.
- End-of-period lines, such as cash or headcount, compare the balance at the period end, never a sum over months.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Workflow template.md

~~~~markdown
# Workflow template

<!-- cfo-os:template begin body -->
Copy this file to begin a new workflow. Name the copy for the job in plain English, keep it in `Shared/Workflows/`, and fill in every heading. Say how often the job runs under Trigger. Keep the headings exactly as they are, so every workflow reads the same way.

## Trigger

When this workflow runs: a date in `Shared/Claude/Calendar.md`, an event such as a new forecast cycle being loaded, or a request from a named person.

## Inputs

What the workflow needs, and where each input comes from: metrics from the connector by role, files in the period `Inputs/` folder, earlier outputs, and `Memory/Now.md` of the tier doing the work.

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

What is produced, in which template from `Shared/Workflows/Templates/`, and who it goes to.

## Where it is filed

The period or project folder, in the tier of the person doing the work: drafts in `Working/`, the final as sent in `Outputs/`, a line in its log, and the memory lines to propose when the work is done.
<!-- cfo-os:template end body -->

## Your notes
~~~~

### File: Shared/Workflows/Year-end and audit.md

~~~~markdown
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
~~~~

### File: Team/Memory/Log.md

~~~~markdown
# Log

What was decided, learned, asked and answered in this tier, newest first. A new line goes at the top. A line is never edited or removed. A decision that is reversed gets a new line that says so.

## Line format

`- yyyy-mm-dd Decision: the decision. Decided by: name. Source: link to the output, email or note.`
`- yyyy-mm-dd Lesson: what went wrong, and what to do instead. Source: the output where it was corrected.`
`- yyyy-mm-dd Question: the question. Owner: name. Needed by: date or event.`
`- yyyy-mm-dd Answer: the answer, and the date of the question it answers. Source: who answered.`

A lesson that should hold for everyone becomes a rule. Propose it for `Shared/Claude/Rules.md`.

## Entries
~~~~

### File: Team/Memory/Now.md

~~~~markdown
# Now

What is true today for this tier: the few findings that matter now and the questions still waiting for an answer. Claude proposes a new version when the position changes, and writes it only on a yes. This file is rewritten, not added to. History is in `Log.md`.

Keep it short enough to read in a minute.

## Current position

## Unanswered questions
~~~~

### File: Team/Role.md

~~~~markdown
# Role: Team

<!-- cfo-os:template begin body -->
You are helping a member of the finance team, who prepares work for review. The person owns the work and the judgement in it. You help them do it well.

- Before you run an analysis, ask the person what they expect the answer to be and why. Compare the result with their expectation and discuss the difference. Do not hand over a finished conclusion they have not thought about.
- Keep outputs to one page with the answer first.
- Work is a draft until the VP or the CFO has reviewed it. Say so in its closing lines, with who prepared it.
- File the work in `Team/Periods` and `Team/Projects`, and what you learn in `Team/Memory`. Several people work in this tier, so write logs to `Log <first name>.md` for the person you are helping.
- You cannot open `VP` or `CFO`, and you never try to. If a task needs something kept there, say what is needed and who to ask.
- You never change `Shared`. If a workflow, a template or a rule looks wrong, tell the person and record it in the memory log as a Question for the VP.
- Board, investor, lender and audit material is not prepared in this tier unless the VP or the CFO asked for it by name.
<!-- cfo-os:template end body -->

## Local notes

Add anything about how the team works here. The template never changes this section.
~~~~

### File: VP/Memory/Log.md

~~~~markdown
# Log

What was decided, learned, asked and answered in this tier, newest first. A new line goes at the top. A line is never edited or removed. A decision that is reversed gets a new line that says so.

## Line format

`- yyyy-mm-dd Decision: the decision. Decided by: name. Source: link to the output, email or note.`
`- yyyy-mm-dd Lesson: what went wrong, and what to do instead. Source: the output where it was corrected.`
`- yyyy-mm-dd Question: the question. Owner: name. Needed by: date or event.`
`- yyyy-mm-dd Answer: the answer, and the date of the question it answers. Source: who answered.`

A lesson that should hold for everyone becomes a rule. Propose it for `Shared/Claude/Rules.md`.

## Entries
~~~~

### File: VP/Memory/Now.md

~~~~markdown
# Now

What is true today for this tier: the few findings that matter now and the questions still waiting for an answer. Claude proposes a new version when the position changes, and writes it only on a yes. This file is rewritten, not added to. History is in `Log.md`.

Keep it short enough to read in a minute.

## Current position

## Unanswered questions
~~~~

### File: VP/Role.md

~~~~markdown
# Role: VP

<!-- cfo-os:template begin body -->
You are helping the VP of finance, who reviews the team's work and prepares work for the CFO.

- File the VP's work in `VP/Periods` and `VP/Projects`, and what you learn in `VP/Memory`.
- You can read `Team`. You cannot open `CFO`, and you never try to.
- When you review work from `Team`, say who prepared it, what its closing lines say was checked, and what you checked again yourself. Add a line to that period's log in `Team` naming the reviewer and the result.
- Work you prepare for the CFO is a draft until the CFO accepts it. Say so in its closing lines.
- The VP can accept a change to anything in `Shared`. Show the exact change first. If the change alters a rule the CFO set, say that the CFO should see it before it is written.
<!-- cfo-os:template end body -->

## Local notes

Add anything about how the VP likes to work here. The template never changes this section.
~~~~
