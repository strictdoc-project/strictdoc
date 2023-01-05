import os
import shutil

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test_02_CreatingSectionMalformedRSTStatement(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

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

        self.click_link("+S⬊")

        self.type("#section_title", "Section title")

        self.type(
            "#section_content",
            """
- Broken RST markup

  - AAA
  ---
""".strip(),
        )

        self.click_xpath("//button[@type='submit' and text()='Save']")

        self.assert_text(
            "RST markup syntax error on line 4: "
            "Bullet list ends without a blank line; unexpected unindent."
        )
