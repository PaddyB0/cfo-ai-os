# Security

## Reporting

Report a vulnerability through GitHub private vulnerability reporting on this repository: open the Security tab and choose "Report a vulnerability". Please do not open a public issue.

Include what you found, where, and how to reproduce it. You will get a reply as soon as practical. This is a personal project, so there is no fixed response time.

## What counts

- **A leak of client data is treated as a vulnerability.** This repository must hold no real company's name, people, figures, ids, entity structure or dates. If you find anything that looks like it came from a real company, report it privately in the same way.
- A secret, token or credential anywhere in the repository or its history.
- A way for `cfo-os deploy`, `upgrade` or `check` to write outside the target folder, delete a file, or overwrite text the CFO or Claude wrote.
- A way for the public-safety scan, `cfo-os scrub`, to miss something it is meant to catch.

## Supported versions

Only the latest release receives fixes.
