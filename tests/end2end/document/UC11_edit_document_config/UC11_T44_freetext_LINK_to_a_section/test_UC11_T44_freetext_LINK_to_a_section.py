from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC11_T44_FreeTextLINKToSection(BaseCase):
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

            screen_document.assert_on_screen()
            screen_document.assert_text("See the section Referenced section")

            form_config: Form_EditConfig = (
                screen_document.do_open_form_edit_config()
            )

            modified_text = (
                "MODIFIED by test. See the section [LINK: SDOC_UG_CONTACT]."
            )
            form_config.do_fill_in_document_abstract(modified_text)
            form_config.assert_document_abstract_contains(modified_text)

            form_config.do_form_submit()

            screen_document.assert_text(
                "MODIFIED by test. See the section Referenced section"
            )

        assert test_setup.compare_sandbox_and_expected_output()
