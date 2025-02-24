# mypy: disable-error-code="no-untyped-call,no-untyped-def,type-arg,union-attr"
import datetime
import uuid
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Tuple

from reqif.models.reqif_core_content import ReqIFCoreContent
from reqif.models.reqif_data_type import (
    ReqIFDataTypeDefinitionEnumeration,
    ReqIFDataTypeDefinitionString,
    ReqIFDataTypeDefinitionXHTML,
    ReqIFEnumValue,
)
from reqif.models.reqif_namespace_info import ReqIFNamespaceInfo
from reqif.models.reqif_req_if_content import ReqIFReqIFContent
from reqif.models.reqif_reqif_header import ReqIFReqIFHeader
from reqif.models.reqif_spec_hierarchy import ReqIFSpecHierarchy
from reqif.models.reqif_spec_object import ReqIFSpecObject, SpecObjectAttribute
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_spec_relation import ReqIFSpecRelation
from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_specification_type import ReqIFSpecificationType
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.object_lookup import ReqIFObjectLookup
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    SDOC_SPECIFICATION_TYPE_SINGLETON,
    SDOC_TO_REQIF_FIELD_MAP,
    ReqIFChapterField,
    SDocRequirementReservedField,
)
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.ordered_set import OrderedSet
from strictdoc.helpers.string import escape


class StrictDocReqIFTypes(Enum):
    SINGLE_LINE_STRING = "SDOC_DATATYPE_SINGLE_LINE_STRING"
    MULTI_LINE_STRING = "SDOC_DATATYPE_MULTI_LINE_STRING"
    SINGLE_CHOICE = "SDOC_DATATYPE_SINGLE_CHOICE"
    MULTI_CHOICE = "SDOC_DATATYPE_MULTI_CHOICE"


def generate_unique_identifier(element_type: str) -> str:
    return f"{element_type}-{uuid.uuid4()}"


class P01_SDocToReqIFBuildContext:
    def __init__(self, *, multiline_is_xhtml: bool, enable_mid: bool):
        self.multiline_is_xhtml: bool = multiline_is_xhtml
        self.enable_mid: bool = enable_mid
        self.map_uid_to_spec_objects: Dict[str, ReqIFSpecObject] = {}
        self.map_node_uids_to_their_relations: Dict[str, List[Reference]] = (
            defaultdict(list)
        )
        self.map_grammar_node_tags_to_spec_object_type: Dict[
            SDocDocument, Dict[str, ReqIFSpecObjectType]
        ] = defaultdict(dict)
        self.map_spec_relation_tuple_to_spec_relation_type: Dict[
            Tuple[str, Optional[str]], ReqIFSpecRelationType
        ] = {}


class P01_SDocToReqIFObjectConverter:
    @classmethod
    def convert_document_tree(
        cls,
        document_tree: DocumentTree,
        multiline_is_xhtml: bool,
        enable_mid: bool,
    ):
        creation_time = datetime.datetime.now(
            datetime.datetime.now().astimezone().tzinfo
        ).isoformat()

        namespace = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"

        context: P01_SDocToReqIFBuildContext = P01_SDocToReqIFBuildContext(
            multiline_is_xhtml=multiline_is_xhtml, enable_mid=enable_mid
        )

        spec_types: List = []
        spec_objects: List[ReqIFSpecObject] = []
        spec_relations: List[ReqIFSpecRelation] = []
        specifications: List[ReqIFSpecification] = []
        data_types: List = []
        data_types_lookup = {}

        specification_type = ReqIFSpecificationType(
            identifier=SDOC_SPECIFICATION_TYPE_SINGLETON,
            description=None,
            last_change=creation_time,
            long_name=SDOC_SPECIFICATION_TYPE_SINGLETON,
            spec_attributes=None,
            spec_attribute_map={},
            is_self_closed=True,
        )
        spec_types.append(specification_type)

        document: SDocDocument
        for document in document_tree.document_list:
            for element in document.grammar.elements:
                fields_names = element.get_field_titles()
                statement_field_idx = fields_names.index("STATEMENT")
                for field_idx_, field in enumerate(element.fields):
                    multiline = field_idx_ >= statement_field_idx

                    if isinstance(field, GrammarElementFieldString):
                        data_type: ReqIFDataTypeDefinitionString
                        if multiline:
                            if (
                                StrictDocReqIFTypes.MULTI_LINE_STRING.value
                                in data_types_lookup
                            ):
                                continue
                            if multiline_is_xhtml:
                                data_type = ReqIFDataTypeDefinitionXHTML(
                                    identifier=(
                                        StrictDocReqIFTypes.MULTI_LINE_STRING.value
                                    ),
                                    is_self_closed=True,
                                )
                            else:
                                data_type = ReqIFDataTypeDefinitionString.create(
                                    identifier=(
                                        StrictDocReqIFTypes.MULTI_LINE_STRING.value
                                    ),
                                )
                            data_types_lookup[
                                StrictDocReqIFTypes.MULTI_LINE_STRING.value
                            ] = data_type.identifier
                        else:
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
                            data_types_lookup[
                                StrictDocReqIFTypes.SINGLE_LINE_STRING.value
                            ] = data_type.identifier
                        data_types.append(data_type)
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
                        data_types_lookup[field.title] = data_type.identifier
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
                        data_types_lookup[field.title] = data_type.identifier
                    else:
                        raise NotImplementedError(field) from None

            document_spec_types = cls._convert_document_grammar_to_spec_types(
                grammar=assert_cast(document.grammar, DocumentGrammar),
                data_types_lookup=data_types_lookup,
                context=context,
            )
            spec_types.extend(document_spec_types)

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

            # FIXME: ReqIF must export complete documents including fragments.
            for node_ in document_iterator.all_content(
                print_fragments=False, print_fragments_from_files=False
            ):
                if node_.is_composite_requirement:
                    raise NotImplementedError(
                        "Exporting composite requirements is not "
                        "supported yet.",
                        node_,
                    )
                if node_.is_section:
                    section: SDocSection = assert_cast(node_, SDocSection)
                    # fmt: off
                    spec_object = (
                        P01_SDocToReqIFObjectConverter
                        ._convert_section_to_spec_object(
                            section=section,
                            context=context,
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
                        level=section.ng_level,
                    )
                    if section.ng_level > current_hierarchy.level:
                        parents[hierarchy] = current_hierarchy
                        current_hierarchy.add_child(hierarchy)
                    elif section.ng_level < current_hierarchy.level:
                        for _ in range(
                            0, (current_hierarchy.level - section.ng_level + 1)
                        ):
                            current_hierarchy = parents[current_hierarchy]
                        current_hierarchy.add_child(hierarchy)
                        parents[hierarchy] = current_hierarchy
                    else:
                        current_hierarchy_parent = parents[current_hierarchy]
                        current_hierarchy_parent.add_child(hierarchy)
                        parents[hierarchy] = current_hierarchy_parent
                    current_hierarchy = hierarchy

                elif node_.is_requirement:
                    requirement = assert_cast(node_, SDocNode)
                    spec_object = cls._convert_requirement_to_spec_object(
                        requirement=requirement,
                        grammar=assert_cast(document.grammar, DocumentGrammar),
                        context=context,
                        data_types=data_types,
                        data_types_lookup=data_types_lookup,
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
                        level=requirement.ng_level,
                    )
                    for _ in range(
                        0, (current_hierarchy.level - requirement.ng_level + 1)
                    ):
                        current_hierarchy = parents[current_hierarchy]
                    parents[hierarchy] = current_hierarchy
                    current_hierarchy.add_child(hierarchy)

            specification_identifier: str
            if context.enable_mid and document.reserved_mid is not None:
                specification_identifier = document.reserved_mid
            else:
                specification_identifier = generate_unique_identifier(
                    "SPECIFICATION"
                )
            specification = ReqIFSpecification(
                xml_node=None,
                description=None,
                identifier=specification_identifier,
                last_change=None,
                long_name=document.title,
                values=None,
                specification_type=specification_type.identifier,
                children=root_hierarchy.children,
            )
            specifications.append(specification)

        for (
            requirement_id,
            node_relations_,
        ) in context.map_node_uids_to_their_relations.items():
            spec_object = context.map_uid_to_spec_objects[requirement_id]
            for node_relation_ in node_relations_:
                # For now, the File-relations are not supported.
                if not isinstance(
                    node_relation_, (ParentReqReference, ChildReqReference)
                ):
                    continue
                related_node_uid = node_relation_.ref_uid
                parent_spec_object = context.map_uid_to_spec_objects[
                    related_node_uid
                ]
                spec_relation_type: ReqIFSpecRelationType = (
                    context.map_spec_relation_tuple_to_spec_relation_type[
                        (node_relation_.ref_type, node_relation_.role)
                    ]
                )
                spec_relations.append(
                    ReqIFSpecRelation(
                        xml_node=None,
                        description=None,
                        identifier=generate_unique_identifier("SPEC-RELATION"),
                        last_change=None,
                        relation_type_ref=spec_relation_type.identifier,
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
            configuration=None,
            namespace_id=None,
            namespace_xhtml="http://www.w3.org/1999/xhtml",
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
    def _convert_section_to_spec_object(
        cls,
        *,
        section: SDocSection,
        context: P01_SDocToReqIFBuildContext,
    ) -> ReqIFSpecObject:
        assert isinstance(section, SDocSection)
        parent_document: SDocDocument = assert_cast(
            section.get_document(), SDocDocument
        )

        attributes = []
        title_attribute = SpecObjectAttribute(
            xml_node=None,
            attribute_type=SpecObjectAttributeType.STRING,
            definition_ref=ReqIFChapterField.CHAPTER_NAME,
            value=section.title,
        )
        attributes.append(title_attribute)

        """
        If MIDs is enabled and this section has an MID, use it for
        SPEC-OBJECT IDENTIFIER.
        """
        enable_mid = context.enable_mid and parent_document.config.enable_mid
        section_identifier: str
        if enable_mid and section.reserved_mid is not None:
            section_identifier = section.reserved_mid
        else:
            section_identifier = generate_unique_identifier("SECTION")

        spec_object_type: ReqIFSpecObjectType = (
            context.map_grammar_node_tags_to_spec_object_type[parent_document][
                "SECTION"
            ]
        )
        spec_object = ReqIFSpecObject(
            xml_node=None,
            description=None,
            identifier=section_identifier,
            last_change=None,
            long_name=None,
            spec_object_type=spec_object_type.identifier,
            attributes=attributes,
        )
        return spec_object

    @classmethod
    def _convert_requirement_to_spec_object(
        cls,
        requirement: SDocNode,
        grammar: DocumentGrammar,
        context: P01_SDocToReqIFBuildContext,
        data_types: List,
        data_types_lookup: Dict[str, str],
    ) -> ReqIFSpecObject:
        node_document = assert_cast(requirement.get_document(), SDocDocument)

        enable_mid = context.enable_mid and node_document.config.enable_mid

        requirement_identifier: str
        if enable_mid and requirement.reserved_mid is not None:
            requirement_identifier = requirement.reserved_mid
        else:
            requirement_identifier = generate_unique_identifier("REQUIREMENT")

        grammar_element = grammar.elements_by_type[requirement.node_type]

        attributes: List[SpecObjectAttribute] = []
        for field in requirement.fields_as_parsed:
            # The MID field, if exists, is extracted separately as a ReqIF Identifier.
            if field.field_name == "MID":
                continue
            grammar_field = grammar_element.fields_map[field.field_name]
            if isinstance(grammar_field, GrammarElementFieldSingleChoice):
                data_type_ref = data_types_lookup[field.field_name]

                enum_ref_value = None
                for data_type in data_types:
                    if data_type_ref == data_type.identifier:
                        for data_type_value in data_type.values:
                            if data_type_value.key == field.get_text_value():
                                enum_ref_value = data_type_value.identifier
                                break

                assert enum_ref_value is not None

                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=SpecObjectAttributeType.ENUMERATION,
                    definition_ref=field.field_name,
                    value=[enum_ref_value],
                )
            elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
                field_values: List[str] = field.get_text_value().split(",")
                field_values = list(map(lambda v: v.strip(), field_values))

                data_type_ref = data_types_lookup[field.field_name]

                data_type_lookup = {}
                for data_type in data_types:
                    if data_type_ref == data_type.identifier:
                        for data_type_value in data_type.values:
                            data_type_lookup[data_type_value.key] = (
                                data_type_value.identifier
                            )

                field_values_refs = []
                for field_value_ in field_values:
                    field_values_refs.append(data_type_lookup[field_value_])

                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=SpecObjectAttributeType.ENUMERATION,
                    definition_ref=field.field_name,
                    value=field_values_refs,
                )
            elif isinstance(grammar_field, GrammarElementFieldString):
                is_multiline_field = field.is_multiline()

                field_value: str = field.get_text_value().rstrip()

                attribute_type: SpecObjectAttributeType
                if context.multiline_is_xhtml:
                    attribute_type = (
                        SpecObjectAttributeType.XHTML
                        if is_multiline_field
                        else SpecObjectAttributeType.STRING
                    )
                else:
                    field_value = escape(field_value)
                    attribute_type = SpecObjectAttributeType.STRING

                field_name = field.field_name
                if field_name in SDocRequirementReservedField.SET:
                    field_name = SDOC_TO_REQIF_FIELD_MAP[field_name]
                attribute = SpecObjectAttribute(
                    xml_node=None,
                    attribute_type=attribute_type,
                    definition_ref=field_name,
                    value=field_value,
                )
            else:
                raise NotImplementedError(grammar_field) from None
            attributes.append(attribute)

        if requirement.reserved_uid is not None:
            if len(requirement.relations) > 0:
                context.map_node_uids_to_their_relations[
                    requirement.reserved_uid
                ] = requirement.relations

        spec_object_type: ReqIFSpecObjectType = (
            context.map_grammar_node_tags_to_spec_object_type[node_document][
                requirement.node_type
            ]
        )
        spec_object = ReqIFSpecObject.create(
            identifier=requirement_identifier,
            spec_object_type=spec_object_type.identifier,
            attributes=attributes,
        )
        if requirement.reserved_uid is not None:
            context.map_uid_to_spec_objects[requirement.reserved_uid] = (
                spec_object
            )
        return spec_object

    @classmethod
    def _convert_document_grammar_to_spec_types(
        cls,
        grammar: DocumentGrammar,
        data_types_lookup,
        context: P01_SDocToReqIFBuildContext,
    ):
        spec_object_types: List = []

        for element in grammar.elements:
            fields_names = element.get_field_titles()
            statement_field_idx = fields_names.index("STATEMENT")

            attribute_definitions = []

            field: GrammarElementField
            for field_idx_, field in enumerate(element.fields):
                multiline = field_idx_ >= statement_field_idx

                if isinstance(field, GrammarElementFieldString):
                    field_title = field.title
                    if field_title in SDocRequirementReservedField.SET:
                        field_title = SDOC_TO_REQIF_FIELD_MAP[field_title]
                    if multiline:
                        attribute_type = (
                            SpecObjectAttributeType.XHTML
                            if context.multiline_is_xhtml
                            else SpecObjectAttributeType.STRING
                        )
                        attribute = SpecAttributeDefinition.create(
                            attribute_type=attribute_type,
                            identifier=field_title,
                            datatype_definition=(
                                StrictDocReqIFTypes.MULTI_LINE_STRING.value
                            ),
                            long_name=field_title,
                        )
                    else:
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
                        datatype_definition=data_types_lookup[field.title],
                        long_name=field.title,
                        multi_valued=False,
                    )
                elif isinstance(field, GrammarElementFieldMultipleChoice):
                    attribute = SpecAttributeDefinition.create(
                        attribute_type=SpecObjectAttributeType.ENUMERATION,
                        identifier=field.title,
                        datatype_definition=data_types_lookup[field.title],
                        long_name=field.title,
                        multi_valued=True,
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

            spec_object_type_identifier = element.tag + "_" + uuid.uuid4().hex
            spec_object_type = ReqIFSpecObjectType.create(
                identifier=spec_object_type_identifier,
                long_name=element.tag,
                attribute_definitions=attribute_definitions,
            )
            spec_object_types.append(spec_object_type)
            context.map_grammar_node_tags_to_spec_object_type[grammar.parent][
                element.tag
            ] = spec_object_type

        assert grammar.parent is not None
        section_spec_type = (
            P01_SDocToReqIFObjectConverter._create_section_spec_object_type()
        )
        context.map_grammar_node_tags_to_spec_object_type[grammar.parent][
            "SECTION"
        ] = section_spec_type
        spec_object_types.append(section_spec_type)

        # Using dict as an ordered set.
        spec_relation_tuples: OrderedSet = OrderedSet()
        for element_ in grammar.elements:
            for relation_ in element_.relations:
                spec_relation_tuples.add(
                    (relation_.relation_type, relation_.relation_role)
                )

        spec_relation_types: List = []
        for spec_relation_tuple_ in spec_relation_tuples:
            spec_relation_type_name = (
                spec_relation_tuple_[1]
                if spec_relation_tuple_[1] is not None
                else spec_relation_tuple_[0]
            )
            spec_relation_type = ReqIFSpecRelationType(
                identifier=generate_unique_identifier(spec_relation_type_name),
                long_name=spec_relation_type_name,
            )
            spec_relation_types.append(spec_relation_type)
            context.map_spec_relation_tuple_to_spec_relation_type[
                spec_relation_tuple_
            ] = spec_relation_type

        return spec_object_types + spec_relation_types

    @classmethod
    def _create_section_spec_object_type(
        cls,
    ):
        attribute_definitions = []
        chapter_name_attribute = SpecAttributeDefinition.create(
            attribute_type=SpecObjectAttributeType.STRING,
            identifier="ReqIF.ChapterName",
            datatype_definition=StrictDocReqIFTypes.SINGLE_LINE_STRING.value,
            long_name="ReqIF.ChapterName",
        )
        attribute_definitions.append(chapter_name_attribute)

        spec_object_type_identifier = "SECTION_" + uuid.uuid4().hex
        spec_object_type = ReqIFSpecObjectType.create(
            identifier=spec_object_type_identifier,
            long_name="SECTION",
            attribute_definitions=attribute_definitions,
        )
        return spec_object_type
