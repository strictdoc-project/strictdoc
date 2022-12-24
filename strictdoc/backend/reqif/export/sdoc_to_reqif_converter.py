import uuid
import datetime
from enum import Enum
from typing import Dict, List

from reqif.models.reqif_core_content import ReqIFCoreContent
from reqif.models.reqif_data_type import (
    ReqIFDataTypeDefinitionString,
    ReqIFDataTypeDefinitionEnumeration,
    ReqIFEnumValue,
)
from reqif.models.reqif_namespace_info import ReqIFNamespaceInfo
from reqif.models.reqif_reqif_header import ReqIFReqIFHeader
from reqif.models.reqif_req_if_content import ReqIFReqIFContent
from reqif.models.reqif_spec_hierarchy import ReqIFSpecHierarchy
from reqif.models.reqif_spec_object import ReqIFSpecObject, SpecObjectAttribute
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_spec_relation import ReqIFSpecRelation
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_specification_type import ReqIFSpecificationType
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.object_lookup import ReqIFObjectLookup
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    ReqIFChapterField,
    SDocRequirementReservedField,
    SDOC_TO_REQIF_FIELD_MAP,
    SDOC_SPEC_OBJECT_TYPE_SINGLETON,
    SDOC_SPECIFICATION_TYPE_SINGLETON,
    SDOC_SPEC_RELATION_PARENT_TYPE_SINGLETON,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    RequirementFieldName,
    ReferenceType,
    GrammarElementFieldReference,
)
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.helpers.string import escape


class StrictDocReqIFTypes(Enum):
    SINGLE_LINE_STRING = "SDOC_DATATYPE_SINGLE_LINE_STRING"
    MULTI_LINE_STRING = "SDOC_DATATYPE_MULTI_LINE_STRING"
    SINGLE_CHOICE = "SDOC_DATATYPE_SINGLE_CHOICE"
    MULTI_CHOICE = "SDOC_DATATYPE_MULTI_CHOICE"


def generate_unique_identifier(element_type: str) -> str:
    return f"{element_type}-{uuid.uuid4()}"


class SDocToReqIFBuildContext:
    def __init__(self):
        self.map_uid_to_spec_objects = {}
        self.map_uid_to_parent_uids = {}


class SDocToReqIFObjectConverter:
    @classmethod
    def convert_document_tree(
        cls,
        document_tree: DocumentTree,
    ):
        creation_time = datetime.datetime.now(
            datetime.datetime.now().astimezone().tzinfo
        ).isoformat()

        # TODO
        namespace = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
        configuration = "https://github.com/strictdoc-project/strictdoc"

        context: SDocToReqIFBuildContext = SDocToReqIFBuildContext()
        spec_types: List = []
        spec_objects: List[ReqIFSpecObject] = []
        spec_relations: List[ReqIFSpecRelation] = []
        specifications: List[ReqIFSpecification] = []
        data_types: List = []
        data_types_lookup = {}
        document: Document
        for document in document_tree.document_list:
            document_spec_object_type = (
                SDOC_SPEC_OBJECT_TYPE_SINGLETON + "_" + uuid.uuid4().hex
            )
            for element in document.grammar.elements:
                for field in element.fields:
                    if isinstance(field, GrammarElementFieldString):
                        if (
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            in data_types_lookup
                        ):
                            continue
                        data_type = ReqIFDataTypeDefinitionString.create(
                            identifier=(
                                StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            ),
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ] = data_type.identifier
                    elif isinstance(field, GrammarElementFieldSingleChoice):
                        values = []
                        values_map = {}
                        for option in field.options:
                            value = ReqIFEnumValue.create(
                                identifier=generate_unique_identifier(
                                    "ENUM-VALUE"
                                ),
                                key=option,
                            )
                            values.append(value)
                            values_map[option] = option

                        data_type = ReqIFDataTypeDefinitionEnumeration.create(
                            identifier=(
                                generate_unique_identifier(
                                    StrictDocReqIFTypes.SINGLE_CHOICE.value
                                )
                            ),
                            values=values,
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.SINGLE_CHOICE.value
                        ] = data_type.identifier
                    elif isinstance(field, GrammarElementFieldMultipleChoice):
                        values = []
                        values_map = {}
                        for option in field.options:
                            value = ReqIFEnumValue.create(
                                identifier=generate_unique_identifier(
                                    "ENUM-VALUE"
                                ),
                                key=option,
                            )
                            values.append(value)
                            values_map[option] = option

                        data_type = ReqIFDataTypeDefinitionEnumeration.create(
                            identifier=(
                                generate_unique_identifier(
                                    StrictDocReqIFTypes.MULTI_CHOICE.value
                                )
                            ),
                            values=values,
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.MULTI_CHOICE.value
                        ] = data_type.identifier
                    elif isinstance(field, GrammarElementFieldReference):
                        # TODO: implement correct reqIF Encoding for
                        #  GrammarElementFieldReference. Treat as
                        #  GrammarElementFieldString for now.
                        if (
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            in data_types_lookup
                        ):
                            continue
                        data_type = ReqIFDataTypeDefinitionString.create(
                            identifier=(
                                StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            ),
                        )
                        data_types.append(data_type)
                        data_types_lookup[
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ] = data_type.identifier
                    else:
                        raise NotImplementedError(field) from None

            document_spec_types = cls._convert_document_grammar_to_spec_types(
                grammar=document.grammar,
                data_types_lookup=data_types_lookup,
                document_spec_object_type=document_spec_object_type,
            )
            spec_types.extend(document_spec_types)

            specification_type = ReqIFSpecificationType(
                description=None,
                identifier=SDOC_SPECIFICATION_TYPE_SINGLETON,
                last_change=creation_time,
                long_name=SDOC_SPECIFICATION_TYPE_SINGLETON,
                spec_attributes=None,
                spec_attribute_map={},
            )
            spec_types.append(specification_type)
            document_iterator = DocumentCachingIterator(document)

            parents: Dict[ReqIFSpecHierarchy, ReqIFSpecHierarchy] = {}

            # TODO: This is a throw-away object. It gets discarded when the
            # iteration is over. Find a way to do without it.
            root_hierarchy = ReqIFSpecHierarchy(
                xml_node=None,
                is_self_closed=False,
                identifier="NOT_USED",
                last_change=None,
                long_name=None,
                spec_object="NOT_USED",
                children=[],
                ref_then_children_order=True,
                level=0,
            )

            current_hierarchy = root_hierarchy
            if len(document.free_texts) > 0:
                # fmt: off
                document_free_text_spec_object = (
                    SDocToReqIFObjectConverter
                    ._convert_document_free_text_to_spec_object(
                        document,
                        document_spec_object_type=document_spec_object_type
                    )
                )
                # fmt: on
                spec_objects.append(document_free_text_spec_object)
                hierarchy = ReqIFSpecHierarchy(
                    xml_node=None,
                    is_self_closed=False,
                    identifier=generate_unique_identifier("SPEC-HIERARCHY"),
                    last_change=None,
                    long_name=None,
                    spec_object=document_free_text_spec_object.identifier,
                    children=[],
                    ref_then_children_order=True,
                    level=document.ng_level + 1,
                )
                current_hierarchy.add_child(hierarchy)
            for node in document_iterator.all_content():
                if node.is_composite_requirement:
                    raise NotImplementedError(
                        "Exporting composite requirements is not "
                        "supported yet.",
                        node,
                    )
                if node.is_section:
                    # fmt: off
                    spec_object = (
                        SDocToReqIFObjectConverter
                        ._convert_section_to_spec_object(
                            node,
                            document_spec_object_type,
                        )
                    )
                    # fmt: on
                    spec_objects.append(spec_object)
                    hierarchy = ReqIFSpecHierarchy(
                        xml_node=None,
                        is_self_closed=False,
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
                        requirement=node,
                        grammar=document.grammar,
                        context=context,
                        document_spec_object_type=document_spec_object_type,
                    )
                    spec_objects.append(spec_object)
                    hierarchy = ReqIFSpecHierarchy(
                        xml_node=None,
                        is_self_closed=False,
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
                xml_node=None,
                description=None,
                identifier=generate_unique_identifier("SPECIFICATION"),
                last_change=None,
                long_name=document.title,
                values=None,
                specification_type=specification_type.identifier,
                children=root_hierarchy.children,
            )
            specifications.append(specification)

        for (
            requirement_id,
            parent_uids,
        ) in context.map_uid_to_parent_uids.items():
            spec_object = context.map_uid_to_spec_objects[requirement_id]
            for parent_uid in parent_uids:
                parent_spec_object = context.map_uid_to_spec_objects[parent_uid]
                spec_relations.append(
                    ReqIFSpecRelation(
                        xml_node=None,
                        description=None,
                        identifier=generate_unique_identifier("SPEC-RELATION"),
                        last_change=None,
                        relation_type_ref=SDOC_SPEC_RELATION_PARENT_TYPE_SINGLETON,  # noqa: E501
                        source=spec_object.identifier,
                        target=parent_spec_object.identifier,
                        values_attribute=None,
                    )
                )

        reqif_reqif_content = ReqIFReqIFContent(
            data_types=data_types,
            spec_types=spec_types,
            spec_objects=spec_objects,
            spec_relations=spec_relations,
            specifications=specifications,
            spec_relation_groups=None,
        )
        core_content_or_none = ReqIFCoreContent(reqif_reqif_content)

        namespace_info: ReqIFNamespaceInfo = ReqIFNamespaceInfo(
            original_reqif_tag_dump=None,
            doctype_is_present=True,
            encoding="UTF-8",
            namespace=namespace,
            configuration=configuration,
            namespace_id=None,
            namespace_xhtml=None,
            schema_namespace=None,
            schema_location=None,
            language=None,
        )

        req_reqif_header = ReqIFReqIFHeader(
            identifier=generate_unique_identifier("REQ-IF-HEADER"),
            creation_time=creation_time,
            title="Documentation export by StrictDoc",
            req_if_tool_id="strictdoc",
            req_if_version="1.0",
            source_tool_id="strictdoc",
            repository_id=None,
            comment=None,
        )

        reqif_bundle = ReqIFBundle(
            namespace_info=namespace_info,
            req_if_header=req_reqif_header,
            core_content=core_content_or_none,
            tool_extensions_tag_exists=False,
            lookup=ReqIFObjectLookup(
                data_types_lookup={},
                spec_types_lookup={},
                spec_objects_lookup={},
                spec_relations_parent_lookup={},
            ),
            exceptions=[],
        )
        return reqif_bundle

    @classmethod
    def _convert_document_free_text_to_spec_object(
        cls, document: Document, document_spec_object_type: str
    ) -> ReqIFSpecObject:
        assert isinstance(document, Document)
        assert len(document.free_texts) > 0
        attributes = []
        # See SDOC_IMPL_1.
        title_attribute = SpecObjectAttribute(
            xml_node=None,
            attribute_type=SpecObjectAttributeType.STRING,
            definition_ref=ReqIFChapterField.CHAPTER_NAME,
            value="Abstract",
        )
        attributes.append(title_attribute)
        free_text_value = escape(
            SDWriter.print_free_text_content(document.free_texts[0])
        )
        free_text_attribute = SpecObjectAttribute(
            xml_node=None,
            attribute_type=SpecObjectAttributeType.STRING,
            definition_ref=ReqIFChapterField.TEXT,
            value=free_text_value,
        )
        attributes.append(free_text_attribute)
        spec_object = ReqIFSpecObject(
            xml_node=None,
            description=None,
            identifier=generate_unique_identifier("DOCUMENT_FREETEXT"),
            last_change=None,
            long_name=None,
            spec_object_type=document_spec_object_type,
            attributes=attributes,
        )
        return spec_object

    @classmethod
    def _convert_section_to_spec_object(
        cls, section: Section, document_spec_object_type: str
    ) -> ReqIFSpecObject:
        assert isinstance(section, Section)
        attributes = []
        title_attribute = SpecObjectAttribute(
            xml_node=None,
            attribute_type=SpecObjectAttributeType.STRING,
            definition_ref=ReqIFChapterField.CHAPTER_NAME,
            value=section.title,
        )
        attributes.append(title_attribute)
        if len(section.free_texts) > 0:
            free_text_value = escape(
                SDWriter.print_free_text_content(section.free_texts[0])
            )
            free_text_attribute = SpecObjectAttribute(
                xml_node=None,
                attribute_type=SpecObjectAttributeType.STRING,
                definition_ref=ReqIFChapterField.TEXT,
                value=free_text_value,
            )
            attributes.append(free_text_attribute)
        spec_object = ReqIFSpecObject(
            xml_node=None,
            description=None,
            identifier=generate_unique_identifier("SECTION"),
            last_change=None,
            long_name=None,
            spec_object_type=document_spec_object_type,
            attributes=attributes,
        )
        return spec_object

    @classmethod
    def _convert_requirement_to_spec_object(
        cls,
        requirement: Requirement,
        grammar: DocumentGrammar,
        context: SDocToReqIFBuildContext,
        document_spec_object_type: str,
    ) -> ReqIFSpecObject:
        requirement_identifier = generate_unique_identifier("REQUIREMENT")
        grammar_element = grammar.elements_by_type[requirement.requirement_type]

        attributes: List[SpecObjectAttribute] = []
        for field in requirement.fields:
            if field.field_name == RequirementFieldName.REFS:
                parent_references = []
                for reference in field.field_value_references:
                    if reference.ref_type != ReferenceType.PARENT:
                        continue
                    parent_references.append(reference.ref_uid)
                    context.map_uid_to_parent_uids[
                        requirement.uid
                    ] = parent_references
                continue
            grammar_field = grammar_element.fields_map[field.field_name]
            if isinstance(grammar_field, GrammarElementFieldSingleChoice):
                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=SpecObjectAttributeType.ENUMERATION,
                    definition_ref=field.field_name,
                    value=field.field_value,
                )
            elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=SpecObjectAttributeType.ENUMERATION,
                    definition_ref=field.field_name,
                    value=field.field_value,
                )
            elif isinstance(grammar_field, GrammarElementFieldString):
                field_value = escape(
                    field.field_value_multiline
                    if field.field_value_multiline is not None
                    else field.field_value
                )
                field_name = field.field_name
                if field_name in SDocRequirementReservedField.SET:
                    field_name = SDOC_TO_REQIF_FIELD_MAP[field_name]
                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=SpecObjectAttributeType.STRING,
                    definition_ref=field_name,
                    value=field_value,
                )
            else:
                raise NotImplementedError(grammar_field) from None
            attributes.append(attribute)

        spec_object = ReqIFSpecObject.create(
            identifier=requirement_identifier,
            spec_object_type=document_spec_object_type,
            attributes=attributes,
        )
        context.map_uid_to_spec_objects[requirement.uid] = spec_object
        return spec_object

    @classmethod
    def _convert_document_grammar_to_spec_types(
        cls,
        grammar: DocumentGrammar,
        data_types_lookup,
        document_spec_object_type: str,
    ):
        spec_object_types: List = []

        assert (
            len(grammar.elements) == 1
        ), "Only one grammar element is currently supported."

        for element in grammar.elements:
            attribute_definitions = []

            field: GrammarElementField
            for field in element.fields:
                if isinstance(field, GrammarElementFieldString):
                    field_title = field.title
                    if field_title in SDocRequirementReservedField.SET:
                        field_title = SDOC_TO_REQIF_FIELD_MAP[field_title]
                    attribute = SpecAttributeDefinition.create(
                        attribute_type=SpecObjectAttributeType.STRING,
                        identifier=field_title,
                        datatype_definition=(
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ),
                        long_name=field_title,
                    )
                elif isinstance(field, GrammarElementFieldSingleChoice):
                    attribute = SpecAttributeDefinition.create(
                        attribute_type=SpecObjectAttributeType.ENUMERATION,
                        identifier=field.title,
                        datatype_definition=(
                            data_types_lookup[
                                StrictDocReqIFTypes.SINGLE_CHOICE.value
                            ]
                        ),
                        long_name=field.title,
                        multi_valued=False,
                    )
                elif isinstance(field, GrammarElementFieldMultipleChoice):
                    attribute = SpecAttributeDefinition.create(
                        attribute_type=SpecObjectAttributeType.ENUMERATION,
                        identifier=field.title,
                        datatype_definition=(
                            data_types_lookup[
                                StrictDocReqIFTypes.MULTI_CHOICE.value
                            ]
                        ),
                        long_name=field.title,
                        multi_valued=True,
                    )
                elif isinstance(field, GrammarElementFieldReference):
                    # TODO: implement correct reqIF Encoding for
                    #  GrammarElementFieldReference. Treat as
                    #  GrammarElementFieldString for now.
                    field_title = field.title
                    if field_title in SDocRequirementReservedField.SET:
                        field_title = SDOC_TO_REQIF_FIELD_MAP[field_title]
                    attribute = SpecAttributeDefinition.create(
                        attribute_type=SpecObjectAttributeType.STRING,
                        identifier=field_title,
                        datatype_definition=(
                            StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                        ),
                        long_name=field_title,
                    )

                else:
                    raise NotImplementedError(field) from None
                attribute_definitions.append(attribute)

            # Extra chapter name attribute.
            chapter_name_attribute = SpecAttributeDefinition.create(
                attribute_type=SpecObjectAttributeType.STRING,
                identifier="ReqIF.ChapterName",
                datatype_definition=(
                    StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                ),
                long_name="ReqIF.ChapterName",
            )
            attribute_definitions.append(chapter_name_attribute)

            spec_object_type = ReqIFSpecObjectType.create(
                identifier=document_spec_object_type,
                long_name=element.tag,
                attribute_definitions=attribute_definitions,
            )
            spec_object_types.append(spec_object_type)

        return spec_object_types
