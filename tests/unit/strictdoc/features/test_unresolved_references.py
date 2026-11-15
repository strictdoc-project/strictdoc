from pathlib import Path
from typing import Tuple

import pytest
from bs4 import BeautifulSoup

from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.reference import FileEntry, FileReference
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.constants import GraphLinkType
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.feature import FeatureContext
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import NormalHTMLTemplates
from strictdoc.features.unresolved_references.feature import (
    UnresolvedReferencesFeature,
)
from strictdoc.helpers.file_system import file_open_read_utf8
from tests.unit.helpers.document_builder import DocumentBuilder


@pytest.mark.parametrize("relaxed_mode", [False, True])
@pytest.mark.parametrize("registered", [False, True])
def test_unresolved_references_activation_follows_relaxed_mode(
    relaxed_mode: bool,
    registered: bool,
) -> None:
    project_config = ProjectConfig(
        relaxed_mode=relaxed_mode,
        project_features=[UnresolvedReferencesFeature()]
        if registered
        else None,
    )

    feature = project_config.get_feature("UNRESOLVED_REFERENCES_SCREEN")

    assert (feature is not None) is relaxed_mode
    if feature is not None:
        assert feature.supports_export()
        assert feature.supports_server()
        assert feature.screen_filename() == "unresolved_references.html"


def test_unresolved_references_lists_all_categories(tmp_path: Path) -> None:
    document_builder, traceability_index = _create_index()
    requirement = document_builder.requirements[0]
    requirement.relations.append(
        FileReference(
            parent=requirement,
            g_file_entry=FileEntry(
                parent=None,
                g_file_format=None,
                g_file_path="missing.txt",
                g_line_range=None,
            ),
            role="Implementation",
        )
    )
    statement = requirement.get_content_field()
    statement.parts.extend(
        [
            InlineLink(statement, "MISSING-LINK"),
            InlineLink(statement, "REQ-001"),
        ]
    )
    source = (
        "# @relation(REQ-001, MISSING-RANGE, scope=range_start)\n"
        "code\n"
        "# @relation(REQ-001, MISSING-RANGE, scope=range_end)\n"
        "# @relation(MISSING-LINE, scope=line)\n"
        "code\n"
        "# @relation(MISSING-FILE, scope=file)\n"
    )
    _attach_source(document_builder, traceability_index, tmp_path, source)

    output = _render(document_builder, traceability_index, tmp_path)
    page = BeautifulSoup(output, "html.parser")
    total = page.select_one('[data-testid="unresolved-references-total"]')
    assert total is not None
    assert total.get_text(strip=True) == "7"
    rows = page.select('[data-testid="unresolved-reference-row"]')
    assert len(rows) == 7
    assert {row_.get("data-reference-type") for row_ in rows} == {
        "Parent",
        "Child",
        "File",
        "Source marker",
        "Inline link",
    }
    assert "Implementation" in output
    assert 'href="_source_files/source.txt.html##1#3"' in output
    assert "source.txt:4" in output
    assert "source.txt:6" in output
    assert "STATEMENT" in output
    assert (
        page.select_one(
            '[data-testid="project-tree-link-unresolved-references"]'
        )
        is not None
    )


def test_unresolved_references_empty_state_and_repaired_relations(
    tmp_path: Path,
) -> None:
    document_builder, traceability_index = _create_index()
    initial_output = _render(document_builder, traceability_index, tmp_path)
    assert "MISSING-PARENT" in initial_output
    document_builder.requirements[0].relations.clear()

    output = _render(document_builder, traceability_index, tmp_path)

    assert "No unresolved references." in output
    assert 'data-testid="unresolved-reference-row"' not in output


def test_unresolved_references_escapes_targets_and_links_nodes_without_uids(
    tmp_path: Path,
) -> None:
    document_builder, traceability_index = _create_index()
    requirement = document_builder.requirements[0]
    requirement.relations.clear()
    requirement.reserved_uid = None
    statement = requirement.get_content_field()
    target = '<img src=x onerror="alert(1)">&'
    statement.parts.append(InlineLink(statement, target))

    output = _render(document_builder, traceability_index, tmp_path)
    page = BeautifulSoup(output, "html.parser")
    row = page.select_one('[data-testid="unresolved-reference-row"]')

    assert row is not None
    assert target in row.get_text()
    assert row.find("img") is None
    owner_link = row.find("a")
    assert owner_link is not None
    assert "#" in owner_link["href"]
    assert owner_link["href"].endswith("#1-Requirement-title")


def test_unresolved_references_updates_source_markers_after_node_changes(
    tmp_path: Path,
) -> None:
    document_builder, traceability_index = _create_index()
    requirement = document_builder.requirements[0]
    requirement.relations.clear()
    _attach_source(
        document_builder,
        traceability_index,
        tmp_path,
        "# @relation(REQ-001, MISSING-SOURCE, scope=file)\n",
    )
    initial_page = BeautifulSoup(
        _render(document_builder, traceability_index, tmp_path), "html.parser"
    )
    assert (
        len(initial_page.select('[data-testid="unresolved-reference-row"]'))
        == 1
    )

    traceability_index.graph_database.delete_link(
        link_type=GraphLinkType.UID_TO_NODE,
        lhs_node="REQ-001",
        rhs_node=requirement,
    )
    missing_page = BeautifulSoup(
        _render(document_builder, traceability_index, tmp_path), "html.parser"
    )
    assert (
        len(missing_page.select('[data-testid="unresolved-reference-row"]'))
        == 2
    )

    traceability_index.graph_database.create_link(
        link_type=GraphLinkType.UID_TO_NODE,
        lhs_node="REQ-001",
        rhs_node=requirement,
    )
    new_requirement = document_builder.add_requirement("MISSING-SOURCE")
    traceability_index.create_requirement(new_requirement)
    repaired_output = _render(document_builder, traceability_index, tmp_path)
    assert "No unresolved references." in repaired_output


def _attach_source(
    document_builder: DocumentBuilder,
    traceability_index: TraceabilityIndex,
    tmp_path: Path,
    source: str,
) -> None:
    source_path = tmp_path / "source.txt"
    source_path.write_text(source, encoding="utf-8")
    source_file = SourceFile(
        level=0,
        full_path=str(source_path),
        in_doctree_source_file_rel_path="source.txt",
        output_dir_full_path=str(tmp_path),
        output_file_full_path=str(tmp_path / "source.txt.html"),
    )
    file_index = traceability_index.get_file_traceability_index()
    file_index.create_traceability_info(
        source_file, SourceFileTraceabilityReader().read(source)
    )
    file_index.validate_and_resolve(
        traceability_index, document_builder.project_config
    )


def _create_index() -> Tuple[DocumentBuilder, TraceabilityIndex]:
    document_builder = DocumentBuilder()
    document_builder.project_config.relaxed_mode = True
    requirement = document_builder.add_requirement("REQ-001")
    requirement.ng_including_document_reference = (
        requirement.ng_document_reference
    )
    for relation_type_ in ("Parent", "Child"):
        document_builder.add_requirement_relation(
            relation_type=relation_type_,
            source_requirement_id="REQ-001",
            target_requirement_id=f"MISSING-{relation_type_.upper()}",
            role="Implementation",
        )
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_builder.build()],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    return document_builder, TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )


def _render(
    document_builder: DocumentBuilder,
    traceability_index: TraceabilityIndex,
    tmp_path: Path,
) -> str:
    project_config = document_builder.project_config
    project_config.export_output_html_root = str(tmp_path)
    feature = project_config.get_feature("UNRESOLVED_REFERENCES_SCREEN")
    assert feature is not None
    feature.export(
        FeatureContext(
            project_config=project_config,
            traceability_index=traceability_index,
            html_templates=NormalHTMLTemplates(),
        )
    )
    with file_open_read_utf8(
        str(tmp_path / feature.screen_filename())
    ) as file_:
        return file_.read()
