from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class MergedNodeUIE2ECase(E2ECase):
    """
    E2E Test: Verifies that when a node is hybrid (exists in .sdoc but fields
    are populated from source code), destructive actions (Delete, Clone) are
    disabled, but constructive actions (Edit, Add Child) remain enabled.
    """

    def test_merged_node_ui_actions(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_project_index.assert_contains_document("Hybrid Document")
            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()

            node = screen_document.get_node()

            # Edit & Add are allowed. Clone & Delete are blocked!
            node.assert_add_action_is_unlocked()
            node.assert_edit_node_action_is_unlocked()
            node.assert_clone_node_action_is_locked()
            node.assert_delete_node_action_is_locked()

            form_edit_requirement: Form_EditRequirement = (
                node.do_open_form_edit_requirement()
            )

            form_edit_requirement.assert_field_is_readonly("TITLE")
            form_edit_requirement.assert_field_is_readonly("STATEMENT")
            form_edit_requirement.assert_field_is_editable("RATIONALE")
