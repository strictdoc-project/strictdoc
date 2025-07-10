import json
import os.path
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementField,
    RequirementFieldType,
)
from strictdoc.backend.sdoc.models.model import SDocElementIF
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
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
        self,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        output_json_root: str,
    ) -> None:
        project_tree_dict: Dict[str, Any] = {
            "_COMMENT": (
                "Fields with _ are metadata. "
                "Fields without _ are the actual document/section/requirement/other content."
            ),
            "DOCUMENTS": [],
        }
        document_tree: DocumentTree = assert_cast(
            traceability_index.document_tree, DocumentTree
        )
        for document_ in document_tree.document_list:
            if not project_config.export_included_documents:
                if document_.document_is_included():
                    continue

            document_json_dict = self._write_document(document_)

            project_tree_dict["DOCUMENTS"].append(document_json_dict)

        path_output_json_file = os.path.join(output_json_root, "index.json")
        project_tree_json = json.dumps(project_tree_dict, indent=4)
        with open(path_output_json_file, "w") as output_json_file:
            output_json_file.write(project_tree_json + "\n")

    @classmethod
    def _write_document(cls, document: SDocDocument) -> Dict[str, Any]:
        document_dict: Dict[str, Any] = {
            "_NODE_TYPE": "DOCUMENT",
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
                document_dict["PREFIX"] = requirement_prefix

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
                document_dict[JSONKey.OPTIONS] = {}

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
                    document_dict[JSONKey.OPTIONS]["VIEW_STYLE"] = (
                        requirement_style
                    )

                if requirement_in_toc is not None:
                    document_dict[JSONKey.OPTIONS]["NODE_IN_TOC"] = (
                        requirement_in_toc
                    )

                if default_view is not None:
                    document_dict[JSONKey.OPTIONS]["DEFAULT_VIEW"] = (
                        default_view
                    )

        document_dict["TITLE"] = document.title

        #
        # Grammar.
        #

        document_dict[JSONKey.GRAMMAR] = {"ELEMENTS": []}

        assert document.grammar is not None
        document_grammar: DocumentGrammar = document.grammar

        for element_ in document_grammar.elements:
            element_dict: Dict[str, Any] = {
                "NODE_TYPE": element_.tag,
                "FIELDS": [],
                "RELATIONS": [],
            }

            for grammar_field in element_.fields:
                element_dict["FIELDS"].append(
                    cls._write_grammar_field_type(grammar_field)
                )

            if len(element_.relations) > 0:
                for element_relation_ in element_.relations:
                    relation_dict: Dict[str, str] = {
                        "TYPE": element_relation_.relation_type,
                    }
                    if element_relation_.relation_role is not None:
                        relation_dict["ROLE"] = element_relation_.relation_role
                    element_dict["RELATIONS"].append(relation_dict)

            document_dict[JSONKey.GRAMMAR]["ELEMENTS"].append(element_dict)

        node_dict = JSONGenerator._write_node(document, document, ())
        document_dict[JSONKey.NODES] = node_dict[JSONKey.NODES]

        return document_dict

    @classmethod
    def _write_node(
        cls,
        node: SDocElementIF,
        document: SDocDocument,
        level_stack: Tuple[int, ...],
    ) -> Dict[str, Any]:
        if isinstance(node, SDocSection):
            section_dict: Dict[str, Any] = cls._write_section(
                node, document, level_stack
            )
            return section_dict

        elif isinstance(node, SDocNode):
            subnode_dict = cls._write_requirement(
                node=node,
                document=document,
                level_stack=level_stack,
            )
            return subnode_dict

        elif isinstance(node, SDocDocument):
            node_dict: Dict[str, Any] = cls._write_included_document(
                node,
                level_stack=level_stack,
            )

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None:
                    current_number += 1
                document_subnode_dict: Dict[str, Any] = cls._write_node(
                    subnode_, document, level_stack + (current_number,)
                )
                node_dict[JSONKey.NODES].append(document_subnode_dict)

            return node_dict

        elif isinstance(node, DocumentFromFile):
            resolved_document = assert_cast(
                node.resolved_document, SDocDocument
            )
            subnode_dict = cls._write_node(
                resolved_document, document, level_stack
            )
            return subnode_dict

        else:
            raise NotImplementedError

    @classmethod
    def _write_included_document(
        cls,
        node: SDocDocument,
        level_stack: Tuple[int, ...],
    ) -> Dict[str, Any]:
        node_dict: Dict[str, Any] = {
            "_TOC": cls._get_level_string(node, level_stack=level_stack),
            "_NODE_TYPE": "SECTION",
            "TITLE": node.reserved_title,
            JSONKey.NODES: [],
        }
        return node_dict

    @classmethod
    def _write_section(
        cls,
        section: SDocSection,
        document: SDocDocument,
        level_stack: Tuple[int, ...],
    ) -> Dict[str, Any]:
        assert isinstance(section, (SDocSection, SDocDocument))
        node_dict: Dict[str, Any] = {
            "_TOC": cls._get_level_string(section, level_stack),
            "_NODE_TYPE": "SECTION",
        }

        if section.mid_permanent or document.config.enable_mid:
            node_dict["MID"] = section.reserved_mid

        if section.reserved_uid is not None:
            node_dict["UID"] = section.uid

        if (
            isinstance(section, SDocSection)
            and section.custom_level is not None
        ):
            node_dict["LEVEL"] = section.custom_level

        if section.requirement_prefix is not None:
            node_dict["PREFIX"] = section.requirement_prefix

        node_dict["TITLE"] = str(section.title)
        node_dict[JSONKey.NODES] = []

        current_number = 0
        for subnode_ in section.section_contents:
            if subnode_.ng_resolved_custom_level is None:
                current_number += 1

            section_subnode_dict: Dict[str, Any] = cls._write_node(
                subnode_, document, level_stack + (current_number,)
            )
            node_dict[JSONKey.NODES].append(section_subnode_dict)

        return node_dict

    @classmethod
    def _write_requirement(
        cls,
        node: SDocNode,
        document: SDocDocument,
        level_stack: Tuple[int, ...],
    ) -> Dict[str, Any]:
        node_dict: Dict[str, Any] = {
            "_TOC": cls._get_level_string(node, level_stack),
            "_NODE_TYPE": node.node_type,
        }

        if node.mid_permanent or document.config.enable_mid:
            node_dict["MID"] = node.reserved_mid

        document_grammar = assert_cast(document.grammar, DocumentGrammar)
        element = document_grammar.elements_by_type[node.node_type]

        for element_field in element.fields:
            field_name = element_field.title
            if field_name not in node.ordered_fields_lookup:
                continue
            fields = node.ordered_fields_lookup[field_name]
            for field in fields:
                node_dict[field_name] = field.get_text_value()

        if len(node.relations) > 0:
            node_dict["RELATIONS"] = cls._write_requirement_relations(node)

        if node.is_composite:
            node_dict[JSONKey.NODES] = []

            current_number = 0
            for subnode_ in node.section_contents:
                if subnode_.ng_resolved_custom_level is None:
                    current_number += 1

                section_subnode_dict: Dict[str, Any] = cls._write_node(
                    subnode_, document, level_stack + (current_number,)
                )
                node_dict[JSONKey.NODES].append(section_subnode_dict)

        return node_dict

    @classmethod
    def _write_grammar_field_type(
        cls, grammar_field: GrammarElementField
    ) -> Dict[str, str]:
        grammar_field_dict = {
            "TITLE": grammar_field.title,
            "REQUIRED": "True" if grammar_field.required else "False",
            # FIXME: Support more grammar types.
            "TYPE": RequirementFieldType.STRING,
        }
        return grammar_field_dict

    @staticmethod
    def _write_requirement_relations(node: SDocNode) -> List[Dict[str, str]]:
        relations_list = []

        reference: Reference
        for reference in node.relations:
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
                raise AssertionError("Must not reach here.")  # pragma: no cover

            relations_list.append(relation_dict)

        return relations_list

    @classmethod
    def _get_level_string(
        cls,
        node_: Union[SDocNode, SDocSection, SDocDocument],
        level_stack: Tuple[int, ...],
    ) -> str:
        return (
            ""
            if node_.ng_resolved_custom_level == "None"
            else (
                node_.ng_resolved_custom_level
                if node_.ng_resolved_custom_level is not None
                else ".".join(map(str, level_stack))
            )
        )
