"""
@relation(SDOC-SRS-107, scope=file)
"""

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

            form_add_document: Form_AddDocument = (
                screen_project_index.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 1")

            # First, fill in an invalid path.
            form_add_document.do_fill_in_path("document")
            form_add_document.do_form_submit_and_catch_error(
                "Document path is not a valid path according to the project "
                "config's setting 'include_doc_paths': ['docs/**']."
            )

            # Then, fill in a valid path.
            form_add_document.do_fill_in_path("docs/document")
            form_add_document.do_form_submit()

            screen_project_index.assert_contains_document("Document 1")

        assert test_setup.compare_sandbox_and_expected_output()
