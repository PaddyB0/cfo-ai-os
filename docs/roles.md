# Roles and access

A `CFO OS` folder has one folder per tier of the finance team. Which tiers exist is chosen at deploy with `--tiers`. This page says who each tier is for, how to set the folder access, and what that access does and does not protect.

## The tiers

| Tier | Who | Role in the work |
|---|---|---|
| `CFO` | the CFO | owner: sets the rules, accepts changes to `Shared`, signs off outputs |
| `VP` | a VP of finance or financial controller | reviewer: reviews the team's work, prepares work for the CFO and accepts changes to `Shared` |
| `Team` | analysts and accountants | preparer: prepares the work for review |

`CFO` is always deployed. Each tier folder holds its own `Role.md`, which tells Claude how to work with that person, and its own `Memory/`, `Periods/` and `Projects/`.

## Access

| Folder | Read | Edit |
|---|---|---|
| `CFO OS` top level and `Shared` | everyone in finance | CFO and VP |
| `CFO` | CFO | CFO |
| `VP` | CFO and VP | CFO and VP |
| `Team` | CFO, VP and the team | CFO, VP and the team |

On SharePoint, give the `CFO OS` folder its own document library. Set the library to the first row of the table, then break inheritance on the three tier folders and give each one unique permissions as the table shows. On OneDrive, share each tier folder with its people only.

## What Shared shows everyone

Every tier can read `Shared`. Most of it is the team's own rules and workflows. One file is different. `Shared/Claude/Metric catalogue.md` is generated from the metric list of whoever ran the deploy or the setup prompt. It lists each metric's name, kind, roll-up, dimensions, formula and description, and holds no figures. A person whose connector access hides a metric can still read that metric's line in the catalogue.

Decide at deploy which metrics the whole team may know about. `cfo-os deploy --catalogue-exclude <id>,<id>` leaves metrics out of the catalogue, and the setup prompt asks the same question. The manifest keeps their ids as `catalogue_exclude`, so `cfo-os upgrade --catalogue` leaves the same metrics out, and `--catalogue-exclude` on upgrade changes the list. The catalogue says how many metrics were left out, not which.

Three limits:

1. A formula that stays in the catalogue still names the metrics it uses. The tool warns when one of them is left out. Leave the calculated metric out too if the name must not be shared.
2. `cfo-os catalogue`, run on its own, does not read the folder. Pass it `--exclude` with the manifest's list.
3. Leaving a metric out hides its definition from the folder. Who can read its figures is still decided by the connector.

When a tier is added later, check the list again before the new people get access.

## What is enforced and what is not

Two things are enforced: the folder permissions, by SharePoint or OneDrive, and the finance connector's own per-user permissions, if it has them. Claude works with the access of the person using it. It cannot open a folder that person cannot open, or read data the connector does not give them.

Everything else is an instruction to Claude, not a control. The `Role.md` files and the `roles` region of `Shared/Claude/Instructions.md` tell Claude to ask a team member what they expect before it runs an analysis, to keep their outputs to one page, to mark work as a draft until it is reviewed, and never to copy anything from a higher tier's folder into a lower one. Claude follows these, but a person can ask it not to, and a rule written in a prompt is not an access control. Anything that must stay with the CFO goes in a folder only the CFO can open.

## Three things to confirm

1. Each person signs in to the finance connector as themselves, never through a shared login. A shared login gives everyone the data of whoever set it up.
2. Whether the connector applies per-user data permissions is a question for its vendor. This template does not verify it. Ask before you rely on it.
3. A shared Claude Project's own instructions and knowledge are visible to every member of the Project. That is why the Project holds only the one-line pointer from `Read me first.md`, and everything else lives in the folder, behind its permissions.

## Several people in one tier

When more than one person works in a tier, each keeps a `Log <first name>.md` next to the shared `Log.md`, in `Memory/` and in each period or project folder. Claude writes to the log of the person it is working with. Before it rewrites `Memory/Now.md`, Claude checks that the file has not changed since it read it, so one person's chat does not overwrite another's.

## Adding a tier later

```
cfo-os upgrade --folder "<path>/CFO OS" --tiers CFO,VP --apply
```

This writes the new tier folder's files and records the tier in the manifest. Then set the new folder's access as the table above shows. A tier is never removed by the tool; see [upgrade.md](upgrade.md).
