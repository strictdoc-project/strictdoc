from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer
from tests.end2end.test_helpers import available_systems


class Test(E2ECase):
    @available_systems(["macos", "windows"])
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

            section_1 = screen_document.get_section(node_order=1)
            section_1.do_copy_anchor_to_buffer()
            copied_text = self.paste_text()

            section = screen_document.get_section(node_order=2)
            form_edit_section: Form_EditSection = (
                section.do_open_form_edit_section()
            )
            form_edit_section.do_fill_in_title("Section with LINK")
            form_edit_section.do_fill_in_text(
                f"""
Statement with LINK:

[LINK: {copied_text}]
"""
            )

            form_edit_section.do_form_submit()
        assert test_setup.compare_sandbox_and_expected_output()
