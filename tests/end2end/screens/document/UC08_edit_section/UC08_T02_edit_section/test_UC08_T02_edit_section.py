from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC08_T02_EditSection(BaseCase):
    def test_01(self):
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

            section = screen_document.get_section()
            form_edit_section: Form_EditSection = (
                section.do_open_form_edit_section()
            )
            form_edit_section.do_fill_in_title("Modified title")
            form_edit_section.do_fill_in_text("Modified statement.")
            form_edit_section.do_form_submit()

            section.assert_section_title("Modified title", "1")
            section.assert_section_text("Modified statement.")
            screen_document.assert_toc_contains("Modified title")

        assert test_setup.compare_sandbox_and_expected_output()
