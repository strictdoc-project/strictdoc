from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.document_root import Form_EditConfig
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
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

        # Run server.
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            # Create Document 2 and change UID to DOC-2
            form_add_document: Form_AddDocument = (
                screen_project_index.do_open_modal_form_add_document()
            )
            form_add_document.do_fill_in_title("Document 2")
            form_add_document.do_fill_in_path("document2.sdoc")
            form_add_document.do_form_submit()

            screen_document = screen_project_index.do_click_on_the_document(2)
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 2")

            document_node = screen_document.get_root_node()
            form_edit_document: Form_EditConfig = (
                document_node.do_open_form_edit_config()
            )
            form_edit_document.do_fill_in_document_uid("DOC-2")
            form_edit_document.do_form_submit()

            # Go to Document 1 and link requirement statement to DOC-2
            screen_document.do_click_on_tree_document(1)
            screen_document.assert_header_document_title("Document 1")

            req_node_1 = screen_document.get_node(1)
            req_node_edit_form: Form_EditRequirement = (
                req_node_1.do_open_form_edit_requirement()
            )
            req_node_edit_form.do_fill_in_field_statement(
                "Modified. [LINK: DOC-2]"
            )
            req_node_edit_form.do_form_submit()

            # Click new link and verify it brings us to Document 2
            self.click_xpath("//sdoc-node//a[contains(., 'Document 2')]")
            screen_document.assert_header_document_title("Document 2")

        assert test_setup.compare_sandbox_and_expected_output()
