from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.viewtype_selector import ViewType_Selector
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
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
            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document")

            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()

            self.clear_local_storage()

            viewtype_selector = ViewType_Selector(self)
            screen_table = viewtype_selector.do_go_to_table()
            screen_table.assert_on_screen_table()

            # REQ-001 is in row 1, REQ-002 is in row 2, REQ-003 is in row 3.
            req001_mid = screen_table.get_node_mid_from_row(row_order=1)
            req002_mid = screen_table.get_node_mid_from_row(row_order=2)
            req003_mid = screen_table.get_node_mid_from_row(row_order=3)
            assert req001_mid is not None
            assert req002_mid is not None
            assert req003_mid is not None

            # REQ-002 and REQ-003 have no relations of their own and no
            # computed ones yet.
            screen_table.assert_cell_dom_text(req002_mid, "RELATIONS", "")
            screen_table.assert_cell_dom_text(req003_mid, "RELATIONS", "")

            form = Form_EditRequirement(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.do_open_inline_cell(req001_mid, "RELATIONS")

            # Add two relations from REQ-001 to REQ-002 and REQ-003 in one
            # editing session.
            new_relation_mid_1 = form.do_form_add_field_relation()
            form.do_fill_in_field_relation_and_autocomplete(
                new_relation_mid_1, "REQ-002"
            )
            new_relation_mid_2 = form.do_form_add_field_relation()
            form.do_fill_in_field_relation_and_autocomplete(
                new_relation_mid_2, "REQ-003"
            )

            screen_table.do_save_inline_cell_by_outside_click()
            self.sleep(0.5)

            # REQ-001 keeps both newly declared Parent relations.
            screen_table.assert_cell_dom_text_contains(
                req001_mid, "RELATIONS", "REQ-002"
            )
            screen_table.assert_cell_dom_text_contains(
                req001_mid, "RELATIONS", "REQ-003"
            )

            # Both REQ-002 and REQ-003 now show the computed
            # "Children: REQ-001" relation, without a reload.
            screen_table.assert_cell_dom_text_contains(
                req002_mid, "RELATIONS", "REQ-001"
            )
            screen_table.assert_cell_dom_text_contains(
                req003_mid, "RELATIONS", "REQ-001"
            )

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
