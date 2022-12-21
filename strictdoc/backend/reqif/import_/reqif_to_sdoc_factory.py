from typing import Optional, Union, Dict

from reqif.models.reqif_spec_object import ReqIFSpecObject
from reqif.models.reqif_spec_object_type import SpecAttributeDefinition
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    ReqIFChapterField,
    REQIF_MAP_TO_SDOC_FIELD_MAP,
    ReqIFRequirementReservedField,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section, FreeText
from strictdoc.helpers.string import unescape


class ReqIFToSDocFactory:
    @staticmethod
    def create_document(title: Optional[str]) -> Document:
        document_config = DocumentConfig.default_config(None)
        document_title = title if title else "<No title>"
        document = Document(document_title, document_config, None, [], [])
        document.grammar = DocumentGrammar.create_default(document)
        return document

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
            if long_name_or_none == "ReqIF.ForeignID":
                foreign_key_id_or_none = attribute.definition_ref
            field_name: str = long_name_or_none
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
