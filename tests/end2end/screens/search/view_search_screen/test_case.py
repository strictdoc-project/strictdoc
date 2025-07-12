import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.search.search import (
    Screen_Search,
    Screen_SearchResults,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_01_search_links(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())
            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_link_to_search_screen_present()

            screen_search: Screen_Search = (
                screen_project_index.do_click_on_search_screen_link()
            )
            screen_search.assert_on_screen("search")

            screen_search_results: Screen_SearchResults = (
                screen_search.do_click_on_search_requirements()
            )
            screen_search_results.assert_text("Requirement statement.")
            screen_search_results.assert_no_text("Section title")
            self.go_back()

            screen_search_results = screen_search.do_click_on_search_sections()
            screen_search_results.assert_text("Section title")
            screen_search_results.assert_text("New section title")
            screen_search_results.assert_no_text("Requirement statement.")
            self.go_back()

            screen_search_results = (
                screen_search.do_click_on_search_node_with_system_title()
            )
            screen_search_results.assert_nr_results(0)
            self.go_back()

    def test_02_empty_search(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_search: Screen_Search = (
                screen_project_index.do_click_on_search_screen_link()
            )
            screen_search_results = screen_search.do_search(
                """(node.is_requirement and node["STATEMENT"] == "BOGUS_STATEMENT")"""
            )

            screen_search_results.assert_nr_results(0)

    def test_03_invalid_search(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_search: Screen_Search = (
                screen_project_index.do_click_on_search_screen_link()
            )
            screen_search_results = screen_search.do_search("""foo""")

            self.assertRegex(
                screen_search_results.get_search_error_msg(),
                "error:.+Expected.+[*]foo",
            )
