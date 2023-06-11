from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_config import (
    Form_EditConfig,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC11_T50_EscapeHTML(BaseCase):
    def test(self):
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
            screen_document.assert_text("Link does not get corrupted")

            root_node = screen_document.get_root_node()
            form_config: Form_EditConfig = root_node.do_open_form_edit_config()

            form_config.assert_document_abstract_contains(
                "`Link does not get corrupted "
                "<https://github.com/strictdoc-project/"
                "sphinx-latex-reqspec-template>`_"
            )

            form_config.do_form_submit()

            root_node.assert_document_abstract_contains(
                "Link does not get corrupted\n"
                "Link does not get corrupted\n"
                "Link does not get corrupted\n"
            )

        assert test_setup.compare_sandbox_and_expected_output()
