"""
@relation(SDOC-SRS-107, scope=function)
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

            # An extension that no editable format supports is rejected
            # with a format-specific error. This project uses the default,
            # unrestricted server settings (no include_doc_paths/
            # exclude_doc_paths), so this error is distinct from -- and not
            # to be confused with -- the include/exclude path-filter
            # errors covered by the sibling tests in this folder.
            form_add_document.do_fill_in_path("document.pdf")
            form_add_document.do_form_submit_and_catch_error(
                "Document path must end with one of the supported "
                "document extensions: .sdoc, .md, .markdown."
            )

            # A supported extension (.sdoc) succeeds on the same, standard
            # settings.
            form_add_document.do_fill_in_path("document.sdoc")
            form_add_document.do_form_submit()

            screen_project_index.assert_contains_document("Document 1")

        assert test_setup.compare_sandbox_and_expected_output()
