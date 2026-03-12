from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.aside_project_tree import AsideProjectTree
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)
        original_title = "Test document"
        updated_title = "Document with modified title"

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document(original_title)

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title(original_title)

            aside_tree = AsideProjectTree(self)
            aside_tree.assert_is_aside_tree()
            aside_tree.assert_tree_contains_document_title(original_title)

            root_node = screen_document.get_root_node()
            form_config: Form_EditConfig = root_node.do_open_form_edit_config()

            form_config.do_fill_in_document_title(updated_title)
            form_config.do_form_submit()

            root_node.assert_document_title_contains(updated_title)
            aside_tree.assert_tree_contains_not(original_title)
            aside_tree.assert_tree_contains_document_title(updated_title)
