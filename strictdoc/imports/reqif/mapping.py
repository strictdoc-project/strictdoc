from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import Section
from strictdoc.imports.reqif.stage1.models.reqif_spec_object import (
    ReqIFSpecObject,
)


class AbstractMapping:
    def create_document(self) -> Document:
        raise NotImplementedError

    def is_spec_object_section(self, spec_object):
        raise NotImplementedError

    def is_spec_object_requirement(self, spec_object):
        raise NotImplementedError

    def create_section_from_spec_object(
        self, spec_object: ReqIFSpecObject, level
    ) -> Section:
        raise NotImplementedError

    def create_requirement_from_spec_object(
        self, spec_object, document, level
    ) -> Requirement:
        raise NotImplementedError


class StrictDocReqIFMapping(AbstractMapping):
    SPEC_OBJECT_FIELD_MAPPING = {
        "TYPE": "TYPE",
        "UID": "UID",
        "TITLE": "TITLE",
        "STATEMENT": "STATEMENT",
    }
    SPEC_OBJECT_TYPE_MAPPING = {
        "NODE_TYPE_SECTION": "NODE_TYPE_SECTION",
        "NODE_TYPE_REQUIREMENT": "NODE_TYPE_REQUIREMENT",
    }

    def create_document(self) -> Document:
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

    def is_spec_object_section(self, spec_object):
        type_field_key = self.SPEC_OBJECT_FIELD_MAPPING["TYPE"]
        if type_field_key not in spec_object.attribute_map:
            return False
        spec_object_type = spec_object.attribute_map[type_field_key]
        return spec_object_type == "NODE_TYPE_SECTION"

    def is_spec_object_requirement(self, spec_object):
        type_field_key = self.SPEC_OBJECT_FIELD_MAPPING["TYPE"]
        if type_field_key not in spec_object.attribute_map:
            return False
        spec_object_type = spec_object.attribute_map[type_field_key]
        return spec_object_type == "NODE_TYPE_REQUIREMENT"

    def create_section_from_spec_object(
        self, spec_object: ReqIFSpecObject, level
    ) -> Section:
        title = spec_object.attribute_map[
            self.SPEC_OBJECT_FIELD_MAPPING["TITLE"]
        ]
        section = Section(None, None, None, title, [], [])
        section.ng_level = level
        return section

    def create_requirement_from_spec_object(
        self, spec_object, document, level
    ) -> Requirement:
        uid = spec_object.attribute_map[self.SPEC_OBJECT_FIELD_MAPPING["UID"]]
        statement = spec_object.attribute_map[
            self.SPEC_OBJECT_FIELD_MAPPING["STATEMENT"]
        ]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = Requirement(
            parent=document,
            statement=statement,
            statement_multiline=None,
            uid=uid,
            level=None,
            status=None,
            tags=None,
            references=None,
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


class DoorsMapping(AbstractMapping):
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
    SPEC_OBJECT_FIELD_MAPPING = {
        "TYPE": "_stype_requirement_kind",
        "UID": "_stype_requirement_requirementID",
        "TITLE": "_stype_requirement_PlainText",
        "STATEMENT": "_stype_requirement_PlainText",
    }
    SPEC_OBJECT_TYPE_MAPPING = {
        "NODE_TYPE_SECTION": "_enumVal_Kind_HEADING",
        "NODE_TYPE_REQUIREMENT": "_enumVal_Kind_ORDINARY",
    }

    def create_document(self):
        document_config = DocumentConfig(
            parent=None,
            version=None,
            number=None,
            special_fields=[],
            markup="Text",
            auto_levels="Off",
        )
        document = Document(
            None, "Empty ReqIF document", document_config, [], []
        )
        assert not document.config.auto_levels
        return document

    def is_spec_object_section(self, spec_object):
        type_field_key = self.SPEC_OBJECT_FIELD_MAPPING["TYPE"]
        if type_field_key not in spec_object.attribute_map:
            return False
        spec_object_type = spec_object.attribute_map[type_field_key]
        return (
            spec_object_type
            == self.SPEC_OBJECT_TYPE_MAPPING["NODE_TYPE_SECTION"]
        )

    def is_spec_object_requirement(self, spec_object):
        type_field_key = self.SPEC_OBJECT_FIELD_MAPPING["TYPE"]
        if type_field_key not in spec_object.attribute_map:
            return False
        spec_object_type = spec_object.attribute_map[type_field_key]
        return (
            spec_object_type
            == self.SPEC_OBJECT_TYPE_MAPPING["NODE_TYPE_REQUIREMENT"]
        )

    def create_section_from_spec_object(
        self, spec_object: ReqIFSpecObject, level
    ) -> Section:
        uid = spec_object.attribute_map[self.SPEC_OBJECT_FIELD_MAPPING["UID"]]

        title = spec_object.attribute_map[
            self.SPEC_OBJECT_FIELD_MAPPING["TITLE"]
        ]
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

    def create_requirement_from_spec_object(
        self, spec_object, document, level
    ) -> Requirement:
        uid = spec_object.attribute_map[self.SPEC_OBJECT_FIELD_MAPPING["UID"]]
        statement = spec_object.attribute_map[
            self.SPEC_OBJECT_FIELD_MAPPING["STATEMENT"]
        ]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = Requirement(
            parent=document,
            statement=statement,
            statement_multiline=None,
            uid=uid,
            level=uid,
            status=None,
            tags=None,
            references=None,
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


class MagnaReqIFMapping(AbstractMapping):
    # ReqIFSpecObject(
    #   identifier: _eDO24C2IEeyvlO4vtsM_UA,
    #   attribute_map: {
    #       '_FEHY0C2GEeyvlO4vtsM_UA': 'SR001',
    #       '_OlZh0C2GEeyvlO4vtsM_UA': 'Draft',
    #       '_KMVP0C2GEeyvlO4vtsM_UA': 'Software',
    #       '_MZGCUC2GEeyvlO4vtsM_UA': 'none',
    #       '_Hx6b0C2GEeyvlO4vtsM_UA': 'The import function shall import a
    #           .reqif file and convert it to an .sdoc file.'
    #   }
    # )
    SPEC_OBJECT_FIELD_MAPPING = {
        "_dSe2wC2FEeyvlO4vtsM_UA": {
            "UID": "_oE860C2FEeyvlO4vtsM_UA",
            "STATEMENT": "_rWmRwC2FEeyvlO4vtsM_UA",
        },
        "_gV9O0C2FEeyvlO4vtsM_UA": {
            "UID": "_FEHY0C2GEeyvlO4vtsM_UA",
            "STATEMENT": "_Hx6b0C2GEeyvlO4vtsM_UA",
        },
        "_BSKKIC2GEeyvlO4vtsM_UA": {
            "UID": "_BSKKIS2GEeyvlO4vtsM_UA",
            "STATEMENT": "_BSKKJi2GEeyvlO4vtsM_UA",
        },
    }

    def create_document(self):
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

    def is_spec_object_section(self, spec_object):
        return False

    def is_spec_object_requirement(self, spec_object):
        return True

    def create_section_from_spec_object(
        self, spec_object: ReqIFSpecObject, level
    ) -> Section:
        raise NotImplementedError

    def create_requirement_from_spec_object(
        self, spec_object, document, level
    ) -> Requirement:
        object_type_mapping = self.SPEC_OBJECT_FIELD_MAPPING[
            spec_object.spec_object_type
        ]
        uid = spec_object.attribute_map[object_type_mapping["UID"]]
        statement = spec_object.attribute_map[object_type_mapping["STATEMENT"]]
        statement = statement if statement else "<STATEMENT MISSING>"

        requirement = Requirement(
            parent=document,
            statement=statement,
            statement_multiline=None,
            uid=uid,
            level=None,
            status=None,
            tags=None,
            references=None,
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
