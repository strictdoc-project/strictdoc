from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            # start: on the document tree
            screen_project_index.assert_on_screen()

            # go to document
            screen_document = screen_project_index.do_click_on_first_document()
            screen_toc: TOC = screen_document.get_toc()

            viewtype_selector = ViewType_Selector(self)

            # toc is on the document view, opened
            screen_document.assert_on_screen_document()
            screen_toc.assert_toc_opened()

            # go to table view
            screen_table = viewtype_selector.do_go_to_table()

            # toc is on the table view, opened
            screen_table.assert_on_screen_table()
            screen_toc.assert_toc_opened()

            # hide the toc
            screen_toc.do_toggle_toc()

            # toc is on the table view, closed
            screen_table.assert_on_screen_table()
            screen_toc.assert_toc_closed()

            # go back to document view
            screen_document = viewtype_selector.do_go_to_document()
            # toc is on the document view, closed
            screen_document.assert_on_screen_document()
            screen_toc.assert_toc_closed()

            # show the toc
            screen_toc.do_toggle_toc()

            # toc is open
            screen_document.assert_on_screen_document()
            screen_toc.assert_toc_opened()

        assert test_setup.compare_sandbox_and_expected_output()
