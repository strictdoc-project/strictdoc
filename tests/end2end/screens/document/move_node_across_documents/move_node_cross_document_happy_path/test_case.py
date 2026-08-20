from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.node import Node
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
            screen_document.assert_text("First requirement")

            # A node containing an inserted image keeps a visible Move action,
            # but the action is disabled because its asset path cannot be
            # recalculated, unlike Move for a plain node.
            first_requirement = Requirement.with_node(self, node_order=1)
            first_requirement.assert_requirement_title("First requirement")
            first_requirement.assert_move_node_action_is_unlocked()

            image_requirement = Requirement.with_node(self, node_order=2)
            image_requirement.assert_requirement_title(
                "Requirement with an image"
            )
            image_requirement.assert_move_node_action_is_locked_with_tooltip(
                "Moving nodes with images is not supported yet"
            )

            image_branch = Node(
                test_case=self,
                node_xpath="//sdoc-node[contains(., "
                "'Branch containing an image')]",
            )
            image_branch.assert_move_node_action_is_locked_with_tooltip(
                "Moving nodes with images is not supported yet"
            )

            # First move: cross-document, dismissed with the modal's close
            # button. The content behind the modal already reflects the
            # move, so closing needs no further update.
            modal = first_requirement.do_open_move_node_modal()
            modal.assert_document_present("Document One")
            modal.assert_document_present("Document Two")
            modal.assert_row_marked_as_moved("First requirement")

            # Exercise the feature-local collapse script through its real
            # controls. Destination documents start collapsed, and the same
            # button must support both expansion and collapse.
            modal.assert_document_collapsed("Document Two")
            modal.do_toggle_document("Document Two")
            modal.assert_document_expanded("Document Two")
            modal.assert_row_present("Other document requirement")
            modal.do_toggle_document("Document Two")
            modal.assert_document_collapsed("Document Two")

            modal.do_click_after("Other document requirement")
            modal.assert_move_confirmation_for_node(
                document_title="Document Two",
                placement_label="after",
                node_title="Other document requirement",
                node_type="REQUIREMENT",
            )
            modal.do_cancel_move()
            modal.assert_move_confirmation_absent()

            modal.do_click_after("Other document requirement")
            modal.do_cancel_move_with_escape()
            modal.assert_move_confirmation_absent()

            modal.do_click_after("Other document requirement")
            modal.do_confirm_move_with_enter()
            modal.assert_success()
            modal.do_close_modal_with_button()

            screen_document.assert_no_text("First requirement")
            screen_document.assert_text("Third requirement")

            # Second move: cross-document again, this time followed through
            # the modal's "go to new location" link instead of closing it.
            third_requirement = Node(
                test_case=self,
                node_xpath="//sdoc-node[contains(., 'Third requirement')]",
            )
            modal = third_requirement.do_open_move_node_modal()
            modal.do_click_after("Other document requirement")
            modal.do_confirm_move()
            modal.assert_success()
            modal.assert_go_to_new_location_href_contains("document_2.html#")

            destination_screen = modal.do_go_to_new_location()
            destination_screen.assert_on_screen_document()
            destination_screen.assert_header_document_title("Document Two")
            self.assert_url_contains("document_2.html#")
            destination_screen.assert_node_containing_text_in_viewport(
                "Third requirement"
            )

        assert test_setup.compare_sandbox_and_expected_output()
