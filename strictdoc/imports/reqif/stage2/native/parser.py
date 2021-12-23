from typing import List

from strictdoc.backend.dsl.models.config_special_field import ConfigSpecialField
from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    RequirementField,
)
from strictdoc.backend.dsl.models.section import Section
from strictdoc.imports.reqif.stage1.models.reqif_bundle import ReqIFBundle
from strictdoc.imports.reqif.stage2.abstract_parser import (
    AbstractReqIFStage2Parser,
)
from strictdoc.imports.reqif.stage2.native.mapping import (
    StrictDocReqIFMapping,
    ReqIFField,
)


class StrictDocReqIFStage2Parser(AbstractReqIFStage2Parser):
    def parse_reqif(self, reqif_bundle: ReqIFBundle):
        mapping = StrictDocReqIFMapping()
        document = mapping.create_document()
        # TODO: Should we rather show an error that there are no specifications?
        if len(reqif_bundle.specifications) == 0:
            return document

        native_fields = ReqIFField.list()
        special_fields: List[str] = []
        if len(reqif_bundle.spec_object_types) > 0:
            for field in reqif_bundle.spec_object_types[0].attribute_map:
                if field not in native_fields:
                    special_fields.append(field)
                    special_field = ConfigSpecialField(
                        document.config, field, "String", False
                    )
                    document.config.special_fields.append(special_field)

        specification = reqif_bundle.specifications[0]

        document.section_contents = []
        current_section = document

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
                        spec_object,
                        document,
                        current_hierarchy.level,
                        special_fields,
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
                    requirement.ordered_fields_lookup["REFS"] = [
                        RequirementField(
                            parent=requirement,
                            field_name="REFS",
                            field_value=None,
                            field_value_multiline=None,
                            field_value_references=parent_refs,
                            field_value_special_fields=None,
                        )
                    ]
                current_section.section_contents.append(requirement)
            else:
                continue

        return document
