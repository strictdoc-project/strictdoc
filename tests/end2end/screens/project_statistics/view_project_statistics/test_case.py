import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.project_statistics.project_statistics import (
    Screen_ProjectStatistics,
)
from tests.end2end.helpers.screens.search.search import Screen_SearchResults
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    expected_search_results = [
        ("search-total-sections", 1),
        ("search-sections-without-any-text", 1),
        ("search-total-requirements", 5),
        ("search-requirements-with-no-uid", 2),
        (
            "search-root-level-requirements-not-connected-to-by-any-requirement",
            0,
        ),
        (
            "search-non-root-level-requirements-not-connected-to-any-parent-requirement",
            4,
        ),
        ("search-requirements-with-no-rationale", 4),
        ("search-requirements-with-no-status", 1),
        ("search-requirements-with-status-active", 1),
        ("search-requirements-with-status-draft", 1),
        ("search-requirements-with-status-backlog", 1),
        ("search-requirements-with-all-other-statuses", 1),
        ("search-total-tbd", 2),
        ("search-total-tbc", 1),
    ]

    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_link_to_project_statistics_present()

            screen_requirements_coverage: Screen_ProjectStatistics = (
                screen_project_index.do_click_on_project_statistics_link()
            )
            screen_requirements_coverage.assert_on_screen()

            for test_id, nr_results in self.expected_search_results:
                screen_search_results: Screen_SearchResults = (
                    screen_requirements_coverage.do_click_on_search_link(
                        test_id
                    )
                )
                screen_search_results.assert_nr_results(nr_results)
                self.go_back()
