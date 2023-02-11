from typing import Dict, List, Optional, Set, Union

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionEnumeration
from reqif.models.reqif_spec_object import ReqIFSpecObject
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    DEFAULT_SDOC_GRAMMAR_FIELDS,
    REQIF_MAP_TO_SDOC_FIELD_MAP,
    ReqIFChapterField,
    ReqIFRequirementReservedField,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
)
from strictdoc.helpers.string import unescape


class ReqIFToSDocConverter:
    @staticmethod
    def convert_reqif_bundle(reqif_bundle: ReqIFBundle) -> List[Document]:
        # TODO: Should we rather show an error that there are no specifications?
        if (
            reqif_bundle.core_content is None
            or reqif_bundle.core_content.req_if_content is None
            or len(reqif_bundle.core_content.req_if_content.specifications) == 0
        ):
            return [ReqIFToSDocConverter.create_document(title=None)]

        documents: List[Document] = []
        for (
            specification
        ) in reqif_bundle.core_content.req_if_content.specifications:
            document = (
                ReqIFToSDocConverter._create_document_from_reqif_specification(
                    specification=specification,
                    reqif_bundle=reqif_bundle,
                )
            )
            documents.append(document)
        return documents

    @staticmethod
    def is_spec_object_section(
        spec_object: ReqIFSpecObject, reqif_bundle: ReqIFBundle
    ):
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        attribute_map: Dict[
            str, SpecAttributeDefinition
        ] = spec_object_type.attribute_map
        for attribute in spec_object.attributes:
            long_name_or_none: Optional[str] = attribute_map[
                attribute.definition_ref
            ].long_name
            if long_name_or_none is None:
                raise NotImplementedError(attribute_map)
            field_name: str = long_name_or_none
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                return True
        return False

    @staticmethod
    def is_spec_object_requirement(_):
        return True

    @staticmethod
    def _create_document_from_reqif_specification(
        *,
        specification: ReqIFSpecification,
        reqif_bundle: ReqIFBundle,
    ):
        document = ReqIFToSDocConverter.create_document(
            title=specification.long_name
        )
        elements: List[GrammarElement] = []
        document.section_contents = []
        current_section = document
        used_spec_object_types_ids: Set[str] = set()

        for current_hierarchy in reqif_bundle.iterate_specification_hierarchy(
            specification
        ):
            spec_object = reqif_bundle.get_spec_object_by_ref(
                current_hierarchy.spec_object
            )
            used_spec_object_types_ids.add(spec_object.spec_object_type)
            if ReqIFToSDocConverter.is_spec_object_section(
                spec_object,
                reqif_bundle=reqif_bundle,
            ):
                # fmt: off
                section = (
                    ReqIFToSDocConverter.create_section_from_spec_object(
                        spec_object,
                        current_hierarchy.level,
                        reqif_bundle=reqif_bundle,
                    )
                )
                # fmt: on
                if current_hierarchy.level > current_section.ng_level:
                    current_section.section_contents.append(section)
                elif current_hierarchy.level < current_section.ng_level:
                    for _ in range(
                        0, current_section.ng_level - current_hierarchy.level
                    ):
                        assert not isinstance(current_section, Document)
                        if isinstance(current_section, Section):
                            current_section = current_section.parent
                    current_section.section_contents.append(section)
                else:
                    raise NotImplementedError
            elif ReqIFToSDocConverter.is_spec_object_requirement(spec_object):
                # fmt: off
                requirement: Requirement = (
                    ReqIFToSDocConverter
                    .create_requirement_from_spec_object(
                        spec_object=spec_object,
                        parent_section=current_section,
                        reqif_bundle=reqif_bundle,
                        level=current_hierarchy.level,
                    )
                )
                # fmt: on
                current_section.section_contents.append(requirement)
            else:
                raise NotImplementedError(spec_object) from None

        # See SDOC_IMPL_1.
        if (
            len(document.section_contents) > 0
            and isinstance(document.section_contents[0], Section)
            and document.section_contents[0].title == "Abstract"
        ):
            assert len(document.section_contents[0].free_texts)
            document.free_texts = document.section_contents[0].free_texts
            document.section_contents.pop(0)

        for used_spec_object_type_id in used_spec_object_types_ids:
            spec_object_type_or_none: Optional[
                ReqIFSpecObjectType
            ] = reqif_bundle.get_spec_object_type_by_ref(
                ref=used_spec_object_type_id,
            )
            assert (
                spec_object_type_or_none is not None
            ), "Expect the spec object type to be present."
            spec_object_type: ReqIFSpecObjectType = spec_object_type_or_none
            attributes = list(spec_object_type.attribute_map.keys())
            if attributes != DEFAULT_SDOC_GRAMMAR_FIELDS:
                # fmt: off
                grammar_element = (
                    ReqIFToSDocConverter
                    .create_grammar_element_from_spec_object_type(
                        spec_object_type=spec_object_type,
                        reqif_bundle=reqif_bundle
                    )
                )
                # fmt: on
                elements.append(grammar_element)
        if len(elements) > 0:
            grammar = DocumentGrammar(parent=document, elements=elements)
            grammar.is_default = False
        else:
            grammar = DocumentGrammar.create_default(parent=document)
        document.grammar = grammar

        return document

    @staticmethod
    def create_grammar_element_from_spec_object_type(
        *,
        spec_object_type: ReqIFSpecObjectType,
        reqif_bundle: ReqIFBundle,
    ):
        fields = []
        for attribute in spec_object_type.attribute_definitions:
            field_name = REQIF_MAP_TO_SDOC_FIELD_MAP.get(
                attribute.long_name, attribute.long_name
            )

            # Chapter name is a reserved field for sections.
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                continue
            if attribute.attribute_type == SpecObjectAttributeType.STRING:
                fields.append(
                    GrammarElementFieldString(
                        parent=None,
                        title=field_name,
                        required="False",
                    )
                )
            elif attribute.attribute_type == SpecObjectAttributeType.XHTML:
                fields.append(
                    GrammarElementFieldString(
                        parent=None,
                        title=field_name,
                        required="False",
                    )
                )
            elif (
                attribute.attribute_type == SpecObjectAttributeType.ENUMERATION
            ):
                enum_data_type: ReqIFDataTypeDefinitionEnumeration = (
                    reqif_bundle.lookup.get_data_type_by_ref(
                        attribute.datatype_definition
                    )
                )
                options = list(map(lambda v: v.key, enum_data_type.values))
                if attribute.multi_valued is True:
                    fields.append(
                        GrammarElementFieldMultipleChoice(
                            parent=None,
                            title=field_name,
                            options=options,
                            required="False",
                        )
                    )
                else:
                    fields.append(
                        GrammarElementFieldSingleChoice(
                            parent=None,
                            title=field_name,
                            options=options,
                            required="False",
                        )
                    )
            elif attribute.attribute_type == SpecObjectAttributeType.DATE:
                # Recognize the DATE attributes but do nothing about them,
                # since StrictDoc has no concept of "date" for its grammar
                # fields.
                pass
            else:
                raise NotImplementedError(attribute) from None
        requirement_element = GrammarElement(
            parent=None, tag="REQUIREMENT", fields=fields
        )
        return requirement_element

    @staticmethod
    def create_document(title: Optional[str]) -> Document:
        document_config = DocumentConfig.default_config(None)
        document_title = title if title else "<No title>"
        document = Document(document_title, document_config, None, [], [])
        document.grammar = DocumentGrammar.create_default(document)
        return document

    @staticmethod
    def create_section_from_spec_object(
        spec_object: ReqIFSpecObject, level, reqif_bundle: ReqIFBundle
    ) -> Section:
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        attribute_map: Dict[
            str, SpecAttributeDefinition
        ] = spec_object_type.attribute_map
        assert attribute_map is not None
        for attribute in spec_object.attributes:
            field_name_or_none: Optional[str] = attribute_map[
                attribute.definition_ref
            ].long_name
            if field_name_or_none is None:
                raise NotImplementedError
            field_name: str = field_name_or_none
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                section_title = attribute.value
                break
        else:
            raise NotImplementedError(attribute_map)

        free_texts = []
        if ReqIFChapterField.TEXT in spec_object.attribute_map:
            free_text = unescape(
                spec_object.attribute_map[ReqIFChapterField.TEXT].value
            )
            free_texts.append(
                FreeText(
                    parent=None,
                    parts=[free_text],
                )
            )
        # Sanitize the title. Titles can also come from XHTML attributes with
        # custom newlines such as:
        #             <ATTRIBUTE-VALUE-XHTML>
        #               <THE-VALUE>
        #                 Some value
        #               </THE-VALUE>
        section_title = section_title.strip().replace("\n", " ")
        section = Section(
            parent=None,
            uid=None,
            custom_level=None,
            title=section_title,
            free_texts=free_texts,
            section_contents=[],
        )
        section.ng_level = level
        return section

    @staticmethod
    def create_requirement_from_spec_object(
        spec_object: ReqIFSpecObject,
        parent_section: Union[Section, Document],
        reqif_bundle: ReqIFBundle,
        level,
    ) -> Requirement:
        fields = []
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        attribute_map: Dict[
            str, SpecAttributeDefinition
        ] = spec_object_type.attribute_map

        foreign_key_id_or_none: Optional[str] = None
        for attribute in spec_object.attributes:
            long_name_or_none = attribute_map[
                attribute.definition_ref
            ].long_name
            if long_name_or_none is None:
                raise NotImplementedError
            field_name: str = long_name_or_none
            if attribute.attribute_type == SpecObjectAttributeType.ENUMERATION:
                assert isinstance(attribute.value, list)
                enum_values_list = list(attribute.value)
                for enum_value_idx, _ in enumerate(enum_values_list):
                    enum_values_list[enum_value_idx] = enum_values_list[
                        enum_value_idx
                    ].strip()
                enum_values = ", ".join(enum_values_list)
                fields.append(
                    RequirementField(
                        parent=None,
                        field_name=field_name,
                        field_value=enum_values,
                        field_value_multiline=None,
                        field_value_references=None,
                    )
                )
                continue
            assert isinstance(attribute.value, str)
            if long_name_or_none == "ReqIF.ForeignID":
                foreign_key_id_or_none = attribute.definition_ref
            attribute_value: Optional[str] = unescape(attribute.value)
            attribute_multiline_value = None
            if (
                "\n" in attribute_value
                or field_name == ReqIFRequirementReservedField.TEXT
                or field_name == ReqIFRequirementReservedField.COMMENT_NOTES
            ):
                attribute_multiline_value = attribute_value.lstrip()
                attribute_value = None

            if field_name in ReqIFRequirementReservedField.SET:
                field_name = REQIF_MAP_TO_SDOC_FIELD_MAP[field_name]
            fields.append(
                RequirementField(
                    parent=None,
                    field_name=field_name,
                    field_value=attribute_value,
                    field_value_multiline=attribute_multiline_value,
                    field_value_references=None,
                )
            )
        requirement = Requirement(
            parent=parent_section, requirement_type="REQUIREMENT", fields=fields
        )
        requirement.ng_level = level

        if foreign_key_id_or_none is not None:
            spec_object_parents = reqif_bundle.get_spec_object_parents(
                spec_object.identifier
            )
            parent_refs = []
            for spec_object_parent in spec_object_parents:
                parent_spec_object_parent = (
                    reqif_bundle.lookup.get_spec_object_by_ref(
                        spec_object_parent
                    )
                )

                parent_refs.append(
                    ParentReqReference(
                        requirement,
                        parent_spec_object_parent.attribute_map[
                            foreign_key_id_or_none
                        ].value,
                    )
                )
            if len(parent_refs) > 0:
                requirement_field = RequirementField(
                    parent=requirement,
                    field_name="REFS",
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=parent_refs,
                )
                fields.append(requirement_field)
                requirement.ordered_fields_lookup["REFS"] = [requirement_field]
        return requirement
