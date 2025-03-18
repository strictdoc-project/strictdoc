import os
import tempfile

from strictdoc import environment
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc_source_code.test_reports.junit_xml_reader import (
    JUnitXMLReader,
)
from strictdoc.core.file_tree import File
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

    project_config: ProjectConfig = ProjectConfig.default_config(
        environment=environment
    )

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
