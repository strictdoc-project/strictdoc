from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class NormalDocumentUIE2ECase(E2ECase):
    """
    E2E Test: Verifies the "Happy Path" of the ActionPolicy.
    A standard document parsed from an .sdoc file with no source-code
    inclusions should have all document and node actions fully enabled.
    """

    def test_normal_document_ui_actions(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_project_index.assert_contains_document("Normal Document")
            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()

            # VERIFY: Document Level Unlocked
            screen_document.assert_document_config_edit_is_unlocked()

            # VERIFY: Node Level Unlocked
            node = screen_document.get_node()
            node.assert_add_action_is_unlocked()
            node.assert_edit_node_action_is_unlocked()
            node.assert_clone_node_action_is_unlocked()
            node.assert_delete_node_action_is_unlocked()
