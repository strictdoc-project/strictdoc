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
    """
    This test exercises that StrictDoc validates the UID uniqueness when a
    requirement is being created. It is not a regression, we have simply not
    covered this validation case as we were implementing the Create Requirement
    forms and the corresponding Python flow.
    The issue has been reported here:
    https://github.com/strictdoc-project/strictdoc/issues/1587.
    """

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

            requirement_node = screen_document.get_requirement(1)
            root_node_menu = requirement_node.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                root_node_menu.do_node_add_requirement_below()
            )

            # Deliberately entering the UID that already exists.
            form_edit_requirement.do_fill_in_field_uid("REQ-001")
            form_edit_requirement.do_fill_in_field_statement("Shall do")

            form_edit_requirement.do_form_submit_and_catch_error(
                "The chosen UID must be unique. "
                "Another requirement with this UID already exists: 'REQ-001'."
            )

        assert test_setup.compare_sandbox_and_expected_output()
