"""cfo-os: deploy, upgrade and check a CFO OS folder.

    cfo-os deploy     a new folder from the template, an answers file and a metric list
    cfo-os upgrade    move a deployed folder to this template version (dry run by default)
    cfo-os check      check a folder against its filing rules
    cfo-os catalogue  render a metric list as the metric catalogue
    cfo-os prompt     build the setup prompt, SETUP.md (from a clone of the repository)
    cfo-os scrub      the public-safety scan of this repository
    cfo-os skills     package the plugin's skills as zip files for upload in Claude
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
    elif command == "prompt":
        from .setup_prompt import main as run
    elif command == "catalogue":
        from .catalogue.build import main as run
    elif command == "scrub":
        from .scrub_check import main as run
    elif command == "skills":
        from .skills import main as run
    else:
        print(f"unknown command {command!r}; run cfo-os --help", file=sys.stderr)
        return 2
    return run(rest)
