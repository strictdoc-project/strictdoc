from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.constants import RST_STRING_THAT_NEEDS_HTML_ESCAPING
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC11_T51_ReescapeHTMLByValidation(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_text("Link does not get corrupted")

            form_config: Form_EditConfig = (
                screen_document.do_open_form_edit_config()
            )
            form_config.do_fill_in_document_abstract(
                RST_STRING_THAT_NEEDS_HTML_ESCAPING
            )
            form_config.do_form_submit_and_catch_error(
                "RST markup syntax error on line 2: "
                "Bullet list ends without a blank line; unexpected unindent."
            )
            form_config.assert_contenteditable_contains(
                RST_STRING_THAT_NEEDS_HTML_ESCAPING
            )

        assert test_setup.compare_sandbox_and_expected_output()
