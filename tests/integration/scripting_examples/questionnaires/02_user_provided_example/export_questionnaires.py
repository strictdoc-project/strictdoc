import os
import sys
from typing import Optional

import xlsxwriter

from strictdoc import environment
from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.cli.cli_arg_parser import (
    ExportCommandConfig,
    create_sdoc_args_parser,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import GraphLinkType, TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer

CLOUD_SEC_REQ = "(Cloud Component) Security Requirements"
CONNECTIVITY_SEC_REQ = "(Connectivity or Communications Component) Security Requirements"
VEHICLE_CONN_SEC_REQ = "(Vehicle Connection Component) Security Requirements"
MOBILE_SEC_REQ = "(Mobile App Component) Security Requirements"


class ExportQuestionnaires:
    def __init__(self, project_config, parallelizer):
        self.project_config = project_config
        self.parallelizer = parallelizer
        self.traceability_index: Optional[TraceabilityIndex] = None

    def build_index(self) -> None:
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(project_config=self.project_config, parallelizer=self.parallelizer, ))
            self.traceability_index = traceability_index
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

    def export(self):
        assert self.traceability_index

        tsrm_path = os.path.join(project_config.output_dir, "tsrm_questionnaires.xlsx")

        fields = ["Criticality", "Requirement", "Yes", "In-Part", "No", "N/A", "Notes"]
        column_widths = ExcelGenerator._init_columns_width(fields)
        # extra width for Requirements text
        column_widths["Requirement"].update({"max_width": column_widths["Requirement"]["max_width"] * 5})
        # extra width for Notes responses
        column_widths["Notes"].update({"max_width": column_widths["Notes"]["max_width"] * 4})

        with xlsxwriter.Workbook(tsrm_path) as workbook:
            workbook.set_properties({"title": "Telematics Security Requirements Matrix Questionnaires",
                                     "comments": "Created with StrictDoc from sources in "
                                                 "https://github.com/nmfta-repo/nmfta-telematics_security_requirements .", })
            wrap_format = workbook.add_format({"text_wrap": True})
            for name in [MOBILE_SEC_REQ, VEHICLE_CONN_SEC_REQ, CONNECTIVITY_SEC_REQ, CLOUD_SEC_REQ]:
                document = self.find_doc(name)
                worksheet = workbook.add_worksheet(name=name[:30])
                for idx, field in enumerate(fields):
                    worksheet.write(0, idx, field)

                document_iterator = DocumentCachingIterator(document)
                nodes = []
                for node in document_iterator.all_content(print_fragments=False, print_fragments_from_files=False):
                    if isinstance(node, SDocNode):
                        if not node.is_requirement:
                            continue
                        nodes.append(node)

                # get criticality of parent req and sort on criticality of parent req
                criticality_order = {"High": 2, "Medium": 1, "Low": 0}
                nodes = sorted(nodes, key=lambda node: criticality_order[self.get_parent_criticality(node)],
                               reverse=True)

                # write each row
                for row, node in enumerate(nodes):
                    worksheet.write(row + 1, 0, str(self.get_parent_criticality(node)), wrap_format)
                    worksheet.write(row + 1, 1,
                                    str(node.get_field_by_name("STATEMENT").get_text_value().strip()) + ":\n" + str(
                                        self.get_parent_statement(node)), wrap_format)

                # add a table around all this data, allowing filtering and ordering in Excel
                worksheet.add_table(0, 0, row - 1, len(fields) - 1,
                                    {"columns": ExcelGenerator._init_headers(fields), "style": "Table Style Medium 4"})

                # enforce columns width
                ExcelGenerator._set_columns_width(workbook, worksheet, column_widths, fields)

    def get_parent_criticality(self, node):
        parent = self.get_parent(node)
        parent_criticality = parent.get_field_by_name("CRITICALITY").get_text_value().strip()
        return parent_criticality

    def get_parent_statement(self, node):
        parent = self.get_parent(node)
        parent_statement = parent.get_field_by_name("STATEMENT").get_text_value().strip()
        return parent_statement

    def get_parent(self, node) -> SDocNode:
        parent: SDocNode
        parent = self.traceability_index.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_REQUIREMENT_CONNECTIONS,
            lhs_node=node.get_field_by_name("UID").get_text_value()).parents[0][0]
        return parent

    def find_doc(self, name):
        document: SDocDocument
        applicable_doc = None
        for document in self.traceability_index.document_tree.document_list:
            if name in document.title:
                applicable_doc = document
        return applicable_doc


if __name__ == "__main__":
    parser = create_sdoc_args_parser()
    project_config: ProjectConfig

    export_config: ExportCommandConfig = parser.get_export_config()
    project_config = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=export_config.get_path_to_config(), environment=environment)
    project_config.integrate_export_config(export_config)

    parallelizer = Parallelizer.create(False)

    export_action = ExportQuestionnaires(project_config=project_config, parallelizer=parallelizer)
    export_action.build_index()
    export_action.export()
