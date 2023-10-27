from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.form_add_document import (
    Form_AddDocument,
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
            screen_project_index.assert_empty_tree()

            # Add file with .sdoc extension
            form_add_document: Form_AddDocument = (
                screen_project_index.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 1")  # Empty document
            form_add_document.do_fill_in_path("docs/document1.sdoc")
            form_add_document.do_form_submit()

            # Add file without .sdoc extension
            form_add_document: Form_AddDocument = (
                screen_project_index.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 2")  # Empty document
            form_add_document.do_fill_in_path("docs/document2")
            form_add_document.do_form_submit()

            screen_project_index.assert_contains_document("Document 2")

        assert test_setup.compare_sandbox_and_expected_output()
