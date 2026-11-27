"""
A stable link <file>.html?a=<UID> opens the page of the node.

@relation(SDOC-SRS-217, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.html_single.html_single_test_exporter import (
    HTMLSingleTestExporter,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_FRAME = "iframe.strictdoc-html-single-frame"


class Test(E2ECase):
    def test(self):
        with HTMLSingleTestExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            file_uri = exporter.get_file_uri("Single_file_test.html")
            self.open(file_uri + "?a=REQ-2")

            self.switch_to_frame(SELECTOR_FRAME)
            self.assert_text("System X shall do B.")
            self.switch_to_default_content()
            assert self.get_current_url() == (
                file_uri + "#/02_stable_link/input/input.sdoc.html#REQ-2"
            )

            # A route to a page that the export leaves out shows a notice.
            self.open(file_uri + "#/_source_files/missing.py.html")
            self.switch_to_frame(SELECTOR_FRAME)
            self.assert_element('[data-testid="html-single-missing-page"]')
