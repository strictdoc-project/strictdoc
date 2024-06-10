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
            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                root_node_menu.do_node_add_requirement_first()
            )
            form_edit_requirement.do_fill_in_field_uid("REQ-1")
            form_edit_requirement.do_fill_in_field_title("Req #1")
            form_edit_requirement.do_fill_in_field_statement(
                "[ANCHOR: ANC-1, Anchor title]"
            )
            form_edit_requirement.do_form_submit()

            # Requirement 2
            root_node = screen_document.get_node(1)
            root_node_menu = root_node.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                root_node_menu.do_node_add_requirement_below()
            )
            form_edit_requirement.do_fill_in_field_uid("REQ-2")
            form_edit_requirement.do_fill_in_field_title("Req #2")
            form_edit_requirement.do_fill_in_field_statement(
                "See [LINK: ANC-1]."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 1:

            requirement_2 = screen_document.get_node(2)
            requirement_2.assert_requirement_statement_contains(
                "See 🔗 Anchor title"
            )

        assert test_setup.compare_sandbox_and_expected_output()
