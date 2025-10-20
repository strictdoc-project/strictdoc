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

            section = screen_document.get_node(1)
            form_edit_section: Form_EditRequirement = (
                section.do_open_form_edit_requirement()
            )
            form_edit_section.do_fill_in("UID", "Existing-Section-UID")
            form_edit_section.do_form_submit_and_catch_error(
                "The chosen UID must be unique. "
                "Another node with this UID already exists: "
                "'Existing-Section-UID'."
            )

        assert test_setup.compare_sandbox_and_expected_output()
