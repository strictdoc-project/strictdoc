import os
import platform

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)

MODIFIER_KEY = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_copy_stable_link(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            target = "ROOT-1"

            # open the project index with the target UID reference
            self.open(
                exporter.get_output_path_as_uri()
                + "copy_stable_link/input/index.html#"
                + target
            )

            screen_document = Screen_Document(self)
            screen_document.assert_on_screen("document")

            # move mouse to hover over target, so that button becomes visible
            screen_document.test_case.hover_on_element(
                f'//sdoc-field-content[sdoc-autogen[text()="{target}"]]'
            )

            # now click on the target's copy_stable_link button
            screen_document.test_case.click_xpath(
                f'//div[@class="copy_stable_link-button" and @data-path="../../#{target}"]'
            )

            # focus on the input field
            screen_document.test_case.click_xpath(
                '//input[@id="copy_stable_link_form_field"]'
            )

            # Send Ctrl+V to paste clipboard content into input field
            actions = ActionChains(screen_document.test_case.driver)
            actions.key_down(MODIFIER_KEY).send_keys("v").key_up(
                MODIFIER_KEY
            ).perform()

            # read the content of the input field
            input_field = screen_document.test_case.find_element(
                '//input[@id="copy_stable_link_form_field"]'
            )

            # Get the text from the input field
            value = input_field.get_attribute("value")

            # check if stable link is as expected
            assert (
                value
                == exporter.get_output_path_as_uri() + "index.html#" + target
            )
