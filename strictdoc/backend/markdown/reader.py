"""
Markdown reader for importing CommonMark documents into SDoc objects.
"""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

from markdown_it import MarkdownIt
from markdown_it.token import Token

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.free_text_reader import SDFreeTextReader
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileEntry,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.backend.sdoc_source_code.reader_registry import (
    SourceCodeReaderRegistry,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import strip_bom


@dataclass
class MarkdownHeadingNode:
    level: int
    title: str
    body: str
    line_start: int


@dataclass
class ParsedField:
    """Markdown specific intermediate precursor for a SDocNodeField"""

    name: str
    value: str
    human_name: str
    is_block_format: bool = False


@dataclass
class ParsedMarkdownNode:
    """Markdown specific intermediate precursor for a SDocNode."""

    fields: List[ParsedField]
    valid_for_requirement: bool
    has_duplicates: bool
    explicit_node_type: Optional[str] = None
    # Body after the meta block stripped, used as effective body for section
    # TEXT children so that **TYPE**: / **PREFIX**: / **MID**: lines do not
    # reappear as prose.  None means "use the raw heading body" (fallback for
    # ambiguous meta blocks such as duplicate-field invalid nodes).
    processed_body: Optional[str] = None


class SDMarkdownReader:
    markdown_parser = MarkdownIt("commonmark")
    default_meta_style = "backslash"
    plain_field_pattern = re.compile(
        r"^\*\*(?P<name>[A-Za-z0-9][A-Za-z0-9 _-]*)\*\*:(?P<value>.*)$"
    )
    # Patterns for detecting the **TYPE**: TEXT \ **MID**: ... prefix in TEXT
    # node bodies (used when the grammar's TEXT element declares a MID field).
    _text_type_line_re = re.compile(r"^\*\*TYPE\*\*: TEXT(?: \\)?$")
    _text_mid_line_re = re.compile(r"^\*\*MID\*\*: (\S+)$")
    dict_entry_pattern = re.compile(
        r"^\s*\*\*(?P<name>[A-Za-z0-9][A-Za-z0-9 _-]*)\*\*:\s*`?(?P<value>[^`]*)`?\s*(?:\\)?$"
    )
    bullet_item_start_pattern = re.compile(r"^\s*-\s+")
    dict_bullet_start_pattern = re.compile(r"^\s*-\s+\*\*")
    valid_requirement_fields = {
        "MID",
        "UID",
        "LEVEL",
        "STATUS",
        "TAGS",
        "RELATIONS",
        "TITLE",
        "STATEMENT",
        "RATIONALE",
        "COMMENT",
    }
    requirement_meta_fields = {"MID", "UID", "LEVEL", "STATUS", "TAGS"}

    @staticmethod
    def read(
        input_string: str,
        file_path: Optional[str],
        project_config: Optional[ProjectConfig] = None,
    ) -> SDocDocument:
        """Convert a StrictDoc-conventional markdown file into SDocDocument."""
        input_string = strip_bom(input_string)

        markdown_tokens: Sequence[Token] = (
            SDMarkdownReader.markdown_parser.parse(input_string)
        )
        heading_nodes = SDMarkdownReader._extract_heading_nodes(
            markdown_tokens, input_string
        )

        if len(heading_nodes) == 0 or heading_nodes[0].level != 1:
            raise StrictDocSemanticError(
                title=(
                    "Markdown parsing error: the document must start with "
                    "an H1 heading."
                ),
                hint=None,
                example="# Document title",
                line=1,
                col=1,
                filename=file_path,
            )

        SDMarkdownReader._validate_no_content_before_h1(
            input_string=input_string,
            first_heading=heading_nodes[0],
            file_path=file_path,
        )

        SDMarkdownReader._validate_no_redundant_empty_lines(
            input_string, markdown_tokens, file_path
        )

        document_title = heading_nodes[0].title
        if len(document_title) == 0:
            document_title = SDMarkdownReader._fallback_document_title(
                file_path
            )

        (
            document,
            document_reference,
            including_document_reference,
        ) = SDMarkdownReader._make_new_empty_document(
            title=document_title,
            file_raw_text_content=input_string,
        )

        document.ng_including_document_reference = including_document_reference

        SDMarkdownReader._parse_document_root(
            root_heading=heading_nodes[0],
            document=document,
            document_reference=document_reference,
            including_document_reference=including_document_reference,
            file_path=file_path,
        )

        has_custom_grammar = (
            document.grammar is not None
            and document.grammar.import_from_file is not None
        )
        SDMarkdownReader._create_document_tree(
            heading_nodes=heading_nodes[1:],
            document=document,
            document_reference=document_reference,
            including_document_reference=including_document_reference,
            file_path=file_path,
            project_config=project_config,
            has_custom_grammar=has_custom_grammar,
        )

        return document

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> SDocDocument:
        """Read and parse a .md file, with pickle-cache support for fast reloads."""
        unpickled_content = PickleCache.read_from_cache(
            file_path,
            project_config,
            "markdown",
        )
        if unpickled_content is not None:
            return assert_cast(unpickled_content, SDocDocument)

        # Keep original line endings in fields; writer normalizes to LF.
        with open(file_path, encoding="utf-8-sig", newline="") as file:
            markdown_content = file.read()

        document = self.read(
            markdown_content, file_path=file_path, project_config=project_config
        )
        document.build_search_index()

        PickleCache.save_to_cache(
            document,
            file_path,
            project_config,
            "markdown",
        )

        return document

    @staticmethod
    def _make_new_empty_document(
        title: str,
        file_raw_text_content: str,
    ) -> Tuple[SDocDocument, DocumentReference, DocumentReference]:
        """
        Create an empty document SDocDocument skeleton.

        title is the title of the new SDocDocument.
        file_raw_text_content is the plain .md file content. It's attached to the SDocDocument for future (currently unused).

        Returned document_reference and including_document_reference are helpers to support DOCUMENT_FROM_FILE resolution
        at a later stage with configure_with_resolved_document.
        """
        document = SDocDocument(
            mid=None,
            title=title,
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )
        document.config.markup = SDocMarkup.MARKDOWN
        document.grammar = DocumentGrammar.create_default(
            parent=document,
            enable_mid=True,
            include_child_relation=True,
        )
        document.ng_has_requirements = False
        document.ng_source_content = file_raw_text_content
        document_reference = DocumentReference()
        document_reference.set_document(document)
        including_document_reference = DocumentReference()
        return document, document_reference, including_document_reference

    @staticmethod
    def _parse_document_root(
        root_heading: MarkdownHeadingNode,
        document: SDocDocument,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        file_path: Optional[str],
    ) -> None:
        """
        Extend SDocDocument with data from first H1 heading.

        root_heading is expected to provide the first H1 heading from the md, as previously discovered by markdown-it-py.
        The caller is expected to create an empty document and document_references and pass them to any _parse_* function.
        The passed document is mutated in place to add custom metadata, section contents and freeform prose from H1.
        Callers should also pass the md file_path as a hint for better error messages.
        """
        root_body_lines = root_heading.body.splitlines(keepends=True)

        (
            root_meta_fields,
            root_body_lines_without_meta,
            root_meta_valid,
        ) = SDMarkdownReader._parse_meta_fields(
            root_body_lines, file_path=file_path
        )

        if root_meta_valid and len(root_meta_fields) > 0:
            root_field_names = list(
                map(lambda field_: field_.name, root_meta_fields)
            )
            if len(set(root_field_names)) != len(root_field_names):
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: duplicate field names in "
                        "root document metadata are not allowed."
                    ),
                    hint=None,
                    example=None,
                    line=root_heading.line_start,
                    col=1,
                    filename=file_path,
                )

            metadata_entries = []
            for field_ in root_meta_fields:
                if field_.name == "GRAMMAR":
                    document.grammar = DocumentGrammar(
                        parent=document,
                        elements=[],
                        import_from_file=field_.value,
                    )
                    continue
                if field_.name == "PREFIX":
                    document.config.requirement_prefix = field_.value
                metadata_entries.append(
                    DocumentCustomMetadataKeyValuePair(
                        key=field_.human_name,
                        value=field_.value,
                    )
                )
            document.config.custom_metadata = DocumentCustomMetadata(
                entries=metadata_entries
            )
        else:
            root_body_lines_without_meta = root_body_lines
            document.config.custom_metadata = None

        root_text = "".join(root_body_lines_without_meta)
        if len(root_text.strip()) > 0:
            root_text_node = SDMarkdownReader._create_text_node(
                parent=document,
                statement=root_text,
                document_reference=document_reference,
                including_document_reference=including_document_reference,
            )
            document.section_contents.append(root_text_node)

    @staticmethod
    def _create_document_tree(
        heading_nodes: List[MarkdownHeadingNode],
        document: SDocDocument,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        file_path: Optional[str],
        project_config: Optional[ProjectConfig] = None,
        has_custom_grammar: bool = False,
    ) -> None:
        """
        Populate document section contents from H2+ heading nodes.

        Each md heading becomes either a REQUIREMENT node (if it passes
        _parse_markdown_node validation) or a plain section node.
        Nesting follows heading levels via a depth stack.
        """
        stack: List[Tuple[int, Union[SDocDocument, SDocNode]]] = [(1, document)]
        previous_level = 1

        for heading_node in heading_nodes:
            if heading_node.level == 1:
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: only the first heading may "
                        "use level H1."
                    ),
                    hint=None,
                    example="# Document title",
                    line=heading_node.line_start,
                    col=1,
                    filename=file_path,
                )

            if heading_node.level > previous_level + 1:
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: heading level forward jumps "
                        f"are not allowed: L{previous_level} -> "
                        f"L{heading_node.level}."
                    ),
                    hint=None,
                    example="# H1\\n## H2",
                    line=heading_node.line_start,
                    col=1,
                    filename=file_path,
                )

            while len(stack) > 0 and stack[-1][0] >= heading_node.level:
                stack.pop()
            assert len(stack) > 0

            parent_node = stack[-1][1]
            parsed_node = SDMarkdownReader._parse_markdown_node(
                heading_node.title,
                heading_node.body,
                file_path=file_path,
                has_custom_grammar=has_custom_grammar,
            )

            if parsed_node.valid_for_requirement:
                if parsed_node.has_duplicates:
                    raise StrictDocSemanticError(
                        title=(
                            "Markdown parsing error: duplicate field names "
                            "in a valid requirement node are not allowed."
                        ),
                        hint=None,
                        example=None,
                        line=heading_node.line_start,
                        col=1,
                        filename=file_path,
                    )

                requirement_node = SDMarkdownReader._create_requirement_node(
                    parent=parent_node,
                    title=heading_node.title,
                    fields=parsed_node.fields,
                    document_reference=document_reference,
                    including_document_reference=including_document_reference,
                    file_path=file_path,
                    project_config=project_config,
                    node_type=parsed_node.explicit_node_type or "REQUIREMENT",
                )
                parent_node.section_contents.append(requirement_node)
                stack.append((heading_node.level, requirement_node))

                SDMarkdownReader._memorize_requirement_human_titles(
                    document=document,
                    markdown_fields=parsed_node.fields,
                )

                document.ng_has_requirements = True
                cursor_node: Optional[SDocNode]
                if isinstance(parent_node, SDocNode):
                    cursor_node = parent_node
                else:
                    cursor_node = None
                while cursor_node is not None:
                    cursor_node.ng_has_requirements = True
                    parent_candidate = cursor_node.parent
                    if isinstance(parent_candidate, SDocNode):
                        cursor_node = parent_candidate
                    else:
                        cursor_node = None
            else:
                section_node = SDocNode.create_section(
                    parent_node,
                    document,
                    heading_node.title,
                )
                section_node.ng_including_document_reference = (
                    including_document_reference
                )
                # Preserve MID from the section meta block (e.g. **TYPE**: SECTION \ **MID**: ...).
                # create_section does not accept fields, so we patch it in afterwards.
                # MID must be inserted before TITLE to match the grammar field order.
                mid_field = next(
                    (f for f in parsed_node.fields if f.name == "MID"), None
                )
                if mid_field is not None:
                    mid_sdoc_field = SDocNodeField.create_from_string(
                        parent=section_node,
                        field_name="MID",
                        field_value=mid_field.value,
                        multiline=False,
                    )
                    existing = list(section_node.ordered_fields_lookup.items())
                    section_node.ordered_fields_lookup.clear()
                    section_node.ordered_fields_lookup["MID"] = [mid_sdoc_field]
                    section_node.ordered_fields_lookup.update(existing)
                    section_node.reserved_mid = MID(mid_field.value)
                    section_node.mid_permanent = True
                # Preserve PREFIX from the section meta block.
                # PREFIX is inserted before TITLE (after MID) to keep the
                # field order: MID, LEVEL, PREFIX, TITLE.
                prefix_field = next(
                    (f for f in parsed_node.fields if f.name == "PREFIX"), None
                )
                if prefix_field is not None:
                    prefix_sdoc_field = SDocNodeField.create_from_string(
                        parent=section_node,
                        field_name="PREFIX",
                        field_value=prefix_field.value,
                        multiline=False,
                    )
                    title_entry = section_node.ordered_fields_lookup.pop(
                        "TITLE", None
                    )
                    section_node.ordered_fields_lookup["PREFIX"] = [
                        prefix_sdoc_field
                    ]
                    if title_entry is not None:
                        section_node.ordered_fields_lookup["TITLE"] = (
                            title_entry
                        )
                parent_node.section_contents.append(section_node)

                # When processed_body is set the meta block has been stripped;
                # use it to avoid duplicating **TYPE**: / **PREFIX**: / **MID**:
                # lines as prose in the TEXT child.  Otherwise fall back to the
                # raw heading body so ambiguous content is preserved.
                effective_body = (
                    parsed_node.processed_body
                    if parsed_node.processed_body is not None
                    else heading_node.body
                )
                if len(effective_body.strip()) > 0:
                    text_mid, text_statement = (
                        SDMarkdownReader._try_parse_text_meta(effective_body)
                    )
                    text_node = SDMarkdownReader._create_text_node(
                        parent=section_node,
                        statement=text_statement,
                        document_reference=document_reference,
                        including_document_reference=including_document_reference,
                        mid=text_mid,
                    )
                    section_node.section_contents.append(text_node)

                stack.append((heading_node.level, section_node))

            previous_level = heading_node.level

    @staticmethod
    def _memorize_requirement_human_titles(
        document: SDocDocument, markdown_fields: List[ParsedField]
    ) -> None:
        """
        Copy markdown field names (e.g. "Statement") from markdown to default grammar REQUIREMENT element.

        The markdown writer will later use the names to reproduce original capitalisation.
        """
        assert document.grammar is not None
        requirement_element = document.grammar.elements_by_type.get(
            "REQUIREMENT"
        )
        if requirement_element is None:
            return
        for markdown_field in markdown_fields:
            if markdown_field.name not in requirement_element.fields_map:
                continue
            grammar_field = requirement_element.fields_map[markdown_field.name]
            if grammar_field.human_title is None:
                grammar_field.human_title = markdown_field.human_name

    @staticmethod
    def _fallback_document_title(file_path: Optional[str]) -> str:
        """Return the file stem as a title when the H1 heading text is empty."""
        if file_path is not None and len(file_path) > 0:
            file_name = os.path.basename(file_path)
            file_name_stem, _ = os.path.splitext(file_name)
            if len(file_name_stem) > 0:
                return file_name_stem
        return "NONAME"

    @staticmethod
    def _validate_no_content_before_h1(
        input_string: str,
        first_heading: MarkdownHeadingNode,
        file_path: Optional[str],
    ) -> None:
        """Raise if any non-empty line precedes the H1 heading."""
        input_lines = input_string.splitlines()
        first_heading_line_index = first_heading.line_start - 1
        for line_index in range(0, first_heading_line_index):
            if len(input_lines[line_index].strip()) == 0:
                continue
            raise StrictDocSemanticError(
                title=(
                    "Markdown parsing error: the first content of the "
                    "document must be an H1 heading."
                ),
                hint=None,
                example="# Document title",
                line=line_index + 1,
                col=1,
                filename=file_path,
            )

    @staticmethod
    def _extract_heading_nodes(
        markdown_tokens: Sequence[Token], input_string: str
    ) -> List[MarkdownHeadingNode]:
        """
        Convert a markdown-it-py token stream into a flat list of MarkdownHeadingNodes.

        Each node captures the heading level, title text, body text (everything
        between this heading and the next), and the 1-based source line number.
        """
        input_lines = input_string.splitlines(keepends=True)
        heading_data: List[Tuple[int, int, str, int]] = []

        token_count = len(markdown_tokens)
        for token_index, token in enumerate(markdown_tokens):
            if token.type != "heading_open":
                continue
            if token.tag is None or len(token.tag) != 2 or token.tag[0] != "h":
                continue

            heading_level = int(token.tag[1])
            token_map = token.map
            if token_map is None:
                continue

            line_start = token_map[0] + 1
            body_start = token_map[1]

            next_token_index = token_index + 1
            if next_token_index >= token_count:
                heading_title = ""
            else:
                next_token = markdown_tokens[next_token_index]
                heading_title = (
                    next_token.content.strip()
                    if next_token.type == "inline"
                    else ""
                )

            heading_data.append(
                (heading_level, body_start, heading_title, line_start)
            )

        heading_nodes: List[MarkdownHeadingNode] = []
        heading_count = len(heading_data)
        for heading_index, heading_item in enumerate(heading_data):
            (
                heading_level,
                body_start,
                heading_title,
                line_start,
            ) = heading_item

            if heading_index + 1 < heading_count:
                next_heading = heading_data[heading_index + 1]
                body_end = next_heading[1] - 1
            else:
                body_end = len(input_lines)

            body = "".join(input_lines[body_start:body_end])

            heading_nodes.append(
                MarkdownHeadingNode(
                    level=heading_level,
                    title=heading_title,
                    body=body,
                    line_start=line_start,
                )
            )

        return heading_nodes

    @staticmethod
    def _validate_no_redundant_empty_lines(
        input_string: str,
        markdown_tokens: Sequence[Token],
        file_path: Optional[str],
    ) -> None:
        """Raise if two or more consecutive empty lines appear outside code blocks and blockquotes."""
        exempt_line_indexes: Set[int] = set()
        for token in markdown_tokens:
            if token.type not in ("fence", "code_block", "blockquote_open"):
                continue
            if token.map is None:
                continue
            for line_index in range(token.map[0], token.map[1]):
                exempt_line_indexes.add(line_index)

        input_lines = input_string.splitlines()
        empty_line_count = 0
        for line_index, line in enumerate(input_lines):
            if line_index in exempt_line_indexes:
                empty_line_count = 0
                continue

            if len(line.strip()) == 0:
                empty_line_count += 1
                if empty_line_count >= 2:
                    raise StrictDocSemanticError(
                        title=(
                            "Markdown parsing error: two or more consecutive "
                            "empty lines are not allowed outside of code "
                            "blocks and blockquotes."
                        ),
                        hint=None,
                        example=None,
                        line=line_index + 1,
                        col=1,
                        filename=file_path,
                    )
            else:
                empty_line_count = 0

    @staticmethod
    def _parse_markdown_node(
        title: str,
        body: str,
        file_path: Optional[str],
        has_custom_grammar: bool = False,
    ) -> ParsedMarkdownNode:
        """
        Parse a heading's body text into a ParsedMarkdownNode.

        Determines whether the node qualifies as a REQUIREMENT (has UID/MID,
        a STATEMENT, only known fields, no duplicates, no empty values) or
        should be treated as a plain section.
        """
        body_lines = body.splitlines(keepends=True)

        (
            meta_fields,
            body_lines_without_meta,
            meta_is_valid,
        ) = SDMarkdownReader._parse_meta_fields(body_lines, file_path=file_path)
        content_fields, content_is_valid = (
            SDMarkdownReader._parse_content_fields(
                body_lines_without_meta, file_path=file_path
            )
        )

        parsed_fields = meta_fields + content_fields

        # Extract TYPE before further validation; it controls the node type and
        # must not be forwarded as a regular SDoc field.
        # Only the first TYPE field is honoured: for SECTION nodes the body may
        # contain a **TYPE**: TEXT \ prefix in the TEXT child content (MD-28),
        # and that body-level TYPE must not override the meta-block TYPE.
        explicit_node_type: Optional[str] = None
        parsed_fields_without_type: List[ParsedField] = []
        for field_ in parsed_fields:
            if field_.name == "TYPE":
                if explicit_node_type is None:
                    explicit_node_type = field_.value.strip()
                # Subsequent TYPE fields (e.g. in the TEXT body) are discarded.
            else:
                parsed_fields_without_type.append(field_)
        parsed_fields = parsed_fields_without_type

        parsed_field_names = list(
            map(lambda field_: field_.name, parsed_fields)
        )
        parsed_field_names.append("TITLE")

        has_duplicates = len(set(parsed_field_names)) != len(parsed_field_names)
        has_mid_or_uid = (
            "MID" in parsed_field_names or "UID" in parsed_field_names
        )
        has_content_field = "STATEMENT" in parsed_field_names
        has_only_known_fields = True
        has_empty_field_values = any(
            len(field_.value) == 0 for field_ in parsed_fields
        )

        if explicit_node_type == "SECTION":
            # Explicit TYPE: SECTION always creates a section, regardless of
            # whether the body would otherwise qualify as a requirement.
            valid_for_requirement = False
        elif explicit_node_type is not None:
            # Any other explicit TYPE is accepted as long as the markdown syntax
            # is well-formed and the heading has a non-empty title.  Grammar
            # field validation is deferred to TraceabilityIndexBuilder.
            valid_for_requirement = (
                meta_is_valid and content_is_valid and len(title) > 0
            )
        elif has_custom_grammar:
            # When a custom grammar is attached, drop the hardcoded UID/STATEMENT
            # assumptions and defer field validation to TraceabilityIndexBuilder.
            valid_for_requirement = (
                meta_is_valid
                and content_is_valid
                and has_only_known_fields
                and not has_empty_field_values
                and len(parsed_fields) > 0
                and len(title) > 0
            )
        else:
            valid_for_requirement = (
                meta_is_valid
                and content_is_valid
                and has_mid_or_uid
                and has_content_field
                and has_only_known_fields
                and not has_empty_field_values
                and len(title) > 0
            )

        # Use body_lines_without_meta (meta block stripped) as processed_body
        # only when the meta block contains section-specific fields (TYPE, MID,
        # PREFIX) so those lines do not reappear as prose in the TEXT child.
        # For ambiguous meta blocks (e.g. duplicate UID fields in an invalid
        # requirement node) fall back to None so _create_document_tree uses the
        # raw heading body and preserves the content.
        _parsed_field_names: Set[str] = {f.name for f in parsed_fields}
        processed_body: Optional[str] = None
        if explicit_node_type is not None or (
            "MID" in _parsed_field_names or "PREFIX" in _parsed_field_names
        ):
            processed_body = "".join(body_lines_without_meta)

        return ParsedMarkdownNode(
            fields=parsed_fields,
            valid_for_requirement=valid_for_requirement,
            has_duplicates=has_duplicates,
            explicit_node_type=explicit_node_type,
            processed_body=processed_body,
        )

    @staticmethod
    def _parse_meta_fields(
        body_lines: List[str],
        file_path: Optional[str],
    ) -> Tuple[List[ParsedField], List[str], bool]:
        """
        Extract the leading meta-field block from raw markdown content of a requirement.

        body_lines is the line-split raw markdown content of a requirement (everything after the heading).

        The meta block is the contiguous run of **Key**: value lines that follows
        the first empty line (SDOC-LLR-186 convention).

        Returns:
        - parsed key/value pairs from the meta block (empty if none found)
        - remaining body lines after the meta block, passed on to _parse_content_fields
        - True on success, False on parse error
        """
        if len(body_lines) == 0 or not SDMarkdownReader._is_empty_line(
            body_lines[0]
        ):
            return [], body_lines, True

        next_line_index = 1
        if next_line_index >= len(body_lines):
            return [], body_lines, True

        line_text = SDMarkdownReader._line_without_line_ending(
            body_lines[next_line_index]
        )
        if SDMarkdownReader._detect_meta_style(line_text) is None:
            return [], body_lines, True

        meta_lines: List[str] = []
        while next_line_index < len(body_lines):
            line = body_lines[next_line_index]
            if SDMarkdownReader._is_empty_line(line):
                break
            meta_lines.append(line)
            next_line_index += 1

        if len(meta_lines) == 0:
            return [], body_lines, True

        parsed_fields, parse_success = SDMarkdownReader._parse_meta_lines(
            meta_lines,
        )
        if not parse_success:
            return [], body_lines, True

        if next_line_index < len(
            body_lines
        ) and SDMarkdownReader._is_empty_line(body_lines[next_line_index]):
            next_nonempty_line_index = next_line_index + 1
            while next_nonempty_line_index < len(body_lines):
                if not SDMarkdownReader._is_empty_line(
                    body_lines[next_nonempty_line_index]
                ):
                    break
                next_nonempty_line_index += 1
            if next_nonempty_line_index < len(body_lines):
                next_nonempty_line_text = (
                    SDMarkdownReader._line_without_line_ending(
                        body_lines[next_nonempty_line_index]
                    )
                )
                next_field_match = SDMarkdownReader.plain_field_pattern.match(
                    next_nonempty_line_text
                )
                if (
                    next_field_match is not None
                    and next_field_match.group("name").upper() == "RELATIONS"
                ):
                    raise StrictDocSemanticError(
                        title=(
                            "Markdown parsing error: Relations must directly "
                            "follow requirement metadata without an empty line."
                        ),
                        hint=None,
                        example="**UID**: REQ-1\n**Relations**:",
                        line=1,
                        col=1,
                        filename=file_path,
                    )
            next_line_index += 1

        return parsed_fields, body_lines[next_line_index:], True

    @staticmethod
    def _detect_meta_style(line_text: str) -> Optional[str]:
        """Return "backslash" if the line is a plain `**Key**: value` field, else None."""
        if SDMarkdownReader.plain_field_pattern.match(line_text) is not None:
            return "backslash"
        return None

    @staticmethod
    def _parse_meta_lines(
        meta_lines: List[str],
    ) -> Tuple[List[ParsedField], bool]:
        """
        Parse meta fields in backslash style.

        A field with an empty inline value (e.g. "**Relations**:") is a
        list-valued field: the following lines up to the next plain field
        header are consumed as its value.

        Returns:
        - successfully parsed fields (empty on failure)
        - False if any line fails to match; callers treat this as "not a requirement"
        """
        parsed_fields: List[ParsedField] = []
        meta_line_count = len(meta_lines)
        meta_line_index = 0

        while meta_line_index < meta_line_count:
            line_text = SDMarkdownReader._line_without_line_ending(
                meta_lines[meta_line_index]
            )
            meta_line_index += 1

            match = SDMarkdownReader.plain_field_pattern.match(line_text)
            if match is None:
                return [], False
            value = SDMarkdownReader._trim_single_space_prefix(
                match.group("value")
            )

            if len(value) == 0:
                # List-valued field: collect following lines until the
                # next plain field header as the field value.
                list_lines: List[str] = []
                while meta_line_index < meta_line_count:
                    candidate_text = SDMarkdownReader._line_without_line_ending(
                        meta_lines[meta_line_index]
                    )
                    if (
                        SDMarkdownReader.plain_field_pattern.match(
                            candidate_text
                        )
                        is not None
                    ):
                        break
                    list_lines.append(meta_lines[meta_line_index])
                    meta_line_index += 1
                value = "".join(list_lines)
            else:
                is_last_field = meta_line_index == meta_line_count
                if not is_last_field:
                    if value.endswith(" \\"):
                        value = value[:-2]
                elif value.endswith("\\"):
                    return [], False

            if value.startswith("`") and value.endswith("`") and len(value) > 1:
                value = value[1:-1]

            parsed_fields.append(
                ParsedField(
                    name=match.group("name").upper(),
                    human_name=match.group("name"),
                    value=value,
                )
            )

        return parsed_fields, True

    @staticmethod
    def _parse_content_fields(
        body_lines: List[str],
        file_path: Optional[str],
    ) -> Tuple[List[ParsedField], bool]:
        """
        Parse content fields and freeform STATEMENT prose from the post-meta body lines.

        A **Key**: line at column 0 starts a named field. If its value is empty
        and the next line opens a dict bullet (- **), the field is a structured
        list (e.g. RELATIONS); otherwise the field value is collected as
        multiline prose until the next field header or end of body.
        Lines that match no field header are accumulated as an implicit STATEMENT.

        Returns:
        - parsed fields including any implicit STATEMENT (empty on failure)
        - True on success, False on parse error
        """
        parsed_fields: List[ParsedField] = []
        line_index = 0
        line_count = len(body_lines)

        # Pre-compute line indices that fall *inside* fenced code blocks
        # (between the opening and closing fence markers).  Those lines must
        # not be matched against plain_field_pattern — they are opaque content.
        fence_interior: Set[int] = set()
        _fence_open_re = re.compile(r"^(`{3,}|~{3,})")
        _fi = 0
        while _fi < line_count:
            _m = _fence_open_re.match(
                SDMarkdownReader._line_without_line_ending(body_lines[_fi])
            )
            if _m:
                _fence_char = _m.group(1)[0]
                _fence_min = len(_m.group(1))
                _close_re = re.compile(
                    rf"^{re.escape(_fence_char)}{{{_fence_min},}}\s*$"
                )
                _fi += 1
                while _fi < line_count:
                    _inner = SDMarkdownReader._line_without_line_ending(
                        body_lines[_fi]
                    )
                    if _close_re.match(_inner):
                        _fi += 1
                        break
                    fence_interior.add(_fi)
                    _fi += 1
            else:
                _fi += 1

        while line_index < line_count:
            line = body_lines[line_index]
            if SDMarkdownReader._is_empty_line(line):
                next_nonempty_line_index = line_index + 1
                while next_nonempty_line_index < line_count:
                    if not SDMarkdownReader._is_empty_line(
                        body_lines[next_nonempty_line_index]
                    ):
                        break
                    next_nonempty_line_index += 1
                if (
                    len(parsed_fields) > 0
                    and parsed_fields[-1].name
                    in SDMarkdownReader.requirement_meta_fields
                    and next_nonempty_line_index < line_count
                ):
                    next_line_text = SDMarkdownReader._line_without_line_ending(
                        body_lines[next_nonempty_line_index]
                    )
                    next_field_match = (
                        SDMarkdownReader.plain_field_pattern.match(
                            next_line_text
                        )
                    )
                    if (
                        next_field_match is not None
                        and next_field_match.group("name").upper()
                        == "RELATIONS"
                    ):
                        raise StrictDocSemanticError(
                            title=(
                                "Markdown parsing error: Relations must "
                                "directly follow requirement metadata without "
                                "an empty line."
                            ),
                            hint=None,
                            example="**UID**: REQ-1\n**Relations**:",
                            line=1,
                            col=1,
                            filename=file_path,
                        )
                line_index += 1
                continue

            line_text = SDMarkdownReader._line_without_line_ending(line)
            plain_match = SDMarkdownReader.plain_field_pattern.match(line_text)
            if plain_match is not None and line_index not in fence_interior:
                field_name_upper = plain_match.group("name").upper()
                field_name_human = plain_match.group("name")
                inline_value = SDMarkdownReader._trim_single_space_prefix(
                    plain_match.group("value")
                )
                line_index += 1

                if len(inline_value) > 0:
                    continuation_lines: List[str] = []
                    while line_index < line_count:
                        candidate_line = body_lines[line_index]
                        candidate_line_text = (
                            SDMarkdownReader._line_without_line_ending(
                                candidate_line
                            )
                        )
                        if (
                            SDMarkdownReader.plain_field_pattern.match(
                                candidate_line_text
                            )
                            is not None
                            and line_index not in fence_interior
                        ):
                            break
                        continuation_lines.append(candidate_line)
                        line_index += 1
                    while (
                        continuation_lines
                        and SDMarkdownReader._is_empty_line(
                            continuation_lines[-1]
                        )
                    ):
                        continuation_lines.pop()
                    if continuation_lines:
                        field_value = (
                            inline_value + "\n" + "".join(continuation_lines)
                        )
                    else:
                        field_value = inline_value
                    parsed_fields.append(
                        ParsedField(
                            name=field_name_upper,
                            human_name=field_name_human,
                            value=field_value,
                        )
                    )
                    continue

                is_list_field = (
                    line_index < line_count
                    and SDMarkdownReader.dict_bullet_start_pattern.match(
                        SDMarkdownReader._line_without_line_ending(
                            body_lines[line_index]
                        )
                    )
                    is not None
                )
                if (
                    not is_list_field
                    and line_index < line_count
                    and SDMarkdownReader._is_empty_line(body_lines[line_index])
                ):
                    line_index += 1

                multiline_field_lines: List[str] = []
                while line_index < line_count:
                    candidate_line = body_lines[line_index]
                    candidate_line_text = (
                        SDMarkdownReader._line_without_line_ending(
                            candidate_line
                        )
                    )
                    if (
                        SDMarkdownReader.plain_field_pattern.match(
                            candidate_line_text
                        )
                        is not None
                        and line_index not in fence_interior
                    ):
                        break
                    if is_list_field and SDMarkdownReader._is_empty_line(
                        candidate_line
                    ):
                        break
                    multiline_field_lines.append(candidate_line)
                    line_index += 1

                field_value = "".join(multiline_field_lines)
                parsed_fields.append(
                    ParsedField(
                        name=field_name_upper,
                        human_name=field_name_human,
                        value=field_value,
                        is_block_format=True,
                    )
                )
                continue

            statement_lines: List[str] = []
            while line_index < line_count:
                candidate_line = body_lines[line_index]
                candidate_line_text = (
                    SDMarkdownReader._line_without_line_ending(candidate_line)
                )
                if (
                    SDMarkdownReader.plain_field_pattern.match(
                        candidate_line_text
                    )
                    and line_index not in fence_interior
                ):
                    break
                statement_lines.append(candidate_line)
                line_index += 1

            statement_value = "".join(statement_lines)
            if len(statement_value.strip()) == 0:
                continue
            parsed_fields.append(
                ParsedField(
                    name="STATEMENT",
                    human_name="Statement",
                    value=statement_value,
                )
            )

        return parsed_fields, True

    @staticmethod
    def _create_requirement_node(
        parent: Union[SDocDocument, SDocNode],
        title: str,
        fields: List[ParsedField],
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        file_path: Optional[str] = None,
        project_config: Optional[ProjectConfig] = None,
        node_type: str = "REQUIREMENT",
    ) -> SDocNode:
        """Build a SDocNode from parsed fields, attaching relations and document references."""
        parsed_meta_fields: List[ParsedField] = []
        parsed_content_fields: List[ParsedField] = []
        relations_field: Optional[ParsedField] = None
        for field in fields:
            if field.name == "RELATIONS":
                relations_field = field
                continue
            if field.name in SDMarkdownReader.requirement_meta_fields:
                parsed_meta_fields.append(field)
            else:
                parsed_content_fields.append(field)

        requirement_fields: List[SDocNodeField] = []
        for field in parsed_meta_fields:
            requirement_fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=field.name,
                    field_value=field.value,
                    multiline="\n" in field.value,
                )
            )
        requirement_fields.append(
            SDocNodeField.create_from_string(
                parent=None,
                field_name="TITLE",
                field_value=title,
                multiline=False,
            )
        )
        for field in parsed_content_fields:
            sdoc_field = SDocNodeField(
                parent=None,
                field_name=field.name,
                parts=SDMarkdownReader._parse_text_parts(field.value),
                multiline__="multiline" if field.is_block_format else None,
            )
            requirement_fields.append(sdoc_field)

        requirement = SDocNode(
            parent=parent,
            node_type=node_type,
            fields=requirement_fields,
            relations=[],
        )
        SDMarkdownReader._wire_node_field_parents(requirement)
        if relations_field is not None:
            requirement.relations = SDMarkdownReader._build_references(
                SDMarkdownReader._parse_bullet_list_of_dicts(
                    relations_field.value
                ),
                requirement,
                file_path,
                project_config,
            )
        requirement.ng_document_reference = document_reference
        requirement.ng_including_document_reference = (
            including_document_reference
        )
        return requirement

    @staticmethod
    def _try_parse_text_meta(body: str) -> Tuple[Optional[str], str]:
        r"""
        Detect and extract a **TYPE**: TEXT \\ **MID**: <value> prefix block
        from a section body string.

        Returns (mid_value, remaining_body) when the prefix is found, or
        (None, body) when it is not present.  The remaining_body is the content
        after the blank line that follows the meta block.
        """
        lines = body.splitlines(keepends=True)
        if len(lines) < 2:
            return None, body

        line0 = lines[0].rstrip("\r\n")
        if not SDMarkdownReader._text_type_line_re.match(line0):
            return None, body

        line1 = lines[1].rstrip("\r\n")
        mid_match = SDMarkdownReader._text_mid_line_re.match(line1)
        if not mid_match:
            return None, body

        mid_value = mid_match.group(1)

        idx = 2
        while idx < len(lines) and not SDMarkdownReader._is_empty_line(
            lines[idx]
        ):
            idx += 1
        while idx < len(lines) and SDMarkdownReader._is_empty_line(lines[idx]):
            idx += 1

        remaining = "".join(lines[idx:])
        return mid_value, remaining

    @staticmethod
    def _create_text_node(
        parent: Union[SDocDocument, SDocNode],
        statement: str,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        mid: Optional[str] = None,
    ) -> SDocNode:
        """Build a TEXT SDocNode wrapping raw Markdown prose."""
        fields = []
        if mid is not None:
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name="MID",
                    field_value=mid,
                    multiline=False,
                )
            )
        fields.append(
            SDocNodeField(
                parent=None,
                field_name="STATEMENT",
                parts=SDMarkdownReader._parse_text_parts(statement),
                multiline__="multiline" if "\n" in statement else None,
            )
        )
        text_node = SDocNode(
            parent=parent,
            node_type="TEXT",
            fields=fields,
            relations=[],
        )
        SDMarkdownReader._wire_node_field_parents(text_node)
        text_node.ng_document_reference = document_reference
        text_node.ng_including_document_reference = including_document_reference
        return text_node

    @staticmethod
    def _parse_text_parts(value: str) -> List[Any]:
        """
        Parse a field value string into parts (str, InlineLink, Anchor).

        [LINK:] and [ANCHOR:] tokens inside inline code spans or fenced code
        blocks are treated as plain text and never turned into InlineLink /
        Anchor objects.
        """
        if "[LINK:" not in value and "[ANCHOR:" not in value:
            return [value]

        # Split into code / non-code segments so that [LINK:] / [ANCHOR:]
        # inside backtick spans or fenced code blocks are not parsed.
        segments = SDMarkdownReader._split_by_code_contexts(value)
        has_link_outside_code = any(
            not is_code and ("[LINK:" in seg or "[ANCHOR:" in seg)
            for is_code, seg in segments
        )
        if not has_link_outside_code:
            return [value]

        parts: List[Any] = []
        for is_code, seg in segments:
            if is_code:
                parts.append(seg)
            elif "[LINK:" in seg or "[ANCHOR:" in seg:
                parts.extend(SDFreeTextReader.read(seg).parts)
            else:
                parts.append(seg)

        # Merge adjacent plain strings so the output is compact.
        merged: List[Any] = []
        for part in parts:
            if isinstance(part, str) and merged and isinstance(merged[-1], str):
                merged[-1] += part
            else:
                merged.append(part)
        return merged if merged else [value]

    @staticmethod
    def _split_by_code_contexts(value: str) -> List[Tuple[bool, str]]:
        """
        Split a markdown field value into (is_code, text) segment pairs.

        Segments with is_code=True originate from fenced code blocks or inline
        code spans; their content is opaque and must not be parsed for
        [LINK:] / [ANCHOR:] tags.
        """
        # --- Step 1: mark lines that belong to fenced code blocks ---
        lines = value.splitlines(keepends=True)
        line_count = len(lines)
        fence_open_re = re.compile(r"^(`{3,}|~{3,})")

        in_fence = False
        fence_close_re: Optional[re.Pattern[str]] = None
        code_line_set: Set[int] = set()

        for li in range(line_count):
            line_text = lines[li].rstrip("\r\n")
            if not in_fence:
                m = fence_open_re.match(line_text)
                if m:
                    fence_char = m.group(1)[0]
                    fence_min = len(m.group(1))
                    fence_close_re = re.compile(
                        rf"^{re.escape(fence_char)}{{{fence_min},}}\s*$"
                    )
                    in_fence = True
                    code_line_set.add(li)
            else:
                code_line_set.add(li)
                if fence_close_re is not None and fence_close_re.match(
                    line_text
                ):
                    in_fence = False
                    fence_close_re = None

        # --- Step 2: build coarse segments from line groups ---
        fence_segments: List[Tuple[bool, str]] = []
        if line_count > 0:
            current_is_code = 0 in code_line_set
            current_lines: List[str] = []
            for li, line in enumerate(lines):
                is_code = li in code_line_set
                if is_code != current_is_code:
                    if current_lines:
                        fence_segments.append(
                            (current_is_code, "".join(current_lines))
                        )
                    current_lines = [line]
                    current_is_code = is_code
                else:
                    current_lines.append(line)
            if current_lines:
                fence_segments.append((current_is_code, "".join(current_lines)))
        else:
            fence_segments = [(False, value)]

        # --- Step 3: within non-code segments, find inline code spans ---
        inline_code_re = re.compile(r"(`+)(.*?)\1", re.DOTALL)
        result: List[Tuple[bool, str]] = []
        for is_code, seg in fence_segments:
            if is_code:
                result.append((True, seg))
                continue
            inner_pos = 0
            for m in inline_code_re.finditer(seg):
                if m.start() > inner_pos:
                    result.append((False, seg[inner_pos : m.start()]))
                result.append((True, m.group(0)))
                inner_pos = m.end()
            if inner_pos < len(seg):
                result.append((False, seg[inner_pos:]))

        return result

    @staticmethod
    def _wire_node_field_parents(node: SDocNode) -> None:
        """Wire SDocNodeField.parent and InlineLink/Anchor.parent for a node."""
        for fields_list in node.ordered_fields_lookup.values():
            for field in fields_list:
                field.parent = node
                for part in field.parts:
                    if isinstance(part, (InlineLink, Anchor)):
                        part.parent = field

    @staticmethod
    def _is_empty_line(line: str) -> bool:
        return len(line.strip()) == 0

    @staticmethod
    def _line_without_line_ending(line: str) -> str:
        return line.rstrip("\r\n")

    @staticmethod
    def _trim_single_space_prefix(value: str) -> str:
        if len(value) > 0 and value[0] == " ":
            return value[1:]
        return value

    @staticmethod
    def _parse_bullet_list_of_dicts(field_value: str) -> List[Dict[str, str]]:
        """
        Parse a bullet list of bold-key dicts from a field value string.

        Each "- " line starts a new dict item; continuation lines (indented)
        belong to the same item. Returns a list of {key: value} dicts,
        one per bullet. RELATIONS-agnostic: any structured list field can use this.
        """
        items: List[List[str]] = []
        current_item: Optional[List[str]] = None
        for line_ in field_value.splitlines():
            if SDMarkdownReader.bullet_item_start_pattern.match(line_):
                if current_item is not None:
                    items.append(current_item)
                current_item = [
                    SDMarkdownReader.bullet_item_start_pattern.sub(
                        "", line_, count=1
                    )
                ]
            elif current_item is not None:
                current_item.append(line_)
        if current_item is not None:
            items.append(current_item)
        return [
            SDMarkdownReader._parse_dict_item_lines(item_lines_)
            for item_lines_ in items
        ]

    @staticmethod
    def _build_references(
        items: List[Dict[str, str]],
        requirement: SDocNode,
        file_path: Optional[str],
        project_config: Optional[ProjectConfig] = None,
    ) -> List[Reference]:
        """Convert the list of parsed relation dicts to Reference objects. Raises if items is empty."""
        if len(items) == 0:
            raise StrictDocSemanticError(
                title=(
                    "Markdown parsing error: Relations list must not be empty."
                ),
                hint=None,
                example=None,
                line=1,
                col=1,
                filename=file_path,
            )
        return [
            SDMarkdownReader._build_reference(
                kv_, requirement, file_path, project_config
            )
            for kv_ in items
        ]

    @staticmethod
    def _parse_dict_item_lines(item_lines: List[str]) -> Dict[str, str]:
        """Parse bold-key/backtick-value pairs from one bullet item's lines into a dict."""
        kv: Dict[str, str] = {}
        for line in item_lines:
            # Strip line ending, trailing backslash continuation marker, and
            # leading indentation whitespace.
            stripped = line.rstrip("\r\n")
            if stripped.endswith(" \\"):
                stripped = stripped[:-2]
            stripped = stripped.lstrip()
            match = SDMarkdownReader.dict_entry_pattern.match(stripped)
            if match is None:
                continue
            key = match.group("name").strip()
            value = match.group("value").strip()
            kv[key] = value
        return kv

    @staticmethod
    def _build_reference(
        kv: Dict[str, str],
        requirement: SDocNode,
        file_path: Optional[str],
        project_config: Optional[ProjectConfig] = None,
    ) -> Reference:
        """Dispatch a single relation dict to ParentReqReference, ChildReqReference, or FileReference."""
        relation_type = kv.get("Type")
        if relation_type is None:
            raise StrictDocSemanticError(
                title=(
                    "Markdown parsing error: each relation dictionary must "
                    "contain a mandatory 'Type' key."
                ),
                hint=None,
                example=None,
                line=1,
                col=1,
                filename=file_path,
            )

        if relation_type in ("Parent", "Child"):
            allowed_keys = {"Type", "ID", "Role"}
            unknown = set(kv.keys()) - allowed_keys
            if len(unknown) > 0:
                raise StrictDocSemanticError(
                    title=(
                        f"Markdown parsing error: unknown key(s) in relation "
                        f"dictionary: {', '.join(sorted(unknown))}."
                    ),
                    hint=None,
                    example=None,
                    line=1,
                    col=1,
                    filename=file_path,
                )
            ref_uid = kv.get("ID")
            if ref_uid is None or len(ref_uid) == 0:
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: relation dictionary with "
                        f"Type '{relation_type}' must contain a mandatory "
                        "'ID' key."
                    ),
                    hint=None,
                    example=None,
                    line=1,
                    col=1,
                    filename=file_path,
                )
            role_value = kv.get("Role")
            role = (
                role_value
                if role_value is not None and len(role_value) > 0
                else None
            )
            if relation_type == "Parent":
                return ParentReqReference(
                    parent=requirement,
                    ref_uid=ref_uid,
                    role=role,
                )
            return ChildReqReference(
                parent=requirement,
                ref_uid=ref_uid,
                role=role if role is not None else "",
            )

        if relation_type == "File":
            allowed_keys = {"Type", "Path", "Element", "ID", "Hash", "Lines"}
            unknown = set(kv.keys()) - allowed_keys
            if len(unknown) > 0:
                raise StrictDocSemanticError(
                    title=(
                        f"Markdown parsing error: unknown key(s) in File "
                        f"relation dictionary: {', '.join(sorted(unknown))}."
                    ),
                    hint=None,
                    example=None,
                    line=1,
                    col=1,
                    filename=file_path,
                )
            path = kv.get("Path")
            if path is None or len(path) == 0:
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: File relation dictionary "
                        "must contain a mandatory 'Path' key."
                    ),
                    hint=None,
                    example=None,
                    line=1,
                    col=1,
                    filename=file_path,
                )
            element_value = kv.get("Element")
            id_value = kv.get("ID")
            line_range_value = kv.get("Lines")
            hash_value = kv.get("Hash")
            has_element_kv = element_value is not None or id_value is not None
            if (
                element_value is not None
                and len(element_value) > 0
                and project_config is not None
            ):
                reader = SourceCodeReaderRegistry.get_reader(
                    path, project_config
                )
                valid_elements = reader.supported_elements()
                if element_value not in valid_elements:
                    raise StrictDocSemanticError(
                        title=(
                            f"Markdown parsing error: unknown Element value "
                            f"'{element_value}' for file '{path}'. "
                            f"Valid values: {valid_elements if valid_elements else '(none for this file type)'}."
                        ),
                        hint=None,
                        example=None,
                        line=1,
                        col=1,
                        filename=file_path,
                    )
            has_line_kv = (
                line_range_value is not None and len(line_range_value) > 0
            )
            if has_element_kv and has_line_kv:
                raise StrictDocSemanticError(
                    title=(
                        "Markdown parsing error: File relation dictionary "
                        "must not combine language element keys (Element, ID) "
                        "with Lines."
                    ),
                    hint=None,
                    example=None,
                    line=1,
                    col=1,
                    filename=file_path,
                )
            file_entry = FileEntry(
                parent=requirement,
                g_file_format=None,
                g_file_path=path,
                g_line_range=line_range_value if has_line_kv else None,
                element=element_value
                if element_value is not None and len(element_value) > 0
                else None,
                id=id_value
                if id_value is not None and len(id_value) > 0
                else None,
                hash=hash_value
                if hash_value is not None and len(hash_value) > 0
                else None,
            )
            return FileReference(parent=requirement, g_file_entry=file_entry)

        raise StrictDocSemanticError(
            title=(
                f"Markdown parsing error: unknown relation Type "
                f"'{relation_type}'. Expected 'Parent', 'Child', or 'File'."
            ),
            hint=None,
            example=None,
            line=1,
            col=1,
            filename=file_path,
        )
