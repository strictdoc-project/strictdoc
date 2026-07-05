# The cross-node refresh in main_router.py (table__update_node_relations)
# walks `affected_related_nodes` with one loop, regardless of how many
# relations were touched. A 2-relation removal exercises that loop the same
# way a 1-relation removal would, plus it additionally proves that several
# extra turbo-stream blocks in one response are all applied. So this single
# test stands in for the simpler 1-relation case too -
# see edit_table_cell_relations_add_two_links_updates_two_linked_nodes for
# the matching "add" side.
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

            # REQ-001 declares "Parent: REQ-002" and "Parent: REQ-003", so
            # REQ-002 and REQ-003 start out showing the computed
            # "Children: REQ-001" relation.
            screen_table.assert_cell_dom_text_contains(
                req002_mid, "RELATIONS", "REQ-001"
            )
            screen_table.assert_cell_dom_text_contains(
                req003_mid, "RELATIONS", "REQ-001"
            )

            form = Form_EditRequirement(self)

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_on()

            screen_table.do_open_inline_cell(req001_mid, "RELATIONS")

            # Remove both relations from REQ-001 in one editing session.
            form.assert_form_has_relations()
            form.do_delete_relation(1)
            form.do_delete_relation(1)
            form.assert_form_has_no_relations()

            screen_table.do_save_inline_cell_by_outside_click()
            screen_table.wait_for_cell_not_editing(req001_mid, "RELATIONS")

            # REQ-001 no longer declares any relations.
            # data-mode is cleared synchronously before the save's Turbo Stream
            # is applied (see wait_for_cell_save_applied), so wait_for_* is
            # needed here too, not just for the cross-node updates below.
            screen_table.wait_for_cell_dom_text(req001_mid, "RELATIONS", "")

            # Once REQ-001 no longer declares "Parent: REQ-002"/"Parent:
            # REQ-003", REQ-002's and REQ-003's computed "Children: REQ-001"
            # relations must disappear too, without a reload.
            # Use wait_for_* here because these cells are updated by a separate
            # cross-node turbo-stream that arrives asynchronously after the save.
            screen_table.wait_for_cell_dom_text(req002_mid, "RELATIONS", "")
            screen_table.wait_for_cell_dom_text(req003_mid, "RELATIONS", "")

            screen_table.do_toggle_edit_mode()
            screen_table.assert_edit_mode_off()

        assert test_setup.compare_sandbox_and_expected_output()
