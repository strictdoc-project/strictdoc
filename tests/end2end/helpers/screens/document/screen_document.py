import os
from datetime import datetime

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase

from tests.end2end.helpers.components.actions_menu import (
    ActionsMenu,
)
from tests.end2end.helpers.screens.document.form_edit_grammar_elements import (
    Form_EditGrammarElements,
)
from tests.end2end.helpers.screens.screen import Screen


class Screen_Document(Screen):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)
        self.actions_menu = ActionsMenu(test_case)

    #
    # Overridden for Screen_Document.
    #

    def assert_on_screen_document(self) -> None:
        super().assert_on_screen("document")

    def assert_empty_document(self) -> None:
        super().assert_empty_view("document-root-placeholder")

    def assert_not_empty_document(self) -> None:
        super().assert_not_empty_view("document-root-placeholder")

    def assert_target_by_anchor(self, anchor) -> None:
        # check if the link was successfully clicked
        # and that the target is highlighted
        targeted_anchor = f"sdoc-anchor[id='{anchor}']:target"
        self.test_case.assert_element_present(targeted_anchor)

    #
    # Actions on the page.
    #

    def do_export_reqif(self) -> None:
        self.actions_menu.do_click_action("document-export-reqif-action")

    def do_export_pdf(self) -> None:
        self.actions_menu.do_click_action("document-export-html2pdf-action")

    #
    # Open forms.
    #

    def do_open_modal_form_edit_grammar(self) -> Form_EditGrammarElements:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.actions_menu.do_click_action("document-edit-grammar-action")
        self.test_case.assert_element(
            "//sdoc-modal",
            by=By.XPATH,
        )
        return Form_EditGrammarElements(self.test_case)

    def do_drag_first_toc_node_to_the_second(self) -> None:
        xpath_first_toc_node = '(//li[@draggable="true"])[1]'
        xpath_second_toc_node = '(//li[@draggable="true"])[2]'

        first_toc_node = self.test_case.find_element(xpath_first_toc_node)
        first_toc_node_mid = first_toc_node.get_attribute("data-nodeid")

        second_toc_node = self.test_case.find_element(xpath_second_toc_node)
        second_toc_node_mid = second_toc_node.get_attribute("data-nodeid")

        self.test_case.drag_and_drop(
            xpath_first_toc_node, xpath_second_toc_node
        )

        #
        # Drag and drop action takes some time before server/Turbo sends
        # an updated AJAX HTML template back. Sometimes a
        # StaleElementReferenceException is thrown by Selenium because it still
        # finds an old element as it is being moved. To solve this, set a timeout
        # to wait some time until the new TOC is rendered.
        #
        start_time = datetime.now()
        while True:
            new_root_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{second_toc_node_mid}"])[1]'
            )
            moved_node = self.test_case.find_element(
                f'(//li[@data-nodeid="{first_toc_node_mid}"])[1]'
            )

            try:
                if new_root_node.location["y"] < moved_node.location["y"]:
                    break
            except StaleElementReferenceException:
                # The element is the one from an old TOC. Keep waiting.
                self.test_case.sleep(0.1)

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "StrictDoc custom timeout: Moving element in the TOC"
                )

    def do_click_on_tree_document(self, doc_order: int = 1) -> None:
        self.test_case.assert_element_not_present("//sdoc-modal", by=By.XPATH)
        self.test_case.click_xpath(
            f'(//*[@data-testid="tree-document-link"])[{doc_order}]'
        )

    def do_drop_image_to_requirement(
        self, field_name: str, image_path: str, field_order: int = 1
    ) -> None:
        # Verify the file exists locally
        absolute_image_path = os.path.abspath(image_path)
        assert os.path.exists(absolute_image_path), (
            f"Test image not found at {absolute_image_path}"
        )

        # Find the target editable field for the specific requirement
        field_order_str = "last()" if field_order == -1 else str(field_order)
        xpath_field = (
            f"(//*[@data-testid='form-field-{field_name}'])[{field_order_str}]"
        )
        target_element = self.test_case.find_element(By.XPATH, xpath_field)

        # Use a JS script to simulate the drop event.
        # Selenium cannot drag from the OS, so we need to simulate the DataTransfer object.
        js_drop_files = """
            var target = arguments[0];
            var offsetX = 0;
            var offsetY = 0;
            var document = target.ownerDocument || document;
            var window = document.defaultView || window;

            var input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.onchange = function () {
            var rect = target.getBoundingClientRect();
            var x = rect.left + (offsetX || (rect.width >> 1));
            var y = rect.top + (offsetY || (rect.height >> 1));

            var dataTransfer = { files: this.files, types: ['Files'], dropEffect: 'copy' };

            ['dragenter', 'dragover', 'drop'].forEach(function (name) {
                var evt = document.createEvent('MouseEvent');
                evt.initMouseEvent(name, true, true, window, 0, 0, 0, x, y, false, false, false, false, 0, null);
                evt.dataTransfer = dataTransfer;
                target.dispatchEvent(evt);
            });

            setTimeout(function () { document.body.removeChild(input); }, 20);
            };
            document.body.appendChild(input);
            return input;
        """

        # Execute the script to create the input, then "upload" the file to it
        file_input = self.test_case.driver.execute_script(
            js_drop_files, target_element
        )
        file_input.send_keys(absolute_image_path)

        # Wait for the UI to update
        # We wait until the placeholder "Uploading..." disappears
        # and is replaced by the actual RST directive path.
        start_time = datetime.now()
        while True:
            current_content = target_element.text
            if ".. image:: @assets/" in current_content:
                break
            if '<img src="@assets/' in current_content:
                break
            if "![](@assets/" in current_content:
                break
            if "Image upload failed" in current_content:
                break

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "Image upload failed or RST path never appeared."
                )

            self.test_case.sleep(0.5)

    def do_paste_image_to_requirement(
        self, field_name: str, image_path: str, field_order: int = 1
    ) -> None:
        # Verify the file exists locally
        absolute_image_path = os.path.abspath(image_path)
        assert os.path.exists(absolute_image_path), (
            f"Test image not found at {absolute_image_path}"
        )

        # Find the target editable field for the specific requirement
        field_order_str = "last()" if field_order == -1 else str(field_order)
        xpath_field = (
            f"(//*[@data-testid='form-field-{field_name}'])[{field_order_str}]"
        )
        target_element = self.test_case.find_element(By.XPATH, xpath_field)

        # Use a JS script to simulate the image paste event with a mocked ClipboardEvent.
        js_paste_files = """
            var target = arguments[0];
            var document = target.ownerDocument || document;

            var input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.onchange = function () {
                var files = this.files;

                // Mock the DataTransfer/Clipboard items structure
                var mockClipboardItems = [];
                for (var i = 0; i < files.length; i++) {
                    let file = files[i];
                    mockClipboardItems.push({
                        type: file.type || 'image/png', // Fallback type just in case
                        getAsFile: function() { return file; }
                    });
                }

                var mockClipboardData = {
                    items: mockClipboardItems,
                    getData: function(format) { return ''; } // Mock getData to prevent errors
                };

                // Create the paste event and define the clipboardData property
                var pasteEvent = new Event('paste', { bubbles: true, cancelable: true });
                Object.defineProperty(pasteEvent, 'clipboardData', { value: mockClipboardData });

                target.dispatchEvent(pasteEvent);

                setTimeout(function () { document.body.removeChild(input); }, 20);
            };
            document.body.appendChild(input);
            return input;
        """

        # Execute the script to create the input, then "upload" the file to it
        file_input = self.test_case.driver.execute_script(
            js_paste_files, target_element
        )
        file_input.send_keys(absolute_image_path)

        # Wait for the UI to update
        # We wait until the placeholder "Uploading..." disappears
        # and is replaced by the actual RST directive path.
        start_time = datetime.now()
        while True:
            current_content = target_element.text
            # Checking for both asset path variations just to be safe
            if ".. image:: @assets/" in current_content:
                break
            if '<img src="@assets/' in current_content:
                break
            if "![](@assets/" in current_content:
                break
            if "Image upload failed" in current_content:
                break

            if (datetime.now() - start_time).total_seconds() > 10:
                raise TimeoutError(
                    "Image paste failed or RST path never appeared."
                )

            self.test_case.sleep(0.5)
