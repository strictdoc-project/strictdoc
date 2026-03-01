"""
Markdown reader for importing CommonMark documents into SDoc objects.
"""

import os
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Set, Tuple, Union

from markdown_it import MarkdownIt
from markdown_it.token import Token

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import strip_bom


@dataclass
class MarkdownHeadingNode:
    level: int
    title: str
    body: str
    line_start: int


@dataclass
class ParsedField:
    name: str
    value: str
    human_name: str


@dataclass
class ParsedMarkdownNode:
    fields: List[ParsedField]
    valid_for_requirement: bool
    has_duplicates: bool
    meta_style: Optional[str]


class SDMarkdownReader:
    markdown_parser = MarkdownIt("commonmark")
    default_meta_style = "backslash"
    bullet_field_pattern = re.compile(
        r"^\s*-\s+\*\*(?P<name>[A-Za-z0-9][A-Za-z0-9 _-]*)\*\*:(?P<value>.*)$"
    )
    plain_field_pattern = re.compile(
        r"^\s*\*\*(?P<name>[A-Za-z0-9][A-Za-z0-9 _-]*)\*\*:(?P<value>.*)$"
    )
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
    def read(input_string: str, file_path: Optional[str]) -> SDocDocument:
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

        document = SDocDocument(
            mid=None,
            title=document_title,
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )
        document.config.markup = SDocMarkup.MARKDOWN

        document.grammar = DocumentGrammar.create_default(
            parent=document,
            enable_mid=True,
        )
        document.ng_has_requirements = False
        document.ng_source_content = input_string

        document_reference = DocumentReference()
        document_reference.set_document(document)
        including_document_reference = DocumentReference()

        detected_meta_style = SDMarkdownReader._parse_document_root(
            root_heading=heading_nodes[0],
            document=document,
            document_reference=document_reference,
            including_document_reference=including_document_reference,
            file_path=file_path,
        )

        tree_meta_style = SDMarkdownReader._create_document_tree(
            heading_nodes=heading_nodes[1:],
            document=document,
            document_reference=document_reference,
            including_document_reference=including_document_reference,
            file_path=file_path,
        )
        if detected_meta_style is None:
            detected_meta_style = tree_meta_style
        document.ng_markdown_meta_style = (
            detected_meta_style or SDMarkdownReader.default_meta_style
        )

        return document

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> SDocDocument:
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

        document = self.read(markdown_content, file_path=file_path)
        document.build_search_index()

        PickleCache.save_to_cache(
            document,
            file_path,
            project_config,
            "markdown",
        )

        return document

    @staticmethod
    def _parse_document_root(
        root_heading: MarkdownHeadingNode,
        document: SDocDocument,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        file_path: Optional[str],
    ) -> Optional[str]:
        root_body_lines = root_heading.body.splitlines(keepends=True)

        (
            root_meta_fields,
            root_body_lines_without_meta,
            root_meta_valid,
            root_meta_style,
        ) = SDMarkdownReader._parse_meta_fields(root_body_lines)

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

            metadata_entries = [
                DocumentCustomMetadataKeyValuePair(
                    key=field_.human_name,
                    value=field_.value,
                )
                for field_ in root_meta_fields
            ]
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

        if not root_meta_valid:
            return None
        return root_meta_style

    @staticmethod
    def _create_document_tree(
        heading_nodes: List[MarkdownHeadingNode],
        document: SDocDocument,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
        file_path: Optional[str],
    ) -> Optional[str]:
        stack: List[Tuple[int, Union[SDocDocument, SDocNode]]] = [(1, document)]
        previous_level = 1
        detected_meta_style: Optional[str] = None

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
                )
                parent_node.section_contents.append(requirement_node)
                stack.append((heading_node.level, requirement_node))

                SDMarkdownReader._memorize_requirement_human_titles(
                    document=document,
                    fields=parsed_node.fields,
                )

                if (
                    detected_meta_style is None
                    and parsed_node.meta_style is not None
                ):
                    detected_meta_style = parsed_node.meta_style

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
                parent_node.section_contents.append(section_node)

                if len(heading_node.body) > 0:
                    text_node = SDMarkdownReader._create_text_node(
                        parent=section_node,
                        statement=heading_node.body,
                        document_reference=document_reference,
                        including_document_reference=including_document_reference,
                    )
                    section_node.section_contents.append(text_node)

                stack.append((heading_node.level, section_node))

            previous_level = heading_node.level

        return detected_meta_style

    @staticmethod
    def _memorize_requirement_human_titles(
        document: SDocDocument, fields: List[ParsedField]
    ) -> None:
        assert document.grammar is not None
        requirement_element = document.grammar.elements_by_type["REQUIREMENT"]
        for field in fields:
            if field.name not in requirement_element.fields_map:
                continue
            grammar_field = requirement_element.fields_map[field.name]
            if grammar_field.human_title is None:
                grammar_field.human_title = field.human_name

    @staticmethod
    def _fallback_document_title(file_path: Optional[str]) -> str:
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
    def _parse_markdown_node(title: str, body: str) -> ParsedMarkdownNode:
        body_lines = body.splitlines(keepends=True)

        (
            meta_fields,
            body_lines_without_meta,
            meta_is_valid,
            meta_style,
        ) = SDMarkdownReader._parse_meta_fields(body_lines)
        content_fields, content_is_valid = (
            SDMarkdownReader._parse_content_fields(body_lines_without_meta)
        )

        parsed_fields = meta_fields + content_fields
        parsed_field_names = list(
            map(lambda field_: field_.name, parsed_fields)
        )
        parsed_field_names.append("TITLE")

        has_duplicates = len(set(parsed_field_names)) != len(parsed_field_names)
        has_mid_or_uid = (
            "MID" in parsed_field_names or "UID" in parsed_field_names
        )
        has_content_field = "STATEMENT" in parsed_field_names
        has_only_known_fields = all(
            map(
                lambda field_name_: (
                    field_name_ in SDMarkdownReader.valid_requirement_fields
                ),
                parsed_field_names,
            )
        )
        has_empty_field_values = any(
            map(lambda field_: len(field_.value) == 0, parsed_fields)
        )

        valid_for_requirement = (
            meta_is_valid
            and content_is_valid
            and has_mid_or_uid
            and has_content_field
            and has_only_known_fields
            and not has_empty_field_values
            and len(title) > 0
        )

        return ParsedMarkdownNode(
            fields=parsed_fields,
            valid_for_requirement=valid_for_requirement,
            has_duplicates=has_duplicates,
            meta_style=meta_style,
        )

    @staticmethod
    def _parse_meta_fields(
        body_lines: List[str],
    ) -> Tuple[List[ParsedField], List[str], bool, Optional[str]]:
        if len(body_lines) == 0 or not SDMarkdownReader._is_empty_line(
            body_lines[0]
        ):
            return [], body_lines, True, None

        next_line_index = 1
        if next_line_index >= len(body_lines):
            return [], body_lines, True, None

        line_text = SDMarkdownReader._line_without_line_ending(
            body_lines[next_line_index]
        )
        meta_style = SDMarkdownReader._detect_meta_style(line_text)
        if meta_style is None:
            return [], body_lines, True, None

        meta_lines: List[str] = []
        while next_line_index < len(body_lines):
            line = body_lines[next_line_index]
            if SDMarkdownReader._is_empty_line(line):
                break
            meta_lines.append(line)
            next_line_index += 1

        if len(meta_lines) == 0:
            return [], body_lines, True, meta_style

        parsed_fields, parse_success = SDMarkdownReader._parse_meta_lines(
            meta_lines,
            meta_style,
        )
        if not parse_success:
            return [], body_lines, False, None

        if next_line_index < len(
            body_lines
        ) and SDMarkdownReader._is_empty_line(body_lines[next_line_index]):
            next_line_index += 1

        return parsed_fields, body_lines[next_line_index:], True, meta_style

    @staticmethod
    def _detect_meta_style(line_text: str) -> Optional[str]:
        if SDMarkdownReader.bullet_field_pattern.match(line_text) is not None:
            return "bullet"

        plain_field_match = SDMarkdownReader.plain_field_pattern.match(
            line_text
        )
        if plain_field_match is None:
            return None

        field_value = SDMarkdownReader._trim_single_space_prefix(
            plain_field_match.group("value")
        )
        if field_value.endswith(" \\"):
            return "backslash"
        if field_value.endswith("  "):
            return "two_spaces"
        return None

    @staticmethod
    def _parse_meta_lines(
        meta_lines: List[str], meta_style: str
    ) -> Tuple[List[ParsedField], bool]:
        parsed_fields: List[ParsedField] = []
        meta_line_count = len(meta_lines)

        for meta_line_index, meta_line in enumerate(meta_lines):
            line_text = SDMarkdownReader._line_without_line_ending(meta_line)

            if meta_style == "bullet":
                match = SDMarkdownReader.bullet_field_pattern.match(line_text)
                if match is None:
                    return [], False
                value = SDMarkdownReader._trim_single_space_prefix(
                    match.group("value")
                )
            else:
                match = SDMarkdownReader.plain_field_pattern.match(line_text)
                if match is None:
                    return [], False
                value = SDMarkdownReader._trim_single_space_prefix(
                    match.group("value")
                )

                if meta_style == "backslash":
                    is_last_line = meta_line_index == meta_line_count - 1
                    if not is_last_line:
                        if not value.endswith(" \\"):
                            return [], False
                        value = value[:-2]
                    elif value.endswith("\\"):
                        return [], False
                elif meta_style == "two_spaces":
                    if not value.endswith("  "):
                        return [], False
                    value = value[:-2]
                else:
                    return [], False

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
    ) -> Tuple[List[ParsedField], bool]:
        parsed_fields: List[ParsedField] = []
        line_index = 0
        line_count = len(body_lines)

        while line_index < line_count:
            line = body_lines[line_index]
            if SDMarkdownReader._is_empty_line(line):
                line_index += 1
                continue

            line_text = SDMarkdownReader._line_without_line_ending(line)
            if (
                SDMarkdownReader.bullet_field_pattern.match(line_text)
                is not None
            ):
                return [], False

            plain_match = SDMarkdownReader.plain_field_pattern.match(line_text)
            if plain_match is not None:
                field_name_upper = plain_match.group("name").upper()
                field_name_human = plain_match.group("name")
                inline_value = SDMarkdownReader._trim_single_space_prefix(
                    plain_match.group("value")
                )
                line_index += 1

                if len(inline_value) > 0:
                    parsed_fields.append(
                        ParsedField(
                            name=field_name_upper,
                            human_name=field_name_human,
                            value=inline_value,
                        )
                    )
                    continue

                if line_index < line_count and SDMarkdownReader._is_empty_line(
                    body_lines[line_index]
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
                    )
                )
                continue

            statement_lines: List[str] = []
            while line_index < line_count:
                candidate_line = body_lines[line_index]
                candidate_line_text = (
                    SDMarkdownReader._line_without_line_ending(candidate_line)
                )
                if SDMarkdownReader.plain_field_pattern.match(
                    candidate_line_text
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
    ) -> SDocNode:
        parsed_meta_fields: List[ParsedField] = []
        parsed_content_fields: List[ParsedField] = []
        parent_relation_uids: List[str] = []
        for field in fields:
            if field.name == "RELATIONS":
                parent_relation_uids.extend(
                    SDMarkdownReader._parse_relations_field(field.value)
                )
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
            requirement_fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=field.name,
                    field_value=field.value,
                    multiline="\n" in field.value,
                )
            )

        requirement = SDocNode(
            parent=parent,
            node_type="REQUIREMENT",
            fields=requirement_fields,
            relations=[],
        )
        if len(parent_relation_uids) > 0:
            requirement.relations = [
                ParentReqReference(
                    parent=requirement,
                    ref_uid=relation_uid,
                    role=None,
                )
                for relation_uid in parent_relation_uids
            ]
        requirement.ng_document_reference = document_reference
        requirement.ng_including_document_reference = (
            including_document_reference
        )
        return requirement

    @staticmethod
    def _create_text_node(
        parent: Union[SDocDocument, SDocNode],
        statement: str,
        document_reference: DocumentReference,
        including_document_reference: DocumentReference,
    ) -> SDocNode:
        text_node = SDocNode(
            parent=parent,
            node_type="TEXT",
            fields=[
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name="STATEMENT",
                    field_value=statement,
                    multiline="\n" in statement,
                )
            ],
            relations=[],
        )
        text_node.ng_document_reference = document_reference
        text_node.ng_including_document_reference = including_document_reference
        return text_node

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
    def _parse_relations_field(field_value: str) -> List[str]:
        return [
            relation_uid.strip()
            for relation_uid in field_value.split(",")
            if len(relation_uid.strip()) > 0
        ]
