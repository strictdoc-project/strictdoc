import os
from pathlib import Path

from strictdoc.backend.dsl.writer import SDWriter
from strictdoc.cli.cli_arg_parser import ImportCommandConfig
from strictdoc.imports.reqif.mapping import (
    DoorsMapping,
    StrictDocReqIFMapping,
    MagnaReqIFMapping,
    AbstractMapping,
)
from strictdoc.imports.reqif.stage1.models.reqif_bundle import ReqIFBundle
from strictdoc.imports.reqif.stage1.reqif_stage1_parser import ReqIFStage1Parser


class ReqIFImport:
    @staticmethod
    def import_from_file(import_config: ImportCommandConfig):
        mapping = (
            DoorsMapping()
            if import_config.mapping == "doors"
            else MagnaReqIFMapping()
            if import_config.mapping == "magna"
            else StrictDocReqIFMapping()
        )
        reqif_bundle = ReqIFStage1Parser.parse(import_config.input_path)

        document = ReqIFImport.parse_reqif(reqif_bundle, mapping)

        document_content = SDWriter().write(document)
        output_folder = os.path.dirname(import_config.output_path)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        with open(
            import_config.output_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)

    @staticmethod
    def parse_reqif(reqif_bundle: ReqIFBundle, mapping: AbstractMapping):
        document = mapping.create_document()
        # TODO: Should we rather show an error that there are no specifications?
        if len(reqif_bundle.specifications) == 0:
            return document

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
                    for i in range(
                        0, current_section.ng_level - current_hierarchy.level
                    ):
                        current_section = current_section.parent
                    current_section.section_contents.append(section)
                else:
                    raise NotImplementedError
            elif mapping.is_spec_object_requirement(spec_object):
                requirement = mapping.create_requirement_from_spec_object(
                    spec_object,
                    document,
                    current_hierarchy.level,
                )
                current_section.section_contents.append(requirement)
            else:
                continue

        return document
