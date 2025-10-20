"""
@relation(SDOC-SRS-106, SDOC-SRS-120, scope=file)
"""

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

            #
            # Edit the requirement 2 and set "TAGS: Tag2".
            #
            requirement = screen_document.get_node(2)
            form_edit_requirement_2: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement_2.assert_on_form()

            form_edit_requirement_2.do_fill_in("TAGS", "Tag2")
            form_edit_requirement_2.do_form_submit()

            #
            # Create a requirement after the existing requirements.
            #
            test_case_node = screen_document.get_node(2)

            test_case_menu = test_case_node.do_open_node_menu()

            form_edit_requirement_new: Form_EditRequirement = (
                test_case_menu.do_node_add_element_below("REQUIREMENT")
            )

            form_edit_requirement_new.do_fill_in_field_uid("REQ-3")
            form_edit_requirement_new.do_fill_in_field_title("New Requirement")
            form_edit_requirement_new.do_fill_in_field_statement(
                "Shall test foo 2."
            )

            #
            # Typing 'tag' in field TAGS should be autocompleted to 'Tag1'.
            #
            form_edit_requirement_new.do_fill_in_field_and_autocomplete(
                "TAGS", "tag"
            )

            #
            # Typing 'tag' in field TAGS should be autocompleted to 'Tag2',
            # the next matching choice that is not yet selected.
            #
            form_edit_requirement_new.do_fill_in_field_and_autocomplete_again(
                "TAGS", "tag"
            )

            form_edit_requirement_new.do_form_submit()

            node_2 = screen_document.get_node(node_order=3)

            node_2.assert_requirement_title("New Requirement", "3")
            screen_document.assert_toc_contains("New Requirement")

            screen_document.assert_text("Tag1, Tag2")

        assert test_setup.compare_sandbox_and_expected_output()
