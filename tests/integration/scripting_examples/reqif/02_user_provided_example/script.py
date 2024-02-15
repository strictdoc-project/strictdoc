import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionEnumeration
from reqif.models.reqif_spec_object import ReqIFSpecObject
from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.parser import ReqIFParser
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.sdoc_reqif_fields import (
    DEFAULT_SDOC_GRAMMAR_FIELDS,
    ReqIFChapterField,
    ReqIFRequirementReservedField,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.node import Requirement, SDocNodeField
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldString,
)
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.helpers.string import unescape


class AUREON_NodeType(str, Enum):
    DEFINITION = "Definition"
    HEADING = "Heading"
    INFORMATION = "Information"
    REQUIREMENT = "Requirement"


AUREON_FIELDS_MAP = {
    "Artifact Type": "ARTIFACT_TYPE",
    "Primary Text": "PRIMARY_TEXT",

    "AuReOn-Source ID": "AUREON_SOURCE_ID",
    "Cert-Tag": "CERT_TAG",
    "Link to Regulation and SI": "LINK_TO_REGULATION_AND_SI",
    "Version Number": "VERSION_NUMBER",
    "Markets/Regions": "MARKETS_AND_REGIONS",

    "Effective Date": "EFFECTIVE_DATE",
    "Effective Date - Remarks": "EFFECTIVE_DATE_REMARKS",

    "Supplemental Information": "SUPPLEMENTAL_INFORMATION",
    "Supplemental Information - Labels": "SUPPLEMENTAL_INFORMATION_LABELS",
    "Supplemental Information - Modification Date": "SUPPLEMENTAL_INFORMATION_MODIFICATION_DATE",

    "Regulation Number": "REGULATION_NUMBER",
    "Regulation Status": "REGULATION_STATUS",

    "Technical Compliance Relevance": "TECHNICAL_COMPLIANCE_RELEVANCE",
    "Vehicle Category": "VEHICLE_CATEGORY",
}


class AUREON_ReqIFSchemaHelper:
    def __init__(self, reqif_bundle: ReqIFBundle):
        fragment_spec_type = None
        artifact_type_spec_object_type_attribute = None
        artifact_type_datatype = None
        datatype_heading = None
        datatype_information = None
        datatype_definition = None
        datatype_requirement = None

        for spec_type in reqif_bundle.core_content.req_if_content.spec_types:
            if spec_type.long_name == "Fragment":
                fragment_spec_type = spec_type
                for spec_object_type_attribute in spec_type.attribute_definitions:
                    if spec_object_type_attribute.long_name == "Artifact Type":
                        artifact_type_spec_object_type_attribute = spec_object_type_attribute
                        break
                else:
                    raise NotImplementedError(
                        'Could not find "Artifact Type" spec object type attribute.'
                    )
                break
        else:
            raise NotImplementedError('Could not find "Fragment" spec type.')

        for data_type in reqif_bundle.core_content.req_if_content.data_types:
            if data_type.identifier == artifact_type_spec_object_type_attribute.datatype_definition:
                artifact_type_datatype = data_type
                for datatype_value in data_type.values:
                    if datatype_value.long_name == AUREON_NodeType.HEADING:
                        datatype_heading = datatype_value
                    elif datatype_value.long_name == AUREON_NodeType.DEFINITION:
                        datatype_definition = datatype_value
                    elif datatype_value.long_name == AUREON_NodeType.INFORMATION:
                        datatype_information = datatype_value
                    elif datatype_value.long_name == AUREON_NodeType.REQUIREMENT:
                        datatype_requirement = datatype_value
                    else:
                        raise NotImplementedError("Must not reach here.")
                break
        else:
            raise NotImplementedError("Could not find \"Artifact Type\"'s attribute data type.")

        self.fragment_spec_type = fragment_spec_type
        self.artifact_type_spec_object_type_attribute = artifact_type_spec_object_type_attribute
        self.artifact_type_datatype = artifact_type_datatype
        self.datatype_heading = datatype_heading
        self.datatype_definition = datatype_definition
        self.datatype_information = datatype_information
        self.datatype_requirement = datatype_requirement

    def get_spec_object_type(self, spec_object) -> AUREON_NodeType:
        assert isinstance(spec_object, ReqIFSpecObject), spec_object
        assert spec_object.spec_object_type == self.fragment_spec_type.identifier

        for attribute in spec_object.attributes:
            if attribute.definition_ref == self.artifact_type_spec_object_type_attribute.identifier:
                data_type_ref = attribute.value[0]
                if data_type_ref == self.datatype_heading.identifier:
                    return AUREON_NodeType.HEADING
                if data_type_ref == self.datatype_information.identifier:
                    return AUREON_NodeType.INFORMATION
                if data_type_ref == self.datatype_definition.identifier:
                    return AUREON_NodeType.DEFINITION
                if data_type_ref == self.datatype_requirement.identifier:
                    return AUREON_NodeType.REQUIREMENT
        raise NotImplementedError("Must not reach here.")


class AUREON_ReqIFToSDocConverter:  # pylint: disable=invalid-name
    @staticmethod
    def convert_reqif_bundle(
        reqif_bundle: ReqIFBundle,
    ) -> List[Document]:
        # TODO: Should we rather show an error that there are no specifications?
        if (
            reqif_bundle.core_content is None
            or reqif_bundle.core_content.req_if_content is None
            or len(reqif_bundle.core_content.req_if_content.specifications) == 0
        ):
            return [AUREON_ReqIFToSDocConverter.create_document(title=None)]

        # Analyze the ReqIF bundle to extract some useful information before
        # the conversion ReqIF-to-SDoc starts.
        # This information will be useful when converting specific spec objects.
        helper = AUREON_ReqIFSchemaHelper(reqif_bundle)

        documents: List[Document] = []
        for (
            specification
        ) in reqif_bundle.core_content.req_if_content.specifications:
            document = AUREON_ReqIFToSDocConverter.create_document_from_reqif_specification(
                specification=specification,
                reqif_bundle=reqif_bundle,
                helper=helper,
            )
            documents.append(document)
        return documents

    @staticmethod
    def get_requirement_field_from_reqif(field_name: str) -> str:
        return AUREON_FIELDS_MAP[field_name]

    @staticmethod
    def is_spec_object_section(
        spec_object: ReqIFSpecObject,
        reqif_bundle: ReqIFBundle,  # noqa: ARG004
        helper: AUREON_ReqIFSchemaHelper
    ):
        return helper.get_spec_object_type(spec_object) == AUREON_NodeType.HEADING

    @staticmethod
    def is_spec_object_requirement(
        spec_object, reqif_bundle, helper: AUREON_ReqIFSchemaHelper  # noqa: ARG004
    ):
        return helper.get_spec_object_type(spec_object) == AUREON_NodeType.REQUIREMENT

    @staticmethod
    def is_spec_object_definition(spec_object, reqif_bundle, helper):  # noqa: ARG004
        return helper.get_spec_object_type(spec_object) == AUREON_NodeType.DEFINITION

    @staticmethod
    def create_document_from_reqif_specification(
        *,
        specification: ReqIFSpecification,
        reqif_bundle: ReqIFBundle,
        helper: AUREON_ReqIFSchemaHelper,
    ):
        document = AUREON_ReqIFToSDocConverter.create_document(
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
            print(  # noqa: T201
                f"NODE: {current_hierarchy.level} {helper.get_spec_object_type(spec_object)} {spec_object}"
            )
            used_spec_object_types_ids.add(spec_object.spec_object_type)
            if AUREON_ReqIFToSDocConverter.is_spec_object_section(
                spec_object,
                reqif_bundle=reqif_bundle,
                helper=helper,
            ):
                section = (
                    AUREON_ReqIFToSDocConverter.create_section_from_spec_object(
                        spec_object,
                        current_hierarchy.level,
                        reqif_bundle=reqif_bundle,
                    )
                )
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
            elif AUREON_ReqIFToSDocConverter.is_spec_object_requirement(
                spec_object, reqif_bundle, helper
            ):
                requirement: Requirement = AUREON_ReqIFToSDocConverter.create_requirement_from_spec_object(
                    spec_object=spec_object,
                    parent_section=current_section,
                    reqif_bundle=reqif_bundle,
                    level=current_hierarchy.level,
                )
                current_section.section_contents.append(requirement)
            elif AUREON_ReqIFToSDocConverter.is_spec_object_definition(
                spec_object, reqif_bundle, helper
            ):
                # SKIP definitions for now.
                continue
            else:
                raise NotImplementedError(spec_object) from None

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
                grammar_element = AUREON_ReqIFToSDocConverter.create_grammar_element_from_spec_object_type(
                    spec_object_type=spec_object_type,
                    reqif_bundle=reqif_bundle,
                )
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
            field_name = AUREON_ReqIFToSDocConverter.get_requirement_field_from_reqif(
                attribute.long_name
            )
            # Chapter name is a reserved field for sections.
            if field_name == ReqIFChapterField.CHAPTER_NAME:
                continue
            if attribute.attribute_type == SpecObjectAttributeType.STRING:
                fields.append(
                    GrammarElementFieldString(
                        parent=None,
                        title=field_name,
                        human_title=None,
                        required="False",
                    )
                )
            elif attribute.attribute_type == SpecObjectAttributeType.XHTML:
                fields.append(
                    GrammarElementFieldString(
                        parent=None,
                        title=field_name,
                        human_title=None,
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
                            human_title=None,
                            options=options,
                            required="False",
                        )
                    )
                else:
                    fields.append(
                        GrammarElementFieldSingleChoice(
                            parent=None,
                            title=field_name,
                            human_title=None,
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
            parent=None, tag="REQUIREMENT", fields=fields, relations=[]
        )
        return requirement_element

    @staticmethod
    def create_document(title: Optional[str]) -> Document:
        document_config = DocumentConfig.default_config(None)
        document_title = title if title else "<No title>"
        document = Document(
            None, document_title, document_config, None, None, None, [], []
        )
        document.grammar = DocumentGrammar.create_default(document)
        return document

    @staticmethod
    def create_section_from_spec_object(
        spec_object: ReqIFSpecObject, level, reqif_bundle: ReqIFBundle
    ) -> Section:
        spec_object_type = reqif_bundle.lookup.get_spec_type_by_ref(
            spec_object.spec_object_type
        )
        primary_text_attribute = None
        for spec_object_type_attribute_ in spec_object_type.attribute_definitions:
            if spec_object_type_attribute_.long_name == "Primary Text":
                primary_text_attribute = spec_object_type_attribute_
                break
        else:
            raise NotImplementedError

        section_title = None
        for attribute in spec_object.attributes:
            spec_object_type_ref = attribute.definition_ref
            if spec_object_type_ref == primary_text_attribute.identifier:
                section_title = attribute.value_stripped_xhtml
                break
        else:
            raise NotImplementedError

        # Sanitize the title. Titles can also come from XHTML attributes with
        # custom newlines such as:
        #             <ATTRIBUTE-VALUE-XHTML>
        #               <THE-VALUE>
        #                 Some value
        #               </THE-VALUE>
        section_title = section_title.strip().replace("\n", " ")
        section = Section(
            parent=None,
            mid=None,
            uid=None,
            custom_level=None,
            title=section_title,
            requirement_prefix=None,
            free_texts=[],
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
                sdoc_field_name = AUREON_ReqIFToSDocConverter.get_requirement_field_from_reqif(
                    field_name,
                )
                enum_values_resolved = []
                for attribute_definition_ in spec_object_type.attribute_definitions:
                    if attribute.definition_ref == attribute_definition_.identifier:
                        datatype_definition = attribute_definition_.datatype_definition

                        datatype: ReqIFDataTypeDefinitionEnumeration = reqif_bundle.lookup.get_data_type_by_ref(datatype_definition)

                        enum_values_list = list(attribute.value)
                        for enum_value in enum_values_list:
                            enum_values_resolved.append(datatype.values_map[enum_value].key)

                        break
                else:
                    raise NotImplementedError

                enum_values = ", ".join(enum_values_resolved)
                fields.append(
                    SDocNodeField(
                        parent=None,
                        field_name=sdoc_field_name,
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

            sdoc_field_name = AUREON_ReqIFToSDocConverter.get_requirement_field_from_reqif(
                field_name,
            )
            fields.append(
                SDocNodeField(
                    parent=None,
                    field_name=sdoc_field_name,
                    field_value=attribute_value,
                    field_value_multiline=attribute_multiline_value,
                    field_value_references=None,
                )
            )
        requirement = Requirement(
            parent=parent_section, requirement_type="REQUIREMENT", mid=None, fields=fields
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
                requirement_field = SDocNodeField(
                    parent=requirement,
                    field_name="REFS",
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=parent_refs,
                )
                fields.append(requirement_field)
                requirement.ordered_fields_lookup["REFS"] = [requirement_field]
        return requirement


def main():
    reqif_bundle: ReqIFBundle = ReqIFParser.parse(
        "sample.reqif"
    )

    converter = AUREON_ReqIFToSDocConverter()
    documents: List[Document] = converter.convert_reqif_bundle(reqif_bundle)

    document = documents[0]

    document_content = SDWriter().write(document)
    output_folder = os.path.join(os.getcwd(), "Output")
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    with open(
        os.path.join(output_folder, "sample.sdoc"), "w", encoding="utf8"
    ) as output_file:
        output_file.write(document_content)


if __name__ == "__main__":
    main()
