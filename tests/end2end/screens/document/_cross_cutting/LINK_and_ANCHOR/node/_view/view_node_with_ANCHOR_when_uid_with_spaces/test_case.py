from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        """
        This basic test ensures that an ANCHOR that has a UID with a space character
        can be followed to by clicking a LINK that points to it.
        The HTML anchors should have all space characters replaced with "-".
        https://github.com/strictdoc-project/strictdoc/issues/1916
        https://github.com/strictdoc-project/strictdoc/pull/1917
        """
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
            screen_document.assert_header_document_title("Document 1")

            self.click_xpath("//a[contains(., 'Anchor title')]")

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 2")

            self.assert_url_contains("#ANC-1")
