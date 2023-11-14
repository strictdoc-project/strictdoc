from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
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
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")
            screen_document.assert_text("Hello world!")

            # Requirement 1 has UID.
            # It shouldn't have a reset button.
            requirement1 = screen_document.get_requirement(1)
            requirement1.assert_requirement_uid_contains("REQ-1")
            form_edit_requirement1: Form_EditRequirement = (
                requirement1.do_open_form_edit_requirement()
            )
            form_edit_requirement1.assert_on_form()
            form_edit_requirement1.assert_uid_field_contains("REQ-1")
            form_edit_requirement1.assert_uid_field_has_not_reset_button()
            form_edit_requirement1.do_form_cancel()

            # New requirement form shouldn't have a reset button,
            # but must have the correct UID entered in the field.
            node_menu = requirement1.do_open_node_menu()
            form_add_requirement: Form_EditRequirement = (
                node_menu.do_node_add_requirement_above()
            )
            form_add_requirement.assert_on_form()
            form_add_requirement.assert_uid_field_has_not_reset_button()
            form_add_requirement.assert_uid_field_contains("REQ-2")
            form_add_requirement.do_form_cancel()

            # Requirement 2 has UID.
            # It shouldn't have a reset button.
            requirement2 = screen_document.get_requirement(2)
            requirement2.assert_requirement_has_no_uid()
            form_edit_requirement2: Form_EditRequirement = (
                requirement2.do_open_form_edit_requirement()
            )
            form_edit_requirement2.assert_on_form()
            form_edit_requirement2.assert_uid_field_has_reset_button()
            form_edit_requirement2.assert_uid_field_does_not_contain("REQ-2")
            # Use the reset button.
            form_edit_requirement2.do_reset_uid_field()
            form_edit_requirement2.assert_uid_field_contains("REQ-2")
            form_edit_requirement2.do_form_submit()

            # Checking the success of the button.
            requirement2.assert_requirement_uid_contains("REQ-2")

        assert test_setup.compare_sandbox_and_expected_output()
