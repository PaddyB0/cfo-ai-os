"""cfo-os: deploy, upgrade and check a CFO OS folder.

    cfo-os deploy     a new folder from the template, an answers file and a metric list
    cfo-os upgrade    move a deployed folder to this template version (dry run by default)
    cfo-os check      check a folder against its filing rules
    cfo-os pasted     record that Instructions.md was pasted into the Claude Project
    cfo-os catalogue  render a metric list as the metric catalogue
    cfo-os scrub      the public-safety scan of this repository
"""

from __future__ import annotations

import sys

from . import __version__


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if argv[0] == "--version":
        print(__version__)
        return 0
    command, rest = argv[0], argv[1:]
    if command == "deploy":
        from .deploy import main as run
    elif command == "upgrade":
        from .upgrade import main as run
    elif command == "check":
        from .check_folder import main as run
    elif command == "pasted":
        from .check_folder import main as check_main
        return check_main(rest, pasted=True)
    elif command == "catalogue":
        from .catalogue.build import main as run
    elif command == "scrub":
        from .scrub_check import main as run
    else:
        print(f"unknown command {command!r}; run cfo-os --help", file=sys.stderr)
        return 2
    return run(rest)
