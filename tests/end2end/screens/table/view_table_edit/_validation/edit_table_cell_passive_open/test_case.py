from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.form.form import Form
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

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            node_mid = screen_table.get_node_mid_from_row(row_order=1)
            assert node_mid is not None

            form = Form(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            #
            # [FEATURE: passive-open]
            # Case 1: edit STATEMENT (clear it → required field error), then click
            # TITLE directly WITHOUT clicking outside first.
            # Expected: STATEMENT stays open with error, TITLE is NOT opened.
            #
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            form.do_clear_field("STATEMENT")
            screen_table.do_click_cell(node_mid, "TITLE")
            self.sleep(0.5)

            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")
            screen_table.assert_cell_has_validation_error(node_mid, "STATEMENT")
            screen_table.assert_cell_is_not_inline_editing(node_mid, "TITLE")

            #
            # [FEATURE: passive-open]
            # Case 2: click outside — STATEMENT stays passive-open, no re-save.
            #
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.3)

            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")
            screen_table.assert_cell_has_validation_error(node_mid, "STATEMENT")

            #
            # [FEATURE: passive-open]
            # Case 3: click TITLE while STATEMENT is passive-open — TITLE opens,
            # STATEMENT stays passive-open alongside it.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            self.sleep(0.3)

            screen_table.assert_cell_is_inline_editing(node_mid, "TITLE")
            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")
            screen_table.assert_cell_has_validation_error(node_mid, "STATEMENT")

            screen_table.do_cancel_inline_cell_by_escape()
            screen_table.assert_cell_is_not_inline_editing(node_mid, "TITLE")

            #
            # [FEATURE: passive-open]
            # Case 4: re-activate STATEMENT by clicking it — form NOT re-fetched,
            # just reactivated. Then Escape cancels: restores original value.
            #
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            screen_table.do_cancel_inline_cell_by_escape()

            screen_table.assert_cell_is_not_inline_editing(
                node_mid, "STATEMENT"
            )
            screen_table.assert_cell_dom_text(
                node_mid, "STATEMENT", "Requirement statement."
            )
            screen_table.assert_cell_has_no_validation_error(
                node_mid, "STATEMENT"
            )

            #
            # [FEATURE: passive-open]
            # Case 5: edit mode OFF closes passive-open cells.
            #
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            form.do_clear_field("STATEMENT")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()
            screen_table.assert_cell_is_not_inline_editing(
                node_mid, "STATEMENT"
            )

        assert test_setup.compare_sandbox_and_expected_output()
