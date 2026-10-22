"""
Helpers for running StrictDoc as a frozen (PyInstaller) binary.

A frozen binary has no Python interpreter that can run "python -m ..." and no
console scripts such as "html2pdf4doc" on PATH. StrictDoc re-invokes its own
executable instead, and main() routes the internal helper command below
before StrictDoc's own argument parsing.
"""

import sys
from typing import List

# Internal command line marker. When a frozen StrictDoc binary is started as
# "strictdoc _html2pdf4doc <args>", it runs html2pdf4doc's CLI with <args>.
FROZEN_HTML2PDF4DOC_COMMAND = "_html2pdf4doc"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_html2pdf4doc_command() -> List[str]:
    if is_frozen():  # pragma: no cover
        return [sys.executable, FROZEN_HTML2PDF4DOC_COMMAND]
    return ["html2pdf4doc"]


def get_strictdoc_command() -> List[str]:
    if is_frozen():  # pragma: no cover
        return [sys.executable]
    return [sys.executable or "python", "-m", "strictdoc.cli.main"]


def run_frozen_helper_command_if_requested() -> None:  # pragma: no cover
    if not is_frozen():
        return
    if len(sys.argv) < 2 or sys.argv[1] != FROZEN_HTML2PDF4DOC_COMMAND:
        return
    # Imported lazily: html2pdf4doc.main loads Selenium and replaces
    # sys.stdout at import time, which only the helper process should do.
    from html2pdf4doc.main import (  # noqa: PLC0415
        main as html2pdf4doc_main,
    )

    sys.argv = ["html2pdf4doc", *sys.argv[2:]]
    html2pdf4doc_main()
    sys.exit(0)
