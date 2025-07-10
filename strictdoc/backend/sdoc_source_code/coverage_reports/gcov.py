"""
@relation(SDOC-SRS-144, scope=file)
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    FileEntry,
    FileEntryFormat,
    FileReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.file_tree import File
from strictdoc.core.project_config import ProjectConfig


@dataclass
class GCovStatsObject:
    total_number_of_covered_functions: int = 0
    total_number_of_non_covered_functions: int = 0

    def add_function(self, covered: bool) -> None:
        if covered:
            self.total_number_of_covered_functions += 1
        else:
            self.total_number_of_non_covered_functions += 1


class GCovJSONReader:
    @classmethod
    def read_from_file(
        cls: "GCovJSONReader", doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        with open(doc_file.full_path, encoding="UTF-8") as file:
            content = file.read()
        return cls.read_from_string(content, doc_file, project_config)

    @classmethod
    def read_from_string(
        cls: "GCovJSONReader",
        content: str,
        doc_file: File,  # noqa: ARG003
        project_config: ProjectConfig,  # noqa: ARG003
    ) -> SDocDocument:
        if len(content) == 0:
            raise RuntimeError("Document is empty")
        try:
            json_content = json.loads(content)
        except Exception as exception:  # pylint: disable=broad-except
            raise RuntimeError(str(exception)) from None

        document = SDocDocument(
            mid=None,
            title="Code coverage report",
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )
        document.ng_including_document_reference = DocumentReference()
        grammar = DocumentGrammar.create_for_test_report(document)
        document.grammar = grammar
        document.config.requirement_style = "Table"

        stats = GCovStatsObject()

        """
        Parse individual <testcase> elements.
        """

        json_files = json_content["files"]
        for json_file_ in json_files:
            json_file_name = json_file_["file"]

            file_section = SDocSection(
                parent=document,
                mid=None,
                uid=None,
                custom_level=None,
                title=json_file_name,
                requirement_prefix=None,
                section_contents=[],
            )
            file_section.ng_including_document_reference = DocumentReference()
            file_section.ng_document_reference = DocumentReference()
            file_section.ng_document_reference.set_document(document)
            document.section_contents.append(file_section)

            covered_functions_section = SDocSection(
                parent=document,
                mid=None,
                uid=None,
                custom_level=None,
                title="Covered functions",
                requirement_prefix=None,
                section_contents=[],
            )
            covered_functions_section.ng_including_document_reference = (
                DocumentReference()
            )
            covered_functions_section.ng_document_reference = (
                DocumentReference()
            )
            covered_functions_section.ng_document_reference.set_document(
                document
            )
            file_section.section_contents.append(covered_functions_section)

            non_covered_functions_section = SDocSection(
                parent=document,
                mid=None,
                uid=None,
                custom_level=None,
                title="Non-covered functions",
                requirement_prefix=None,
                section_contents=[],
            )
            non_covered_functions_section.ng_including_document_reference = (
                DocumentReference()
            )
            non_covered_functions_section.ng_document_reference = (
                DocumentReference()
            )
            non_covered_functions_section.ng_document_reference.set_document(
                document
            )
            file_section.section_contents.append(non_covered_functions_section)

            for json_function_ in json_file_["functions"]:
                json_function_name = json_function_["demangled_name"]
                is_function_covered = json_function_["execution_count"] > 0
                stats.add_function(is_function_covered)

                testcase_node = SDocNode(
                    parent=document,
                    node_type="TEST_RESULT",
                    fields=[],
                    relations=[],
                )
                testcase_node.ng_document_reference = DocumentReference()
                testcase_node.ng_document_reference.set_document(document)
                testcase_node.ng_including_document_reference = (
                    DocumentReference()
                )
                testcase_node.set_field_value(
                    field_name="UID",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="UID",
                        parts=[
                            "GCOV:" + json_file_name + ":" + json_function_name
                        ],
                        multiline__=None,
                    ),
                )
                # FIXME: Remove?
                testcase_node.set_field_value(
                    field_name="STATUS",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="STATUS",
                        parts=[
                            "Covered" if is_function_covered else "Non-covered"
                        ],
                        multiline__=None,
                    ),
                )

                path = "src/main.c"
                gcov_path_hash = hashlib.md5(path.encode("utf-8")).hexdigest()
                # FIXME: Resolve the relative path from a project config.
                link = (
                    "../../../../"  # noqa: ISC003
                    + "coverage."
                    + Path(json_file_name).name
                    + ". "
                    + gcov_path_hash
                    + ".html"
                )
                testcase_node.set_field_value(
                    field_name="STATEMENT",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="STATEMENT",
                        parts=[
                            f"""
                            `LINK <{link}>`_
                            """
                        ],
                        multiline__=None,
                    ),
                )
                testcase_node.set_field_value(
                    field_name="TITLE",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="TITLE",
                        parts=[json_function_name],
                        multiline__=None,
                    ),
                )
                testcase_node.relations.append(
                    FileReference(
                        parent=testcase_node,
                        g_file_entry=FileEntry(
                            parent=None,
                            g_file_format=FileEntryFormat.SOURCECODE,
                            g_file_path=json_file_name,
                            g_line_range=None,
                            function=json_function_name,
                            clazz=None,
                        ),
                    )
                )
                if is_function_covered:
                    covered_functions_section.section_contents.append(
                        testcase_node
                    )
                else:
                    non_covered_functions_section.section_contents.append(
                        testcase_node
                    )

            summary_table = f"""\
.. list-table:: Coverage summary
    :widths: 25 10
    :header-rows: 0

    * - **Number of files:**
      - {len(json_content["files"])}
    * - **Total covered functions:**
      - {stats.total_number_of_covered_functions}
    * - **Total non-covered functions:**
      - {stats.total_number_of_non_covered_functions}
        """

            testcase_node = SDocNode(
                parent=document,
                node_type="TEXT",
                fields=[],
                relations=[],
            )
            testcase_node.ng_document_reference = DocumentReference()
            testcase_node.ng_document_reference.set_document(document)
            testcase_node.ng_including_document_reference = DocumentReference()
            testcase_node.set_field_value(
                field_name="STATEMENT",
                form_field_index=0,
                value=SDocNodeField(
                    parent=testcase_node,
                    field_name="STATEMENT",
                    parts=[summary_table],
                    multiline__="True",
                ),
            )
            document.section_contents.insert(0, testcase_node)

        return document
