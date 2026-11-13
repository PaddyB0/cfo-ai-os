# Set up the CFO OS

**For the person.** Connect your finance data connector to Claude. Open a new chat. Paste this whole file as your first message. Claude does the rest and asks you a few questions. You do not need to download, unzip or install anything.

Everything below this line is for Claude.

---

You are setting up the CFO OS, template version [[version]]. It is a folder of plain text files that a finance team works from with Claude. The person who pasted this is a finance professional, not a technical user.

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

[[questions_connector]]

**1.3 Answers only the person has.** Ask these in plain words.

[[questions_person]]

**1.4 Optional answers.** Do not ask these one by one. Say once that they exist, name them in a single line, and use the default for any the person does not offer.

[[questions_optional]]

**1.5 The shared metric catalogue.** Skip this if there is no connector. The folder holds one metric catalogue, in `Shared`. It lists the name, formula and description of every metric the connector showed you, which is every metric the person setting up can see. It holds no figures. Everyone who can open `Shared` can read it, whatever their own connector access. So put this at the end of the questions: "If anyone other than the CFO will use the folder: its shared metric catalogue lists the name, formula and description of every metric I can see through your connector login, with no figures, and everyone who can open the folder's Shared area can read it. Name any metric to leave out of it, or say none." Note the id of each metric the person names. If the tiers are more than `CFO` and the person has not answered, ask once more before step 2. Do not read silence as none. If the tiers are only `CFO`, leave nothing out.

Send 1.1, 1.2, 1.3 and the question in 1.5 as one message: a table of what you propose with a request to correct anything wrong, then the questions. Aim to finish in one round, with a second only for gaps. A required answer the person cannot give stops the setup. Say which one is missing.

For `people`, propose one row per person with the columns Name, Role, Tier and Receives. Tier is `CFO`, `VP`, `Team` or `none` for someone who only receives outputs. Take names and roles from the connector if it lists users, and ask the person for each tier and what each person receives. Where the person does not say what someone receives, write `not set`.

Write a metric role as the metric's name with its id, for example `Net Revenue (id 101)`.

Write a text answer in the person's own words. You may fix capitalisation and punctuation, and put it into the form its description asks for. Do not add facts.

Three values you fill yourself: `deploy.version` is [[version]], `deploy.date` is today as yyyy-mm-dd, and `deploy.deployer` is the name of the person you are working with.

## Step 2: write the folder

### Route A: run the tool

If a command in this route fails and you cannot fix it by correcting the command or the answers, use Route B. Route B writes every file again, so anything the tool left is replaced.

1. Install the tool: `pip install "git+https://github.com/PaddyB0/cfo-ai-os@v[[version]]"`.
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
5. Add this line under `## Entries` in `Shared/Claude/Changelog.md`: `- <today>: set up by hand from template [[version]] by <person's name>.`
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

[[file_list]]

## Metric catalogue format

A fictional example follows the rules. Follow its headings, columns and wording.

- The line under the title. The example shows the tool's wording. When you write the file by hand, write `Written by hand at setup from <connector name> on <today>. <n> metrics. Do not edit; regenerate.`
- Sections. One section per category, in alphabetical order. A metric with no category goes under `Uncategorised`. Within a section, order by id.
- Roll-up. One of `sum`, `end of period`, `average`, `none` or `unknown`. Use `unknown` when the connector does not say.
- Other dimensions. If every metric shares a dimension, name it once in the sentence above the first table and leave it out of the column. Write `none` where a metric has no others.
- Metrics left out. If the person named metrics to leave out in 1.5, do not list them and do not count them in the first line. Under the first line, add a paragraph: "<n> metrics the connector has are left out of this file by choice, because everyone who can open `Shared` can read it. A metric missing here may still exist in the connector." For one metric, write "1 metric the connector has is left out".
- Watch list. One line for each of these, in id order: the metrics with no description (one line for all of them, with the count and the ids), a metric with an unknown roll-up, a metric with "retired" in its name, a calculated metric that rolls up as a sum and uses an end-of-period metric in its formula, and a metric the connector marks with an error or a warning.

[[catalogue_example]]

## Manifest format

[[manifest_example]]

## Payload

Each file starts with a line `### File: <path>` and its text sits between the two `~~~~` lines that follow.

[[payload]]
