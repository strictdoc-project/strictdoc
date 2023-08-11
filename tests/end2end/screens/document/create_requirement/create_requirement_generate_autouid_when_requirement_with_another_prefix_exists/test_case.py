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

            # Requirement 1
            requirement_1 = screen_document.get_requirement(1)
            assert requirement_1 is not None
            requirement_1.assert_requirement_uid_contains("SOME-OTHER-PREFIX-1")

            # Requirement 2
            requirement_1_node_menu = requirement_1.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                requirement_1_node_menu.do_node_add_requirement_below()
            )
            form_edit_requirement.do_fill_in_field_title("Requirement title #2")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #2."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Requirement rationale #2."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 2:
            screen_document.assert_toc_contains("Requirement title #2")

            requirement_2 = screen_document.get_requirement(2)
            requirement_2.assert_requirement_title("Requirement title #2", "2")
            requirement_2.assert_requirement_uid_contains("REQ-1")

            # Requirement 3
            requirement_2_node_menu = requirement_2.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                requirement_2_node_menu.do_node_add_requirement_below()
            )
            form_edit_requirement.do_fill_in_field_title("Requirement title #3")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #3."
            )
            form_edit_requirement.do_fill_in_field_rationale(
                "Requirement rationale #3."
            )
            form_edit_requirement.do_form_submit()

            # Expected for Requirement 3:

            requirement_3 = screen_document.get_requirement(3)
            requirement_3.assert_requirement_title("Requirement title #3", "3")
            requirement_3.assert_requirement_uid_contains("REQ-2")
            screen_document.assert_toc_contains("Requirement title #3")

        assert test_setup.compare_sandbox_and_expected_output()
