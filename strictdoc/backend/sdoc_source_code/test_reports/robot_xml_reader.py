"""
@relation(SDOC-SRS-143, scope=file)
"""

from typing import Dict, Optional, Union

import robot.result
from robot.api import ExecutionResult, ResultVisitor

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
from strictdoc.helpers.paths import path_to_posix_path


class SdocVisitor(ResultVisitor):
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        self.suites: Dict[str, Union[SDocDocument, SDocSection]] = {}
        self.document: Optional[SDocDocument] = None

    def visit_suite(self, suite: robot.result.TestSuite) -> None:
        """
        Create document for top level suite and sections for nested suites.
        """
        assert suite.full_name not in self.suites

        if suite.parent is None:
            self.document = SDocDocument(
                mid=None,
                title=f"Test report: {suite.name}",
                config=None,
                view=None,
                grammar=None,
                section_contents=[],
            )
            self.document.ng_including_document_reference = DocumentReference()
            grammar = DocumentGrammar.create_for_test_report(self.document)
            self.document.grammar = grammar
            self.document.config.requirement_style = "Table"
            self.suites[suite.full_name] = self.document
            summary = self.summary_from_suite(suite, self.document)
            self.document.section_contents.append(summary)
        else:
            assert self.document
            assert suite.parent.full_name in self.suites, (
                "depth-first traversal expected"
            )
            parent_sdoc_node = self.suites[suite.parent.full_name]
            section = SDocSection(
                parent=parent_sdoc_node,
                mid=None,
                uid=None,
                custom_level=None,
                title=suite.name,
                requirement_prefix=None,
                section_contents=[],
            )
            section.ng_including_document_reference = DocumentReference()
            section.ng_document_reference = DocumentReference()
            section.ng_document_reference.set_document(self.document)
            self.suites[suite.full_name] = section
            parent_sdoc_node.section_contents.append(section)
            summary_sdoc_node = self.summary_from_suite(suite, section)
            section.section_contents.append(summary_sdoc_node)

        super().visit_suite(suite)

    def visit_test(self, test: robot.result.TestCase) -> None:
        """
        Create TEST_RESULT node for each test case.
        """
        assert self.document
        assert test.parent and test.parent.full_name in self.suites, (
            "depth-first traversal expected"
        )
        parent_section = self.suites[test.parent.full_name]
        testcase_node = SDocNode(
            parent=parent_section,
            node_type="TEST_RESULT",
            fields=[],
            relations=[],
        )
        testcase_node.ng_document_reference = DocumentReference()
        testcase_node.ng_document_reference.set_document(self.document)
        testcase_node.ng_including_document_reference = DocumentReference()

        # Only executed tests will become traceable.
        if not test.skipped:
            testcase_node.set_field_value(
                field_name="UID",
                form_field_index=0,
                value=SDocNodeField(
                    parent=testcase_node,
                    field_name="UID",
                    parts=[test.full_name.upper()],
                    multiline__=None,
                ),
            )

        # Absolute path will be replaced with relative path to strictdoc root
        # in FileTraceabilityIndex.
        abs_path_on_exec_machine = path_to_posix_path(str(test.source))
        if test.source is not None:
            testcase_node.set_field_value(
                field_name="TEST_PATH",
                form_field_index=0,
                value=SDocNodeField(
                    parent=testcase_node,
                    field_name="TEST_PATH",
                    parts=[abs_path_on_exec_machine],
                    multiline__=None,
                ),
            )

        testcase_node.set_field_value(
            field_name="TEST_FUNCTION",
            form_field_index=0,
            value=SDocNodeField(
                parent=testcase_node,
                field_name="TEST_FUNCTION",
                parts=[test.name],
                multiline__=None,
            ),
        )

        testcase_node.set_field_value(
            field_name="DURATION",
            form_field_index=0,
            value=SDocNodeField(
                parent=testcase_node,
                field_name="DURATION",
                parts=[str(test.elapsed_time.total_seconds())],
                multiline__=None,
            ),
        )

        testcase_node.set_field_value(
            field_name="STATUS",
            form_field_index=0,
            value=SDocNodeField(
                parent=testcase_node,
                field_name="STATUS",
                parts=[test.status],
                multiline__=None,
            ),
        )

        testcase_node.set_field_value(
            field_name="TITLE",
            form_field_index=0,
            value=SDocNodeField(
                parent=testcase_node,
                field_name="TITLE",
                parts=[test.name],
                multiline__=None,
            ),
        )

        if not test.skipped:
            # File path will be resolved in FileTraceabilityIndex.
            testcase_node.relations.append(
                FileReference(
                    parent=testcase_node,
                    g_file_entry=FileEntry(
                        parent=None,
                        g_file_format=FileEntryFormat.SOURCECODE,
                        g_file_path="#FORWARD#",
                        g_line_range=None,
                        function=test.name,
                        clazz=None,
                    ),
                )
            )

        parent_section.section_contents.append(testcase_node)

    def summary_from_suite(
        self,
        suite: robot.result.TestSuite,
        parent: Union[SDocDocument, SDocSection],
    ) -> SDocNode:
        assert self.document
        summary_table = f"""\
.. list-table:: Test suite summary
    :widths: 25 10
    :header-rows: 0

    * - **Number of tests:**
      - {suite.statistics.total}
    * - **Number of successful tests:**
      - {suite.statistics.passed}
    * - **Number of failed tests:**
      - {suite.statistics.failed}
    * - **Number of skipped tests:**
      - {suite.statistics.skipped}
"""
        summary_node = SDocNode(
            parent=parent,
            node_type="TEXT",
            fields=[],
            relations=[],
        )
        summary_node.ng_document_reference = DocumentReference()
        summary_node.ng_document_reference.set_document(self.document)
        summary_node.ng_including_document_reference = DocumentReference()
        summary_node.set_field_value(
            field_name="STATEMENT",
            form_field_index=0,
            value=SDocNodeField(
                parent=summary_node,
                field_name="STATEMENT",
                parts=[summary_table],
                multiline__="True",
            ),
        )
        return summary_node


class RobotOutputXMLReader:
    @classmethod
    def read_from_file(
        cls: "RobotOutputXMLReader",
        doc_file: File,
        project_config: ProjectConfig,
    ) -> SDocDocument:
        execution_result = ExecutionResult(doc_file.full_path)
        sdoc_visitor = SdocVisitor(project_config)
        execution_result.visit(sdoc_visitor)
        if sdoc_visitor.document is None:
            raise RuntimeError(
                f"No test suite could be parsed from {doc_file.full_path}"
            )
        return sdoc_visitor.document
