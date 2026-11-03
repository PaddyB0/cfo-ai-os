# Folder map

Where each kind of work and knowledge lives, and who may write it. Claude follows these rules in every session.

<!-- cfo-os:template begin filing-rules -->
## The eight filing rules

1. **One home per kind of knowledge.** Facts about the company live in `01 Context`. Rules and style live in `02 Rules and style`. What has been learned and decided lives in `03 Memory`. How a job is done lives in `04 Workflows`. Anywhere else, link to the home; do not copy it. A copied fact goes stale and then disagrees with the original.

2. **Recurring work goes in a period; one-off work goes in a project.** Work that comes round every cycle (the close, the management accounts, the board pack, the budget) goes in `05 Periods/<year>/<period>/`. Work with an end date that is not a cycle, such as a refinancing, a system change or an acquisition review, goes in `06 Projects/<name>/`.

3. **Every period and project folder has the same four parts.** `Inputs/` holds files as they were received and is never edited. `Working/` holds drafts and workings. `Outputs/` holds the final version of each output, exactly as sent. `Log.md` records, newest first, what was done and when.

4. **Claude reads the system, the context, the rules and the library, and never edits them on its own.** Claude reads `00 System`, `01 Context`, `02 Rules and style` and `07 Library`. It may propose a change to any of them, shows the exact change, and writes it only when the CFO accepts. Claude writes `03 Memory` at session close, on the CFO's yes.

5. **Nothing is deleted.** A closed year moves to `08 Archive` once its audit is signed. A finished project moves there when its brief says it is done. OneDrive sometimes makes a copy named with "-1" or "-2" at the end when two edits clash. Claude flags these to the CFO and never removes them.

6. **A new workflow starts from the template.** Copy `04 Workflows/Workflow template.md` and fill in every heading. A workflow that has been run the same way three times is a candidate for a Claude Skill. Its source is kept in `00 System/Skills/`.

7. **If work splits into several Claude Projects, memory stays shared.** When one Project per family of workflows (monthly, quarterly, annual) works better than one Project for everything, each Project reads `00 System` to `03 Memory` and its own workflow folder. `03 Memory` stays one shared set of files.

8. **Names follow one pattern.** Only top-level folders carry a two-digit prefix. Months are named yyyy-mm, for example `2027-03`. Quarters are named yyyy-Qn, for example `2027-Q1`. Years are named FYyyyy, for example `FY2027`. Everything else has a plain English name, with spaces, that a person can read.
<!-- cfo-os:template end filing-rules -->

<!-- cfo-os:template begin who-writes -->
## Who writes each folder

| Folder | Holds | Who writes it |
|---|---|---|
| `00 System` | Instructions, folder map, changelog, tests | The template and the person who deploys it. The CFO may add notes outside the template regions. Claude proposes only. |
| `01 Context` | Company, people, data, glossary, calendar | The CFO, or Claude on the CFO's yes. `Metric catalogue.md` is generated and never edited. |
| `02 Rules and style` | Rules, output templates, examples | The CFO, or Claude on the CFO's yes |
| `03 Memory` | Key findings, decisions, open questions, lessons | Claude at session close on the CFO's yes, and the CFO |
| `04 Workflows` | How each recurring job is done | The template; the CFO adds notes and new workflows; Claude proposes only |
| `05 Periods` | Recurring work by month, quarter and year | Claude and the CFO, following rule 3 |
| `06 Projects` | One-off work with an end date | Claude and the CFO, following rule 3 |
| `07 Library` | Reference documents as received | The CFO |
| `08 Archive` | Closed years and finished projects | The CFO moves things here; nothing is edited once archived |
<!-- cfo-os:template end who-writes -->

## Local additions

Add any filing rule of your own here. The template never changes this section.
