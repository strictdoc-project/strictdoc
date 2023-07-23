import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.form_add_document import (
    Form_AddDocument,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_TC51_G1_T04_BadCharacters(E2ECase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_empty_tree()

            form_add_document: Form_AddDocument = (
                screen_project_index.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 1")  # Empty document
            form_add_document.do_fill_in_path("docs/doc!#ument.sdoc")
            form_add_document.do_form_submit_and_catch_error(
                "Document path must be relative and only contain slashes, "
                "alphanumeric characters, and underscore symbols."
            )
