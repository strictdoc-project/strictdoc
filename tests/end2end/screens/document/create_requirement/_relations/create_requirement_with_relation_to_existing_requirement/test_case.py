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

            # Requirement 1
            node_requirement1 = screen_document.get_requirement(1)
            node_menu_requirement1 = node_requirement1.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                node_menu_requirement1.do_node_add_requirement_below()
            )

            form_edit_requirement.assert_tab_is_open("Fields")
            form_edit_requirement.do_fill_in_field_uid("REQ-002")
            form_edit_requirement.do_fill_in_field_title("Requirement #2 title")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement #2 statement."
            )
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement #2 statement."
            )

            form_edit_requirement.do_open_tab("Relations")
            requirement_parent_mid = (
                form_edit_requirement.do_form_add_field_parent_link()
            )
            form_edit_requirement.do_fill_in_field_parent_link(
                requirement_parent_mid, "REQ-001"
            )

            form_edit_requirement.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
