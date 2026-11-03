# Start here

<!-- cfo-os:template begin body -->
This folder is the CFO OS for {{cfo.name}}, {{cfo.title}} of {{company.name}}. It is a set of plain Markdown files that let Claude work as a careful finance analyst. Claude reads the facts, rules and workflows here, reads figures from {{connector.name}}, and files its work back into this folder. There is no database and no app. You can open, read and edit every file yourself.

Deployed from template {{deploy.version}} on {{deploy.date}} by {{deploy.deployer}}.

## Set up once

1. Create a Claude Project for this work.
2. Paste the whole of `00 System/Instructions.md` into the Project instructions. Paste it again whenever that file changes, and tell whoever deployed the folder so they can record it.
3. Connect {{connector.name}} to Claude, read-only.
4. Give Claude access to this folder, so it can read the files and write where the rules below allow.
5. Ask Claude to run the questions in `00 System/Tests/Test questions.md`, and file the result in `00 System/Tests/Runs/`.

## Start a session

Open a chat in the Project and say what you want, for example "start a session: forecast critique for the month just closed". Claude follows `04 Workflows/Every session/Start session.md`. It reads the context, the rules and the memory, then the workflow for the task, and tells you what it has read before it begins.

When you are done, say "close the session". Claude follows `04 Workflows/Every session/Close session.md` and proposes what to remember. Nothing is written to memory until you say yes.

## The three rules

1. **One home per fact.** Each kind of knowledge lives in one file, and everywhere else links to it. `00 System/Folder map.md` says where each thing goes.
2. **Nothing is deleted.** Finished work moves to `08 Archive`. Duplicates are flagged for you, never removed.
3. **Claude writes context and rules only on your yes.** Claude may propose a change to `01 Context` or `02 Rules and style`. It shows you the change and writes it only when you accept. Memory lines are proposed at session close in the same way.

## What is where

| Folder | Holds |
|---|---|
| `00 System` | The instructions Claude follows, the folder map, the changelog and the connector tests |
| `01 Context` | The company, the people, the data, the glossary and the calendar |
| `02 Rules and style` | Your rules, the output templates, and examples of outputs you liked |
| `03 Memory` | Key findings, decisions, open questions and lessons |
| `04 Workflows` | How each recurring job is done, step by step |
| `05 Periods` | Recurring work, one folder per month, quarter or year |
| `06 Projects` | Work with an end date that is not part of a cycle |
| `07 Library` | Reference documents, kept as received |
| `08 Archive` | Closed years and finished projects |
<!-- cfo-os:template end body -->
