from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_T01_EditRequirement(BaseCase):
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

            requirement = screen_document.get_requirement()
            requirement.assert_requirement_title("Requirement title", "1")
            requirement.assert_requirement_uid_contains("Requirement UID")
            requirement.assert_requirement_statement_contains(
                "Requirement statement."
            )
            requirement.assert_requirement_rationale_contains(
                "Requirement rationale."
            )
            # Make sure that the normal (not table-based) requirement is
            # rendered.
            requirement.assert_requirement_style_simple()

            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            form_edit_requirement.assert_on_form()
            form_edit_requirement.do_fill_in_field_uid("Modified UID")
            form_edit_requirement.do_fill_in_field_title("Modified title")
            form_edit_requirement.do_fill_in_field_statement(
                "Modified statement."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Modified rationale."
            )
            form_edit_requirement.do_form_submit()

            requirement.assert_requirement_title("Modified title", "1")
            requirement.assert_requirement_uid_contains("Modified UID")
            requirement.assert_requirement_statement_contains(
                "Modified statement."
            )
            requirement.assert_requirement_rationale_contains(
                "Modified rationale."
            )
            # Make sure that after saving we return to the same display style.
            requirement.assert_requirement_style_simple()
            screen_document.assert_toc_contains("Modified title")

        assert test_setup.compare_sandbox_and_expected_output()
