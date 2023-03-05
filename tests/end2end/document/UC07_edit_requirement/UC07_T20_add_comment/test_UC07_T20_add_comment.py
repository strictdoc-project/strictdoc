from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_T20_AddComment(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_string("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen()
            screen_document.assert_is_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            form_edit_requirement: Form_EditRequirement = (
                screen_document.do_open_edit_form()
            )

            # There should be no open comment fields, only an add comment
            # button.
            form_edit_requirement.assert_form_has_no_comments()

            form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment("Comment #1")

            form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment("Comment #2", 2)

            form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment("Comment #3", 3)

            form_edit_requirement.do_form_submit()

            screen_document.assert_text("Comment #1")
            screen_document.assert_text("Comment #2")
            screen_document.assert_text("Comment #3")

        assert test_setup.compare_sandbox_and_expected_output()
