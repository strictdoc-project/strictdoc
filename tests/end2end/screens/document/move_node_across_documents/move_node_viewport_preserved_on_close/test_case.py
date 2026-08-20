from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.requirement import Requirement
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

WITNESS_TEXT = "Witness requirement"


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
            screen_document.assert_text(WITNESS_TEXT)

            # The restoration mechanism anchors on whatever is actually
            # visible in the viewport at the moment content gets replaced.
            # Scroll the witness into view first, otherwise it is off-screen
            # and irrelevant to what restoration is supposed to preserve.
            self.sdoc_do_scroll_to_element_by_xpath(
                f"//sdoc-node[contains(., '{WITNESS_TEXT}')]"
            )
            screen_document.assert_node_containing_text_in_viewport(
                WITNESS_TEXT
            )

            # Move the very first requirement (above the witness) to the
            # very end (below the witness). This shifts every node between
            # the old and new position, including the witness, unless the
            # content viewport restoration mechanism compensates for it.
            moved_requirement = Requirement.with_node(self, node_order=1)
            moved_requirement.assert_requirement_title("Filler requirement 01")

            modal = moved_requirement.do_open_move_node_modal()
            modal.do_click_after("Filler requirement 15")
            modal.do_confirm_move()
            modal.assert_success()
            modal.do_close_modal_with_button()

            # The reading position must not be lost: the witness the user was
            # looking at is still visible in the content viewport, the same
            # way it stays visible after a node delete.
            screen_document.assert_node_containing_text_in_viewport(
                WITNESS_TEXT
            )

        assert test_setup.compare_sandbox_and_expected_output()
