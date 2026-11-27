"""
@relation(SDOC-SRS-215, SDOC-SRS-216, scope=file)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

SELECTOR_NEW_NODE = '[data-testid="static-editing-new-node"]'
SELECTOR_NEW_NODE_FORM = '[data-testid="static-editing-new-node-form"]'

EXPECTED_DOCUMENT = """\
[DOCUMENT]
TITLE: Static editing document

[REQUIREMENT]
UID: REQ-1
TITLE: Parent requirement
STATEMENT: >>>
System X shall do Y.
<<<

[REQUIREMENT]
UID: REQ-11
TITLE: New requirement
STATEMENT: >>>
System X shall do W.
<<<
COMMENT: >>>
[bob] Please review.
<<<

[REQUIREMENT]
UID: REQ-2
TITLE: Child requirement
STATEMENT: >>>
System X shall do Z.
<<<
RELATIONS:
- TYPE: Parent
  VALUE: REQ-1
"""


def _node_action(node_index: int, action: str) -> str:
    return (
        f'(//sdoc-node[@data-testid="node-requirement"])[{node_index}]'
        f'//*[@data-testid="node-static-{action}-action"]'
    )


def _node(node_index: int) -> str:
    return f'(//sdoc-node[@data-testid="node-requirement"])[{node_index}]'


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "06_add_and_delete_nodes/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")
            self.type('[data-testid="static-editing-author"]', "bob")

            # Add a node below REQ-1. The form suggests the next free UID.
            self.hover(_node(1), by="xpath")
            self.click(_node_action(1, "add"), by="xpath")
            self.assert_text(
                "REQ-11",
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-UID"]',
            )
            self.update_text(
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-TITLE"]',
                "New requirement",
            )
            self.update_text(
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-STATEMENT"]',
                "System X shall do W.",
            )
            self.update_text(
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-COMMENT"]',
                "Please review.",
            )
            self.click('[data-testid="form-submit-action"]')
            self.assert_text("REQ-11", SELECTOR_NEW_NODE)
            self.assert_text("[bob] Please review.", SELECTOR_NEW_NODE)

            # Add a node below the new node and remove it again.
            self.click(
                f'{SELECTOR_NEW_NODE} [data-testid="static-editing-new-node-add-action"]'
            )
            self.assert_text(
                "REQ-12",
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-UID"]',
            )
            self.update_text(
                f'{SELECTOR_NEW_NODE_FORM} [data-testid="form-field-TITLE"]',
                "Temporary requirement",
            )
            self.click('[data-testid="form-submit-action"]')
            assert len(self.find_elements(SELECTOR_NEW_NODE)) == 2
            self.assert_text(
                "2 local changes", '[data-testid="static-editing-change-count"]'
            )
            self.click(
                '(//*[@data-testid="static-editing-new-node"])[2]'
                '//*[@data-testid="static-editing-new-node-remove-action"]',
                by="xpath",
            )
            assert len(self.find_elements(SELECTOR_NEW_NODE)) == 1

            # REQ-1 is the parent of REQ-2 and cannot be deleted.
            self.assert_attribute(
                _node_action(1, "delete"),
                "title",
                "Deleting is not available for nodes that other nodes refer to",
                by="xpath",
            )

            # Mark REQ-10 for deletion, undo, and mark it again.
            self.hover(_node(3), by="xpath")
            self.click(_node_action(3, "delete"), by="xpath")
            self.assert_text(
                "Marked for deletion", '[data-testid="static-editing-preview"]'
            )
            self.click('[data-testid="static-editing-undo-delete-action"]')
            self.assert_element_not_present(
                '[data-testid="static-editing-preview"]'
            )
            self.hover(_node(3), by="xpath")
            self.click(_node_action(3, "delete"), by="xpath")
            self.assert_text(
                "2 local changes", '[data-testid="static-editing-change-count"]'
            )

            changes_export = self.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "window.StrictDoc.staticEditing.getExport().then(done);"
            )
            assert [change_["op"] for change_ in changes_export["changes"]] == [
                "create_node",
                "delete_node",
            ]

        # Apply the exported changes to a copy of the input document.
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = os.path.join(temp_dir, "input")
            shutil.copytree(
                os.path.join(path_to_this_test_file_folder, "input"),
                project_dir,
            )
            path_to_changes = os.path.join(temp_dir, "changes.json")
            with open(path_to_changes, "w", encoding="utf8") as changes_file:
                json.dump(changes_export, changes_file)

            command = [
                sys.executable,
                "-m",
                "strictdoc.cli.main",
                "apply-changes",
                project_dir,
                path_to_changes,
            ]
            completed = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            assert completed.returncode == 0, completed.stdout
            assert "Applied 2 change(s) to 1 document(s)." in completed.stdout

            with open(
                os.path.join(project_dir, "input.sdoc"), encoding="utf8"
            ) as document_file:
                assert document_file.read() == EXPECTED_DOCUMENT
