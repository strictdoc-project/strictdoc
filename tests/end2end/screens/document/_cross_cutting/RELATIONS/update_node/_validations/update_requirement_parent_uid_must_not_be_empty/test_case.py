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

            requirement = screen_document.get_node()

            #
            # Case 1: Adding a new empty relation field — form saves successfully,
            # the empty relation is silently skipped (not saved).
            # The existing PARENT: REQ-002 relation is preserved.
            #
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_open_tab("Relations")
            form_edit_requirement.do_form_add_field_relation()
            form_edit_requirement.do_form_submit()

            #
            # Case 2: Clearing the UID of an existing saved relation (without
            # deleting the row) must raise a validation error.
            # This is distinct from Case 1: the row already exists in the document,
            # so a blank UID is treated as a mistake, not an intent to remove.
            #
            form_edit_requirement = requirement.do_open_form_edit_requirement()
            form_edit_requirement.do_open_tab("Relations")
            form_edit_requirement.do_clear_relation_uid(1)
            form_edit_requirement.do_form_submit_and_catch_error(
                "Requirement relation UID must not be empty."
            )

        assert test_setup.compare_sandbox_and_expected_output()
