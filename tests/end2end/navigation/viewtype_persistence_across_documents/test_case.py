from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import (
    ViewType_Selector,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.table.screen_table import Screen_Table
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1 title")
            screen_project_index.assert_contains_document("Document 2 title")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1 title")

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()

            screen_table.assert_on_screen_table()
            screen_table.assert_header_document_title("Document 1 title")

            self.click_xpath('(//*[@data-testid="tree-document-link"])[2]')

            screen_table_second_document = Screen_Table(self)
            screen_table_second_document.assert_on_screen_table()
            screen_table_second_document.assert_header_document_title(
                "Document 2 title"
            )

        assert test_setup.compare_sandbox_and_expected_output()
