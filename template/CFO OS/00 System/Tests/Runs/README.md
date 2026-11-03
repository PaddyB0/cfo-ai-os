# Test runs

One file per run of `Test questions.md`, named `yyyy-mm-dd.md` for the day of the run. A second run on the same day adds a short suffix in plain English, for example `2027-03-04 after paste.md`. Runs are never edited after they are filed.

## Format

Start each run with these lines:

```
# Test run yyyy-mm-dd

- Template version: the version in Changelog.md
- Instructions last pasted: yyyy-mm-dd
- Reference month: yyyy-mm
- Current forecast cycle: as named in 01 Context/Data.md
- Run by: name
```

Then one row per question, including your own questions:

| Question | Result | Failure class | Note |
|---|---|---|---|
| 1 Board revenue by month | pass | | Actuals to the reference month, then the current cycle |
| 7 Data cannot answer | fail | instruction gap | Estimated a figure instead of declining |

`Result` is `pass` or `fail`. `Failure class` is `instruction gap` or `configuration gap`, and empty for a pass. The note says what was seen, briefly. Each failure becomes an open question in `03 Memory/Open questions.md` with an owner.
