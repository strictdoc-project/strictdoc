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
import zlib
from binascii import crc32
from dataclasses import dataclass, field
from struct import pack
from typing import Any, Dict, List, Optional, Tuple

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

# Page footers sit below 30 pt. No body text comes near that.
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


@dataclass
class SourceDocument:
    """One rules PDF, as declared in the source manifest."""

    prefix: str
    file_name: str
    title: str


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
            )
        )
    return sources


def extract_clauses(
    pdf_path: str,
    prefix: str,
    assets_directory: str,
    document_directory: str,
) -> Tuple[List[Clause], List[str]]:
    """
    Split one rules PDF into clauses, one per numbered heading.

    Images are written next to the clause that owns them, and referenced from
    its statement. Returns the clauses and the image files written.
    """

    reader = PdfReader(pdf_path)
    first_body_page = _find_first_body_page(reader)

    clauses: List[Clause] = []
    written_images: List[str] = []
    chapter = ""
    chapter_title = ""
    current: Optional[Clause] = None
    paragraphs: List[List[str]] = []

    for page_index_ in range(first_body_page, len(reader.pages)):
        page_ = reader.pages[page_index_]
        items = _read_page_items(page_)
        previous_y: Optional[float] = None

        for item_ in items:
            if item_.image_name is not None:
                if current is None:
                    continue
                image_file_name = _write_image(
                    page_,
                    item_.image_name,
                    current.uid,
                    len(
                        [
                            image_
                            for image_ in written_images
                            if image_.startswith(f"{current.uid}-")
                        ]
                    )
                    + 1,
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
            heading = HEADING_PATTERN.match(item_.text)
            if heading is not None and _is_heading_line(item_.text):
                if current is not None:
                    current.statement = _join_paragraphs(paragraphs)
                    clauses.append(current)
                paragraphs = []
                previous_y = None

                letter_, number_, sub_letter_, title_ = heading.groups()
                if number_ is None and sub_letter_ is None:
                    chapter = letter_
                    chapter_title = title_
                clause_number = _format_clause_number(
                    letter_, number_, sub_letter_
                )
                current = Clause(
                    uid=f"RULE-{prefix}-{clause_number}",
                    number=clause_number,
                    chapter=chapter,
                    chapter_title=chapter_title,
                    title=title_,
                    statement="",
                )
                continue

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

    return [clause_ for clause_ in clauses if len(clause_.statement) > 0], (
        written_images
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
            os.path.join(source_directory, source_.file_name),
            source_.prefix,
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


def _read_page_items(page: PageObject) -> List[PageItem]:
    """Read one page as visual lines and image placements, top to bottom."""

    chunks: List[TextChunk] = []
    images: List[Tuple[float, str]] = []

    def visit_text(
        text: str,
        _matrix: List[float],
        text_matrix: List[float],
        _font: Optional[DictionaryObject],
        font_size: Optional[float],
    ) -> None:
        stripped = text.strip()
        if len(stripped) == 0:
            return
        if font_size is None or font_size < MINIMUM_FONT_SIZE:
            return
        if text_matrix[5] < MINIMUM_TEXT_Y:
            return
        chunks.append(
            TextChunk(
                y_position=text_matrix[5],
                x_position=text_matrix[4],
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
        images.append((matrix[5], str(operands[0])))

    page.extract_text(
        space_width=SPACE_WIDTH,
        visitor_text=visit_text,
        visitor_operand_before=visit_operand,
    )

    items: List[PageItem] = []
    for line_y_, line_text_ in _group_lines(chunks):
        items.append(PageItem(y_position=line_y_, text=line_text_))
    for image_y_, image_name_ in images:
        items.append(PageItem(y_position=image_y_, image_name=image_name_))

    items.sort(key=lambda item_: -item_.y_position)
    return items


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
    return re.sub(r"\s+", " ", text).strip()


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
        color_space = str(image_object.get("/ColorSpace"))
        bits_per_component = int(
            str(image_object.get("/BitsPerComponent", 0))
        )
        if bits_per_component != 8:
            return None
        if color_space == "/DeviceRGB":
            channels = 3
        elif color_space == "/DeviceGray":
            channels = 1
        else:
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
