"""
Screencast scenario: creating a project from scratch with `strictdoc new`,
then browsing to it in the web UI, adding a new document, and adding a
requirement to it.

If this test fails, the "hello-world" screencast video is stale and must
be re-recorded (see tests/screencast/README.md).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Page, expect

from tests.end2end.server import SDocTestServer
from tests.screencast.fixture import RECORD_SERVER_PORT
from tests.screencast.helpers.node import DocumentRoot
from tests.screencast.helpers.project_tree import ProjectTree
from tests.screencast.helpers.screen import Screen
from tests.screencast.scenarios.typing import type_text

SCENE_HTML = os.path.abspath(os.path.join(__file__, "../../../terminal.html"))


def run_strictdoc_new(project_dir: Path) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.getcwd()

    result = subprocess.run(
        [sys.executable, "-m", "strictdoc.cli.main", "new", str(project_dir)],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout


class Test:
    def test(self, page: Page, tmp_path: Path) -> None:
        project_dir = tmp_path / "hello-world"
        cli_output = run_strictdoc_new(project_dir)

        page.goto(f"file://{SCENE_HTML}")
        demo_text = page.locator("#demoText")
        expect(demo_text).to_be_visible()

        type_text(demo_text, "$ strictdoc new hello-world\n")
        demo_text.evaluate(
            "(el, text) => { el.textContent += text; }", cli_output
        )
        page.wait_for_timeout(1500)

        with SDocTestServer(
            input_path=str(project_dir),
            port=RECORD_SERVER_PORT,
        ) as server:
            base_url = server.get_host_and_port()

            page.goto(f"{base_url}/")
            screen = Screen(page)
            screen.assert_on_screen("document-tree")

            project_tree = ProjectTree(page)
            project_tree.assert_contains_document("High-Level Requirements")
            project_tree.assert_contains_document("Low-Level Requirements")

            form_add_document = project_tree.do_open_modal_form_add_document()
            form_add_document.do_fill_in_title("Demo Requirements")
            form_add_document.do_fill_in_path("docs/demo_requirements.sdoc")
            form_add_document.do_form_submit()

            project_tree.assert_contains_document("Demo Requirements")
            project_tree.do_click_on_the_document_with_title(
                "Demo Requirements"
            )

            screen.assert_on_screen("document")

            document_root = DocumentRoot(page)
            add_node_menu = document_root.do_open_node_menu()
            form_edit_requirement = (
                add_node_menu.do_node_add_requirement_first()
            )
            form_edit_requirement.do_fill_in_field_uid("DEMO-1")
            form_edit_requirement.do_fill_in_field_title(
                "Hello world requirement"
            )
            form_edit_requirement.do_fill_in_field_statement(
                "StrictDoc shall greet the world."
            )
            form_edit_requirement.do_form_submit()

            expect(
                page.locator("sdoc-node-title", has_text="Hello world requirement")
            ).to_be_visible()
            expect(
                page.locator('[data-field-label="statement"]')
            ).to_contain_text("StrictDoc shall greet the world.")
