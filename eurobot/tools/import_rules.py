"""
Convert the Eurobot competition rules PDFs into RULE nodes.

The converter reads every PDF listed in the source manifest, splits it into
numbered clauses, and merges those clauses into Eurobot_Rules.sdoc. Merging,
rather than regenerating, is what keeps a REQUIREMENT's trace to a RULE alive
across a rules revision: a clause that disappears from the PDF keeps its node
and gets STATUS: Removed, because a relation pointing at a UID that no longer
exists aborts every export and every server rebuild for the whole project.

Running the converter twice on the same PDFs leaves the document untouched.

Usage:

    python eurobot/tools/import_rules.py --project-dir eurobot
"""

import argparse
import json
import os
import re
import sys
import unicodedata
import zlib
from binascii import crc32
from dataclasses import dataclass, field
from struct import pack
from typing import Any, Dict, List, Optional, Set, Tuple

from pypdf import PageObject, PdfReader
from pypdf.generic import DictionaryObject, StreamObject

#
# Text extraction constants, all calibrated against the two 2026-season PDFs.
#
# The rules PDFs come from pdfTeX, which positions capitals in headings with
# kerning offsets wide enough that pypdf's default threshold reads them as
# spaces ("PARTICIPANT" extracts as "P ARTICIP ANT"). A wider threshold reads
# the headings correctly and changes nothing else in either document.
#
SPACE_WIDTH = 250

# Body text and headings are set at 10 pt or larger. Everything below that is
# a footnote, a superscript footnote marker, or a figure sub-caption.
MINIMUM_FONT_SIZE = 9.5

# Page footers sit below 30 pt in the pdfTeX sources. No body text comes near
# that. The Google Docs sources have no running footer and put content as low
# as 40.2 pt, so this filter is per layout rather than global.
MINIMUM_TEXT_Y = 40.0

# Lines within a paragraph are 12 pt apart, paragraphs 26 pt.
PARAGRAPH_GAP = 18.0

# Chunks within this vertical distance belong to the same visual line.
LINE_TOLERANCE = 4.0

# Kerning pairs that survive the SPACE_WIDTH setting above, because the PDF
# holds a real space rather than a wide offset. Widening SPACE_WIDTH further
# does not reach them. A revised PDF may need a new entry here; the sign of
# one is a lone capital letter in front of a lower-case word fragment.
KERNING_REPAIRS: Tuple[Tuple[str, str], ...] = (("Y ou", "You"),)

# A heading: a capital letter, an optional number, an optional lowercase
# letter, then the title. "D.", "D.3.", "D.3.a.". The general rules PDF
# writes its third level with a doubled full stop ("F.4.a.. GENERAL
# ASPECTS"), so one trailing stop is optional.
HEADING_PATTERN = re.compile(
    r"^([A-Z])\.(?:(\d+)\.)?(?:([a-z])\.)?\.?\s+(\S.*)$"
)

# A bullet keeps its own paragraph: the rules set list items closer together
# than paragraphs, so the vertical gap alone does not separate them.
BULLET_CHARACTERS = ("\u2022", "\u2013", "\u2014")

SENTENCE_ENDINGS = (".", "!", "?", ":", ";")

# A chapter section is titled "D. MAIN REGISTRATION REQUIREMENTS".
CHAPTER_TITLE_PREFIX = re.compile(r"^[A-Z]\. ")

OPENING_PUNCTUATION = ("(", "[", "{", "\u201c", "\u2018")
CLOSING_PUNCTUATION = (
    ")",
    "]",
    "}",
    ".",
    ",",
    ";",
    ":",
    "!",
    "?",
    "\u201d",
    "\u2019",
)

STATUS_ACTIVE = "Active"
STATUS_REMOVED = "Removed"

#
# How a source PDF carries its headings.
#
# A pdfTeX export writes them as text, so a heading is a line the body loop
# recognises on its way past. A Google Docs export rasterises every level-1
# and level-2 heading into a picture, leaving only the third level as text. In
# that case the table of contents supplies each clause's number and title, and
# the picture supplies only the position the clause starts at. Nothing ever
# reads the pixels.
#
LAYOUT_HEADINGS_IN_TEXT = "headings-in-text"
LAYOUT_HEADINGS_IN_TOC = "headings-in-toc"

# Rules and separators are drawn as images a fraction of a point tall, and a
# technical drawing arrives as one large picture surrounded by dozens of tiny
# ones holding its dimension callouts. Neither carries meaning on its own, so
# an image has to clear both a minimum side and a minimum area to be kept.
MINIMUM_IMAGE_SIZE = 8.0
MINIMUM_IMAGE_AREA = 2000.0

# A rasterised heading spans the text column and stands one line tall.
HEADING_IMAGE_MINIMUM_WIDTH = 400.0
HEADING_IMAGE_MINIMUM_HEIGHT = 24.0
HEADING_IMAGE_MAXIMUM_HEIGHT = 32.0

# A table-of-contents line: a clause number, a title, then the printed page,
# with dot leaders in between often enough to allow for them.
TOC_PATTERN = re.compile(
    r"^([A-Z])\.\s*(?:(\d+)\.)?\s*\.?\s*(.+?)\s*[.\s]*?(\d+)$"
)

# A page holding at least this many table-of-contents lines is front matter.
TOC_LINES_PER_PAGE = 3

# How far the printed page numbers can sit from the PDF's own page indices.
# The converter tries each offset and keeps the one that lines the two up best.
PAGE_OFFSET_CANDIDATES = (1, 0, 2, 3)


@dataclass
class SourceDocument:
    """One rules PDF, as declared in the source manifest."""

    prefix: str
    file_name: str
    title: str
    layout: str = LAYOUT_HEADINGS_IN_TEXT


@dataclass
class Clause:
    """One numbered clause, extracted from a PDF or read back from the sdoc."""

    uid: str
    number: str
    chapter: str
    chapter_title: str
    title: str
    statement: str
    status: str = STATUS_ACTIVE


@dataclass
class TextChunk:
    """One run of text, with the position the PDF placed it at."""

    y_position: float
    x_position: float
    text: str


@dataclass
class PageItem:
    """A visual line of text, or an image placement, in reading order."""

    y_position: float
    text: Optional[str] = None
    image_name: Optional[str] = None
    image_width: float = 0.0
    image_height: float = 0.0
    heading: Optional[Tuple[str, str]] = None
    used_as_heading: bool = False


@dataclass
class TocEntry:
    """One table-of-contents line: a clause number, a title, a printed page."""

    number: str
    title: str
    printed_page: int


@dataclass
class ImportResult:
    """What one run of the converter did."""

    clauses: List[Clause] = field(default_factory=list)
    written_images: List[str] = field(default_factory=list)
    document_changed: bool = False


def read_source_manifest(manifest_path: str) -> List[SourceDocument]:
    """Read the list of rules PDFs to import."""

    with open(manifest_path, encoding="utf8") as manifest_file_:
        entries = json.load(manifest_file_)

    sources: List[SourceDocument] = []
    for entry_ in entries:
        sources.append(
            SourceDocument(
                prefix=entry_["prefix"],
                file_name=entry_["file"],
                title=entry_["title"],
                layout=entry_.get("layout", LAYOUT_HEADINGS_IN_TEXT),
            )
        )
    return sources


def extract_clauses(
    source: SourceDocument,
    pdf_path: str,
    assets_directory: str,
    document_directory: str,
) -> Tuple[List[Clause], List[str]]:
    """
    Split one rules PDF into clauses, one per numbered heading.

    Images are written next to the clause that owns them, and referenced from
    its statement. Returns the clauses and the image files written.
    """

    reader = PdfReader(pdf_path)
    reads_toc = source.layout == LAYOUT_HEADINGS_IN_TOC

    if reads_toc:
        # A Google Docs export has no running footer to filter out, and it
        # sets the third-level headings a point smaller than the body, so
        # both floors have to come off or those headings disappear.
        minimum_y = 0.0
        minimum_font_size = 0.0
        toc_pages = _find_toc_pages(reader, minimum_font_size)
        first_body_page = max(toc_pages) + 1 if len(toc_pages) > 0 else 0
    else:
        minimum_y = MINIMUM_TEXT_Y
        minimum_font_size = MINIMUM_FONT_SIZE
        toc_pages = []
        first_body_page = _find_first_body_page(reader)

    page_items: Dict[int, List[PageItem]] = {}
    for page_index_ in range(first_body_page, len(reader.pages)):
        page_items[page_index_] = _read_page_items(
            reader.pages[page_index_], minimum_y, minimum_font_size
        )

    anchors: Dict[int, List[PageItem]] = {}
    toc_pages_by_number: Dict[str, int] = {}
    if reads_toc:
        entries = _read_toc_entries(reader, toc_pages, minimum_font_size)
        toc_pages_by_number = {
            entry_.number: entry_.printed_page for entry_ in entries
        }
        anchors = _pair_toc_with_headings(entries, page_items)

    clauses: List[Clause] = []
    written_images: List[str] = []
    chapter = ""
    chapter_title = ""
    current: Optional[Clause] = None
    paragraphs: List[List[str]] = []

    for page_index_ in sorted(page_items):
        page_ = reader.pages[page_index_]
        items = _merge_anchors(
            page_items[page_index_], anchors.get(page_index_, [])
        )
        previous_y: Optional[float] = None

        for item_ in items:
            opened = item_.heading
            if opened is None and item_.text is not None:
                match = HEADING_PATTERN.match(item_.text)
                if match is not None and _is_heading_line(item_.text):
                    letter_, number_, sub_letter_, title_ = match.groups()
                    opened = (
                        _format_clause_number(letter_, number_, sub_letter_),
                        title_,
                    )

            if opened is not None:
                if current is not None:
                    current.statement = _join_paragraphs(paragraphs)
                    clauses.append(current)
                paragraphs = []
                previous_y = None

                clause_number, clause_title = opened
                if "." not in clause_number:
                    chapter = clause_number
                    chapter_title = clause_title
                current = Clause(
                    uid=f"RULE-{source.prefix}-{clause_number}",
                    number=clause_number,
                    chapter=chapter,
                    chapter_title=chapter_title,
                    title=clause_title,
                    statement="",
                )
                continue

            if item_.image_name is not None:
                if current is None:
                    continue
                already_written = len(
                    [
                        image_
                        for image_ in written_images
                        if image_.startswith(f"{current.uid}-")
                    ]
                )
                image_file_name = _write_image(
                    page_,
                    item_.image_name,
                    current.uid,
                    already_written + 1,
                    assets_directory,
                )
                if image_file_name is None:
                    continue
                written_images.append(image_file_name)
                relative_path = os.path.relpath(
                    os.path.join(assets_directory, image_file_name),
                    document_directory,
                ).replace(os.sep, "/")
                paragraphs.append([f".. image:: {relative_path}"])
                previous_y = None
                continue

            assert item_.text is not None
            if current is None:
                continue

            starts_paragraph = (
                previous_y is None
                or (previous_y - item_.y_position) > PARAGRAPH_GAP
                or item_.text.startswith(BULLET_CHARACTERS)
            )
            if starts_paragraph and len(paragraphs) > 0:
                previous_paragraph = paragraphs[-1]
                if _continues_across_gap(previous_paragraph, item_.text):
                    starts_paragraph = False

            if starts_paragraph or len(paragraphs) == 0:
                paragraphs.append([item_.text])
            else:
                paragraphs[-1].append(item_.text)
            previous_y = item_.y_position

    if current is not None:
        current.statement = _join_paragraphs(paragraphs)
        clauses.append(current)

    containers = _find_container_numbers(clauses)

    kept: List[Clause] = []
    for clause_ in clauses:
        if len(clause_.statement) > 0:
            kept.append(clause_)
            continue
        if not reads_toc:
            continue
        # A clause the table of contents names is part of the document's
        # structure even when nothing readable sits under its heading. That
        # happens for a heading whose content is entirely in the clauses
        # below it, and for one whose content is a drawing.
        clause_.statement = _render_empty_statement(
            source,
            clause_.number in containers,
            toc_pages_by_number.get(clause_.number),
        )
        kept.append(clause_)
    return kept, written_images


def _find_container_numbers(clauses: List[Clause]) -> Set[str]:
    """Return the clause numbers that other clauses sit underneath."""

    numbers = {clause_.number for clause_ in clauses}
    containers: Set[str] = set()
    for number_ in numbers:
        prefix = number_ + "."
        if any(other_.startswith(prefix) for other_ in numbers):
            containers.add(number_)
    return containers


def _merge_anchors(
    items: List[PageItem], page_anchors: List[PageItem]
) -> List[PageItem]:
    """Drop the images used as heading anchors and insert the anchors."""

    merged = [item_ for item_ in items if not item_.used_as_heading]
    merged.extend(page_anchors)
    merged.sort(key=lambda item_: -item_.y_position)
    return merged


def _find_toc_pages(
    reader: PdfReader, minimum_font_size: float
) -> List[int]:
    """Return the front-matter pages that hold the table of contents."""

    toc_pages: List[int] = []
    for page_index_ in range(min(6, len(reader.pages))):
        items = _read_page_items(
            reader.pages[page_index_], 0.0, minimum_font_size
        )
        matches = 0
        for item_ in items:
            if item_.text is not None and TOC_PATTERN.match(item_.text):
                matches += 1
        if matches >= TOC_LINES_PER_PAGE:
            toc_pages.append(page_index_)
    return toc_pages


def _read_toc_entries(
    reader: PdfReader, toc_pages: List[int], minimum_font_size: float
) -> List[TocEntry]:
    """Read the table of contents as an ordered list of clauses."""

    entries: List[TocEntry] = []
    for page_index_ in toc_pages:
        for item_ in _read_page_items(
            reader.pages[page_index_], 0.0, minimum_font_size
        ):
            if item_.text is None:
                continue
            match = TOC_PATTERN.match(item_.text)
            if match is None:
                continue
            letter_, number_, title_, printed_page_ = match.groups()
            number = letter_
            if number_ is not None:
                number += "." + number_
            entries.append(
                TocEntry(
                    number=number,
                    title=title_.strip(" ."),
                    printed_page=int(printed_page_),
                )
            )
    return entries


def _pair_toc_with_headings(
    entries: List[TocEntry], page_items: Dict[int, List[PageItem]]
) -> Dict[int, List[PageItem]]:
    """
    Turn table-of-contents entries into positioned heading anchors.

    Each entry names a clause and the page it starts on; each rasterised
    heading on that page marks where one starts. Pairing them in reading order
    recovers the structure without reading a single pixel.
    """

    heading_images: Dict[int, List[PageItem]] = {}
    for page_index_, items_ in page_items.items():
        found = [item_ for item_ in items_ if _is_heading_image(item_)]
        if len(found) > 0:
            heading_images[page_index_] = sorted(
                found, key=lambda item_: -item_.y_position
            )

    offset = _choose_page_offset(entries, heading_images)

    entries_by_page: Dict[int, List[TocEntry]] = {}
    for entry_ in entries:
        entries_by_page.setdefault(
            entry_.printed_page - offset, []
        ).append(entry_)

    anchors: Dict[int, List[PageItem]] = {}
    for page_index_, page_entries_ in sorted(entries_by_page.items()):
        if page_index_ not in page_items:
            continue
        images = heading_images.get(page_index_, [])
        page_anchors: List[PageItem] = []
        top_of_page = _top_of_page(page_items[page_index_])
        for position_, entry_ in enumerate(page_entries_):
            if position_ < len(images):
                image = images[position_]
                page_anchors.append(
                    PageItem(
                        y_position=image.y_position + image.image_height,
                        heading=(entry_.number, entry_.title),
                    )
                )
                # Marking the placement, rather than remembering its name,
                # keeps a second placement of the same XObject elsewhere on
                # the page as an ordinary figure.
                image.used_as_heading = True
                continue
            # More entries than rasterised headings on this page. The clause
            # still exists, so anchor it at the top of the page and let the
            # boundary be coarse rather than lose the node.
            page_anchors.append(
                PageItem(
                    y_position=top_of_page + 1.0 - position_ * 0.001,
                    heading=(entry_.number, entry_.title),
                )
            )
        anchors[page_index_] = page_anchors
    return anchors


def _choose_page_offset(
    entries: List[TocEntry], heading_images: Dict[int, List[PageItem]]
) -> int:
    """
    Work out how the printed page numbers map onto the PDF's page indices.

    Trying each candidate and keeping the one whose per-page counts agree most
    often is self-checking: a wrong offset lines almost nothing up.
    """

    best_offset = PAGE_OFFSET_CANDIDATES[0]
    best_score = -1
    for offset_ in PAGE_OFFSET_CANDIDATES:
        counts: Dict[int, int] = {}
        for entry_ in entries:
            page_index = entry_.printed_page - offset_
            counts[page_index] = counts.get(page_index, 0) + 1
        score = sum(
            1
            for page_index_, count_ in counts.items()
            if len(heading_images.get(page_index_, [])) == count_
        )
        if score > best_score:
            best_score = score
            best_offset = offset_
    return best_offset


def _top_of_page(items: List[PageItem]) -> float:
    if len(items) == 0:
        return 0.0
    return max(item_.y_position for item_ in items)


def _render_empty_statement(
    source: SourceDocument, is_container: bool, printed_page: Optional[int]
) -> str:
    """Say why a clause carries no text of its own, and where to look."""

    where = f"page {printed_page} of " if printed_page is not None else ""
    source_path = f"``_assets/rules/source/{source.file_name}``"
    if is_container:
        return (
            "This heading has no text of its own. Its content is in the "
            "clauses below it."
        )
    return (
        "No text was extracted under this heading. What belongs here is a "
        "drawing, a table, or text the source numbers as part of another "
        f"clause: see {where}{source_path}."
    )


def merge_clauses(
    existing_clauses: List[Clause], extracted_clauses: List[Clause]
) -> List[Clause]:
    """
    Reconcile the extracted clauses against the ones already in the document.

    A clause that is present in both keeps its node and takes the extracted
    text. A clause that is only in the extraction is new. A clause that is
    only in the document survives with STATUS: Removed, so that every
    REQUIREMENT tracing to it keeps resolving.
    """

    extracted_by_uid: Dict[str, Clause] = {
        clause_.uid: clause_ for clause_ in extracted_clauses
    }

    merged: List[Clause] = list(extracted_clauses)
    for existing_clause_ in existing_clauses:
        if existing_clause_.uid in extracted_by_uid:
            continue
        removed_clause = Clause(
            uid=existing_clause_.uid,
            number=existing_clause_.number,
            chapter=existing_clause_.chapter,
            chapter_title=existing_clause_.chapter_title,
            title=existing_clause_.title,
            statement=existing_clause_.statement,
            status=STATUS_REMOVED,
        )
        merged.append(removed_clause)
    return merged


def render_document(
    sources: List[SourceDocument], clauses: List[Clause]
) -> str:
    """Render the merged clauses as the text of Eurobot_Rules.sdoc."""

    lines: List[str] = [
        "[DOCUMENT]",
        "TITLE: Eurobot Rules",
        "",
        "[GRAMMAR]",
        "IMPORT_FROM_FILE: @eurobot",
        "",
        "[TEXT]",
        "STATEMENT: >>>",
    ]
    lines.extend(_render_introduction(sources))
    lines.extend(["<<<", ""])

    clauses_by_source = _group_by_source(sources, clauses)
    for source_ in sources:
        source_clauses = clauses_by_source.get(source_.prefix, [])
        if len(source_clauses) == 0:
            continue
        lines.extend(
            [
                "[[SECTION]]",
                f"TITLE: {source_.title}",
                "",
            ]
        )
        for chapter_title_, chapter_clauses_ in _group_by_chapter(
            source_clauses
        ):
            lines.extend(
                [
                    "[[SECTION]]",
                    f"TITLE: {chapter_title_}",
                    "",
                ]
            )
            for clause_ in chapter_clauses_:
                lines.extend(_render_clause(clause_))
            lines.extend(["[[/SECTION]]", ""])
        lines.extend(["[[/SECTION]]", ""])

    while len(lines) > 0 and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def read_existing_clauses(document_path: str) -> List[Clause]:
    """
    Read the clauses already in Eurobot_Rules.sdoc.

    The document is parsed as text rather than through the SDoc reader, so
    that the converter stays runnable without a StrictDoc installation. The
    result it writes is validated against the real reader by the integration
    tests.
    """

    if not os.path.isfile(document_path):
        return []

    with open(document_path, encoding="utf8") as document_file_:
        content = document_file_.read()

    clauses: List[Clause] = []
    section_titles: List[str] = []
    awaiting_section_title = False
    node_lines: Optional[List[str]] = None
    inside_statement = False

    for line_ in content.split("\n"):
        if inside_statement:
            assert node_lines is not None
            node_lines.append(line_)
            if line_ == "<<<":
                inside_statement = False
            continue

        if line_ == "STATEMENT: >>>" and node_lines is not None:
            node_lines.append(line_)
            inside_statement = True
            continue

        if line_.startswith("["):
            if node_lines is not None:
                clauses.append(_parse_rule_node(node_lines, section_titles))
                node_lines = None
            if line_ == "[[SECTION]]":
                section_titles.append("")
                awaiting_section_title = True
            elif line_ == "[[/SECTION]]":
                if len(section_titles) > 0:
                    section_titles.pop()
                awaiting_section_title = False
            elif line_ == "[RULE]":
                node_lines = []
                awaiting_section_title = False
            else:
                awaiting_section_title = False
            continue

        if awaiting_section_title and line_.startswith("TITLE: "):
            section_titles[-1] = line_[len("TITLE: ") :]
            awaiting_section_title = False
            continue

        if node_lines is not None:
            node_lines.append(line_)

    if node_lines is not None:
        clauses.append(_parse_rule_node(node_lines, section_titles))
    return clauses


def import_rules(project_directory: str) -> ImportResult:
    """Import every PDF in the manifest into the project's rules document."""

    source_directory = os.path.join(
        project_directory, "_assets", "rules", "source"
    )
    manifest_path = os.path.join(source_directory, "sources.json")
    sources = read_source_manifest(manifest_path)

    document_path = os.path.join(project_directory, "Eurobot_Rules.sdoc")
    existing_clauses = read_existing_clauses(document_path)

    result = ImportResult()
    extracted_clauses: List[Clause] = []
    for source_ in sources:
        assets_directory = os.path.join(
            project_directory, "_assets", "rules", source_.prefix
        )
        source_clauses, written_images = extract_clauses(
            source_,
            os.path.join(source_directory, source_.file_name),
            assets_directory,
            project_directory,
        )
        extracted_clauses.extend(source_clauses)
        result.written_images.extend(written_images)

    merged_clauses = merge_clauses(existing_clauses, extracted_clauses)
    result.clauses = merged_clauses

    rendered = render_document(sources, merged_clauses)
    if os.path.isfile(document_path):
        with open(document_path, encoding="utf8") as document_file_:
            if document_file_.read() == rendered:
                return result

    with open(document_path, "w", encoding="utf8") as document_file_:
        document_file_.write(rendered)
    result.document_changed = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="the StrictDoc project holding Eurobot_Rules.sdoc",
    )
    arguments = parser.parse_args()

    result = import_rules(arguments.project_dir)

    active_count = len(
        [
            clause_
            for clause_ in result.clauses
            if clause_.status == STATUS_ACTIVE
        ]
    )
    removed_count = len(result.clauses) - active_count
    print(  # noqa: T201
        f"Imported {active_count} active and {removed_count} removed rules, "
        f"{len(result.written_images)} images."
    )
    if result.document_changed:
        print("Eurobot_Rules.sdoc updated.")  # noqa: T201
    else:
        print("Eurobot_Rules.sdoc unchanged.")  # noqa: T201
    unreadable_count = len(
        [
            clause_
            for clause_ in result.clauses
            if clause_.statement.startswith("No text was extracted")
        ]
    )
    if unreadable_count > 0:
        print(  # noqa: T201
            f"{unreadable_count} clauses have no extracted text. Check "
            "them against the source PDF."
        )
    if removed_count > 0:
        print(  # noqa: T201
            "Review the requirements that trace to a removed rule: search "
            'the RULE nodes with node["STATUS"] == "Removed", then read '
            "their covering requirements off the Traceability Matrix."
        )
    return 0


def _find_first_body_page(reader: PdfReader) -> int:
    """
    Return the first page after the cover and the table of contents.

    The outline's first entry points at the first chapter, which is where the
    body starts. Everything before it repeats the chapter numbering and would
    otherwise be extracted twice.
    """

    entries: Any = reader.outline
    while isinstance(entries, list) and len(entries) > 0:
        first_entry: Any = entries[0]
        if isinstance(first_entry, list):
            entries = first_entry
            continue
        first_page = first_entry.page
        if first_page is None:
            return 0
        page_number = reader.get_page_number(first_page.get_object())
        if page_number is None:
            return 0
        return page_number
    return 0


def _read_page_items(
    page: PageObject, minimum_y: float, minimum_font_size: float
) -> List[PageItem]:
    """
    Read one page as visual lines and image placements, top to bottom.

    A position on the page is the product of the graphics matrix and the text
    matrix, not the text matrix alone. pdfTeX leaves the graphics matrix at
    identity, which is why reading the text matrix by itself worked for the
    English sources. Google Docs sets a flipped and scaled graphics matrix, so
    the same reading puts every line of those documents in the wrong place.
    """

    chunks: List[TextChunk] = []
    images: List[Tuple[float, float, float, str]] = []

    def visit_text(
        text: str,
        matrix: List[float],
        text_matrix: List[float],
        _font: Optional[DictionaryObject],
        font_size: Optional[float],
    ) -> None:
        stripped = text.strip()
        if len(stripped) == 0:
            return
        if font_size is None:
            return
        if abs(font_size * matrix[3]) < minimum_font_size:
            return
        y_position = matrix[5] + matrix[3] * text_matrix[5]
        if y_position < minimum_y:
            return
        chunks.append(
            TextChunk(
                y_position=y_position,
                x_position=matrix[4] + matrix[0] * text_matrix[4],
                text=stripped,
            )
        )

    def visit_operand(
        operator: bytes,
        operands: List[object],
        matrix: List[float],
        _text_matrix: List[float],
    ) -> None:
        if operator != b"Do":
            return
        if len(operands) == 0:
            return
        width, height = abs(matrix[0]), abs(matrix[3])
        if width < MINIMUM_IMAGE_SIZE or height < MINIMUM_IMAGE_SIZE:
            return
        if width * height < MINIMUM_IMAGE_AREA:
            return
        images.append((matrix[5], width, height, str(operands[0])))

    page.extract_text(
        space_width=SPACE_WIDTH,
        visitor_text=visit_text,
        visitor_operand_before=visit_operand,
    )

    items: List[PageItem] = []
    for line_y_, line_text_ in _group_lines(chunks):
        items.append(PageItem(y_position=line_y_, text=line_text_))
    for image_y_, image_w_, image_h_, image_name_ in images:
        items.append(
            PageItem(
                y_position=image_y_,
                image_name=image_name_,
                image_width=image_w_,
                image_height=image_h_,
            )
        )

    items.sort(key=lambda item_: -item_.y_position)
    return items


def _is_heading_image(item: PageItem) -> bool:
    """Decide whether an image placement is a rasterised heading line."""

    if item.image_name is None:
        return False
    if item.image_width < HEADING_IMAGE_MINIMUM_WIDTH:
        return False
    return (
        HEADING_IMAGE_MINIMUM_HEIGHT
        <= item.image_height
        <= HEADING_IMAGE_MAXIMUM_HEIGHT
    )


def _group_lines(chunks: List[TextChunk]) -> List[Tuple[float, str]]:
    """Join the chunks that the PDF placed on the same visual line."""

    chunks = sorted(chunks, key=lambda chunk_: (-chunk_.y_position,))
    lines: List[Tuple[float, List[TextChunk]]] = []
    for chunk_ in chunks:
        if (
            len(lines) > 0
            and abs(lines[-1][0] - chunk_.y_position) <= LINE_TOLERANCE
        ):
            lines[-1][1].append(chunk_)
            continue
        lines.append((chunk_.y_position, [chunk_]))

    grouped: List[Tuple[float, str]] = []
    for line_y_, line_chunks_ in lines:
        ordered = sorted(line_chunks_, key=lambda chunk_: chunk_.x_position)
        text = _join_chunks([chunk_.text for chunk_ in ordered])
        grouped.append((line_y_, _repair_kerning(_normalize_spaces(text))))
    return grouped


def _join_chunks(chunks: List[str]) -> str:
    """
    Join the runs of one visual line back into a sentence.

    A hyperlink or a font change splits a line into several runs, and the
    split falls next to a bracket often enough that joining everything with a
    space would write "( www.eurobot.org/ )".
    """

    text = ""
    for chunk_ in chunks:
        if len(text) == 0:
            text = chunk_
            continue
        if text.endswith(OPENING_PUNCTUATION) or chunk_.startswith(
            CLOSING_PUNCTUATION
        ):
            text += chunk_
            continue
        text += " " + chunk_
    return text


def _normalize_spaces(text: str) -> str:
    r"""
    Collapse runs of whitespace, and drop invisible formatting characters.

    Google Docs writes a zero-width space between a heading's number and its
    title. Python's ``\s`` does not match U+200B, so a pattern expecting
    whitespace there fails on an otherwise ordinary heading.
    """

    visible = "".join(
        character_
        for character_ in text
        if unicodedata.category(character_) != "Cf"
    )
    return re.sub(r"\s+", " ", visible).strip()


def _repair_kerning(text: str) -> str:
    for broken_, repaired_ in KERNING_REPAIRS:
        text = text.replace(broken_, repaired_)
    return text


def _is_heading_line(text: str) -> bool:
    """
    Decide whether a numbered line is a heading rather than prose.

    Every heading in both rules PDFs is short and set in capitals, so a
    numbered line that is neither is body text that happens to start with a
    letter and a full stop.
    """

    if len(text) >= 90:
        return False
    heading = HEADING_PATTERN.match(text)
    if heading is None:
        return False
    title = heading.group(4)
    letters = [character_ for character_ in title if character_.isalpha()]
    if len(letters) == 0:
        return False
    return all(character_.isupper() for character_ in letters)


def _format_clause_number(
    letter: str, number: Optional[str], sub_letter: Optional[str]
) -> str:
    parts = [letter]
    if number is not None:
        parts.append(number)
    if sub_letter is not None:
        parts.append(sub_letter)
    return ".".join(parts)


def _continues_across_gap(
    previous_paragraph: List[str], text: str
) -> bool:
    """
    Decide whether a line continues the paragraph before it.

    The vertical gap alone misreads a paragraph that runs over a page break
    or around a figure. Such a paragraph leaves its last line without
    sentence-final punctuation and picks up in lower case afterwards.
    """

    if len(previous_paragraph) == 0:
        return False
    last_line = previous_paragraph[-1]
    if last_line.startswith(".. image::"):
        return False
    if last_line.endswith(SENTENCE_ENDINGS):
        return False
    first_character = text[0]
    return first_character.islower()


def _join_paragraphs(paragraphs: List[List[str]]) -> str:
    """Rejoin the PDF's line wraps, one line of output per paragraph."""

    joined: List[str] = []
    for paragraph_ in paragraphs:
        if paragraph_[0].startswith(".. image::"):
            joined.append(paragraph_[0])
            continue
        text = _normalize_spaces(_join_wrapped_lines(paragraph_))
        if len(text) > 0:
            joined.append(text)
    return "\n\n".join(joined)


def _join_wrapped_lines(lines: List[str]) -> str:
    """
    Undo the PDF's line wrapping inside one paragraph.

    A word split across two lines leaves a trailing hyphen that belongs to
    the wrapping, not to the word, unless the fragment before it ends in a
    capital: "CE-certified" is a compound that happens to break at its own
    hyphen, while "par-ticipants" is one word.
    """

    text = ""
    for line_ in lines:
        if len(text) == 0:
            text = line_
            continue
        if text.endswith("-") and len(text) > 1:
            if text[-2].isupper():
                text += line_
            else:
                text = text[:-1] + line_
            continue
        text += " " + line_
    return text


def _write_image(
    page: PageObject,
    image_name: str,
    clause_uid: str,
    image_index: int,
    assets_directory: str,
) -> Optional[str]:
    """
    Write one embedded image next to the clause that shows it.

    JPEG streams are copied out as they are. Raw rasters are re-encoded as
    PNG with the standard library, so that the converter needs no image
    library beyond what StrictDoc already depends on.
    """

    image_object = _find_image_object(page, image_name)
    if image_object is None:
        return None

    image_filter = str(image_object.get("/Filter"))
    width = int(str(image_object["/Width"]))
    height = int(str(image_object["/Height"]))

    if image_filter == "/DCTDecode":
        file_name = f"{clause_uid}-{image_index}.jpg"
        content = bytes(image_object.get_data())
    elif image_filter == "/FlateDecode":
        bits_per_component = int(
            str(image_object.get("/BitsPerComponent", 0))
        )
        if bits_per_component != 8:
            return None
        channels = _count_colour_channels(image_object)
        if channels is None:
            return None
        file_name = f"{clause_uid}-{image_index}.png"
        content = _encode_png(
            width, height, channels, image_object.get_data()
        )
    else:
        return None

    os.makedirs(assets_directory, exist_ok=True)
    file_path = os.path.join(assets_directory, file_name)
    if os.path.isfile(file_path):
        with open(file_path, "rb") as existing_file_:
            if existing_file_.read() == content:
                return file_name
    with open(file_path, "wb") as image_file_:
        image_file_.write(content)
    return file_name


def _count_colour_channels(image_object: StreamObject) -> Optional[int]:
    """
    Return how many samples per pixel an image carries, or None if unknown.

    Google Docs tags every image /ICCBased rather than /DeviceRGB, and the
    profile's /N holds the channel count. Reading only the device names would
    skip every image in those documents.
    """

    colour_space: Any = image_object.get("/ColorSpace")
    if hasattr(colour_space, "get_object"):
        colour_space = colour_space.get_object()
    if isinstance(colour_space, list) and len(colour_space) >= 2:
        if str(colour_space[0]) == "/ICCBased":
            profile: Any = colour_space[1]
            if hasattr(profile, "get_object"):
                profile = profile.get_object()
            components = profile.get("/N")
            if components is not None and int(components) in (1, 3):
                return int(components)
        return None
    if str(colour_space) == "/DeviceRGB":
        return 3
    if str(colour_space) == "/DeviceGray":
        return 1
    return None


def _find_image_object(
    page: PageObject, image_name: str
) -> Optional[StreamObject]:
    resources: Any = page.get("/Resources")
    if resources is None:
        return None
    x_objects: Any = resources.get_object().get("/XObject")
    if x_objects is None:
        return None
    entry: Any = x_objects.get_object().get(image_name)
    if entry is None:
        return None
    entry = entry.get_object()
    if not isinstance(entry, StreamObject):
        return None
    if entry.get("/Subtype") != "/Image":
        return None
    return entry


def _encode_png(
    width: int, height: int, channels: int, pixels: bytes
) -> bytes:
    """Encode raw 8-bit pixel rows as a PNG file."""

    color_type = 2 if channels == 3 else 0
    stride = width * channels
    scanlines = bytearray()
    for row_index_ in range(height):
        scanlines.append(0)
        scanlines.extend(pixels[row_index_ * stride : (row_index_ + 1) * stride])

    header = pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", header),
            _png_chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)),
            _png_chunk(b"IEND", b""),
        ]
    )


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    return b"".join(
        [
            pack(">I", len(payload)),
            tag,
            payload,
            pack(">I", crc32(tag + payload) & 0xFFFFFFFF),
        ]
    )


def _render_introduction(sources: List[SourceDocument]) -> List[str]:
    lines = [
        "This document is generated by ``eurobot/tools/import_rules.py``",
        "from the official rules PDFs. Do not edit it by hand: the next",
        "import overwrites every statement.",
        "",
        "Each node holds one numbered clause, under the UID",
        "``RULE-<source>-<clause number>``. A clause that disappears from a",
        "revised PDF keeps its node and gets ``STATUS: Removed``, so that",
        "every requirement tracing to it keeps resolving.",
        "",
        "Source documents:",
        "",
    ]
    for source_ in sources:
        relative_path = f"_assets/rules/source/{source_.file_name}"
        lines.append(f"- {source_.title} (``{relative_path}``)")
    return lines


def _render_clause(clause: Clause) -> List[str]:
    lines = [
        "[RULE]",
        f"UID: {clause.uid}",
        f"TITLE: {clause.title}",
        f"STATUS: {clause.status}",
        "STATEMENT: >>>",
    ]
    lines.extend(clause.statement.split("\n"))
    lines.extend(["<<<", ""])
    return lines


def _group_by_source(
    sources: List[SourceDocument], clauses: List[Clause]
) -> Dict[str, List[Clause]]:
    grouped: Dict[str, List[Clause]] = {}
    for clause_ in clauses:
        for source_ in sources:
            if clause_.uid.startswith(f"RULE-{source_.prefix}-"):
                grouped.setdefault(source_.prefix, []).append(clause_)
                break
    return grouped


def _group_by_chapter(
    clauses: List[Clause],
) -> List[Tuple[str, List[Clause]]]:
    """Group a source's clauses by chapter, in the PDF's own order."""

    chapter_titles: Dict[str, str] = {}
    chapter_clauses: Dict[str, List[Clause]] = {}
    for clause_ in clauses:
        chapter_letter = clause_.number.split(".")[0]
        chapter_clauses.setdefault(chapter_letter, []).append(clause_)
        if chapter_letter not in chapter_titles or len(clause_.chapter) > 0:
            chapter_titles.setdefault(
                chapter_letter, clause_.chapter_title
            )

    grouped: List[Tuple[str, List[Clause]]] = []
    for chapter_letter_ in sorted(chapter_clauses.keys()):
        title = chapter_titles.get(chapter_letter_, chapter_letter_)
        if len(title) == 0:
            title = chapter_letter_
        ordered = sorted(
            chapter_clauses[chapter_letter_],
            key=lambda clause_: _clause_sort_key(clause_.number),
        )
        grouped.append((f"{chapter_letter_}. {title}", ordered))
    return grouped


def _clause_sort_key(number: str) -> Tuple[str, int, str]:
    parts = number.split(".")
    letter = parts[0]
    sub_number = int(parts[1]) if len(parts) > 1 else -1
    sub_letter = parts[2] if len(parts) > 2 else ""
    return (letter, sub_number, sub_letter)


def _parse_rule_node(
    node_lines: List[str], section_titles: List[str]
) -> Clause:
    """Read one [RULE] node back out of the document's text."""

    fields: Dict[str, str] = {}
    statement_lines: List[str] = []
    inside_statement = False
    for line_ in node_lines:
        if inside_statement:
            if line_ == "<<<":
                inside_statement = False
                continue
            statement_lines.append(line_)
            continue
        if line_ == "STATEMENT: >>>":
            inside_statement = True
            continue
        if ": " in line_:
            name, _, value = line_.partition(": ")
            fields[name] = value

    uid = fields.get("UID", "")
    number = uid.split("-")[-1] if len(uid) > 0 else ""
    chapter_title = section_titles[-1] if len(section_titles) > 0 else ""
    return Clause(
        uid=uid,
        number=number,
        chapter=number.split(".")[0],
        chapter_title=CHAPTER_TITLE_PREFIX.sub("", chapter_title),
        title=fields.get("TITLE", ""),
        statement="\n".join(statement_lines).strip("\n"),
        status=fields.get("STATUS", STATUS_ACTIVE),
    )


if __name__ == "__main__":
    sys.exit(main())
