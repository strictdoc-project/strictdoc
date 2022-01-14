from typing import Optional, Union

from reqif.models.reqif_spec_object import ReqIFSpecObject
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    ReqIFChapterField,
    REQIF_MAP_TO_SDOC_FIELD_MAP,
    ReqIFRequirementReservedField,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.reference import Reference
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section, FreeText
from strictdoc.helpers.string import unescape


class ReqIFToSDocConverter:
    @staticmethod
    def create_document(title: Optional[str]) -> Document:
        document_config = DocumentConfig(
            parent=None,
            version=None,
            number=None,
            special_fields=[],
            markup=None,
            auto_levels=None,
        )
        document_title = title if title else "<No title>"
        document = Document(None, document_title, document_config, None, [], [])
        document.grammar = DocumentGrammar.create_default(document)
        return document

    @staticmethod
    def is_spec_object_section(
        spec_object: ReqIFSpecObject, reqif_bundle: ReqIFBundle
    ):
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        attribute_map = spec_object_type.attribute_map
        for attribute in spec_object.attributes:
            field_name = attribute_map[attribute.definition_ref]
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                return True
        return False

    @staticmethod
    def is_spec_object_requirement(_):
        return True

    @staticmethod
    def create_section_from_spec_object(
        spec_object: ReqIFSpecObject, level, reqif_bundle: ReqIFBundle
    ) -> Section:
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        attribute_map = spec_object_type.attribute_map
        section_title = None
        for attribute in spec_object.attributes:
            field_name = attribute_map[attribute.definition_ref]
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                section_title = attribute.value
                break
        else:
            raise NotImplementedError

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
        section = Section(
            parent=None,
            uid=None,
            level=None,
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
        attribute_map = spec_object_type.attribute_map
        for attribute in spec_object.attributes:
            field_name = attribute_map[attribute.definition_ref]
            attribute_value = unescape(attribute.value)
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
                    field_value_special_fields=None,
                )
            )
        requirement = Requirement(
            parent=parent_section, requirement_type="REQUIREMENT", fields=fields
        )

        requirement.ng_level = level
        return requirement

    @staticmethod
    def create_reference(requirement: Requirement, spec_object_parent):
        return Reference(requirement, "Parent", spec_object_parent)
