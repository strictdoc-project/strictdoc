import filecmp
import os

from seleniumbase import BaseCase

from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))
path_to_reqif_sample = os.path.join(
    path_to_this_test_file_folder, "sample.reqif"
)


class Test_UC55_T01_ImportDocumentFromReqIF(BaseCase):
    def test_01(self):
        path_to_sandbox = os.path.join(
            path_to_this_test_file_folder, ".sandbox"
        )

        test_server = SDocTestServer.create(path_to_sandbox)
        test_server.run()

        self.open(test_server.get_host_and_port())

        self.assert_text("PROJECT INDEX")

        self.click('[data-testid="tree-import-reqif-action"]')

        reqif_input_field = self.find_element(
            "//*[@data-testid='form-reqif_file-field']"
        )
        reqif_input_field.send_keys(path_to_reqif_sample)
        self.click_xpath('//*[@data-testid="form-submit-action"]')
        self.assert_element_not_present('[data-testid="form-submit-action"]')

        create_document_path = os.path.join(path_to_sandbox, "Document_1.sdoc")
        assert os.path.exists(create_document_path)
        assert filecmp.cmp(
            create_document_path,
            os.path.join(
                path_to_this_test_file_folder, "document.expected.sdoc"
            ),
        )
