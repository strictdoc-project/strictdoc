"""
Regression tests for enabling grammar editing on a document whose grammar
comes from IMPORT_FROM_FILE (previously blocked outright by the "Editing
imported grammar files is not implemented yet." placeholder). See
strictdoc/core/grammar_file_resolver.py and
strictdoc/server/routers/main_router.py::write_grammar_change_to_file.

Grammar element/field mids are always freshly generated on every parse
(never pinned via MID: like node mids), so these tests scrape them out of
the real rendered HTML rather than hardcoding them — this is what the
browser's own form submission does too, just without a browser.
"""

import os
import re
import shutil
from typing import Dict, Tuple

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import NullParallelizer
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


def _project_config(project_dir: str) -> ProjectConfig:
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=project_dir,
        output_path=os.path.join(project_dir, "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config_ = ProjectConfig.default_config()
    project_config_.integrate_server_config(server_config)
    return project_config_


def _document_mid(document_page_html: str) -> str:
    match = re.search(
        r"actions/document/edit_grammar\?document_mid=([0-9a-f]+)",
        document_page_html,
    )
    assert match is not None, document_page_html
    return match.group(1)


def _element_mid(grammar_page_html: str, tag: str) -> str:
    matches = re.findall(
        r'document_grammar_element_field\[([0-9a-f]+)\]\[field_name\]"'
        r"[^>]*>\s*([A-Z_]+)\s*<",
        grammar_page_html,
    )
    return next(mid for mid, name in matches if name == tag)


def _field_mids(element_page_html: str) -> Dict[str, str]:
    matches = re.findall(
        r'document_grammar_field\[([0-9a-f]+)\]\[field_name\]"'
        r"[^>]*>\s*([A-Za-z_]+)\s*<",
        element_page_html,
    )
    return {name: mid for mid, name in matches}


def _relation_mid(element_page_html: str) -> str:
    match = re.search(
        r"document_grammar_relation\[([0-9a-f]+)\]\[type\]",
        element_page_html,
    )
    assert match is not None, element_page_html
    return match.group(1)


def _open_requirement_element(
    client: TestClient, uid: str
) -> Tuple[str, str, Dict[str, str], str]:
    """
    Navigates the same screens a browser would (document -> edit grammar ->
    edit REQUIREMENT element) and returns everything needed to submit a
    save_grammar_element POST: document_mid, element_mid, {field name: mid},
    relation_mid.
    """

    document_page = client.get(f"/UID/{uid}", follow_redirects=True)
    assert document_page.status_code == 200
    document_mid = _document_mid(document_page.text)

    grammar_page = client.get(
        f"/actions/document/edit_grammar?document_mid={document_mid}"
    )
    assert grammar_page.status_code == 200
    assert (
        "grammar-from-file-editing-blocker-placeholder"
        not in grammar_page.text
    ), "imported grammars must no longer show the not-implemented placeholder"
    element_mid = _element_mid(grammar_page.text, "REQUIREMENT")

    element_page = client.get(
        "/actions/document/edit_grammar_element"
        f"?document_mid={document_mid}&element_mid={element_mid}"
    )
    assert element_page.status_code == 200
    field_mids = _field_mids(element_page.text)
    relation_mid = _relation_mid(element_page.text)

    return document_mid, element_mid, field_mids, relation_mid


def _save_target_revision_options(
    client: TestClient,
    *,
    document_mid: str,
    element_mid: str,
    field_mids: Dict[str, str],
    relation_mid: str,
    options: str,
):
    # A real form submits every field row, not just the one being changed —
    # omitting a field here would delete it from the element (same as the
    # "delete field" action). So this rebuilds the whole set unchanged,
    # except TARGET_REVISION's type/options.
    payload = {
        "document_mid": document_mid,
        "element_mid": element_mid,
        "is_composite": "",
        "prefix": "",
        "view_style": "",
        f"document_grammar_relation[{relation_mid}][type]": "Parent",
        f"document_grammar_relation[{relation_mid}][role]": "",
    }
    for field_name, field_mid in field_mids.items():
        payload[f"document_grammar_field[{field_mid}][field_name]"] = (
            field_name
        )
        payload[
            f"document_grammar_field[{field_mid}][field_human_title]"
        ] = ""
        if field_name == "TARGET_REVISION":
            payload[
                f"document_grammar_field[{field_mid}][field_required]"
            ] = "true"
            payload[
                f"document_grammar_field[{field_mid}][field_type]"
            ] = "SingleChoice"
            payload[
                f"document_grammar_field[{field_mid}][field_options]"
            ] = options
        else:
            payload[
                f"document_grammar_field[{field_mid}][field_required]"
            ] = "false"
    return client.post("/actions/document/save_grammar_element", data=payload)


@pytest.fixture
def single_doc_project(tmp_path) -> str:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    shutil.copy(
        os.path.join(PATH_TO_THIS_TEST_FOLDER, "document.sdoc"),
        project_dir / "document.sdoc",
    )
    shutil.copy(
        os.path.join(PATH_TO_THIS_TEST_FOLDER, "grammar.sgra"),
        project_dir / "grammar.sgra",
    )
    return str(project_dir)


def test_editing_a_field_writes_the_imported_sgra_file_not_the_sdoc(
    single_doc_project,
):
    project_config = _project_config(single_doc_project)
    client = TestClient(create_app(project_config=project_config))

    original_sdoc = open(
        os.path.join(single_doc_project, "document.sdoc")
    ).read()

    document_mid, element_mid, field_mids, relation_mid = (
        _open_requirement_element(client, "REQ-1")
    )
    assert field_mids["TARGET_REVISION"], field_mids

    response = _save_target_revision_options(
        client,
        document_mid=document_mid,
        element_mid=element_mid,
        field_mids=field_mids,
        relation_mid=relation_mid,
        options="C1, C2, D1",
    )
    assert response.status_code == 200, response.text

    grammar_text = open(
        os.path.join(single_doc_project, "grammar.sgra")
    ).read()
    assert "TYPE: SingleChoice(C1, C2, D1)" in grammar_text

    # The .sdoc still only says IMPORT_FROM_FILE — the grammar edit must
    # not have touched it at all.
    sdoc_text = open(os.path.join(single_doc_project, "document.sdoc")).read()
    assert sdoc_text == original_sdoc


def test_a_normal_node_content_edit_still_writes_the_sdoc_not_the_sgra(
    single_doc_project,
):
    # Regression guard for the content-vs-structure distinction: node
    # content (STATEMENT here) always lives in the .sdoc, regardless of
    # where the grammar structure comes from.
    project_config = _project_config(single_doc_project)
    client = TestClient(create_app(project_config=project_config))

    grammar_before = open(
        os.path.join(single_doc_project, "grammar.sgra")
    ).read()

    response = client.post(
        "/actions/table/update_node_field_multiline",
        data={
            "node_mid": "req-1-mid",
            "field_name": "STATEMENT",
            "field_value": "Updated statement text.",
        },
    )
    assert response.status_code == 200, response.text

    sdoc_text = open(os.path.join(single_doc_project, "document.sdoc")).read()
    assert "Updated statement text." in sdoc_text

    grammar_after = open(
        os.path.join(single_doc_project, "grammar.sgra")
    ).read()
    assert grammar_after == grammar_before


def test_saving_the_element_list_unchanged_still_targets_the_sgra_file(
    single_doc_project,
):
    # document__save_grammar (the element list, one level up from the
    # per-field editor) has the same import_from_file round-tripping fix —
    # covers UpdateGrammarCommand specifically, as opposed to
    # UpdateGrammarElementCommand above.
    project_config = _project_config(single_doc_project)
    client = TestClient(create_app(project_config=project_config))

    original_sdoc = open(
        os.path.join(single_doc_project, "document.sdoc")
    ).read()

    document_page = client.get("/UID/REQ-1", follow_redirects=True)
    document_mid = _document_mid(document_page.text)
    grammar_page = client.get(
        f"/actions/document/edit_grammar?document_mid={document_mid}"
    )
    assert (
        "grammar-from-file-editing-blocker-placeholder"
        not in grammar_page.text
    )
    elements = re.findall(
        r'document_grammar_element_field\[([0-9a-f]+)\]\[field_name\]"'
        r"[^>]*>\s*([A-Z_]+)\s*<",
        grammar_page.text,
    )

    payload = {"document_mid": document_mid}
    for mid, name in elements:
        payload[f"document_grammar_element_field[{mid}][field_name]"] = name
        payload[f"document_grammar_element_field[{mid}][is_new]"] = "false"

    response = client.post("/actions/document/save_grammar", data=payload)
    assert response.status_code == 200, response.text

    sdoc_text = open(os.path.join(single_doc_project, "document.sdoc")).read()
    assert sdoc_text == original_sdoc

    grammar_text = open(
        os.path.join(single_doc_project, "grammar.sgra")
    ).read()
    assert "TARGET_REVISION" in grammar_text


def test_editing_a_grammar_shared_by_two_documents_propagates_to_both(
    tmp_path,
):
    # Not the eurobot case today (each of its .sgra files has exactly one
    # importer), but IMPORT_FROM_FILE doesn't prevent sharing in general —
    # confirms the deliberate design choice of not inhibiting the .sgra
    # watcher: propagation is verified at the data layer (a fresh
    # TraceabilityIndexBuilder.create(), what the watcher's rebuild does)
    # rather than via real filesystem-watcher timing, to keep this
    # deterministic.
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    shutil.copy(
        os.path.join(PATH_TO_THIS_TEST_FOLDER, "grammar.sgra"),
        project_dir / "grammar.sgra",
    )
    (project_dir / "doc_a.sdoc").write_text(
        "[DOCUMENT]\n"
        "TITLE: Document A\n\n"
        "[GRAMMAR]\n"
        "IMPORT_FROM_FILE: grammar.sgra\n\n"
        "[REQUIREMENT]\n"
        "UID: REQ-A1\n"
        "STATEMENT: Statement A.\n"
        "TARGET_REVISION: C1\n"
    )
    (project_dir / "doc_b.sdoc").write_text(
        "[DOCUMENT]\n"
        "TITLE: Document B\n\n"
        "[GRAMMAR]\n"
        "IMPORT_FROM_FILE: grammar.sgra\n\n"
        "[REQUIREMENT]\n"
        "UID: REQ-B1\n"
        "STATEMENT: Statement B.\n"
        "TARGET_REVISION: C1\n"
    )

    project_config = _project_config(str(project_dir))
    client = TestClient(create_app(project_config=project_config))

    document_mid, element_mid, field_mids, relation_mid = (
        _open_requirement_element(client, "REQ-A1")
    )
    response = _save_target_revision_options(
        client,
        document_mid=document_mid,
        element_mid=element_mid,
        field_mids=field_mids,
        relation_mid=relation_mid,
        options="C1, C2, D1",
    )
    assert response.status_code == 200, response.text

    rebuilt_index = TraceabilityIndexBuilder.create(
        project_config=project_config, parallelizer=NullParallelizer()
    )
    document_b = next(
        document_
        for document_ in rebuilt_index.document_tree.document_list
        if document_.reserved_title == "Document B"
    )
    target_revision_field = document_b.grammar.elements_by_type[
        "REQUIREMENT"
    ].fields_map["TARGET_REVISION"]
    assert target_revision_field.options == ["C1", "C2", "D1"]
