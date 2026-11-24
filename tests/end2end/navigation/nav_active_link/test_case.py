import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.components.nav import Nav
from tests.end2end.helpers.screens.screen import Screen
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen = Screen(self)
            nav = Nav(self)

            screen.assert_on_screen("document-tree")
            nav.assert_active_link("project-tree-link-project-index")

            for test_id, viewtype in (
                ("project-tree-link-project-statistics", "project-statistics"),
                (
                    "project-tree-link-requirements-coverage",
                    "traceability-matrix",
                ),
                ("project-tree-link-source-coverage", "coverage-tree"),
                ("project-tree-link-search", "search"),
                ("project-tree-link-diff", "diff"),
                ("project-tree-link-tree-map", "tree-map"),
                ("project-configuration-link", "project-configuration"),
            ):
                nav.do_click_link(test_id)
                screen.assert_on_screen(viewtype)
                nav.assert_active_link(test_id)

            nav.do_click_link("project-tree-link-diff")
            self.click_xpath('//*[@data-testid="diff-screen-tab-changelog"]')
            screen.assert_on_screen("changelog")
            nav.assert_active_link("project-tree-link-diff")

            screen.assert_no_js_errors()
