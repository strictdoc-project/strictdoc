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

            project_index = Screen_ProjectIndex(self)
            source_screen = project_index.do_click_on_the_document_with_title(
                "Document One"
            )
            moved_requirement = Requirement.with_node(self, node_order=1)
            moved_requirement.assert_requirement_title("First requirement")

            modal = moved_requirement.do_open_move_node_modal()
            modal.assert_document_present("Empty Document")
            modal.assert_document_has_no_collapse_control("Empty Document")
            modal.assert_row_has_collapse_control("Empty section")
            modal.assert_row_is_child_of(
                "This section has a TEXT child.", "Empty section"
            )
            modal.assert_row_has_no_collapse_control("Empty composite target")

            # The picker offers no child zone for a regular requirement. A
            # forced request still receives a user-facing validation message.
            modal.do_force_inside_non_composite("Second requirement")
            modal.assert_error(
                "A non-composite node cannot contain child nodes."
            )
            modal.do_close_modal()

            modal = moved_requirement.do_open_move_node_modal()
            modal.do_click_inside_document("Empty Document")
            modal.assert_move_confirmation_for_document("Empty Document")
            modal.do_confirm_move()
            modal.assert_success()
            modal.do_close_modal_with_button()

            source_screen.assert_no_text("First requirement")
            source_screen.assert_text("Second requirement")

            # A truly empty composite has no collapse control, but still
            # exposes the child placement needed to receive its first child.
            second_requirement = Requirement.with_node(self, node_order=1)
            second_requirement.assert_requirement_title("Second requirement")
            modal = second_requirement.do_open_move_node_modal()
            modal.assert_row_has_no_collapse_control("Empty composite target")
            modal.do_click_inside("Empty composite target")
            modal.do_confirm_move()
            modal.assert_success()
            modal.do_close_modal_with_button()

            source_screen.assert_text("Second requirement")
            source_screen.assert_text("Empty composite target")

        assert test_setup.compare_sandbox_and_expected_output()
