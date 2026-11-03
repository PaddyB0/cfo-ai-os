# Changelog

All notable changes to this project are recorded here, newest first. The format follows Keep a Changelog, and versions follow Semantic Versioning. Each entry says which template regions changed, so a deployer knows what an upgrade will touch.

## 0.1.0 - 2026-11-02

First release.

### Added

- The `CFO OS` folder template: `START HERE.md`; `00 System` with the Claude Project instructions, the folder map, a changelog and connector test questions; `01 Context` with company, people, data, glossary and calendar files; `02 Rules and style` with a rules file and five output templates (management memo, variance table, board pack, management accounts, investor update); `03 Memory` with key findings, decisions, open questions and lessons; `04 Workflows` with a workflow template and twelve workflows (start session, close session, forecast critique, cash runway, month-end close, management accounts, board pack, quarterly accounts, investor reporting, budget, year-end and audit, board or investor question); and READMEs for `05 Periods` to `08 Archive`.
- The `cfo-os` command: `deploy`, `upgrade`, `check`, `pasted`, `catalogue` and `scrub`.
- A neutral metric list format and an adapter for the Datarails FinanceOS connector's metric list.
- Docs: memory model, working with a connector, the first connector guide, folder map, deploy, upgrade, writing a workflow.
- A fictional example answers file and metric list.

### Template regions

- `00 System/Instructions.md`: `reading-order`, `filing-rules`, `connector-rules`, `every-figure`, `session-close`.
- `00 System/Folder map.md`: `filing-rules`, `who-writes`.
- `00 System/Tests/Test questions.md`: `questions`, `pass-rule`.
- `START HERE.md`, every file in `04 Workflows/` and every file in `02 Rules and style/Templates/`: `body`.
