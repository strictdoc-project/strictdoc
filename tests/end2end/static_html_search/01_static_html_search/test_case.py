import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_uid(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(exporter.get_output_path_as_uri() + "index.html")

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            self._test_unique_query(screen_project_index)
            self._test_common_query(screen_project_index)
            self._test_quoted_query(screen_project_index)
            self._test_quoted_query_with_space(screen_project_index)

            self._test_node_without_uid(screen_project_index)
            self.open(exporter.get_output_path_as_uri() + "index.html")

    def _test_unique_query(self, screen_project_index: Screen_ProjectIndex):
        screen_project_index.do_enter_search_query("UNIQUE_STATEMENT_LINE_1")
        screen_project_index.assert_search_results(1, 5, 7)

        screen_project_index.do_click_search_result_next()
        screen_project_index.assert_search_results(6, 7, 7)

        screen_project_index.do_click_search_result_previous()
        screen_project_index.assert_search_results(1, 5, 7)

    def _test_common_query(self, screen_project_index: Screen_ProjectIndex):
        screen_project_index.do_enter_search_query("COMMON STATEMENT LINE")
        screen_project_index.assert_search_results(1, 5, 15)

    def _test_quoted_query(self, screen_project_index: Screen_ProjectIndex):
        screen_project_index.do_enter_search_query('"COMMON STATEMENT LINE')
        screen_project_index.assert_search_results(1, 5, 15)

    def _test_quoted_query_with_space(
        self, screen_project_index: Screen_ProjectIndex
    ):
        screen_project_index.do_enter_search_query('"COMMON ')
        screen_project_index.assert_search_results(1, 5, 15)

        screen_project_index.do_click_search_result_next()
        screen_project_index.assert_search_results(6, 10, 15)

        screen_project_index.do_click_search_result_next()
        screen_project_index.assert_search_results(11, 15, 15)

        screen_project_index.do_click_search_result_previous()
        screen_project_index.assert_search_results(6, 10, 15)

        screen_project_index.do_click_search_result_previous()
        screen_project_index.assert_search_results(1, 5, 15)

        screen_project_index.do_click_search_result_end()
        screen_project_index.assert_search_results(11, 15, 15)

        screen_project_index.do_click_search_result_start()
        screen_project_index.assert_search_results(1, 5, 15)

    def _test_node_without_uid(self, screen_project_index: Screen_ProjectIndex):
        screen_project_index.do_enter_search_query("req_without_uid")
        screen_project_index.assert_search_results(1, 1, 1)
        screen_project_index.do_go_to_search_result(1)
        screen_document: Screen_Document = Screen_Document(self)
        screen_document.assert_on_screen_document()
