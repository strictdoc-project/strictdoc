from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_G1_T01_AddOneLink(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            # Existing Requirement 1:
            added_requirement_1_level = "1"
            added_requirement_1_position = 1

            requirement1 = screen_document.get_requirement(
                added_requirement_1_position
            )

            requirement1.assert_requirement_title(
                "Requirement title #1",
                added_requirement_1_level,
            )
            screen_document.assert_toc_contains("Requirement title #1")

            # Existing Requirement 2:
            added_requirement_2_level = "2"
            added_requirement_2_position = 2

            requirement2 = screen_document.get_requirement(
                added_requirement_2_position
            )

            requirement2.assert_requirement_title(
                "Requirement title #2",
                added_requirement_2_level,
            )
            screen_document.assert_toc_contains("Requirement title #2")

            # Edit Requirement 2: add one parent link
            form_edit_requirement: Form_EditRequirement = (
                requirement2.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_form_add_field_parent_link()
            form_edit_requirement.do_fill_in_field_parent_link("REQ-001")
            form_edit_requirement.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
