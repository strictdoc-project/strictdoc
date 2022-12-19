from typing import Optional, List, Set

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionEnumeration
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
)
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.import_.reqif_to_sdoc_factory import (
    ReqIFToSDocFactory,
)
from strictdoc.backend.reqif.sdoc_reqif_fields import (
    REQIF_MAP_TO_SDOC_FIELD_MAP,
    ReqIFChapterField,
    DEFAULT_SDOC_GRAMMAR_FIELDS,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    GrammarElement,
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
)


class ReqIFToSDocConverter:
    mapping = ReqIFToSDocFactory()

    @staticmethod
    def convert_reqif_bundle(reqif_bundle: ReqIFBundle) -> List[Document]:
        # TODO: Should we rather show an error that there are no specifications?
        if (
            reqif_bundle.core_content is None
            or reqif_bundle.core_content.req_if_content is None
            or len(reqif_bundle.core_content.req_if_content.specifications) == 0
        ):
            return [ReqIFToSDocConverter.mapping.create_document(title=None)]

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
    def _get_spec_object_type_by_ref(
        *,
        reqif_bundle: ReqIFBundle,
        spec_object_type_id: str,
    ) -> Optional[ReqIFSpecObjectType]:
        for spec_type in reqif_bundle.core_content.req_if_content.spec_types:
            if (
                isinstance(spec_type, ReqIFSpecObjectType)
                and spec_type.identifier == spec_object_type_id
            ):
                return spec_type
        return None

    @staticmethod
    def _create_document_from_reqif_specification(
        *,
        specification: ReqIFSpecification,
        reqif_bundle: ReqIFBundle,
    ):
        document = ReqIFToSDocConverter.mapping.create_document(
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
            if ReqIFToSDocConverter.mapping.is_spec_object_section(
                spec_object,
                reqif_bundle=reqif_bundle,
            ):
                # fmt: off
                section = (
                    ReqIFToSDocConverter
                    .mapping.create_section_from_spec_object(
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
            elif ReqIFToSDocConverter.mapping.is_spec_object_requirement(
                spec_object
            ):
                # fmt: off
                requirement: Requirement = (
                    ReqIFToSDocConverter
                    .mapping
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
            spec_object_type: ReqIFSpecObjectType = (
                ReqIFToSDocConverter._get_spec_object_type_by_ref(
                    reqif_bundle=reqif_bundle,
                    spec_object_type_id=used_spec_object_type_id,
                )
            )

            attributes = list(spec_object_type.attribute_map.keys())
            if attributes != DEFAULT_SDOC_GRAMMAR_FIELDS:
                # fmt: off
                grammar_element = (
                    ReqIFToSDocConverter
                    .create_grammar_element_from_reqif_spec_object_type(
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
    def create_grammar_element_from_reqif_spec_object_type(
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
                if attribute.multi_valued:
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
            else:
                raise NotImplementedError(attribute) from None
        requirement_element = GrammarElement(
            parent=None, tag="REQUIREMENT", fields=fields
        )
        return requirement_element
