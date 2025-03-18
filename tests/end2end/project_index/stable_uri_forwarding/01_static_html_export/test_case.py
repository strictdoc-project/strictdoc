import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_uid(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            target = "REQ-WITHIN-SECTION-3-1"

            # open the project index with a UID reference
            self.open(
                exporter.get_output_path_as_uri() + "index.html#" + target
            )

            # check that we are forwarded on the correct requirement
            screen_document = Screen_Document(self)
            screen_document.assert_target_by_anchor(target)

    def test_mid(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            target = "REQ-WITHIN-SECTION-3-1"
            mid = "3e06d65b527d4cab87680232880a3430"

            # open the project index with a UID reference
            self.open(exporter.get_output_path_as_uri() + "index.html#" + mid)

            # check that we are forwarded on the correct requirement
            screen_document = Screen_Document(self)
            screen_document.assert_target_by_anchor(target)
