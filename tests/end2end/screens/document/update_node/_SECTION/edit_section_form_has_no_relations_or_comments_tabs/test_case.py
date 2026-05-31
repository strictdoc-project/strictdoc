import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
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

            form_edit_section.assert_on_form()

            # SECTION grammar has no relations and no COMMENT field:
            # neither tab should appear.
            form_edit_section.assert_tab_not_present("Relations")
            form_edit_section.assert_tab_not_present("Comments")

            form_edit_section.do_form_cancel()
