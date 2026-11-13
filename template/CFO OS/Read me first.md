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
