import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_UC03_T01_CancelNewSection(BaseCase):
    def test_01(self):
        # Prepare sandbox.
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )
        if os.path.isdir(path_to_sandbox):
            shutil.rmtree(path_to_sandbox)
        os.mkdir(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document.sdoc"),
            os.path.join(path_to_sandbox, "document.sdoc"),
        )

        # Run server.
        with SDocTestServer.create_from_existing(
            path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            self.assert_text("Document 1")
            self.assert_text("PROJECT INDEX")

            self.click_xpath('//*[@data-testid="tree-file-link"]')
            self.assert_text("Hello world!")

            self.hover_and_click(
                "sdoc-node", '[data-testid="node-menu-handler"]'
            )
            self.click('[data-testid="node-add-section-above-action"]')

            self.click_link("Cancel")

            self.assert_element_not_present(
                '[data-testid="form-cancel-action"]'
            )
