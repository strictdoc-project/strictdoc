#!/usr/bin/env python3
"""Print a pass/fail matrix from the junit XML files in a results dir (+ results.md)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

d = Path(sys.argv[1])
lines = ["| suite | test | result |", "|---|---|---|"]
totals = {}
for f in sorted(d.glob("*.junit.xml")):
    root = ET.parse(f).getroot()
    for tc in root.iter("testcase"):
        if tc.find("failure") is not None or tc.find("error") is not None:
            r = "FAIL"
        elif tc.find("skipped") is not None:
            r = "SKIP"
        else:
            r = "PASS"
        totals.setdefault(f.stem, {}).setdefault(r, 0)
        totals[f.stem][r] += 1
        if "lit" not in f.stem or r == "FAIL":
            lines.append(f"| {f.stem} | {tc.get('name')} | {r} |")
summary = ["## Totals"] + [f"- {k}: {v}" for k, v in totals.items()] + ["", "## Tests"] + lines
(d / "results.md").write_text("\n".join(summary) + "\n")
print("\n".join(summary[: len(totals) + 1]))
