import os
import shutil
from pathlib import Path

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_sandbox = os.path.join(path_to_this_test_file_folder, ".sandbox")
path_to_sandbox_document = os.path.join(path_to_sandbox, "document.sdoc")
path_to_expected_document = os.path.join(
    path_to_this_test_file_folder, "document.expected.sdoc"
)


class Test_UC02_04_EscapeHTML(BaseCase):
    def test_01(self):
        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document.sdoc"),
            os.path.join(path_to_sandbox, "document.sdoc"),
        )

        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("Document 1")
        self.assert_text("PROJECT INDEX")

        self.click_link("DOC")

        self.assert_text("Link does not get corrupted")

        self.hover_and_click("sdoc-node", '[data-testid="node-edit-action"]')

        self.assert_text(
            "`Link does not get corrupted "
            "<https://github.com/strictdoc-project/"
            "sphinx-latex-reqspec-template>`_"
        )

        self.click_xpath("//button[@type='submit' and text()='Save']")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))

        sandbox_document = Path(path_to_sandbox_document).read_text()
        expected_document = Path(path_to_expected_document).read_text()
        assert sandbox_document == expected_document
