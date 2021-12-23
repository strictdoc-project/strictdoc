from enum import Enum
from typing import List

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.object_factory import SDocObjectFactory
from strictdoc.backend.dsl.models.reference import Reference
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.dsl.models.section import Section
from strictdoc.backend.dsl.models.special_field import SpecialField
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class ReqIFField(Enum):
    TYPE = "TYPE"
    UID = "UID"
    STATUS = "STATUS"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    COMMENT = "COMMENT"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ReqIFNodeType(Enum):
    SECTION = "NODE_TYPE_SECTION"
    REQUIREMENT = "NODE_TYPE_REQUIREMENT"


class StrictDocReqIFMapping:
    @staticmethod
    def create_document() -> Document:
        document_config = DocumentConfig(
            parent=None,
            version=None,
            number=None,
            special_fields=[],
            markup="Text",
            auto_levels=None,
        )
        document = Document(
            None, "Empty ReqIF document", document_config, None, [], []
        )
        return document

    @staticmethod
    def is_spec_object_section(spec_object):
        assert (
            ReqIFField.TYPE.value in spec_object.attribute_map
        ), spec_object.attribute_map

        spec_object_type = spec_object.attribute_map[ReqIFField.TYPE.value]
        return spec_object_type == ReqIFNodeType.SECTION.value

    @staticmethod
    def is_spec_object_requirement(spec_object):
        assert (
            ReqIFField.TYPE.value in spec_object.attribute_map
        ), spec_object.attribute_map

        spec_object_type = spec_object.attribute_map[ReqIFField.TYPE.value]
        return spec_object_type == ReqIFNodeType.REQUIREMENT.value

    @staticmethod
    def create_section_from_spec_object(
        spec_object: ReqIFSpecObject, level
    ) -> Section:
        title = spec_object.attribute_map[ReqIFField.TITLE.value]
        section = Section(None, None, None, title, [], [])
        section.ng_level = level
        return section

    @staticmethod
    def create_requirement_from_spec_object(
        spec_object, document, level, reqif_special_fields: List[str]
    ) -> Requirement:
        uid = spec_object.attribute_map[ReqIFField.UID.value]
        statement = spec_object.attribute_map[ReqIFField.STATEMENT.value]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = SDocObjectFactory.create_requirement(
            parent=document,
            requirement_type="REQUIREMENT",
            statement=statement,
            statement_multiline=None,
            uid=uid,
            level=None,
            tags=None,
            title=None,
            rationale=None,
            rationale_multiline=None,
            comments=[],
        )
        requirement.ng_level = level

        special_fields = []
        for field in reqif_special_fields:
            special_fields.append(
                SpecialField(
                    requirement, field, spec_object.attribute_map[field]
                )
            )
        if special_fields:
            requirement.ordered_fields_lookup["SPECIAL_FIELDS"] = [
                RequirementField(
                    parent=requirement,
                    field_name="SPECIAL_FIELDS",
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=None,
                    field_value_special_fields=special_fields,
                )
            ]

        return requirement

    @staticmethod
    def create_reference(requirement: Requirement, spec_object_parent):
        return Reference(requirement, "Parent", spec_object_parent)
