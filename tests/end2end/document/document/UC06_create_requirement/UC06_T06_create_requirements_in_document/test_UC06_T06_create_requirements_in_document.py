from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.constants import NODE_1
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC06_T06_CreateRequirementsInDocument(BaseCase):
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

            screen_document.assert_on_screen()
            screen_document.assert_is_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            # Requirement 1
            form_edit_requirement: Form_EditRequirement = (
                screen_document.do_node_add_requirement_first()
            )
            form_edit_requirement.do_fill_in_field_uid("REQ-001")
            form_edit_requirement.do_fill_in_field_title("Requirement title #1")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #1."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Requirement rationale #1."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 1:
            added_requirement_1_level = "1"
            added_requirement_1_position = NODE_1

            screen_document.assert_node_title_contains(
                "Requirement title #1",
                added_requirement_1_level,
                added_requirement_1_position,
            )
            screen_document.assert_toc_contains_string("Requirement title #1")

            # Requirement 2
            form_edit_requirement: Form_EditRequirement = (
                screen_document.do_node_add_requirement_below(
                    added_requirement_1_position
                )
            )
            form_edit_requirement.do_fill_in_field_uid("REQ-002")
            form_edit_requirement.do_fill_in_field_title("Requirement title #2")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #2."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Requirement rationale #2."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 2:
            added_requirement_2_level = "2"
            added_requirement_2_position = added_requirement_1_position + 1

            screen_document.assert_node_title_contains(
                "Requirement title #2",
                added_requirement_2_level,
                added_requirement_2_position,
            )
            screen_document.assert_toc_contains_string("Requirement title #2")

            # Requirement 3
            form_edit_requirement: Form_EditRequirement = (
                screen_document.do_node_add_requirement_below(
                    added_requirement_2_position
                )
            )
            form_edit_requirement.do_fill_in_field_uid("REQ-003")
            form_edit_requirement.do_fill_in_field_title("Requirement title #3")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #3."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Requirement rationale #3."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 3:
            added_requirement_3_level = "3"
            added_requirement_3_position = added_requirement_2_position + 1

            screen_document.assert_node_title_contains(
                "Requirement title #3",
                added_requirement_3_level,
                added_requirement_3_position,
            )
            screen_document.assert_toc_contains_string("Requirement title #3")

            # Check the resulting TOC.
            screen_document.assert_toc_contains_string("Requirement title #1")
            screen_document.assert_toc_contains_string("Requirement title #2")
            screen_document.assert_toc_contains_string("Requirement title #3")

        assert test_setup.compare_sandbox_and_expected_output()
