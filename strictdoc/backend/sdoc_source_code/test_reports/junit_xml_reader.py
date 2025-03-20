import os
from enum import IntEnum
from typing import Any, List, Optional, Union

import bs4
from bs4 import BeautifulSoup

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import FileEntry, FileEntryFormat
from strictdoc.core.file_tree import File
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast, assert_optional_cast
from strictdoc.helpers.paths import path_to_posix_path


class JUnitXMLFormat(IntEnum):
    LLVM_LIT = 1
    CTEST = 2
    GOOGLE_TEST = 3
    PYTEST = 4

    @staticmethod
    def create_from_path(file_path: str) -> "JUnitXMLFormat":
        if file_path.endswith(".lit.junit.xml"):
            return JUnitXMLFormat.LLVM_LIT
        if file_path.endswith(".ctest.junit.xml"):
            return JUnitXMLFormat.CTEST
        if file_path.endswith(".gtest.junit.xml"):
            return JUnitXMLFormat.GOOGLE_TEST
        if file_path.endswith(".pytest.junit.xml"):
            return JUnitXMLFormat.PYTEST
        raise NotImplementedError(file_path)


class JUnitXMLReader:
    @classmethod
    def read_from_file(
        cls: "JUnitXMLReader", doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        with open(doc_file.get_full_path(), encoding="UTF-8") as file:
            content = file.read()
        return cls.read_from_string(content, doc_file, project_config)

    @classmethod
    def read_from_string(
        cls: "JUnitXMLReader",
        content: str,
        doc_file: File,
        project_config: ProjectConfig,
    ) -> SDocDocument:
        if len(content) == 0:
            raise RuntimeError(
                "Document is empty, line 1, column 1 (<string>, line 1)"
            )
        try:
            soup = BeautifulSoup(content, "xml")

        except Exception as exception:  # pylint: disable=broad-except
            raise RuntimeError(str(exception)) from None

        xml_format = JUnitXMLFormat.create_from_path(doc_file.get_full_path())

        document = SDocDocument(
            mid=None,
            title="Test report",
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )
        document.ng_including_document_reference = DocumentReference()
        grammar = DocumentGrammar.create_for_test_report(document)
        document.grammar = grammar
        document.config.requirement_style = "Table"

        xml_testsuite_list: List[
            Union[
                bs4.element.PageElement,
                bs4.element.Tag,
                bs4.element.NavigableString,
            ]
        ]
        xml_testsuites: Optional[bs4.element.Tag] = assert_optional_cast(
            soup.find("testsuites", recursive=False), bs4.element.Tag
        )

        # Some tools, e.g., LLVM LIT, produce JUnit XML files with a top-level
        # <testsuites> tag which allows containing multiple <testsuite> tags.
        # Some tools, e.g., Google Test, produce only a single <testsuite>.
        if xml_testsuites is not None:
            assert isinstance(xml_testsuites, bs4.element.Tag)
            xml_testsuite_list = xml_testsuites.find_all(
                "testsuite", recursive=False
            )
        else:
            xml_testsuite: bs4.element.Tag = assert_cast(
                soup.find("testsuite", recursive=False), bs4.element.Tag
            )
            xml_testsuite_list = [xml_testsuite]
        if len(xml_testsuite_list) == 1:
            assert isinstance(xml_testsuite_list[0], bs4.element.Tag)
            document.title = "Test report: " + assert_cast(
                xml_testsuite_list[0]["name"], str
            )

        for xml_testsuite_ in xml_testsuite_list:
            assert isinstance(xml_testsuite_, bs4.element.Tag)
            title = assert_cast(xml_testsuite_["name"], str)
            total_tests: int = int(str(xml_testsuite_["tests"]))
            total_failures: int = int(str(xml_testsuite_["failures"]))
            total_skipped: int = int(str(xml_testsuite_["skipped"]))
            total_success: int = total_tests - total_failures - total_skipped

            test_suite_section = SDocSection(
                parent=document,
                mid=None,
                uid=None,
                custom_level=None,
                title=title,
                requirement_prefix=None,
                section_contents=[],
            )
            test_suite_section.ng_including_document_reference = (
                DocumentReference()
            )
            test_suite_section.ng_document_reference = DocumentReference()
            test_suite_section.ng_document_reference.set_document(document)
            document.section_contents.append(test_suite_section)

            summary_table = f"""\
.. list-table:: Test suite summary
    :widths: 25 10
    :header-rows: 0

    * - **Number of tests:**
      - {total_tests}
    * - **Number of successful tests:**
      - {total_success}
    * - **Number of failed tests:**
      - {total_failures}
    * - **Number of skipped tests:**
      - {total_skipped}
"""

            testcase_node = SDocNode(
                parent=test_suite_section,
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
            test_suite_section.section_contents.append(testcase_node)

            """
            Parse individual <testcase> elements.
            """

            xml_testcase_list: List[Any] = xml_testsuite_.find_all(
                "testcase", recursive=False
            )
            for xml_testcase_ in xml_testcase_list:
                assert isinstance(xml_testcase_, bs4.element.Tag)

                test_case_node_uid: str
                test_case_node_title: str
                test_case_node_status: str = "PASSED"
                test_case_node_test_path: Optional[str] = None
                test_case_node_test_function: Optional[str] = None

                xml_testcase_name: str = assert_cast(xml_testcase_["name"], str)
                xml_testcase_classname: str = assert_cast(
                    xml_testcase_["classname"], str
                )
                xml_testcase_time: str = assert_cast(xml_testcase_["time"], str)
                xml_error_or_none: Optional[bs4.element.Tag] = (
                    assert_optional_cast(
                        xml_testcase_.find("error"), bs4.element.Tag
                    )
                )
                xml_failure_or_none: Optional[bs4.element.Tag] = (
                    assert_optional_cast(
                        xml_testcase_.find("failure"), bs4.element.Tag
                    )
                )
                xml_skipped_or_none: Optional[bs4.element.Tag] = (
                    assert_optional_cast(
                        xml_testcase_.find("skipped"), bs4.element.Tag
                    )
                )

                if xml_error_or_none is not None:
                    raise RuntimeError(
                        "JUnit XML contains a test that failed due to an error: "
                        f"{xml_testcase_name}"
                    )

                if xml_failure_or_none is not None:
                    test_case_node_status = "FAILED"
                elif xml_skipped_or_none is not None:
                    test_case_node_status = "SKIPPED"

                """
                Different tools produce different outputs when it comes to how
                the test names and paths are stored. Each tool's output is
                handled separately below.
                """
                if xml_format == JUnitXMLFormat.LLVM_LIT:
                    """
                    Example produced by LLVM LIT:
                    <testcase classname="StrictDoc integration tests.tests/integration" name="test.ignored.itest" time="5.50"/>
                    """

                    rel_path_to_test_suite = (
                        project_config.test_report_root_dict.get(
                            doc_file.rel_path.relative_path_posix, None
                        )
                    )

                    if rel_path_to_test_suite is None:
                        raise RuntimeError(
                            "The relative path to the test suite must be "
                            "registered in the strictdoc.toml config under the "
                            "'test_report_root_dict' option: "
                            f"{doc_file.rel_path.relative_path_posix}"
                        )

                    # Relative path to test is a combination of the classname and name,
                    # but we must remove the test suite name prefix.
                    rel_path_to_test: str = os.path.join(
                        xml_testcase_classname, xml_testcase_name
                    )
                    _, _, rel_path_to_test = rel_path_to_test.partition(".")

                    rel_path_to_test = os.path.join(
                        rel_path_to_test_suite, rel_path_to_test
                    )
                    rel_path_to_test = path_to_posix_path(rel_path_to_test)

                    assert project_config.source_root_path is not None
                    full_path_to_test = os.path.join(
                        project_config.source_root_path, rel_path_to_test
                    )
                    assert os.path.isfile(full_path_to_test), full_path_to_test

                    test_case_node_uid = rel_path_to_test
                    test_case_node_title = rel_path_to_test
                    test_case_node_duration = xml_testcase_time
                    test_case_node_test_path = rel_path_to_test
                elif xml_format == JUnitXMLFormat.CTEST:
                    test_case_node_uid = xml_testcase_name
                    test_case_node_title = xml_testcase_name
                    test_case_node_duration = xml_testcase_time
                    test_case_node_test_function = "#GTEST#" + xml_testcase_name
                elif xml_format == JUnitXMLFormat.GOOGLE_TEST:
                    google_test_name = (
                        xml_testcase_classname + "." + xml_testcase_name
                    )
                    test_case_node_uid = google_test_name
                    test_case_node_title = google_test_name
                    test_case_node_duration = xml_testcase_time
                    test_case_node_test_function = "#GTEST#" + google_test_name
                elif xml_format == JUnitXMLFormat.PYTEST:
                    test_case_node_uid = (
                        xml_testcase_classname + "." + xml_testcase_name
                    )
                    test_case_node_duration = xml_testcase_time
                    test_case_node_test_path = (
                        xml_testcase_classname.replace(".", os.path.sep) + ".py"
                    )
                    test_case_node_title = xml_testcase_classname
                    test_case_node_test_function = xml_testcase_name
                else:
                    raise NotImplementedError("Unsupported JUnit XML format")

                testcase_node = SDocNode(
                    parent=test_suite_section,
                    node_type="TEST_RESULT",
                    fields=[],
                    relations=[],
                )
                testcase_node.ng_document_reference = DocumentReference()
                testcase_node.ng_document_reference.set_document(document)
                testcase_node.ng_including_document_reference = (
                    DocumentReference()
                )
                if xml_skipped_or_none is None:
                    testcase_node.set_field_value(
                        field_name="UID",
                        form_field_index=0,
                        value=SDocNodeField(
                            parent=testcase_node,
                            field_name="UID",
                            parts=[test_case_node_uid],
                            multiline__=None,
                        ),
                    )
                if test_case_node_test_path is not None:
                    testcase_node.set_field_value(
                        field_name="TEST_PATH",
                        form_field_index=0,
                        value=SDocNodeField(
                            parent=testcase_node,
                            field_name="TEST_PATH",
                            parts=[
                                path_to_posix_path(test_case_node_test_path)
                            ],
                            multiline__=None,
                        ),
                    )
                if test_case_node_test_function is not None:
                    testcase_node.set_field_value(
                        field_name="TEST_FUNCTION",
                        form_field_index=0,
                        value=SDocNodeField(
                            parent=testcase_node,
                            field_name="TEST_FUNCTION",
                            parts=[test_case_node_test_function],
                            multiline__=None,
                        ),
                    )
                testcase_node.set_field_value(
                    field_name="DURATION",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="DURATION",
                        parts=[test_case_node_duration],
                        multiline__=None,
                    ),
                )
                testcase_node.set_field_value(
                    field_name="STATUS",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="STATUS",
                        parts=[test_case_node_status],
                        multiline__=None,
                    ),
                )
                testcase_node.set_field_value(
                    field_name="TITLE",
                    form_field_index=0,
                    value=SDocNodeField(
                        parent=testcase_node,
                        field_name="TITLE",
                        parts=[test_case_node_title],
                        multiline__=None,
                    ),
                )
                if xml_skipped_or_none is None:
                    if test_case_node_test_path is not None:
                        testcase_node.relations.append(
                            FileReference(
                                parent=testcase_node,
                                g_file_entry=FileEntry(
                                    parent=None,
                                    g_file_format=FileEntryFormat.SOURCECODE,
                                    g_file_path=test_case_node_test_path,
                                    g_line_range=None,
                                    function=test_case_node_test_function,
                                    clazz=None,
                                ),
                            )
                        )
                    elif test_case_node_test_function is not None:
                        testcase_node.relations.append(
                            FileReference(
                                parent=testcase_node,
                                g_file_entry=FileEntry(
                                    parent=None,
                                    g_file_format=FileEntryFormat.SOURCECODE,
                                    g_file_path="#FORWARD#",
                                    g_line_range=None,
                                    function=test_case_node_test_function,
                                    clazz=None,
                                ),
                            )
                        )
                test_suite_section.section_contents.append(testcase_node)

        return document
