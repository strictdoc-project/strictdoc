from typing import Dict, List, Optional, Set, Union

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionEnumeration
from reqif.models.reqif_spec_object import ReqIFSpecObject
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_specification_type import ReqIFSpecificationType
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


class P11_ReqIFToSDocConverter:  # pylint: disable=invalid-name
    @staticmethod
    def convert_reqif_bundle(reqif_bundle: ReqIFBundle) -> List[Document]:
        # TODO: Should we rather show an error that there are no specifications?
        if (
            reqif_bundle.core_content is None
            or reqif_bundle.core_content.req_if_content is None
            or len(reqif_bundle.core_content.req_if_content.specifications) == 0
        ):
            return [P11_ReqIFToSDocConverter._p11_create_document(title=None)]

        documents: List[Document] = []
        for (
            specification
        ) in reqif_bundle.core_content.req_if_content.specifications:
            # fmt: off
            document = (
                P11_ReqIFToSDocConverter._p11_create_document_from_specification(  # noqa: E501
                    specification=specification,
                    reqif_bundle=reqif_bundle,
                )
            )
            # fmt: on
            documents.append(document)
        return documents

    @staticmethod
    def _p11_create_document_from_specification(
        *,
        specification: ReqIFSpecification,
        reqif_bundle: ReqIFBundle,
    ):
        assert isinstance(reqif_bundle, ReqIFBundle)

        document = P11_ReqIFToSDocConverter._p11_create_document(
            title=specification.long_name
        )
        elements: List[GrammarElement] = []
        document.section_contents = []
        current_section = document
        used_spec_object_types_ids: Set[str] = set()

        assert reqif_bundle.core_content is not None
        assert reqif_bundle.core_content.req_if_content is not None
        assert reqif_bundle.core_content.req_if_content.spec_types is not None

        spec_types: List[
            Union[
                ReqIFSpecObjectType,
                ReqIFSpecRelationType,
                ReqIFSpecificationType,
            ]
        ] = reqif_bundle.core_content.req_if_content.spec_types

        found_section_spec_object_type: Optional[ReqIFSpecObjectType] = None
        found_requirement_spec_object_type: Optional[ReqIFSpecObjectType] = None
        for spec_type in spec_types:
            if not isinstance(spec_type, ReqIFSpecObjectType):
                continue
            spec_object_type: ReqIFSpecObjectType = spec_type
            if spec_object_type.long_name == "Heading":
                found_section_spec_object_type = spec_object_type
            elif spec_object_type.long_name in (
                "Software Requirement",
                "DCPRS",
            ):
                found_requirement_spec_object_type = spec_object_type
        assert found_section_spec_object_type is not None, (
            "Expected to find a SPEC-OBJECT-TYPE that represents a "
            "section. Spec types available in this ReqIF document: "
            f"{spec_types}"
        )
        assert found_requirement_spec_object_type is not None, (
            "Expected to find a SPEC-OBJECT-TYPE that represents a "
            "requirement. Spec types available in this ReqIF document: "
            f"{spec_types}"
        )
        used_spec_object_types_ids.add(
            found_requirement_spec_object_type.identifier
        )

        for current_hierarchy in reqif_bundle.iterate_specification_hierarchy(
            specification
        ):
            spec_object = reqif_bundle.get_spec_object_by_ref(
                current_hierarchy.spec_object
            )
            if (
                spec_object.spec_object_type
                == found_section_spec_object_type.identifier
            ):
                # fmt: off
                section = (
                    P11_ReqIFToSDocConverter._p11_create_section_from_spec_object(  # noqa: E501
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
            elif (
                spec_object.spec_object_type
                == found_requirement_spec_object_type.identifier
            ):
                # fmt: off
                requirement: Requirement = (
                    P11_ReqIFToSDocConverter
                    ._p11_create_requirement_from_spec_object(
                        spec_object=spec_object,
                        parent_section=current_section,
                        reqif_bundle=reqif_bundle,
                        level=current_hierarchy.level,
                    )
                )
                # fmt: on
                current_section.section_contents.append(requirement)
            else:
                continue  # raise NotImplementedError(spec_object) from None

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
                    P11_ReqIFToSDocConverter
                    ._p11_create_grammar_element_from_spec_object_type(
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
    def _p11_create_grammar_element_from_spec_object_type(
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
    def _p11_create_document(title: Optional[str]) -> Document:
        document_config: DocumentConfig = DocumentConfig.default_config(None)
        document_config.markup = "HTML"
        document_title = title if title else "<No title>"
        document = Document(document_title, document_config, None, [], [])
        document.grammar = DocumentGrammar.create_default(document)
        return document

    @staticmethod
    def _p11_create_section_from_spec_object(
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
    def _p11_create_requirement_from_spec_object(
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
                if attribute.attribute_type == SpecObjectAttributeType.XHTML:
                    attribute_multiline_value = attribute.value_stripped_xhtml
                    # Another strip() is hidden in .value_stripped_xhtml
                    # but doing this anyway to highlight the intention.
                    attribute_multiline_value = (
                        attribute_multiline_value.strip()
                    )
                else:
                    attribute_multiline_value = attribute_value.strip()
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
