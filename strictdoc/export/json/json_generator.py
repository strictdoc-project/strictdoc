import json
import os.path
from enum import Enum
from typing import Any, Dict, List, Optional

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import CompositeRequirement, SDocNode
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldReference,
    RequirementFieldType,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class JSONKey:
    NODES = "NODES"
    GRAMMAR = "GRAMMAR"

    OPTIONS = "_OPTIONS"


class JSONGenerator:
    def export_tree(
        self, traceability_index: TraceabilityIndex, output_json_root: str
    ):
        project_tree_dict = {
            "_COMMENT": (
                "Fields with _ are metadata. "
                "Fields without _ are the actual document/section/requirement/other content."
            ),
            "DOCUMENTS": [],
        }
        for document_ in traceability_index.document_tree.document_list:
            document_json_dict = self._write_document(document_)

            project_tree_dict["DOCUMENTS"].append(document_json_dict)

        path_output_json_file = os.path.join(output_json_root, "index.json")
        project_tree_json = json.dumps(project_tree_dict, indent=4)
        with open(path_output_json_file, "w") as output_json_file:
            output_json_file.write(project_tree_json)

    @classmethod
    def _write_document(cls, document: SDocDocument) -> Dict:
        document_iterator = DocumentCachingIterator(document)
        document_dict: Dict["str", Any] = {
            "TITLE": document.title,
            "REQ_PREFIX": None,
            JSONKey.GRAMMAR: {"ELEMENTS": []},
            JSONKey.OPTIONS: {},
            JSONKey.NODES: [],
        }

        if document.mid_permanent or document.config.enable_mid:
            document_dict["MID"] = document.reserved_mid

        document_config: DocumentConfig = document.config
        if document_config:
            uid = document_config.uid
            if uid is not None:
                document_dict["UID"] = uid

            version = document_config.version
            if version:
                document_dict["VERSION"] = version

            classification = document_config.classification
            if classification is not None:
                document_dict["CLASSIFICATION"] = classification

            requirement_prefix = document_config.requirement_prefix
            if requirement_prefix is not None:
                document_dict["REQ_PREFIX"] = requirement_prefix

            root = document_config.root
            if root is not None:
                document_dict["ROOT"] = "true" if root else "false"

            enable_mid = document_config.enable_mid
            markup = document_config.markup
            auto_levels_specified = document_config.ng_auto_levels_specified
            requirement_style = document_config.requirement_style
            requirement_in_toc = document_config.requirement_in_toc
            default_view = document_config.default_view

            if (
                enable_mid is not None
                or markup is not None
                or auto_levels_specified
                or requirement_style is not None
                or requirement_in_toc is not None
                or default_view is not None
            ):
                if enable_mid is not None:
                    document_dict[JSONKey.OPTIONS]["ENABLE_MID"] = (
                        True if enable_mid else False
                    )

                if markup is not None:
                    document_dict[JSONKey.OPTIONS]["MARKUP"] = markup

                if auto_levels_specified:
                    document_dict[JSONKey.OPTIONS]["AUTO_LEVELS"] = (
                        True if document_config.auto_levels else False
                    )

                if requirement_style is not None:
                    document_dict[JSONKey.OPTIONS]["REQUIREMENT_STYLE"] = (
                        requirement_style
                    )

                if requirement_in_toc is not None:
                    document_dict[JSONKey.OPTIONS]["REQUIREMENT_IN_TOC"] = (
                        requirement_in_toc
                    )

                if default_view is not None:
                    document_dict[JSONKey.OPTIONS]["DEFAULT_VIEW"] = (
                        default_view
                    )

        """
        Grammar.
        """
        assert document.grammar is not None
        document_grammar: DocumentGrammar = document.grammar

        for element_ in document_grammar.elements:
            element_dict = {
                "NODE_TYPE": element_.tag,
                "FIELDS": [],
                "RELATIONS": [],
            }

            refs_field: Optional[GrammarElementFieldReference] = None
            for grammar_field in element_.fields:
                if grammar_field.title == "REFS":
                    refs_field = assert_cast(
                        grammar_field, GrammarElementFieldReference
                    )
                    continue

                element_dict["FIELDS"].append(
                    cls._write_grammar_field_type(grammar_field)
                )

            relations: List = element_.relations
            assert len(relations) > 0, relations

            # For backward compatibility, we print RELATIONS from REFS
            # grammar field if it exists.
            if not document_grammar.is_default and refs_field is not None:
                relations = refs_field.convert_to_relations()

            assert len(relations) > 0, relations
            for element_relation_ in relations:
                relation_dict = {
                    "TYPE": element_relation_.relation_type,
                }
                if element_relation_.relation_role is not None:
                    relation_dict["ROLE"] = element_relation_.relation_role
                element_dict["RELATIONS"].append(relation_dict)

            document_dict[JSONKey.GRAMMAR]["ELEMENTS"].append(element_dict)

        for free_text in document.free_texts:
            document_dict["FREETEXT"] = cls._write_free_text_content(free_text)

        for content_node in document_iterator.all_content():
            if not content_node.ng_whitelisted:
                continue

            if isinstance(content_node, SDocSection):
                section_dict = cls._write_section(content_node, document)
                document_dict[JSONKey.NODES].append(section_dict)

            elif isinstance(content_node, SDocNode):
                if isinstance(content_node, CompositeRequirement):
                    continue

                node_dict = cls._write_requirement(
                    node=content_node, document=document
                )
                document_dict[JSONKey.NODES].append(node_dict)

        return document_dict

    @classmethod
    def _write_section(
        cls, section: SDocSection, document: SDocDocument
    ) -> Dict:
        assert isinstance(section, SDocSection)
        node_dict: Dict[str, Any] = {
            "_TOC": section.context.title_number_string,
            "TYPE": "SECTION",
            "TITLE": str(section.title),
            JSONKey.NODES: [],
        }

        if section.mid_permanent or document.config.enable_mid:
            node_dict["MID"] = section.reserved_mid

        if section.uid:
            node_dict["UID"] = section.uid

        if section.custom_level:
            node_dict["LEVEL"] = section.custom_level

        if section.requirement_prefix is not None:
            node_dict["REQ_PREFIX"] = section.requirement_prefix

        for free_text in section.free_texts:
            node_dict["FREETEXT"] = cls._write_free_text_content(free_text)

        for node_ in section.section_contents:
            if not node_.ng_whitelisted:
                continue

            if isinstance(node_, SDocSection):
                section_dict = cls._write_section(node_, document)
                node_dict[JSONKey.NODES].append(section_dict)

            elif isinstance(node_, SDocNode):
                if isinstance(node_, CompositeRequirement):
                    continue

                sub_node_dict = cls._write_requirement(
                    node=node_, document=document
                )
                node_dict[JSONKey.NODES].append(sub_node_dict)

        return node_dict

    @classmethod
    def _write_requirement(cls, node: SDocNode, document: SDocDocument) -> Dict:
        node_dict = {
            "_TOC": node.context.title_number_string,
            "TYPE": node.requirement_type,
        }

        if node.mid_permanent or document.config.enable_mid:
            node_dict["MID"] = node.reserved_mid

        element = document.grammar.elements_by_type[node.requirement_type]

        refs_already_printed = False
        for element_field in element.fields:
            field_name = element_field.title
            if field_name not in node.ordered_fields_lookup:
                continue
            fields = node.ordered_fields_lookup[field_name]
            for field in fields:
                if field.field_value_multiline is not None:
                    node_dict[field_name] = field.field_value_multiline
                elif field.field_value_references:
                    node_dict["RELATIONS"] = cls._write_requirement_relations(
                        field
                    )
                    refs_already_printed = True
                elif field.field_value is not None:
                    node_dict[field_name] = field.field_value
                else:
                    raise NotImplementedError

        if not refs_already_printed and "REFS" in node.ordered_fields_lookup:
            requirement_refs_fields = node.ordered_fields_lookup["REFS"]
            node_dict["RELATIONS"] = cls._write_requirement_relations(
                requirement_refs_fields[0]
            )

        return node_dict

    @classmethod
    def _write_grammar_field_type(cls, grammar_field) -> Dict:
        grammar_field_dict = {
            "TITLE": grammar_field.title,
            "REQUIRED": True if grammar_field.required else False,
            # FIXME: Support more grammar types.
            "TYPE": RequirementFieldType.STRING,
        }
        return grammar_field_dict

    @classmethod
    def _write_free_text_content(cls, free_text) -> str:
        assert isinstance(free_text, FreeText)
        output = ""

        for _, part in enumerate(free_text.parts):
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

    @staticmethod
    def _write_requirement_relations(field) -> List:
        relations_list = []

        reference: Reference
        for reference in field.field_value_references:
            relation_dict = {
                "TYPE": reference.ref_type,
            }

            if isinstance(reference, FileReference):
                ref: FileReference = reference
                file_format = ref.get_file_format()
                if file_format is not None:
                    relation_dict["FORMAT"] = file_format

                relation_dict["VALUE"] = ref.get_posix_path()

                if ref.g_file_entry.line_range is not None:
                    relation_dict["LINE_RANGE"] = (
                        str(ref.g_file_entry.line_range[0])
                        + ", "
                        + str(ref.g_file_entry.line_range[1])
                    )

            elif isinstance(reference, ParentReqReference):
                parent_reference: ParentReqReference = reference
                relation_dict["VALUE"] = parent_reference.ref_uid
                if parent_reference.role is not None:
                    relation_dict["ROLE"] = parent_reference.role

            elif isinstance(reference, ChildReqReference):
                child_reference: ChildReqReference = reference
                relation_dict["VALUE"] = child_reference.ref_uid

                if child_reference.role is not None:
                    relation_dict["ROLE"] = child_reference.role
            else:
                raise AssertionError("Must not reach here.")

            relations_list.append(relation_dict)

        return relations_list
