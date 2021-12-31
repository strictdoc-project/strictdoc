import uuid
from enum import Enum
from typing import Dict, List

from reqif.models.reqif_core_content import ReqIFCoreContent
from reqif.models.reqif_data_type import (
    ReqIFDataTypeDefinitionString,
    ReqIFDataTypeDefinitionEnumeration,
    ReqIFEnumValue,
)
from reqif.models.reqif_namespace_info import ReqIFNamespaceInfo
from reqif.models.reqif_req_if_content import ReqIFReqIFContent
from reqif.models.reqif_spec_hierarchy import ReqIFSpecHierarchy
from reqif.models.reqif_spec_object import ReqIFSpecObject, SpecObjectAttribute
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.object_lookup import ReqIFObjectLookup
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_grammar import DocumentGrammar
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.type_system import (
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
)
from strictdoc.backend.dsl.writer import SDWriter
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.imports.reqif.stage2.native.mapping import ReqIFSectionField


class StrictDocReqIFTypes(Enum):
    SINGLE_LINE_STRING = "SDOC_DATATYPE_SINGLE_LINE_STRING"
    MULTI_LINE_STRING = "SDOC_DATATYPE_MULTI_LINE_STRING"
    SINGLE_CHOICE = "SDOC_DATATYPE_SINGLE_CHOICE"
    MULTI_CHOICE = "SDOC_DATATYPE_MULTI_CHOICE"


def generate_unique_identifier(element_type: str) -> str:
    return f"{element_type}-{uuid.uuid4()}"


class SDocToReqIFObjectConverter:
    @classmethod
    def convert_document_tree(
        cls,
        document_tree: DocumentTree,
    ):
        # TODO
        namespace = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
        configuration = "https://github.com/strictdoc-project/strictdoc"

        spec_types: List = []
        spec_objects: [ReqIFSpecObject] = []
        specifications: [ReqIFSpecification] = []
        data_types = []
        data_types_lookup = {}
        document: Document
        for document in document_tree.document_list:
            for element in document.grammar.elements:
                for field in element.fields:
                    if isinstance(field, GrammarElementFieldString):
                        if (
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            in data_types_lookup
                        ):
                            continue
                        data_type = ReqIFDataTypeDefinitionString(
                            is_self_closed=True,
                            description=None,
                            identifier=(
                                StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            ),
                            last_change=None,
                            long_name=None,
                            max_length=None,
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ] = data_type.identifier
                    elif isinstance(field, GrammarElementFieldSingleChoice):
                        values = []
                        values_map = {}
                        for option in field.options:
                            value = ReqIFEnumValue(
                                description=None,
                                identifier=generate_unique_identifier(
                                    "ENUM-VALUE"
                                ),
                                last_change=None,
                                key=option,
                                other_content=None,
                            )
                            values.append(value)
                            values_map[option] = option

                        data_type = ReqIFDataTypeDefinitionEnumeration(
                            is_self_closed=False,
                            description=None,
                            identifier=(
                                generate_unique_identifier(
                                    StrictDocReqIFTypes.SINGLE_CHOICE.value
                                )
                            ),
                            last_change=None,
                            long_name=None,
                            multi_valued=False,
                            values=values,
                            values_map={},
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.SINGLE_CHOICE.value
                        ] = data_type.identifier
                    elif isinstance(field, GrammarElementFieldMultipleChoice):
                        values = []
                        values_map = {}
                        for option in field.options:
                            value = ReqIFEnumValue(
                                description=None,
                                identifier=generate_unique_identifier(
                                    "ENUM-VALUE"
                                ),
                                last_change=None,
                                key=option,
                                other_content=None,
                            )
                            values.append(value)
                            values_map[option] = option

                        data_type = ReqIFDataTypeDefinitionEnumeration(
                            is_self_closed=False,
                            description=None,
                            identifier=(
                                generate_unique_identifier(
                                    StrictDocReqIFTypes.MULTI_CHOICE.value
                                )
                            ),
                            last_change=None,
                            long_name=None,
                            multi_valued=True,
                            values=values,
                            values_map={},
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.MULTI_CHOICE.value
                        ] = data_type.identifier
                    else:
                        raise NotImplementedError(field) from None

            document_spec_types = cls._convert_document_grammar_to_spec_types(
                grammar=document.grammar, data_types_lookup=data_types_lookup
            )
            spec_types.extend(document_spec_types)
            document_iterator = DocumentCachingIterator(document)

            parents: Dict[ReqIFSpecHierarchy, ReqIFSpecHierarchy] = {}

            # TODO: This is a throw-away object. It gets discarded when the
            # iteration is over. Find a way to do without it.
            root_hierarchy = ReqIFSpecHierarchy(
                identifier="NOT_USED",
                last_change=None,
                long_name=None,
                spec_object="NOT_USED",
                children=[],
                ref_then_children_order=True,
                level=0,
            )
            current_hierarchy = root_hierarchy
            for node in document_iterator.all_content():
                if node.is_composite_requirement:
                    raise NotImplementedError(
                        "Exporting composite requirements is not "
                        "supported yet.",
                        node,
                    )
                if node.is_section:
                    attributes = []
                    title_attribute = SpecObjectAttribute(
                        attribute_type=SpecObjectAttributeType.STRING,
                        name="TITLE",
                        value=node.title,
                        enum_values_then_definition_order=None,
                    )
                    attributes.append(title_attribute)
                    if len(node.free_texts) > 0:
                        free_text_value = (
                            SDWriter.print_free_text_content(node.free_texts[0])
                            .encode("unicode_escape")
                            .decode("utf-8")
                        )
                        free_text_attribute = SpecObjectAttribute(
                            attribute_type=SpecObjectAttributeType.STRING,
                            name=ReqIFSectionField.FREETEXT.value,
                            value=free_text_value,
                            enum_values_then_definition_order=None,
                        )
                        attributes.append(free_text_attribute)
                    spec_object = ReqIFSpecObject(
                        description=None,
                        identifier=generate_unique_identifier("SECTION"),
                        last_change=None,
                        long_name=None,
                        spec_object_type="SECTION",
                        attributes=attributes,
                        attribute_map={"TITLE": title_attribute},
                        values_then_type_order=True,
                    )
                    spec_objects.append(spec_object)
                    hierarchy = ReqIFSpecHierarchy(
                        identifier=generate_unique_identifier("SPEC-HIERARCHY"),
                        last_change=None,
                        long_name=None,
                        spec_object=spec_object.identifier,
                        children=[],
                        ref_then_children_order=True,
                        level=node.ng_level,
                    )
                    if node.ng_level > current_hierarchy.level:
                        parents[hierarchy] = current_hierarchy
                        current_hierarchy.add_child(hierarchy)
                    elif node.ng_level < current_hierarchy.level:
                        for _ in range(
                            0, (current_hierarchy.level - node.ng_level + 1)
                        ):
                            current_hierarchy = parents[current_hierarchy]
                        current_hierarchy.add_child(hierarchy)
                        parents[hierarchy] = current_hierarchy
                    else:
                        current_hierarchy_parent = parents[current_hierarchy]
                        current_hierarchy_parent.add_child(hierarchy)
                        parents[hierarchy] = current_hierarchy_parent
                    current_hierarchy = hierarchy

                elif node.is_requirement:
                    spec_object = cls._convert_requirement_to_spec_object(
                        requirement=node, grammar=document.grammar
                    )
                    spec_objects.append(spec_object)
                    hierarchy = ReqIFSpecHierarchy(
                        identifier=generate_unique_identifier(
                            "SPEC-IDENTIFIER"
                        ),
                        last_change=None,
                        long_name=None,
                        spec_object=spec_object.identifier,
                        children=None,
                        ref_then_children_order=True,
                        level=node.ng_level,
                    )
                    for _ in range(
                        0, (current_hierarchy.level - node.ng_level + 1)
                    ):
                        current_hierarchy = parents[current_hierarchy]
                    parents[hierarchy] = current_hierarchy
                    current_hierarchy.add_child(hierarchy)
            specification = ReqIFSpecification(
                type_then_children_order=True,
                description=None,
                identifier=generate_unique_identifier("SPECIFICATION"),
                last_change=None,
                long_name=document.name,
                values=None,
                specification_type=None,
                children=root_hierarchy.children,
            )
            specifications.append(specification)

        reqif_reqif_content = ReqIFReqIFContent(
            data_types=data_types,
            spec_types=spec_types,
            spec_objects=spec_objects,
            spec_relations=[],
            specifications=specifications,
            spec_relation_groups=None,
        )
        core_content_or_none = ReqIFCoreContent(reqif_reqif_content)

        namespace_info: ReqIFNamespaceInfo = ReqIFNamespaceInfo(
            doctype_is_present=True,
            encoding="UTF-8",
            namespace=namespace,
            configuration=configuration,
            schema_namespace=None,
            schema_location=None,
            language=None,
        )
        reqif_bundle = ReqIFBundle(
            namespace_info=namespace_info,
            req_if_header=None,
            core_content=core_content_or_none,
            tool_extensions_tag_exists=False,
            lookup=ReqIFObjectLookup(
                data_types_lookup={},
                spec_objects_lookup={},
                spec_relations_parent_lookup={},
            ),
        )
        return reqif_bundle

    @classmethod
    def _convert_requirement_to_spec_object(
        cls,
        requirement: Requirement,
        grammar: DocumentGrammar,
    ) -> ReqIFSpecObject:
        grammar_element = grammar.elements_by_type[requirement.requirement_type]

        attributes: List[SpecObjectAttribute] = []
        attribute_map: Dict[str, SpecObjectAttribute] = {}
        for field in requirement.fields:
            grammar_field = grammar_element.fields_map[field.field_name]
            if isinstance(grammar_field, GrammarElementFieldSingleChoice):
                attribute = SpecObjectAttribute(
                    SpecObjectAttributeType.ENUMERATION,
                    field.field_name,
                    field.field_value,
                    enum_values_then_definition_order=True,
                )
            elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
                attribute = SpecObjectAttribute(
                    SpecObjectAttributeType.ENUMERATION,
                    field.field_name,
                    field.field_value,
                    enum_values_then_definition_order=True,
                )
            elif isinstance(grammar_field, GrammarElementFieldString):
                attribute = SpecObjectAttribute(
                    SpecObjectAttributeType.STRING,
                    field.field_name,
                    field.field_value,
                    enum_values_then_definition_order=None,
                )
            else:
                raise NotImplementedError(grammar_field) from None
            attributes.append(attribute)
            attribute_map[field.field_name] = attribute

        spec_object = ReqIFSpecObject(
            description=None,
            identifier=generate_unique_identifier("REQUIREMENT"),
            last_change=None,
            long_name=None,
            spec_object_type=requirement.requirement_type,
            attributes=attributes,
            attribute_map=attribute_map,
            values_then_type_order=True,
        )

        return spec_object

    @classmethod
    def _convert_document_grammar_to_spec_types(
        cls, grammar: DocumentGrammar, data_types_lookup
    ):
        spec_object_types: List = []

        for element in grammar.elements:
            attribute_definitions = []
            attribute_map = {}

            field: GrammarElementField
            for field in element.fields:
                if isinstance(field, GrammarElementFieldString):
                    attribute = SpecAttributeDefinition(
                        attribute_type=SpecObjectAttributeType.STRING,
                        description=None,
                        identifier=field.title,
                        last_change=None,
                        datatype_definition=(
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ),
                        long_name=field.title,
                        editable=None,
                        default_value=None,
                        multi_valued=None,
                    )
                elif isinstance(field, GrammarElementFieldSingleChoice):
                    attribute = SpecAttributeDefinition(
                        attribute_type=SpecObjectAttributeType.ENUMERATION,
                        description=None,
                        identifier=field.title,
                        last_change=None,
                        datatype_definition=(
                            data_types_lookup[
                                StrictDocReqIFTypes.SINGLE_CHOICE.value
                            ]
                        ),
                        long_name=field.title,
                        editable=None,
                        default_value=None,
                        multi_valued=False,
                    )
                elif isinstance(field, GrammarElementFieldMultipleChoice):
                    attribute = SpecAttributeDefinition(
                        attribute_type=SpecObjectAttributeType.ENUMERATION,
                        description=None,
                        identifier=field.title,
                        last_change=None,
                        datatype_definition=(
                            data_types_lookup[
                                StrictDocReqIFTypes.MULTI_CHOICE.value
                            ]
                        ),
                        long_name=field.title,
                        editable=None,
                        default_value=None,
                        multi_valued=True,
                    )
                else:
                    raise NotImplementedError(field) from None
                attribute_definitions.append(attribute)
                attribute_map[field.title] = attribute

            spec_object_type = ReqIFSpecObjectType(
                description=None,
                identifier=element.tag,
                last_change=None,
                long_name=element.tag,
                attribute_definitions=attribute_definitions,
                attribute_map=attribute_map,
            )
            spec_object_types.append(spec_object_type)

        return spec_object_types
