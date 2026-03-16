"""
@relation(SDOC-SRS-155, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_search_in_static_html(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + "index.html")
            self._test_common_sequence()

    def test_search_on_server(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())
            self._test_common_sequence()

    def _test_common_sequence(self):
        screen_project_index = Screen_ProjectIndex(self)
        screen_project_index.assert_on_screen()

        self._test_regex_special_character_query(screen_project_index)

    def _test_regex_special_character_query(
        self, screen_project_index: Screen_ProjectIndex
    ):
        # This covers a typical regex-breaking input where a special character
        # is typed together with a known token that still produces results.
        # Similar characters to keep in mind for future coverage: (, [, {, \\
        screen_project_index.do_enter_search_query("( COMMON")
        screen_project_index.assert_search_results(1, 5, 15)
        screen_project_index.assert_no_js_errors()
