"""
@relation(SDOC-SRS-215, scope=file)
"""

import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_EDIT_ACTION = '[data-testid="node-static-edit-action"]'


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "01_edit_node_and_export_changes/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")

            # The node with a UID is editable. The node without a UID and
            # without a MID in the source file is read-only.
            edit_actions = self.find_elements(SELECTOR_EDIT_ACTION)
            assert len(edit_actions) == 2
            self.assert_attribute(
                f"{SELECTOR_EDIT_ACTION}:not(.action_button--disabled)",
                "title",
                "Edit",
            )
            assert (
                len(
                    self.find_elements(
                        f"{SELECTOR_EDIT_ACTION}.action_button--disabled"
                    )
                )
                == 1
            )
            self.assert_element_not_visible(
                '[data-testid="static-editing-panel"]'
            )

            # Edit the STATEMENT and save the change.
            self.hover('[data-testid="node-requirement"]')
            self.click(f"{SELECTOR_EDIT_ACTION}:not(.action_button--disabled)")
            self.assert_element('[data-testid="form-field-UID"]')
            self.assert_attribute(
                '[data-testid="form-field-UID"]', "contenteditable", "false"
            )
            self.update_text(
                '[data-testid="form-field-STATEMENT"]',
                "System X shall do Z.",
            )

            # The node has no COMMENT yet. Add a second COMMENT instance.
            self.update_text(
                '[data-testid="form-field-COMMENT"]',
                "First comment.",
            )
            self.click('[data-testid="form-add-field-COMMENT"]')
            self.update_text(
                '(//*[@data-static-editing-field="COMMENT"])[2]',
                "Second comment.",
                by=By.XPATH,
            )
            self.click('[data-testid="form-submit-action"]')

            self.assert_element('[data-testid="static-editing-preview"]')
            self.assert_text(
                "System X shall do Z.",
                '[data-testid="static-editing-preview"]',
            )
            self.assert_text(
                "1 local change", '[data-testid="static-editing-change-count"]'
            )

            # The change is stored in the browser and survives a reload.
            self.refresh()
            self.assert_text(
                "1 local change", '[data-testid="static-editing-change-count"]'
            )
            self.assert_element('[data-testid="static-editing-preview"]')

            # The export contains the change.
            changes_export = self.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "window.StrictDoc.staticEditing.getExport().then(done);"
            )
            assert changes_export["schema"] == (
                "strictdoc-static-editing-changes"
            )
            assert len(changes_export["changes"]) == 1
            change = changes_export["changes"][0]
            assert change["op"] == "update_node"
            assert change["document_path"] == "input/input.sdoc"
            assert change["node"] == {"uid": "REQ-1", "mid": None}
            assert change["base_hash"].startswith("sha256:")
            assert change["fields"] == [
                {
                    "name": "STATEMENT",
                    "index": 0,
                    "old_value": "System X shall do Y.",
                    "new_value": "System X shall do Z.",
                },
                {
                    "name": "COMMENT",
                    "index": None,
                    "old_value": None,
                    "new_value": "First comment.",
                },
                {
                    "name": "COMMENT",
                    "index": None,
                    "old_value": None,
                    "new_value": "Second comment.",
                },
            ]

            # Discarding needs a confirmation click.
            self.click('[data-testid="static-editing-discard-action"]')
            self.assert_element('[data-testid="static-editing-preview"]')
            self.click('[data-testid="static-editing-discard-action"]')
            self.assert_element_not_present(
                '[data-testid="static-editing-preview"]'
            )
            self.assert_element_not_visible(
                '[data-testid="static-editing-panel"]'
            )
            assert len(self.find_elements("sdoc-node", by=By.CSS_SELECTOR)) > 0
