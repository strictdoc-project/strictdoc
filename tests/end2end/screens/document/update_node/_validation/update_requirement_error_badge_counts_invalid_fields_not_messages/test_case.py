"""
@relation(SDOC-SRS-55, scope=file)
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

            # REQ-002 has both an outgoing Parent relation (to REQ-001) and
            # an incoming Child relation (from REQ-003), so renaming its UID
            # adds two separate error messages to the same UID field.
            requirement = screen_document.get_node(2)
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            form_edit_requirement.do_fill_in_field_uid("Modified UID")
            form_edit_requirement.do_clear_field("STATEMENT")

            form_edit_requirement.do_form_submit_and_catch_error(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has parent "
                "requirement relations. For now, manually delete the relations,"
                " rename the UID, recreate the relations."
            )
            form_edit_requirement.do_form_submit_and_catch_error(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has child "
                "requirement relations. For now, manually delete the relations,"
                " rename the UID, recreate the relations."
            )
            form_edit_requirement.do_form_submit_and_catch_error(
                "Node's STATEMENT must not be empty. "
                "If there is no appropriate value for this field yet, "
                "enter TBD (to be done) or TBC (to be confirmed)."
            )

            # 3 error messages (2 on UID, 1 on STATEMENT) but only 2 fields
            # are actually invalid: the "Fields" tab badge must show 2.
            form_edit_requirement.assert_tab_error_count("Fields", 2)

            form_edit_requirement.do_form_cancel()

        assert test_setup.compare_sandbox_and_expected_output()
