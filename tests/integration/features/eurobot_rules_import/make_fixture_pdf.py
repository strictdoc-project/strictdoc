"""
Write a small rules PDF for the eurobot_rules_import tests.

The fixture is generated rather than committed so that the text the tests
assert on is readable in the repository instead of buried in a binary. The
PDF is written with the standard library only: uncompressed content streams,
one text line per row, which is all eurobot/tools/import_rules.py reads.

The "toc" variant stands in for a Google Docs export, where the headings are
pictures and only the table of contents names them. Its heading images are a
2x2 raster scaled up to the size of a heading line, because the converter
reads an image's position and never its pixels.
"""

import sys
import zlib
from typing import Dict, List, Tuple

# A page is a list of rows, each an ("text" | "heading" | "figure", value)
# pair, laid out from the top of the page downwards.
Row = Tuple[str, str]
Page = Tuple[Row, ...]

HEADINGS_IN_TEXT_ORIGINAL: Tuple[Page, ...] = (
    (
        ("text", "A. FIRST CHAPTER"),
        ("text", "What the first chapter is about."),
        ("text", "A.1. FIRST CLAUSE"),
        ("text", "The first clause says one thing."),
        ("text", "A.2. SECOND CLAUSE"),
        ("text", "The second clause says another thing."),
    ),
)

HEADINGS_IN_TEXT_REVISED: Tuple[Page, ...] = (
    (
        ("text", "A. FIRST CHAPTER"),
        ("text", "What the first chapter is about."),
        ("text", "A.1. FIRST CLAUSE"),
        ("text", "The first clause now says something else."),
        ("text", "A.3. THIRD CLAUSE"),
        ("text", "The third clause did not exist before."),
    ),
)

HEADINGS_IN_TOC: Tuple[Page, ...] = (
    (
        ("text", "A. FIRST CHAPTER 2"),
        ("text", "A.1. FIRST CLAUSE 2"),
        ("text", "A.2. SECOND CLAUSE 2"),
    ),
    (
        ("heading", "A. FIRST CHAPTER"),
        ("text", "What the first chapter is about."),
        ("heading", "A.1. FIRST CLAUSE"),
        ("text", "The first clause says one thing."),
        ("figure", "a picture inside the first clause"),
        ("heading", "A.2. SECOND CLAUSE"),
        ("text", "The second clause says another thing."),
    ),
)

VARIANTS: Dict[str, Tuple[Page, ...]] = {
    "original": HEADINGS_IN_TEXT_ORIGINAL,
    "revised": HEADINGS_IN_TEXT_REVISED,
    "toc": HEADINGS_IN_TOC,
}

FIRST_ROW_Y = 700
ROW_HEIGHT = 40

# Wide enough and short enough for the converter to read as a heading line.
HEADING_WIDTH = 488.0
HEADING_HEIGHT = 25.5

# Neither wide enough nor short enough to be mistaken for a heading.
FIGURE_WIDTH = 200.0
FIGURE_HEIGHT = 150.0

IMAGE_NAME = "Im1"


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in VARIANTS:
        print(  # noqa: T201
            "usage: make_fixture_pdf.py <original|revised|toc> <output.pdf>"
        )
        return 1
    write_pdf(VARIANTS[sys.argv[1]], sys.argv[2])
    return 0


def write_pdf(pages: Tuple[Page, ...], output_path: str) -> None:
    needs_image = any(
        kind_ in ("heading", "figure") for page_ in pages for kind_, _ in page_
    )

    # Object numbers: 1 catalog, 2 page tree, then one page and one content
    # stream per page, then the font, then the image if any page needs one.
    page_numbers = [3 + index_ * 2 for index_ in range(len(pages))]
    font_number = 3 + len(pages) * 2
    image_number = font_number + 1

    resources = b"<</Font<</F1 " + _reference(font_number) + b">>"
    if needs_image:
        resources += (
            b"/XObject<</"
            + IMAGE_NAME.encode("ascii")
            + b" "
            + _reference(image_number)
            + b">>"
        )
    resources += b">>"

    objects: List[bytes] = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids["
        + b" ".join(_reference(number_) for number_ in page_numbers)
        + b"]/Count "
        + str(len(pages)).encode("ascii")
        + b">>",
    ]
    for index_, page_ in enumerate(pages):
        content = _render_content_stream(page_)
        objects.append(
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources "
            + resources
            + b"/Contents "
            + _reference(page_numbers[index_] + 1)
            + b">>"
        )
        objects.append(
            b"<</Length "
            + str(len(content)).encode("ascii")
            + b">>\nstream\n"
            + content
            + b"\nendstream"
        )
    objects.append(b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>")
    if needs_image:
        objects.append(_render_image_object())

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


def _reference(number: int) -> bytes:
    return str(number).encode("ascii") + b" 0 R"


def _render_content_stream(page: Page) -> bytes:
    operators: List[str] = []
    for index_, (kind_, value_) in enumerate(page):
        y_position = FIRST_ROW_Y - index_ * ROW_HEIGHT
        if kind_ == "text":
            operators.append("BT")
            operators.append("/F1 10 Tf")
            operators.append(f"1 0 0 1 56 {y_position} Tm")
            operators.append(f"({_escape(value_)}) Tj")
            operators.append("ET")
            continue
        width, height = (
            (HEADING_WIDTH, HEADING_HEIGHT)
            if kind_ == "heading"
            else (FIGURE_WIDTH, FIGURE_HEIGHT)
        )
        operators.append("q")
        operators.append(f"{width} 0 0 {height} 56 {y_position} cm")
        operators.append(f"/{IMAGE_NAME} Do")
        operators.append("Q")
    return "\n".join(operators).encode("ascii")


def _render_image_object() -> bytes:
    # Two by two, solid grey. The converter never looks at the pixels; it
    # reads where the image sits and how large it is drawn.
    pixels = zlib.compress(bytes([128] * 12), 9)
    return (
        b"<</Type/XObject/Subtype/Image/Width 2/Height 2"
        b"/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/FlateDecode"
        b"/Length " + str(len(pixels)).encode("ascii") + b">>\nstream\n"
        + pixels
        + b"\nendstream"
    )


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


if __name__ == "__main__":
    sys.exit(main())
