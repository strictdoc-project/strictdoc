from enum import Enum

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.object_factory import SDocObjectFactory
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class ReqIFField(Enum):
    TYPE = "_stype_requirement_kind"
    UID = "_stype_requirement_requirementID"
    TITLE = "_stype_requirement_PlainText"
    STATEMENT = "_stype_requirement_PlainText"


class ReqIFNodeType(Enum):
    SECTION = "_enumVal_Kind_HEADING"
    REQUIREMENT = "_enumVal_Kind_ORDINARY"
    NOTE = "_enumVal_Kind_NOTE"
    TABLE = "_enumVal_Kind_TABLE"
    FIGURE = "_enumVal_Kind_FIGURE"


class DoorsMapping:
    # {
    #   '_stype_requirement_WordTraceId': '16',
    #   '_stype_requirement_atomic': 'true',
    #   '_stype_requirement_RichText': 'ABC',
    #   '_stype_requirement_Legal-Obligation':
    #       '_enumVal_LegalObligation_UNKNOWN',
    #   '_stype_requirement_PlainText':
    #       'System Requirements Specification Chapter 3 Principles',
    #   '_stype_requirement_implement': 'false',
    #   '_stype_requirement_implementerEnhanced': 'ABC',
    #   '_stype_requirement_ListNumberText': '',
    #   '_stype_requirement_requirementID': '3',
    #   '_stype_requirement_kind': '_enumVal_Kind_HEADING'
    # }

    @staticmethod
    def create_document() -> Document:
        document_config = DocumentConfig(
            parent=None,
            version=None,
            number=None,
            special_fields=[],
            markup="HTML",
            auto_levels="Off",
        )
        document = Document(
            None, "Empty ReqIF document", document_config, None, [], []
        )
        assert not document.config.auto_levels
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
        return spec_object_type in (
            ReqIFNodeType.REQUIREMENT.value,
            ReqIFNodeType.NOTE.value,
        )

    @staticmethod
    def is_spec_object_table(spec_object):
        assert (
            ReqIFField.TYPE.value in spec_object.attribute_map
        ), spec_object.attribute_map

        spec_object_type = spec_object.attribute_map[ReqIFField.TYPE.value]
        return spec_object_type == ReqIFNodeType.TABLE.value

    @staticmethod
    def is_spec_object_figure(spec_object):
        assert (
            ReqIFField.TYPE.value in spec_object.attribute_map
        ), spec_object.attribute_map

        spec_object_type = spec_object.attribute_map[ReqIFField.TYPE.value]
        return spec_object_type == ReqIFNodeType.FIGURE.value

    @staticmethod
    def create_section_from_spec_object(
        spec_object: ReqIFSpecObject, level
    ) -> Section:
        uid = spec_object.attribute_map[ReqIFField.UID.value]
        title = spec_object.attribute_map[ReqIFField.TITLE.value]
        section = Section(
            parent=None,
            uid=uid,
            level=uid,
            title=title,
            free_texts=[],
            section_contents=[],
        )
        section.ng_level = level
        return section

    @staticmethod
    def create_requirement_from_spec_object(
        spec_object, document, level
    ) -> Requirement:
        uid = spec_object.attribute_map[ReqIFField.UID.value]
        statement = spec_object.attribute_map[ReqIFField.STATEMENT.value]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = SDocObjectFactory.create_requirement(
            parent=document,
            requirement_type="REQUIREMENT",
            uid=uid,
            level=uid,
            title=None,
            statement=None,
            statement_multiline=statement,
            tags=None,
            rationale=None,
            rationale_multiline=None,
            comments=[],
        )
        requirement.ng_level = level
        return requirement
