"""
@relation(SDOC-SRS-157, scope=file)
"""

import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_tree_map_html_renderer(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port() + "/tree_map_html.html")

            self.assert_element(
                '//body[@data-viewtype="tree-map-html"]',
                by=By.XPATH,
            )
            self.assert_elements(
                ".tree-map-html__section",
                3,
            )
            self.assert_element(".tree-map-html__node[data-depth='2']")
            self.assert_no_js_errors()

            rectangles_are_valid = self.execute_script(
                """
                const nodes = Array.from(
                  document.querySelectorAll(
                    ".tree-map-html__node[data-depth='2']",
                  ),
                );
                return nodes.length >= 6 && nodes.every((node) => {
                  const rectangle = node.getBoundingClientRect();
                  return rectangle.width > 0 && rectangle.height > 0;
                });
                """
            )
            assert rectangles_are_valid
