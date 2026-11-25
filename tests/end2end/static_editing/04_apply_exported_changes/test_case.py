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
UID: REQ-1
TITLE: Requirement with UID
STATEMENT: >>>
System X shall do Y within 10 ms.
<<<
COMMENT: >>>
[bob] Please check the timing.
<<<
"""


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            self.open(
                exporter.get_output_path_as_uri()
                + "04_apply_exported_changes/input/input.sdoc.html"
            )
            self.assert_text("System X shall do Y.")

            # Edit the node in the browser.
            self.type('[data-testid="static-editing-author"]', "bob")
            self.hover('[data-testid="node-requirement"]')
            self.click('[data-testid="node-static-edit-action"]')
            self.update_text(
                '[data-testid="form-field-STATEMENT"]',
                "System X shall do Y within 10 ms.",
            )
            self.update_text(
                '[data-testid="form-field-COMMENT"]',
                "Please check the timing.",
            )
            self.click('[data-testid="form-submit-action"]')
            self.assert_element('[data-testid="static-editing-preview"]')

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
            assert "Applied 1 change(s) to 1 document(s)." in completed.stdout

            with open(
                os.path.join(project_dir, "input.sdoc"), encoding="utf8"
            ) as document_file:
                assert document_file.read() == EXPECTED_DOCUMENT
