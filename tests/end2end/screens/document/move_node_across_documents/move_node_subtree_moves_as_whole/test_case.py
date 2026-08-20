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

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Document One"
                )
            )
            screen_document.assert_on_screen_document()
            screen_document.assert_text("Child requirement one")
            screen_document.assert_text("Child requirement two")
            screen_document.assert_text("Sibling requirement")

            # The section has no stable node testid to key off, so it is
            # addressed by its position among all sdoc-node elements.
            # Position 1 is the document root, so the section is position 2.
            moved_section = Node.create_from_node_number(self, node_order=2)

            modal = moved_section.do_open_move_node_modal()
            modal.assert_document_present("Document Two")

            # The section and both of its children are part of the moved
            # branch: none of them can be picked as a drop target, blocked
            # in the UI itself (task.md), not only rejected by the backend.
            modal.assert_row_has_no_move_targets("Moved section")
            modal.assert_row_has_no_move_targets("Child requirement one")
            modal.assert_row_has_no_move_targets("Child requirement two")

            # An unrelated node outside the moved branch remains a valid
            # target.
            modal.assert_row_has_move_targets("Sibling requirement")

            modal.do_click_after("Other document requirement")
            modal.do_confirm_move()
            modal.assert_success()
            modal.do_close_modal_with_button()

            screen_document.assert_no_text("Moved section")
            screen_document.assert_no_text("Child requirement one")
            screen_document.assert_no_text("Child requirement two")
            screen_document.assert_text("Sibling requirement")

        assert test_setup.compare_sandbox_and_expected_output()
