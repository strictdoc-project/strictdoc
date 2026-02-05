import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            #
            # Switch to editing window #1 and edit the node.
            #
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_not_empty_document()

            screen_document.assert_text("Text statement.")

            node = screen_document.get_node(2)
            edit_form: Form_EditRequirement = (
                node.do_open_form_edit_requirement()
            )

            edit_form.assert_on_form()
            edit_form.do_fill_in_field_statement("Modified text statement.")

            #
            # Switch to editing window #2.
            #
            self.open_new_window()
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_not_empty_document()

            screen_document.assert_text("Text statement.")

            node = screen_document.get_node(2)
            edit_form: Form_EditRequirement = (
                node.do_open_form_edit_requirement()
            )

            edit_form.assert_on_form()
            edit_form.do_fill_in_field_statement("Modified text statement.")

            self.switch_to_window(0)
            edit_form.do_form_submit()

            screen_document.assert_text("Modified text statement.")

            self.switch_to_window(1)
            edit_form.do_form_submit_and_catch_error(
                "Cannot update the node because it has already been "
                "modified by another update action."
            )

            assert test_setup.compare_sandbox_and_expected_output()
