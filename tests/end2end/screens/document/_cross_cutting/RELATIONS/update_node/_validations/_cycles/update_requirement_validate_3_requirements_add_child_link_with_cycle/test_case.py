"""
@relation(SDOC-SRS-158, SDOC-SRS-30, scope=file)
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

            # Existing Requirement 1:
            added_requirement_1_level = "1"
            added_requirement_1_position = 1

            requirement1 = screen_document.get_node(
                added_requirement_1_position
            )

            requirement1.assert_requirement_title(
                "Requirement title #1",
                added_requirement_1_level,
            )
            screen_document.assert_toc_contains("Requirement title #1")

            # Existing Requirement 2:
            added_requirement_2_level = "2"
            added_requirement_2_position = 2

            requirement2 = screen_document.get_node(
                added_requirement_2_position
            )

            requirement2.assert_requirement_title(
                "Requirement title #2",
                added_requirement_2_level,
            )
            screen_document.assert_toc_contains("Requirement title #2")

            # Edit Requirement 1: add one relation
            form_edit_requirement: Form_EditRequirement = (
                requirement1.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_open_tab("Relations")
            new_relation_mid = (
                form_edit_requirement.do_form_add_field_relation()
            )
            form_edit_requirement.do_fill_in_field_relation(
                new_relation_mid, "REQ-003"
            )
            form_edit_requirement.do_select_relation_role(
                new_relation_mid, "Child"
            )

            form_edit_requirement.do_form_submit_and_catch_error(
                "A cycle detected: "
                "requirements in the document tree must not reference each "
                "other. Problematic UID: REQ-001, cycle: "
                "['REQ-001', 'REQ-003', 'REQ-002']."
            )

        assert test_setup.compare_sandbox_and_expected_output()
