from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_T10_EditTableRequirement(BaseCase):
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

            # Make sure that the table-based requirement is rendered.
            screen_document.assert_requirement_style_table()

            form_edit_requirement: Form_EditRequirement = (
                screen_document.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_fill_in_field_uid("Modified UID")
            form_edit_requirement.do_fill_in_field_title("Modified title")
            form_edit_requirement.do_fill_in_field_statement(
                "Modified statement."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Modified rationale."
            )
            form_edit_requirement.do_form_submit()

            screen_document.assert_text("1. Modified title")
            screen_document.assert_text("Modified UID")
            screen_document.assert_text("Modified statement.")
            screen_document.assert_text("Modified rationale.")
            # Make sure that after saving we return to the same display style
            # and the table-based requirement is rendered.
            screen_document.assert_requirement_style_table()
            screen_document.assert_toc_contains_string("Modified title")

        assert test_setup.compare_sandbox_and_expected_output()
