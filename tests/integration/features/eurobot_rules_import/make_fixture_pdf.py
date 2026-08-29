"""
Write a small rules PDF for the eurobot_rules_import tests.

The fixture is generated rather than committed so that the text the tests
assert on is readable in the repository instead of buried in a binary. The
PDF is written with the standard library only: uncompressed content streams,
one text line per row, which is all eurobot/tools/import_rules.py reads.
"""

import sys
from typing import List, Tuple

ORIGINAL_LINES: Tuple[str, ...] = (
    "A. FIRST CHAPTER",
    "What the first chapter is about.",
    "A.1. FIRST CLAUSE",
    "The first clause says one thing.",
    "A.2. SECOND CLAUSE",
    "The second clause says another thing.",
)

REVISED_LINES: Tuple[str, ...] = (
    "A. FIRST CHAPTER",
    "What the first chapter is about.",
    "A.1. FIRST CLAUSE",
    "The first clause now says something else.",
    "A.3. THIRD CLAUSE",
    "The third clause did not exist before.",
)

VARIANTS = {"original": ORIGINAL_LINES, "revised": REVISED_LINES}

FIRST_LINE_Y = 700
LINE_HEIGHT = 20


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in VARIANTS:
        print(  # noqa: T201
            "usage: make_fixture_pdf.py <original|revised> <output.pdf>"
        )
        return 1
    write_pdf(VARIANTS[sys.argv[1]], sys.argv[2])
    return 0


def write_pdf(lines: Tuple[str, ...], output_path: str) -> None:
    content = _render_content_stream(lines)
    objects: List[bytes] = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        (
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>"
        ),
        b"<</Length "
        + str(len(content)).encode("ascii")
        + b">>\nstream\n"
        + content
        + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]

    output = bytearray(b"%PDF-1.4\n")
    offsets: List[int] = []
    for number_, body_ in enumerate(objects, start=1):
        offsets.append(len(output))
        output += str(number_).encode("ascii") + b" 0 obj\n" + body_
        output += b"\nendobj\n"

    xref_offset = len(output)
    output += b"xref\n0 " + str(len(objects) + 1).encode("ascii") + b"\n"
    output += b"0000000000 65535 f \n"
    for offset_ in offsets:
        output += f"{offset_:010d} 00000 n \n".encode("ascii")
    output += b"trailer\n<</Size "
    output += str(len(objects) + 1).encode("ascii")
    output += b"/Root 1 0 R>>\nstartxref\n"
    output += str(xref_offset).encode("ascii") + b"\n%%EOF\n"

    with open(output_path, "wb") as pdf_file_:
        pdf_file_.write(bytes(output))


def _render_content_stream(lines: Tuple[str, ...]) -> bytes:
    operators = ["BT", "/F1 10 Tf"]
    for index_, line_ in enumerate(lines):
        y_position = FIRST_LINE_Y - index_ * LINE_HEIGHT
        operators.append(f"1 0 0 1 56 {y_position} Tm")
        operators.append(f"({_escape(line_)}) Tj")
    operators.append("ET")
    return "\n".join(operators).encode("ascii")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


if __name__ == "__main__":
    sys.exit(main())
