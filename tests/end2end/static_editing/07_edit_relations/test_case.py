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

EXPECTED_DOCUMENT = """\
[DOCUMENT]
TITLE: Static editing document

[REQUIREMENT]
UID: REQ-2
TITLE: Child requirement
STATEMENT: >>>
System X shall do Z.
<<<

[REQUIREMENT]
UID: REQ-10
TITLE: Obsolete requirement
RELATIONS:
- TYPE: Parent
  VALUE: REQ-2
"""


def _node(node_index: int) -> str:
    return f'(//sdoc-node[@data-testid="node-requirement"])[{node_index}]'


def _node_action(node_index: int, action: str) -> str:
    return f'{_node(node_index)}//*[@data-testid="node-static-{action}-action"]'


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "07_edit_relations/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")

            # REQ-2 refers to REQ-1, so REQ-1 cannot be deleted yet.
            self.assert_attribute(
                _node_action(1, "delete"),
                "title",
                "Other nodes refer to this node with relations: REQ-2. "
                "Remove the relations first.",
                by="xpath",
            )

            # Remove the relation of REQ-2.
            self.hover(_node(2), by="xpath")
            self.click(_node_action(2, "edit"), by="xpath")
            assert self.get_value('[data-testid="form-relation-value"]') == (
                "REQ-1"
            )
            self.click('[data-testid="form-relation-remove-action"]')
            self.click('[data-testid="form-submit-action"]')
            self.assert_text(
                "RELATION (removed)", '[data-testid="static-editing-preview"]'
            )

            # Now REQ-1 can be marked for deletion.
            self.assert_attribute(
                _node_action(1, "delete"),
                "title",
                "Mark for deletion",
                by="xpath",
            )
            self.hover(_node(1), by="xpath")
            self.click(_node_action(1, "delete"), by="xpath")
            self.assert_text("Marked for deletion")

            # Add a relation to REQ-10.
            self.hover(_node(3), by="xpath")
            self.click(_node_action(3, "edit"), by="xpath")
            self.click('[data-testid="form-add-relation"]')
            self.type('[data-testid="form-relation-value"]', "REQ-2")
            self.click('[data-testid="form-submit-action"]')
            self.assert_text(
                "3 local changes", '[data-testid="static-editing-change-count"]'
            )

            changes_export = self.execute_async_script(
                "const done = arguments[arguments.length - 1];"
                "window.StrictDoc.staticEditing.getExport().then(done);"
            )

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

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "strictdoc.cli.main",
                    "apply-changes",
                    project_dir,
                    path_to_changes,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert completed.returncode == 0, completed.stdout
            assert "Applied 3 change(s) to 1 document(s)." in completed.stdout

            with open(
                os.path.join(project_dir, "input.sdoc"), encoding="utf8"
            ) as document_file:
                assert document_file.read() == EXPECTED_DOCUMENT
