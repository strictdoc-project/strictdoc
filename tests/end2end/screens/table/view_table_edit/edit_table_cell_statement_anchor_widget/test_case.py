"""
@relation(SDOC-SRS-208, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.anchor_widget import AnchorWidget
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
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            node_mid = screen_table.get_node_mid_from_row(row_order=1)
            assert node_mid is not None

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()
            screen_table.do_open_inline_cell(node_mid, "STATEMENT")

            anchor_widget = AnchorWidget(self, "STATEMENT")

            # Escape closes only the form, not the cell.
            anchor_widget.do_place_caret_on_next_line("Text.")
            anchor_widget.do_open_form()
            anchor_widget.do_type_uid("A-1")
            anchor_widget.do_close_form_by_escape()
            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")

            # The form is visible in the narrow cell, and a click on it does
            # not save the cell.
            anchor_widget.do_place_caret_on_next_line("Text.")
            anchor_widget.do_open_form()
            anchor_widget.do_type_uid("A-1")
            anchor_widget.assert_insert_enabled()
            anchor_widget.do_click_insert()
            screen_table.assert_cell_is_inline_editing(node_mid, "STATEMENT")
            anchor_widget.assert_field_text(
                "Text.\n\n[ANCHOR: A-1]\n\nMore text.\n"
            )

            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_save_applied(node_mid, "STATEMENT")
            screen_table.assert_cell_dom_text_contains(
                node_mid, "STATEMENT", "More text."
            )

        assert test_setup.compare_sandbox_and_expected_output()
