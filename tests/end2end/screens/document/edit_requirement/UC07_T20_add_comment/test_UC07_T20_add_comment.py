from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC07_T20_AddComment(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            requirement = screen_document.get_requirement()
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            # There should be no open comment fields, only an add comment
            # button.
            form_edit_requirement.assert_form_has_no_comments()

            comment1_mid = form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment(
                comment1_mid, "Comment #1"
            )

            comment2_mid = form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment(
                comment2_mid, "Comment #2"
            )

            comment3_mid = form_edit_requirement.do_form_add_field_comment()
            form_edit_requirement.do_fill_in_field_comment(
                comment3_mid, "Comment #3"
            )

            form_edit_requirement.do_form_submit()

            screen_document.assert_text("Comment #1")
            screen_document.assert_text("Comment #2")
            screen_document.assert_text("Comment #3")

        assert test_setup.compare_sandbox_and_expected_output()
