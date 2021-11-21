from enum import Enum

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class ReqIFField(Enum):
    TYPE = "TYPE"
    UID = "UID"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"


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
            None, "Empty ReqIF document", document_config, [], []
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
        spec_object, document, level
    ) -> Requirement:
        uid = spec_object.attribute_map[ReqIFField.UID.value]
        statement = spec_object.attribute_map[ReqIFField.STATEMENT.value]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = Requirement(
            parent=document,
            statement=statement,
            statement_multiline=None,
            uid=uid,
            level=None,
            status=None,
            tags=None,
            references=[],
            title=None,
            body=None,
            rationale=None,
            rationale_multiline=None,
            comments=[],
            special_fields=None,
            requirements=None,
        )
        requirement.ng_level = level
        return requirement
