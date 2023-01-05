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


class Test_UC02_03_SanitizingTrailingSymbols(BaseCase):
    def test_01(self):
        test_server = SDocTestServer.create(path_to_sandbox)
        shutil.copyfile(
            os.path.join(path_to_this_test_file_folder, "document.sdoc"),
            os.path.join(path_to_sandbox, "document.sdoc"),
        )

        test_server.run()

        self.open("http://localhost:8001")

        self.assert_text("Document 1")
        self.assert_text("Project index")

        self.click_link("DOC")

        self.assert_text("Hello world!")

        self.click_link("Edit")

        # Contains trailing symbols.
        self.type(
            "#document_freetext",
            """
Hello world!    

Hello world!    

Hello world!    
            """,  # noqa: W291
        )
        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text_not_visible("Save")

        assert os.path.exists(os.path.join(path_to_sandbox, "document.sdoc"))

        sandbox_document = Path(path_to_sandbox_document).read_text()
        expected_document = Path(path_to_expected_document).read_text()
        assert sandbox_document == expected_document
