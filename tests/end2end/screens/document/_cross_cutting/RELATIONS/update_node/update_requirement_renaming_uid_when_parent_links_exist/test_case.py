"""
@relation(SDOC-SRS-158, scope=file)
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

            # Open form and add 1 fields:
            requirement = screen_document.get_node(2)
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement.assert_uid_field_has_not_restore_button()

            form_edit_requirement.do_fill_in_field_uid("Modified UID")

            form_edit_requirement.do_form_submit_and_catch_error(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has parent "
                "requirement relations. For now, manually delete the relations,"
                " rename the UID, recreate the relations."
            )

            form_edit_requirement.assert_uid_field_contains("Modified UID")
            form_edit_requirement.assert_uid_field_has_restore_button()

            form_edit_requirement.do_restore_uid_field()

            form_edit_requirement.assert_uid_field_contains("REQ-002")
            form_edit_requirement.assert_uid_field_does_not_contain(
                "Modified UID"
            )
            form_edit_requirement.assert_error_not_present(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has parent "
                "requirement relations."
            )

            # Clearing the UID entirely (instead of typing a replacement) is
            # a separate code path: an empty UID field is rendered via
            # components/form/row/row_uid_with_reset/frame.jinja, not
            # row_with_text_field.jinja, and triggers both the "must have a
            # UID" and the "renaming blocked" errors at once.
            form_edit_requirement.do_clear_field("UID")

            form_edit_requirement.do_form_submit_and_catch_error(
                "Requirement with parent relations must have an UID. "
                "Either provide a parent UID, or "
                "delete the parent requirement relations."
            )
            form_edit_requirement.do_form_submit_and_catch_error(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has parent "
                "requirement relations. For now, manually delete the relations,"
                " rename the UID, recreate the relations."
            )

            form_edit_requirement.assert_uid_field_has_restore_button()

            form_edit_requirement.do_restore_uid_field()

            form_edit_requirement.assert_uid_field_contains("REQ-002")
            form_edit_requirement.assert_error_not_present(
                "Requirement with parent relations must have an UID."
            )
            form_edit_requirement.assert_error_not_present(
                "Not supported yet: "
                "Renaming a requirement UID when the requirement has parent "
                "requirement relations."
            )

        assert test_setup.compare_sandbox_and_expected_output()
