"""
@relation(SDOC-SRS-143, scope=file)
"""

import os
import tempfile

import pytest

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc_source_code.test_reports.junit_xml_reader import (
    JUnitXMLReader,
)
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.paths import SDocRelativePath


def test_01_ctest():
    source_input = """
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="(empty)"
	tests="8"
	failures="0"
	disabled="0"
	skipped="0"
	hostname=""
	time="0"
	timestamp="2025-03-10T10:30:39"
	>
	<testcase name="TestPrtMath.TransitionDistance" classname="TestPrtMath.TransitionDistance" time="0.023645" status="run">
		<properties/>
		<system-out>xxxxx
</system-out>
	</testcase>
</testsuite>
""".lstrip()

    project_config: ProjectConfig = ProjectConfig.default_config()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, suffix=".ctest.junit.xml"
    ) as temp_file:
        doc_file: File = File(
            0,
            temp_file.name,
            SDocRelativePath(os.path.basename(temp_file.name)),
        )
        document: SDocDocument = JUnitXMLReader.read_from_string(
            source_input, doc_file, project_config
        )
        assert len(document.section_contents) == 1
        assert len(document.section_contents[0].section_contents) == 2

        test_result_node: SDocNode = assert_cast(
            document.section_contents[0].section_contents[1], SDocNode
        )
        assert (
            test_result_node.get_meta_field_value_by_title("TEST_FUNCTION")
            == "#GTEST#TestPrtMath.TransitionDistance"
        )


def test_02_testcase_properties_are_mapped_to_fields():
    source_input = """\
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Test suite" tests="1" failures="0" skipped="0">
  <testcase name="TestSuite.Test1"
            classname="TestSuite.Test1"
            time="0.1">
    <properties>
      <property name="requirement" value="REQ1"/>
      <property name="strictdoc:image" value="test1.png"/>
    </properties>
  </testcase>
</testsuite>
"""

    project_config: ProjectConfig = ProjectConfig.default_config()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, suffix=".ctest.junit.xml"
    ) as temp_file:
        doc_file: File = File(
            0,
            temp_file.name,
            SDocRelativePath(os.path.basename(temp_file.name)),
        )
        document: SDocDocument = JUnitXMLReader.read_from_string(
            source_input, doc_file, project_config
        )

        test_result_grammar = document.grammar.elements_by_type["TEST_RESULT"]
        assert (
            test_result_grammar.fields_map["REQUIREMENT"].human_title
            == "requirement"
        )
        assert (
            test_result_grammar.fields_map["STRICTDOC_IMAGE"].human_title
            == "strictdoc:image"
        )
        assert not test_result_grammar.is_field_multiline("REQUIREMENT")
        assert not test_result_grammar.is_field_multiline("STRICTDOC_IMAGE")

        test_result_node: SDocNode = assert_cast(
            document.section_contents[0].section_contents[1], SDocNode
        )
        assert (
            test_result_node.get_meta_field_value_by_title("REQUIREMENT")
            == "REQ1"
        )
        assert (
            test_result_node.get_meta_field_value_by_title("STRICTDOC_IMAGE")
            == "test1.png"
        )


def test_03_property_names_may_repeat_across_testcases():
    source_input = """\
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Test suite" tests="2" failures="0" skipped="0">
  <testcase name="TestSuite.Test1"
            classname="TestSuite.Test1"
            time="0.1">
    <properties>
      <property name="requirement" value="REQ1"/>
    </properties>
  </testcase>
  <testcase name="TestSuite.Test2"
            classname="TestSuite.Test2"
            time="0.1">
    <properties>
      <property name="requirement" value="REQ2"/>
    </properties>
  </testcase>
</testsuite>
"""

    document: SDocDocument = _read_ctest_source(source_input)
    first_test_result: SDocNode = assert_cast(
        document.section_contents[0].section_contents[1], SDocNode
    )
    second_test_result: SDocNode = assert_cast(
        document.section_contents[0].section_contents[2], SDocNode
    )
    assert (
        first_test_result.get_meta_field_value_by_title("REQUIREMENT") == "REQ1"
    )
    assert (
        second_test_result.get_meta_field_value_by_title("REQUIREMENT")
        == "REQ2"
    )


@pytest.mark.parametrize(
    ("property_xml", "expected_error"),
    [
        (
            '<property name="requirement--id" value="REQ1"/>',
            (
                "JUnit property name cannot be mapped to a StrictDoc field "
                "name: 'requirement--id'."
            ),
        ),
        (
            '<property name="status" value="ignored"/>',
            (
                "JUnit property name maps to a reserved TEST_RESULT field: "
                "'status' -> 'STATUS'."
            ),
        ),
        (
            """\
<property name="strictdoc:image" value="test1.png"/>
<property name="strictdoc-image" value="test2.png"/>\
""",
            (
                "JUnit property names map to the same StrictDoc field: "
                "'strictdoc:image', 'strictdoc-image' -> "
                "'STRICTDOC_IMAGE'."
            ),
        ),
        (
            """\
<property name="requirement" value="REQ1"/>
<property name="requirement" value="REQ2"/>\
""",
            ("JUnit testcase contains duplicate property name: 'requirement'."),
        ),
        (
            '<property value="REQ1"/>',
            "JUnit property is missing required 'name' attribute.",
        ),
        (
            '<property name="requirement"/>',
            "JUnit property is missing required 'value' attribute.",
        ),
    ],
)
def test_04_invalid_testcase_properties_are_rejected(
    property_xml: str, expected_error: str
):
    source_input = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Test suite" tests="1" failures="0" skipped="0">
  <testcase name="TestSuite.Test1"
            classname="TestSuite.Test1"
            time="0.1">
    <properties>
      {property_xml}
    </properties>
  </testcase>
</testsuite>
"""

    with pytest.raises(RuntimeError) as exc_info:
        _ = _read_ctest_source(source_input)
    assert expected_error == str(exc_info.value)


def test__90__error_handling__empty_xml():
    source_input = ""

    project_config: ProjectConfig = ProjectConfig.default_config()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, suffix=".ctest.junit.xml"
    ) as temp_file:
        doc_file: File = File(
            0,
            temp_file.name,
            SDocRelativePath(os.path.basename(temp_file.name)),
        )
        with pytest.raises(RuntimeError) as exc_info:
            _ = JUnitXMLReader.read_from_string(
                source_input, doc_file, project_config
            )
        assert """\
Document is empty, line 1, column 1 (<string>, line 1)\
""" == str(exc_info.value)


def _read_ctest_source(source_input: str) -> SDocDocument:
    project_config: ProjectConfig = ProjectConfig.default_config()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, suffix=".ctest.junit.xml"
    ) as temp_file:
        doc_file: File = File(
            0,
            temp_file.name,
            SDocRelativePath(os.path.basename(temp_file.name)),
        )
        return JUnitXMLReader.read_from_string(
            source_input, doc_file, project_config
        )
