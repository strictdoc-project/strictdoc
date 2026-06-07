import re
from typing import Dict, List, NoReturn, Optional, Set

from strictdoc.backend.markdown.reader import (
    MarkdownHeadingNode,
    SDMarkdownReader,
)
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
    GrammarElementFieldType,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
    GrammarElementRelationType,
)
from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import strip_bom


class MarkdownGrammarReader:
    @staticmethod
    def read(
        input_string: str, file_path: Optional[str] = None
    ) -> DocumentGrammar:
        input_string = strip_bom(input_string)
        markdown_tokens = SDMarkdownReader.markdown_parser.parse(input_string)
        heading_nodes = SDMarkdownReader._extract_heading_nodes(
            markdown_tokens, input_string
        )

        if len(heading_nodes) == 0 or heading_nodes[0].level != 1:
            raise StrictDocSemanticError(
                title=(
                    "Markdown grammar parsing error: the grammar file must "
                    "start with an H1 heading."
                ),
                hint=None,
                example="# StrictDoc Markdown Grammar",
                line=1,
                col=1,
                filename=file_path,
            )

        SDMarkdownReader._validate_no_content_before_h1(
            input_string=input_string,
            first_heading=heading_nodes[0],
            file_path=file_path,
        )

        elements: List[GrammarElement] = []
        element_names: Set[str] = set()
        current_element: Optional[GrammarElement] = None
        current_relation_section: Optional[GrammarElement] = None

        for heading_node in heading_nodes[1:]:
            if heading_node.level == 2:
                tag = MarkdownGrammarReader._parse_named_heading(
                    heading_node, "Element", file_path
                )
                if tag in element_names:
                    MarkdownGrammarReader._raise_error(
                        f"duplicate grammar element: {tag}.",
                        heading_node,
                        file_path,
                    )
                properties = MarkdownGrammarReader._parse_properties(
                    heading_node.body, file_path, heading_node
                )
                unknown_properties = set(properties.keys()) - {
                    "COMPOSITE",
                    "PREFIX",
                    "VIEW STYLE",
                }
                if len(unknown_properties) > 0:
                    MarkdownGrammarReader._raise_error(
                        "unknown element propertie(s): "
                        f"{', '.join(sorted(unknown_properties))}.",
                        heading_node,
                        file_path,
                    )
                property_is_composite = properties.get("COMPOSITE", "")
                if property_is_composite not in ("", "True", "False"):
                    MarkdownGrammarReader._raise_error(
                        "Composite must be True or False.",
                        heading_node,
                        file_path,
                    )
                try:
                    current_element = GrammarElement(
                        parent=None,
                        tag=tag,
                        property_is_composite=property_is_composite,
                        property_prefix=properties.get("PREFIX", ""),
                        property_view_style=properties.get("VIEW STYLE", ""),
                        fields=[],
                        relations=[],
                    )
                except AssertionError as exc:
                    raise StrictDocSemanticError(
                        title=(
                            "Markdown grammar parsing error: invalid element "
                            f"properties for '{tag}'."
                        ),
                        hint=None,
                        example=None,
                        line=heading_node.line_start,
                        col=1,
                        filename=file_path,
                    ) from exc
                elements.append(current_element)
                element_names.add(tag)
                current_relation_section = None
                continue

            if heading_node.level == 3:
                if current_element is None:
                    MarkdownGrammarReader._raise_error(
                        "field or relations section without an element.",
                        heading_node,
                        file_path,
                    )
                if heading_node.title == "Relations":
                    current_relation_section = current_element
                    continue
                current_relation_section = None
                field_name = MarkdownGrammarReader._parse_named_heading(
                    heading_node, "Field", file_path
                )
                if any(
                    field_.title == field_name
                    for field_ in current_element.fields
                ):
                    MarkdownGrammarReader._raise_error(
                        f"duplicate field in element {current_element.tag}: "
                        f"{field_name}.",
                        heading_node,
                        file_path,
                    )
                field = MarkdownGrammarReader._parse_field(
                    field_name,
                    heading_node.body,
                    heading_node,
                    file_path,
                )
                current_element.fields.append(field)
                continue

            if heading_node.level == 4:
                if current_relation_section is None:
                    MarkdownGrammarReader._raise_error(
                        "relation declaration without a Relations section.",
                        heading_node,
                        file_path,
                    )
                relation_type = MarkdownGrammarReader._parse_named_heading(
                    heading_node, "Relation", file_path
                )
                relation = MarkdownGrammarReader._parse_relation(
                    relation_type,
                    heading_node.body,
                    current_relation_section,
                    heading_node,
                    file_path,
                )
                current_relation_section.relations.append(relation)
                continue

            MarkdownGrammarReader._raise_error(
                f"unexpected heading level H{heading_node.level}.",
                heading_node,
                file_path,
            )

        if len(elements) == 0:
            raise StrictDocSemanticError(
                title=(
                    "Markdown grammar parsing error: at least one Element "
                    "declaration is required."
                ),
                hint=None,
                example="## Element: REQUIREMENT",
                line=heading_nodes[0].line_start,
                col=1,
                filename=file_path,
            )

        normalized_elements = [
            MarkdownGrammarReader._normalize_element(element_)
            for element_ in elements
        ]
        grammar = DocumentGrammar(parent=None, elements=normalized_elements)
        grammar.is_default = False
        return grammar

    def read_from_file(
        self, file_path: str, project_config: ProjectConfig
    ) -> DocumentGrammar:
        unpickled_content = PickleCache.read_from_cache(
            file_path,
            project_config,
            "markdown_grammar",
        )
        if unpickled_content is not None:
            return assert_cast(unpickled_content, DocumentGrammar)

        with open(file_path, encoding="utf-8-sig", newline="") as file:
            grammar_content = file.read()

        grammar = self.read(grammar_content, file_path=file_path)
        PickleCache.save_to_cache(
            grammar,
            file_path,
            project_config,
            "markdown_grammar",
        )
        return grammar

    @staticmethod
    def _parse_field(
        field_name: str,
        body: str,
        heading_node: MarkdownHeadingNode,
        file_path: Optional[str],
    ) -> GrammarElementFieldType:
        properties = MarkdownGrammarReader._parse_properties(
            body, file_path, heading_node
        )
        unknown_properties = set(properties.keys()) - {
            "TYPE",
            "REQUIRED",
            "HUMAN TITLE",
        }
        if len(unknown_properties) > 0:
            MarkdownGrammarReader._raise_error(
                "unknown field propertie(s): "
                f"{', '.join(sorted(unknown_properties))}.",
                heading_node,
                file_path,
            )
        field_type = properties.get("TYPE")
        if field_type is None:
            MarkdownGrammarReader._raise_error(
                f"field {field_name} has no Type.",
                heading_node,
                file_path,
            )
        required = properties.get("REQUIRED")
        if required not in ("True", "False"):
            MarkdownGrammarReader._raise_error(
                f"field {field_name} Required must be True or False.",
                heading_node,
                file_path,
            )
        human_title = properties.get("HUMAN TITLE")

        if field_type == "String":
            return GrammarElementFieldString(
                parent=None,
                title=field_name,
                human_title=human_title,
                required=required,
            )
        if field_type == "Tag":
            return GrammarElementFieldTag(
                parent=None,
                title=field_name,
                human_title=human_title,
                required=required,
            )

        choice_match = re.match(
            r"^(SingleChoice|MultipleChoice)\((?P<options>.*)\)$",
            field_type,
        )
        if choice_match is not None:
            options = [
                option_.strip()
                for option_ in choice_match.group("options").split(",")
                if len(option_.strip()) > 0
            ]
            if len(options) == 0:
                MarkdownGrammarReader._raise_error(
                    f"field {field_name} must declare at least one option.",
                    heading_node,
                    file_path,
                )
            if choice_match.group(1) == "SingleChoice":
                return GrammarElementFieldSingleChoice(
                    parent=None,
                    title=field_name,
                    human_title=human_title,
                    options=options,
                    required=required,
                )
            return GrammarElementFieldMultipleChoice(
                parent=None,
                title=field_name,
                human_title=human_title,
                options=options,
                required=required,
            )

        MarkdownGrammarReader._raise_error(
            f"unknown field Type for {field_name}: {field_type}.",
            heading_node,
            file_path,
        )

    @staticmethod
    def _parse_relation(
        relation_type: str,
        body: str,
        parent: GrammarElement,
        heading_node: MarkdownHeadingNode,
        file_path: Optional[str],
    ) -> GrammarElementRelationType:
        properties = MarkdownGrammarReader._parse_properties(
            body, file_path, heading_node
        )
        unknown_properties = set(properties.keys()) - {"ROLE"}
        if len(unknown_properties) > 0:
            MarkdownGrammarReader._raise_error(
                "unknown relation propertie(s): "
                f"{', '.join(sorted(unknown_properties))}.",
                heading_node,
                file_path,
            )
        role = properties.get("ROLE")
        if relation_type == "Parent":
            return GrammarElementRelationParent(parent, relation_type, role)
        if relation_type == "Child":
            return GrammarElementRelationChild(parent, relation_type, role)
        if relation_type == "File":
            return GrammarElementRelationFile(parent, relation_type, role)
        MarkdownGrammarReader._raise_error(
            f"unknown relation type: {relation_type}.",
            heading_node,
            file_path,
        )

    @staticmethod
    def _parse_properties(
        body: str,
        file_path: Optional[str],
        heading_node: MarkdownHeadingNode,
    ) -> Dict[str, str]:
        properties: Dict[str, str] = {}
        for line in body.splitlines():
            if len(line.strip()) == 0:
                continue
            match = SDMarkdownReader.plain_field_pattern.match(line)
            if match is None:
                MarkdownGrammarReader._raise_error(
                    f"invalid property line: {line}.",
                    heading_node,
                    file_path,
                )
            key = match.group("name").strip().upper()
            value = SDMarkdownReader._trim_single_space_prefix(
                match.group("value")
            ).strip()
            if value.startswith("`") and value.endswith("`") and len(value) > 1:
                value = value[1:-1]
            if key in properties:
                MarkdownGrammarReader._raise_error(
                    f"duplicate property: {key}.",
                    heading_node,
                    file_path,
                )
            properties[key] = value
        return properties

    @staticmethod
    def _normalize_element(element: GrammarElement) -> GrammarElement:
        property_is_composite = (
            ""
            if element.property_is_composite is None
            else ("True" if element.property_is_composite else "False")
        )
        normalized_element = GrammarElement(
            parent=None,
            tag=element.tag,
            property_is_composite=property_is_composite,
            property_prefix=element.property_prefix or "",
            property_view_style=element.property_view_style or "",
            fields=element.fields,
            relations=element.relations,
        )
        for field_ in normalized_element.fields:
            field_.parent = normalized_element
        for relation_ in normalized_element.relations:
            relation_.parent = normalized_element
        return normalized_element

    @staticmethod
    def _parse_named_heading(
        heading_node: MarkdownHeadingNode,
        expected_name: str,
        file_path: Optional[str],
    ) -> str:
        prefix = f"{expected_name}: "
        if not heading_node.title.startswith(prefix):
            MarkdownGrammarReader._raise_error(
                f"expected heading '{expected_name}: <name>'.",
                heading_node,
                file_path,
            )
        name = heading_node.title[len(prefix) :].strip()
        if len(name) == 0:
            MarkdownGrammarReader._raise_error(
                f"{expected_name} name must not be empty.",
                heading_node,
                file_path,
            )
        return name

    @staticmethod
    def _raise_error(
        message: str,
        heading_node: MarkdownHeadingNode,
        file_path: Optional[str],
    ) -> NoReturn:
        raise StrictDocSemanticError(
            title=f"Markdown grammar parsing error: {message}",
            hint=None,
            example=None,
            line=heading_node.line_start,
            col=1,
            filename=file_path,
        )
