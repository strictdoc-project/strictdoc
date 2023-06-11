import os

from seleniumbase import BaseCase

from tests.end2end.helpers.screens.project_index.form_import_reqif import (
    Form_ImportReqIF,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_G1_T01_NotAReqIFormat(BaseCase):
    def test(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_empty_tree()

            form_import: Form_ImportReqIF = (
                screen_project_index.do_open_modal_import_reqif()
            )
            form_import.do_choose_file(path_to_reqif_sample)

            form_import.do_form_submit_and_catch_error(
                "Cannot parse ReqIF file: "
                "Start tag expected, '<' not found, line 1, column 1 (, line 1)"
            )
