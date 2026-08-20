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

            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Document One"
                )
            )
            screen_document.assert_on_screen_document()

            parent_requirement = Requirement.with_node(self, node_order=1)
            parent_requirement.assert_requirement_title("Parent requirement")

            moved_requirement = Requirement.with_node(self, node_order=2)
            moved_requirement.assert_requirement_title("Child requirement")
            moved_requirement.assert_requirement_has_parent_relation("REQ-002")

            modal = moved_requirement.do_open_move_node_modal()
            modal.do_click_after("Other document requirement")
            modal.do_confirm_move()
            modal.assert_success()
            modal.do_close_modal_with_button()

            # The requirement left behind still resolves its reverse (child)
            # relation to the moved requirement.
            parent_requirement.assert_requirement_has_child_relation("REQ-001")

            self.open(test_server.get_host_and_port())
            screen_project_index.assert_on_screen()
            destination_screen = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Document Two"
                )
            )
            destination_screen.assert_on_screen_document()

            relocated_requirement = Requirement.with_node(self, node_order=2)
            relocated_requirement.assert_requirement_title("Child requirement")
            # The moved requirement's own relation field is unchanged and
            # still resolves after the cross-document move.
            relocated_requirement.assert_requirement_has_parent_relation(
                "REQ-002"
            )

        assert test_setup.compare_sandbox_and_expected_output()
