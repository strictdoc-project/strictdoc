from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
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
            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document")

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document")

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()
            screen_table.assert_not_empty_view()

            # Columns that exist in the grammar union (TESTNODE or TEST) must be present.
            screen_table.assert_column_header_visible("Title")
            screen_table.assert_column_header_visible("Statement")
            screen_table.assert_column_header_visible("Rationale")
            screen_table.assert_column_header_visible("STEPS")

            # Columns absent from every grammar element must not appear at all.
            screen_table.assert_column_header_not_present("Comment")
            screen_table.assert_column_header_not_present("REFS")

            # TESTNODE has only TITLE — its cells for columns defined in TEST
            # but absent from TESTNODE must carry the dimmed modifier class.
            # data-field-name uses the internal field name (uppercase), not the display label.
            screen_table.assert_table_cell_is_dimmed("TESTNODE", "STATEMENT")
            screen_table.assert_table_cell_is_dimmed("TESTNODE", "RATIONALE")
            screen_table.assert_table_cell_is_dimmed("TESTNODE", "STEPS")

        assert test_setup.compare_sandbox_and_expected_output()
