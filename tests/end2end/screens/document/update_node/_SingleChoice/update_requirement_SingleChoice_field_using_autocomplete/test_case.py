"""
@relation(SDOC-SRS-55, SDOC-SRS-120, scope=file)
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
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            form_edit_requirement.assert_on_form()

            #
            # Text 'acc' in field STATUS should be autocompleted to 'accepted'.
            #
            form_edit_requirement.do_fill_in_field_and_autocomplete(
                "STATUS", "acc"
            )

            #
            # Text 'acc' in field OWNER should be autocompleted to 'Abigail ACCURACY'.
            #
            form_edit_requirement.do_fill_in_field_and_autocomplete(
                "OWNER", "acc"
            )

            form_edit_requirement.do_form_submit()

            screen_document.assert_text("accepted")

            screen_document.assert_text("Abigail ACCURACY")

        assert test_setup.compare_sandbox_and_expected_output()
