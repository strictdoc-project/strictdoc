# mypy: disable-error-code="arg-type,attr-defined,no-untyped-call,no-untyped-def,union-attr,type-arg"
import os.path
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.document_view import (
    DefaultViewElement,
    ViewElement,
)
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import (
    SDocCompositeNode,
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import FreeText, SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    FileEntry,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
    GrammarElementFieldTag,
    RequirementFieldType,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.string import ensure_newline


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class SDWriter:
    def __init__(self, project_config: ProjectConfig):
        self.project_config: ProjectConfig = project_config

    def write_to_file(self, document: SDocDocument):
        document_content, fragments_dict = self.write_with_fragments(document)

        document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)

        with open(
            document_meta.input_doc_full_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

        path_to_output_file_dir = os.path.dirname(
            document_meta.input_doc_full_path
        )
        Path(path_to_output_file_dir).mkdir(parents=True, exist_ok=True)

        for fragment_path_, fragment_content_ in fragments_dict.items():
            path_to_output_fragment = os.path.join(
                path_to_output_file_dir, fragment_path_
            )
            with open(path_to_output_fragment, "w", encoding="utf8") as file_:
                file_.write(fragment_content_)

    def write(self, document: SDocDocument):
        document_output, _ = self.write_with_fragments(document)
        return document_output

    def write_with_fragments(
        self, document: SDocDocument, convert_free_text_to_text: bool = False
    ) -> Tuple[str, Dict[str, str]]:
        fragments_dict: Dict[str, str] = {}

        document_iterator = DocumentCachingIterator(document)
        output = ""

        output += "[DOCUMENT]"
        output += "\n"

        if document.mid_permanent or document.config.enable_mid:
            output += "MID: "
            output += document.reserved_mid
            output += "\n"

        output += "TITLE: "
        output += document.title
        output += "\n"

        document_config: DocumentConfig = document.config
        if document_config:
            uid = document_config.uid
            if uid:
                output += f"UID: {uid}"
                output += "\n"

            version = document_config.version
            if version:
                output += f"VERSION: {version}"
                output += "\n"

            classification = document_config.classification
            if classification is not None:
                output += f"CLASSIFICATION: {classification}"
                output += "\n"

            requirement_prefix = document_config.requirement_prefix
            if requirement_prefix is not None:
                output += f"REQ_PREFIX: {requirement_prefix}"
                output += "\n"

            root = document_config.root
            if root is not None:
                output += "ROOT: "
                output += "True" if root else "False"
                output += "\n"

            enable_mid = document_config.enable_mid
            markup = document_config.markup
            auto_levels_specified = document_config.ng_auto_levels_specified
            layout = document_config.layout
            requirement_style = document_config.requirement_style
            requirement_in_toc = document_config.requirement_in_toc
            default_view = document_config.default_view

            if (
                enable_mid is not None
                or markup is not None
                or auto_levels_specified
                or layout is not None
                or requirement_style is not None
                or requirement_in_toc is not None
                or default_view is not None
            ):
                output += "OPTIONS:"
                output += "\n"

                if enable_mid is not None:
                    output += "  ENABLE_MID: "
                    output += "True" if enable_mid else "False"
                    output += "\n"

                if markup is not None:
                    output += "  MARKUP: "
                    output += markup
                    output += "\n"

                if auto_levels_specified:
                    output += "  AUTO_LEVELS: "
                    output += "On" if document_config.auto_levels else "Off"
                    output += "\n"

                if layout is not None:
                    output += "  LAYOUT: "
                    output += layout
                    output += "\n"

                if requirement_style is not None:
                    output += "  REQUIREMENT_STYLE: "
                    output += requirement_style
                    output += "\n"

                if requirement_in_toc is not None:
                    output += "  REQUIREMENT_IN_TOC: "
                    output += requirement_in_toc
                    output += "\n"

                if default_view is not None:
                    output += "  DEFAULT_VIEW: "
                    output += default_view
                    output += "\n"

        document_view = document.view
        assert len(document_view.views) > 0
        if not isinstance(document_view.views[0], DefaultViewElement):
            views = document_view.views
            output += "VIEWS:"
            output += "\n"
            for view in views:
                output += f"- ID: {view.view_id}\n"
                if view.name is not None:
                    output += f"  NAME: {view.name}\n"
                assert len(view.tags) > 0
                output += "  TAGS:\n"
                for tag in view.tags:
                    output += f"  - OBJECT_TYPE: {tag.object_type}\n"
                    output += "    VISIBLE_FIELDS:\n"
                    for field in tag.visible_fields:
                        output += f"    - NAME: {field.name}\n"
                        placement = field.placement
                        if placement:
                            output += f"      PLACEMENT: {placement}\n"
                hidden_tags = view.hidden_tags
                if hidden_tags is not None and len(hidden_tags) > 0:
                    output += "  HIDDEN_TAGS:\n"
                    for hidden_tag in hidden_tags:
                        output += f"  - {hidden_tag.hidden_tag}\n"

        assert document.grammar is not None
        document_grammar: DocumentGrammar = document.grammar
        if not document_grammar.is_default:
            output += "\n[GRAMMAR]\n"
            if document_grammar.import_from_file is not None:
                output += (
                    f"IMPORT_FROM_FILE: {document_grammar.import_from_file}\n"
                )
            else:
                output += "ELEMENTS:\n"
                for element in document_grammar.elements:
                    output += "- TAG: "
                    output += element.tag
                    output += "\n  FIELDS:\n"
                    for grammar_field in element.fields:
                        output += SDWriter._print_grammar_field_type(
                            grammar_field
                        )

                    relations: List = element.relations
                    if len(relations) > 0:
                        output += "  RELATIONS:\n"

                        for element_relation in relations:
                            output += (
                                f"  - TYPE: {element_relation.relation_type}\n"
                            )
                            if element_relation.relation_role is not None:
                                output += f"    ROLE: {element_relation.relation_role}\n"

        output += "\n"

        output += self._print_node(
            document,
            document,
            document_iterator,
            convert_free_text_to_text=convert_free_text_to_text,
        )
        output = output.rstrip()
        output += "\n"

        return output, fragments_dict

    def _print_node(
        self,
        root_node: Union[SDocDocument, SDocSection, SDocNode, DocumentFromFile],
        document: SDocDocument,
        document_iterator: DocumentCachingIterator,
        convert_free_text_to_text: bool = False,
    ):
        assert isinstance(
            document_iterator, DocumentCachingIterator
        ), document_iterator

        if isinstance(root_node, SDocDocument):
            output = ""

            for node_ in root_node.section_contents:
                if not node_.ng_whitelisted:
                    continue
                output += self._print_node(
                    node_,
                    document,
                    document_iterator=document_iterator,
                    convert_free_text_to_text=convert_free_text_to_text,
                )
            return output

        if isinstance(root_node, DocumentFromFile):
            document_from_file: DocumentFromFile = assert_cast(
                root_node, DocumentFromFile
            )
            return self._print_document_from_file(document_from_file)

        if isinstance(root_node, SDocSection):
            return self._print_section(
                root_node,
                document,
                document_iterator,
                convert_free_text_to_text,
            )

        elif isinstance(root_node, SDocNode):
            output = ""

            # Special case for backward compatibility.
            if (
                not convert_free_text_to_text
                and root_node.node_type == "TEXT"
                and root_node.basic_free_text
            ):
                output += self._print_free_text(root_node)
                output += "\n"
                return output
            if isinstance(root_node, SDocCompositeNode):
                output += "[COMPOSITE_"
                output += root_node.node_type
                output += "]\n"
            else:
                output += "["
                output += root_node.node_type
                output += "]\n"

            output += self._print_requirement_fields(
                section_content=root_node, document=document
            )
            output += "\n"

            if isinstance(root_node, SDocCompositeNode):
                for node_ in root_node.requirements:
                    if not node_.ng_whitelisted:
                        continue
                    output += self._print_node(
                        node_, document, document_iterator=document_iterator
                    )

                output += "[/COMPOSITE_"
                output += root_node.node_type
                output += "]\n"
                output += "\n"

            return output

        raise AssertionError("Must not reach here")

    def _print_document_from_file(self, document_from_file: DocumentFromFile):
        assert isinstance(document_from_file, DocumentFromFile)
        output = ""
        output += "[DOCUMENT_FROM_FILE]"
        output += "\n"

        output += "FILE: "
        output += document_from_file.file
        output += "\n\n"

        return output

    def _print_section(
        self,
        section: SDocSection,
        document: SDocDocument,
        iterator: DocumentCachingIterator,
        convert_free_text_to_text: bool = False,
    ):
        assert isinstance(section, SDocSection)
        output = ""
        output += "[SECTION]"
        output += "\n"

        if section.mid_permanent or document.config.enable_mid:
            output += "MID: "
            output += section.reserved_mid
            output += "\n"

        if section.uid:
            output += "UID: "
            output += section.uid
            output += "\n"

        if section.custom_level:
            output += "LEVEL: "
            output += section.custom_level
            output += "\n"

        output += "TITLE: "
        output += str(section.title)
        output += "\n"
        if section.requirement_prefix is not None:
            output += "REQ_PREFIX: "
            output += section.requirement_prefix
            output += "\n"

        output += "\n"

        for node_ in section.section_contents:
            output += self._print_node(
                node_,
                document,
                document_iterator=iterator,
                convert_free_text_to_text=convert_free_text_to_text,
            )

        output += "[/SECTION]"
        output += "\n\n"

        return output

    def _print_requirement_fields(
        self, section_content: SDocNode, document: SDocDocument
    ):
        output = ""

        current_view: ViewElement = document.view.get_current_view(
            self.project_config.view
        )
        element = document.grammar.elements_by_type[section_content.node_type]

        for element_field in element.fields:
            field_name = element_field.title
            if field_name not in section_content.ordered_fields_lookup:
                if field_name == "MID" and document.config.enable_mid:
                    output += "MID: "
                    output += section_content.reserved_mid
                    output += "\n"
                continue
            if not current_view.includes_field(
                section_content.node_type, field_name
            ):
                continue
            fields = section_content.ordered_fields_lookup[field_name]
            for field in fields:
                field_value = field.get_text_value()
                if field.is_multiline():
                    output += f"{field_name}: >>>"
                    output += "\n"
                    if len(field_value) > 0:
                        if field_value != "\n":
                            output += ensure_newline(field_value)
                    output += "<<<"
                    output += "\n"
                else:
                    if len(field_value) > 0:
                        output += f"{field_name}: "
                        output += field_value
                    else:
                        output += f"{field_name}:"
                    output += "\n"

        output += SDWriter._print_requirement_relations(section_content)

        return output

    @staticmethod
    def _print_closing_tag(closing_tag):
        output = ""
        if closing_tag == TAG.SECTION:
            output += "\n"
            output += "[/SECTION]"
            output += "\n"
        if closing_tag == TAG.COMPOSITE_REQUIREMENT:
            output += "\n"
            output += "[/COMPOSITE_REQUIREMENT]"
            output += "\n"
        return output

    @staticmethod
    def _print_free_text(free_text: Union[FreeText, SDocNode]):
        assert isinstance(free_text, FreeText) or (
            isinstance(free_text, SDocNode) and free_text.basic_free_text
        )
        output = ""
        output += "[FREETEXT]"
        output += "\n"
        output += SDWriter.print_free_text_content(free_text)
        if output[-1] != "\n":
            output += "\n"
        output += "[/FREETEXT]"
        output += "\n"
        return output

    @staticmethod
    def _print_grammar_field_type(grammar_field):
        output = ""
        output += "  - TITLE: "
        output += grammar_field.title
        output += "\n"
        if grammar_field.human_title is not None:
            output += "    HUMAN_TITLE: "
            output += grammar_field.human_title
            output += "\n"
        output += "    TYPE: "

        if isinstance(grammar_field, GrammarElementFieldString):
            output += RequirementFieldType.STRING
        elif isinstance(grammar_field, GrammarElementFieldSingleChoice):
            output += RequirementFieldType.SINGLE_CHOICE
            output += "("
            output += ", ".join(grammar_field.options)
            output += ")"
        elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
            output += RequirementFieldType.MULTIPLE_CHOICE
            output += "("
            output += ", ".join(grammar_field.options)
            output += ")"
        elif isinstance(grammar_field, GrammarElementFieldTag):
            output += RequirementFieldType.TAG
        else:
            raise NotImplementedError from None

        output += "\n"
        output += "    REQUIRED: "
        output += "True" if grammar_field.required else "False"
        output += "\n"
        return output

    @staticmethod
    def _print_file_entry(row_separator, file_entry: FileEntry) -> str:
        output = ""
        if row_separator:
            output += "- "
        else:
            output += "  "
        if file_entry.g_file_format:
            output += "FORMAT: "
            output += file_entry.g_file_format
            output += "\n  "
        output += "VALUE: "
        output += file_entry.g_file_path
        output += "\n"

        return output

    @staticmethod
    def print_free_text_content(free_text: Union[FreeText, SDocNode]):
        assert isinstance(free_text, FreeText) or (
            isinstance(free_text, SDocNode) and free_text.basic_free_text
        )

        object_with_parts: Union[FreeText, SDocNodeField]
        if isinstance(free_text, SDocNode):
            object_with_parts = free_text.get_content_field()
        else:
            object_with_parts = free_text

        output = ""

        for _, part in enumerate(object_with_parts.parts):
            if isinstance(part, str):
                output += part
            elif isinstance(part, InlineLink):
                output += "[LINK: "
                output += part.link
                output += "]"
            elif isinstance(part, Anchor):
                output += "[ANCHOR: "
                output += part.value
                if part.has_title:
                    output += ", "
                    output += part.title
                output += "]"
                output += "\n"
            else:
                raise NotImplementedError(part)
        return output

    @classmethod
    def _print_requirement_relations(cls, requirement: SDocNode):
        assert isinstance(requirement, SDocNode)

        if len(requirement.relations) == 0:
            return ""

        output = "RELATIONS:\n"

        reference: Reference
        for reference in requirement.relations:
            output += "- TYPE: "
            output += reference.ref_type
            output += "\n"

            if isinstance(reference, FileReference):
                ref: FileReference = reference
                file_format = ref.get_file_format()
                if file_format:
                    output += "  FORMAT: "
                    output += file_format
                    output += "\n"
                output += "  VALUE: "
                output += ref.get_posix_path()
                output += "\n"
                if ref.g_file_entry.line_range is not None:
                    output += "  LINE_RANGE: "
                    output += str(ref.g_file_entry.line_range[0])
                    output += ", "
                    output += str(ref.g_file_entry.line_range[1])
                    output += "\n"

            elif isinstance(reference, ParentReqReference):
                parent_reference: ParentReqReference = reference
                output += "  VALUE: "
                output += parent_reference.ref_uid
                output += "\n"
                if parent_reference.role is not None:
                    output += "  ROLE: "
                    output += parent_reference.role
                    output += "\n"
            elif isinstance(reference, ChildReqReference):
                child_reference: ChildReqReference = reference
                output += "  VALUE: "
                output += child_reference.ref_uid
                output += "\n"
                if child_reference.role is not None:
                    output += "  ROLE: "
                    output += child_reference.role
                    output += "\n"
            else:
                raise AssertionError("Must not reach here.")
        return output
