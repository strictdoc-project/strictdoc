import os

from seleniumbase import BaseCase

from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.source_coverage.screen_source_coverage import (  # noqa: E501
    Screen_SourceCoverage,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC251_T01_ViewSourceFile(BaseCase):
    def test_01(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_link_to_source_coverage_present()

            screen_source_coverage: Screen_SourceCoverage = (
                screen_project_index.do_click_on_source_coverage_link()
            )
            screen_source_coverage.assert_on_screen()

            # FIXME: When the source files root path becomes configurable,
            # implement more specific assertions.
            screen_source_coverage.assert_contains_text(
                "excel_to_sdoc_converter.py"
            )
