from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.requirement import Requirement
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

            moved_requirement = Requirement.with_node(self, node_order=1)
            moved_requirement.assert_requirement_title("First requirement")

            modal = moved_requirement.do_open_move_node_modal()
            modal.assert_row_marked_as_moved("First requirement")
            modal.do_click_after("Second requirement")
            modal.do_confirm_move()
            modal.assert_success()
            modal.assert_go_to_new_location_href_contains("#REQ-001")
            destination_screen = modal.do_go_to_new_location()
            destination_screen.assert_node_containing_text_in_viewport(
                "First requirement"
            )
            self.assert_url_contains("#REQ-001")

            # Same-document move: the moved node reappears at its new
            # position instead of disappearing, per task.md.
            screen_document.assert_text("First requirement")
            screen_document.assert_text("Second requirement")

            reordered_first = Requirement.with_node(self, node_order=1)
            reordered_first.assert_requirement_title("Second requirement")
            reordered_second = Requirement.with_node(self, node_order=2)
            reordered_second.assert_requirement_title("First requirement")

        assert test_setup.compare_sandbox_and_expected_output()
