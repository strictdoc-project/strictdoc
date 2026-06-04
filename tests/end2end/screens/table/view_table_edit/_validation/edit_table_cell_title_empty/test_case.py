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
            assert node_mid is not None, "Could not find node MID in table row"

            form = Form(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            #
            # Clear TITLE and save by click-outside — server rejects (422),
            # form stays open in the cell, validation error is marked on the cell.
            #
            screen_table.assert_cell_has_no_validation_error(node_mid, "TITLE")
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_clear_field("TITLE")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            screen_table.assert_cell_has_validation_error(node_mid, "TITLE")
            screen_table.assert_cell_is_inline_editing(node_mid, "TITLE")

            #
            # Click the cell (re-focus), then Escape — cancels editing, restores
            # original value, clears validation error indicator.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            screen_table.do_cancel_inline_cell_by_escape()

            screen_table.assert_cell_dom_text(node_mid, "TITLE", "Old title")
            screen_table.assert_cell_has_no_validation_error(node_mid, "TITLE")

            #
            # Case 2: After a 422 on TITLE, click a different cell (STATEMENT).
            # [FEATURE: passive-open] TITLE stays open with the error — it is NOT
            # automatically restored when focus moves to another cell.
            # STATEMENT has no value in the fixture, but its cell is always rendered
            # with data-field-type="contenteditable" and is therefore clickable.
            #
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            form.do_clear_field("TITLE")
            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            screen_table.assert_cell_has_validation_error(node_mid, "TITLE")

            screen_table.do_open_inline_cell(node_mid, "STATEMENT")
            self.sleep(0.5)

            # TITLE is passive-open: form still visible, validation error still shown.
            screen_table.assert_cell_is_inline_editing(node_mid, "TITLE")
            screen_table.assert_cell_has_validation_error(node_mid, "TITLE")

            # Re-activate TITLE by clicking it (STATEMENT closes via skip-save),
            # then Escape — discards the invalid edit and restores original value.
            screen_table.do_open_inline_cell(node_mid, "TITLE")
            screen_table.do_cancel_inline_cell_by_escape()

            screen_table.assert_cell_dom_text(node_mid, "TITLE", "Old title")
            screen_table.assert_cell_has_no_validation_error(node_mid, "TITLE")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
