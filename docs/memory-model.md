# The memory model

Claude does not remember one chat in the next. Everything it should know next time has to be written down, and everything written down has to be found again. The CFO OS folder does this with three ideas: one home per kind of knowledge, a clear rule for who writes each home, and a session close that turns a chat into a few dated lines.

## One home per kind of knowledge

| Kind of knowledge | Home | Changes |
|---|---|---|
| How Claude should behave | `00 System/Instructions.md`, pasted into the Claude Project | Rarely, on an upgrade or an accepted change |
| Where things go | `00 System/Folder map.md` | Rarely |
| Facts about the company | `01 Context/` | When the company changes |
| What is connected, and which metric plays which role | `01 Context/Data.md` | Each month (reference month and cycle) |
| What the metrics are | `01 Context/Metric catalogue.md` | Regenerated, never edited |
| What must always or never be done | `02 Rules and style/Rules.md` | When the CFO says so |
| What good output looks like | `02 Rules and style/Templates/` and `Examples/` | Occasionally |
| What we know now | `03 Memory/Key findings.md` | Rewritten at each session close |
| What was decided, and when | `03 Memory/Decisions.md` | A dated line per decision |
| What is not yet known, and who owes the answer | `03 Memory/Open questions.md` | A dated line per question |
| What went wrong and how to avoid it | `03 Memory/Lessons.md` | A dated line per correction |
| How a job is done | `04 Workflows/` | When a workflow improves |
| What was done in a period or project | `Log.md` in that folder | A dated line per session |

Anywhere else, link to the home. A fact copied into two files will one day disagree with itself, and Claude cannot tell which copy is right.

## Current state and history are kept apart

`Key findings.md` says what is true now. It is rewritten, not appended, so it stays short enough to read at the beginning of every session. `Decisions.md`, `Open questions.md` and `Lessons.md` are logs: newest line first, nothing removed. A finding that stops being true leaves `Key findings.md`; the decision it led to stays in `Decisions.md`.

## Who writes what

- The template owns the text inside template regions in system files. See [upgrade.md](upgrade.md).
- The CFO owns everything else, and may edit any file.
- Claude reads `00 System`, `01 Context`, `02 Rules and style` and `07 Library`, and never edits them on its own. It may propose a change, show the exact text, and write it when the CFO accepts. Each accepted change gets a line in `Decisions.md` and in `00 System/Changelog.md`.
- Claude writes `03 Memory` and the period or project `Log.md` only at session close, and only what the CFO accepts.
- Claude writes working files and outputs in `05 Periods` and `06 Projects` as the workflow says.

## The session close

At the end of a session Claude follows `04 Workflows/Every session/Close session.md`. It proposes, all at once:

- dated lines for `Decisions.md`, each with who decided and a source;
- a rewrite of `Key findings.md`;
- new lines for `Open questions.md`, each with an owner, and answers to any closed in the session;
- lines for `Lessons.md` for each correction the CFO made;
- a line for the period or project `Log.md`;
- any change to the system, context or rules the session suggests.

The CFO says yes, no or edits each one. Claude checks that no file has changed since it read it, then writes only what was accepted.

This is slower than letting Claude write as it goes. It is worth it: memory that the CFO has read and accepted is memory the CFO can trust, and a wrong line caught at close does not mislead the next ten sessions.

## Several Projects

If one Claude Project for everything becomes too broad, split it into one Project per workflow family. Each reads `00 System` to `03 Memory` and its own workflow folder. `03 Memory` stays one shared set of files, so a decision made in the monthly Project is known to the quarterly one.
