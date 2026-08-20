from selenium.webdriver.common.by import By

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
            document_screen = project_index.do_click_on_first_document()
            document_content_before_no_op = self.driver.find_element(
                By.ID, "frame_document_content"
            )

            first_text_node = Node(
                self,
                "(//sdoc-node[contains(., 'Hidden text content')])[last()]",
            )
            modal = first_text_node.do_open_move_node_modal()

            # The move tree is a structural copy of the document. It keeps
            # consecutive titleless nodes in source order and uses their
            # content as labels. An image-only field falls back to its file
            # name. Nested TEXT remains under its composite parent.
            modal.assert_row_marked_as_moved("Hidden text content.")
            modal.assert_row_has_node_type("Hidden text content.", "TEXT")
            modal.assert_row_has_move_targets("Consecutive text content.")
            modal.assert_row_precedes(
                "Hidden text content.", "Consecutive text content."
            )
            modal.assert_row_precedes(
                "Consecutive text content.", "only-image.png"
            )
            modal.assert_row_precedes(
                "only-image.png", "Visible node after text"
            )
            modal.assert_row_is_child_of(
                "Nested text content.", "Composite container"
            )

            # Selecting the first TEXT node's current boundary is still a
            # valid no-op now that the node itself appears in the tree.
            modal.do_click_after("Visible node before text")
            modal.do_confirm_move()
            modal.assert_no_change()
            modal.do_close_modal_with_button()
            document_screen.assert_text("Hidden text content")

            # A child placement appends to the container. Repeating it for the
            # existing last child is the corresponding composite-node no-op.
            last_child = Node(
                self,
                "(//sdoc-node[contains(., 'Last child requirement')])[last()]",
            )
            modal = last_child.do_open_move_node_modal()
            modal.do_click_inside("Composite container")
            modal.do_confirm_move()
            modal.assert_no_change()
            modal.do_close_modal_with_button()
            document_screen.assert_text("Last child requirement")
            document_content_after_no_op = self.driver.find_element(
                By.ID, "frame_document_content"
            )
            assert document_content_after_no_op == document_content_before_no_op

        assert test_setup.compare_sandbox_and_expected_output()
