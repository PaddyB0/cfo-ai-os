# The memory model

Claude does not remember one chat in the next. Everything it should know next time has to be written down, and everything written down has to be found again. The CFO OS folder does this with three ideas: one home per kind of knowledge, a clear rule for who writes each home, and a short proposal at the end of each piece of work that turns a chat into a few dated lines.

## One home per kind of knowledge

| Kind of knowledge | Home | Changes |
|---|---|---|
| How Claude should behave | `Shared/Claude/Instructions.md`, which the Claude Project's one-line instruction points to | Rarely, on an upgrade or an accepted change |
| How Claude works in a tier | `<tier>/Role.md` | Rarely |
| Facts about the company, its people and terms | `Shared/Claude/Company.md` | When the company changes |
| What is connected, and which metric plays which role | `Shared/Claude/Data.md` | Each month (reference month and cycle) |
| Recurring dates | `Shared/Claude/Calendar.md` | When a date moves |
| What the metrics are | `Shared/Claude/Metric catalogue.md` | Regenerated, never edited |
| What must always or never be done | `Shared/Claude/Rules.md` | When the CFO says so |
| How a job is done | `Shared/Workflows/` | When a workflow improves |
| What good output looks like | `Shared/Workflows/Templates/` and `Examples/` | Occasionally |
| What is true now, and what is unanswered | `<tier>/Memory/Now.md` | Rewritten when the position changes |
| Decisions, lessons, questions and answers, with dates | `<tier>/Memory/Log.md` | A dated, tagged line each |
| What was done in a period or project | the log in that folder | A dated line per piece of work |

Anywhere else, link to the home. A fact copied into two files will one day disagree with itself, and Claude cannot tell which copy is right.

## Current state and history are kept apart

`Now.md` says what is true today and which questions are unanswered. It is rewritten, not appended, so it stays short enough to read at the start of every chat. `Log.md` is history: newest line first, nothing removed, each line tagged Decision, Lesson, Question or Answer. A finding that stops being true leaves `Now.md`; the decision it led to stays in `Log.md`.

Memory belongs to a tier. What Claude learns working with the VP goes in `VP/Memory`, not in the CFO's. See [roles.md](roles.md).

## Who writes what

- The template owns the text inside template regions in system files. See [upgrade.md](upgrade.md).
- People own everything else, and may edit any file their access allows.
- Claude reads `Shared` and never edits it on its own. It may propose a change and show the exact text. A person in the `CFO` or `VP` tier can accept it; Claude then writes it and adds a line to `Shared/Claude/Changelog.md`.
- Claude writes `Memory/` and the period or project log in the tier it is working in, and only what the person accepts.
- Claude writes working files and outputs in that tier's `Periods/` and `Projects/` as the workflow says.

## When a piece of work is done

The `finish` region of `Instructions.md` says what Claude does, without being asked, each time a piece of work is finished. It proposes, all at once:

- the line for the period or project log;
- tagged lines for `Memory/Log.md`: a Decision with who decided, a Lesson for each correction, a Question with who must answer and by when, an Answer to a question closed;
- a new `Memory/Now.md` if the position changed;
- any change to `Shared` the work suggests.

The person says yes, no or edits each one. Claude checks that no file has changed since it read it, then writes only what was accepted. Where several people share a tier, each has a `Log <first name>.md`, and the check before rewriting `Now.md` stops one person's chat from overwriting another's.

This is slower than letting Claude write as it goes. A memory a person has read and accepted is one they can trust, and a wrong line caught when the work is done does not mislead the next ten chats.
