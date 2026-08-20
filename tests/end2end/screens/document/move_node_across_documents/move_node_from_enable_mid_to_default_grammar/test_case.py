from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.node import Node
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

            project_index = Screen_ProjectIndex(self)
            source_screen = project_index.do_click_on_the_document_with_title(
                "MID Document"
            )
            source_screen.assert_text("Moved section")

            moved_section = Node.create_from_node_number(self, node_order=2)
            modal = moved_section.do_open_move_node_modal()
            modal.assert_document_incompatible("Default Document")
            modal.do_close_modal_with_button()
            source_screen.assert_text("Moved section")

        assert test_setup.compare_sandbox_and_expected_output()
