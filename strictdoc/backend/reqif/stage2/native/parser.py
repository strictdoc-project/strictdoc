from typing import Optional, List

from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionEnumeration
from reqif.models.reqif_spec_object_type import ReqIFSpecObjectType
from reqif.models.reqif_types import SpecObjectAttributeType
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    GrammarElement,
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
)
from strictdoc.backend.reqif.stage2.abstract_parser import (
    AbstractReqIFStage2Parser,
)
from strictdoc.backend.reqif.stage2.native.mapping import StrictDocReqIFMapping

DEFAULT_SDOC_GRAMMAR_FIELDS = [
    "UID",
    "LEVEL",
    "STATUS",
    "TAGS",
    "SPECIAL_FIELDS",
    "REFS",
    "TITLE",
    "STATEMENT",
    "BODY",
    "RATIONALE",
    "COMMENT",
]


class StrictDocReqIFStage2Parser(AbstractReqIFStage2Parser):
    def parse_reqif(self, reqif_bundle: ReqIFBundle):
        mapping = StrictDocReqIFMapping()

        # TODO: Should we rather show an error that there are no specifications?
        if (
            reqif_bundle.core_content is None
            or reqif_bundle.core_content.req_if_content is None
            or len(reqif_bundle.core_content.req_if_content.specifications) == 0
        ):
            return mapping.create_document(title=None)

        specification = reqif_bundle.core_content.req_if_content.specifications[
            0
        ]
        document = mapping.create_document(title=specification.long_name)

        document.section_contents = []
        current_section = document

        requirement_spec_type: Optional[ReqIFSpecObjectType] = None
        for spec_type in reqif_bundle.core_content.req_if_content.spec_types:
            if isinstance(spec_type, ReqIFSpecObjectType):
                if spec_type.identifier == "REQUIREMENT":
                    requirement_spec_type = spec_type
        if requirement_spec_type:
            attributes = list(requirement_spec_type.attribute_map.keys())
            if attributes != DEFAULT_SDOC_GRAMMAR_FIELDS:
                fields = []
                for attribute in requirement_spec_type.attribute_definitions:
                    if (
                        attribute.attribute_type
                        == SpecObjectAttributeType.STRING
                    ):
                        fields.append(
                            GrammarElementFieldString(
                                parent=None,
                                title=attribute.long_name,
                                required="True",
                            )
                        )
                    elif (
                        attribute.attribute_type
                        == SpecObjectAttributeType.ENUMERATION
                    ):
                        enum_data_type: ReqIFDataTypeDefinitionEnumeration = (
                            reqif_bundle.lookup.get_data_type_by_ref(
                                attribute.datatype_definition
                            )
                        )
                        options = list(
                            map(lambda v: v.key, enum_data_type.values)
                        )
                        if attribute.multi_valued:
                            fields.append(
                                GrammarElementFieldMultipleChoice(
                                    parent=None,
                                    title=attribute.long_name,
                                    options=options,
                                    required="True",
                                )
                            )
                        else:
                            fields.append(
                                GrammarElementFieldSingleChoice(
                                    parent=None,
                                    title=attribute.long_name,
                                    options=options,
                                    required="True",
                                )
                            )
                    else:
                        raise NotImplementedError(attribute) from None
                requirement_element = GrammarElement(
                    parent=None, tag="REQUIREMENT", fields=fields
                )
                elements: List[GrammarElement] = [requirement_element]
                grammar = DocumentGrammar(parent=document, elements=elements)
                grammar.is_default = False
                document.grammar = grammar

        for current_hierarchy in reqif_bundle.iterate_specification_hierarchy(
            specification
        ):
            spec_object = reqif_bundle.get_spec_object_by_ref(
                current_hierarchy.spec_object
            )

            if mapping.is_spec_object_section(spec_object):
                section = mapping.create_section_from_spec_object(
                    spec_object,
                    current_hierarchy.level,
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
            elif mapping.is_spec_object_requirement(spec_object):
                requirement: Requirement = (
                    mapping.create_requirement_from_spec_object(
                        spec_object=spec_object,
                        parent_section=current_section,
                        level=current_hierarchy.level,
                    )
                )
                spec_object_parents = reqif_bundle.get_spec_object_parents(
                    spec_object.identifier
                )
                parent_refs = []
                for spec_object_parent in spec_object_parents:
                    parent_refs.append(
                        mapping.create_reference(
                            requirement, spec_object_parent
                        )
                    )
                if len(parent_refs) > 0:
                    requirement_field = RequirementField(
                        parent=requirement,
                        field_name="REFS",
                        field_value=None,
                        field_value_multiline=None,
                        field_value_references=parent_refs,
                        field_value_special_fields=None,
                    )
                    # TODO: This is extremely wrong.
                    requirement.fields.append(requirement_field)
                    requirement.ordered_fields_lookup["REFS"] = [
                        requirement_field
                    ]
                current_section.section_contents.append(requirement)
            else:
                raise NotImplementedError(spec_object) from None

        return document
