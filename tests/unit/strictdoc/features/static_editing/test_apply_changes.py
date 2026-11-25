"""
@relation(SDOC-SRS-216, scope=file)
"""

import json
from typing import Any, Dict, List, Optional

import pytest

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.features.static_editing.apply_changes import (
    ChangeApplier,
    ChangesFileError,
    ChangeStatus,
    load_changes_file,
)
from strictdoc.features.static_editing.edit_data import (
    compute_node_content_hash,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def _build_traceability_index(
    document_builder: DocumentBuilder,
) -> TraceabilityIndex:
    document = document_builder.build()
    for requirement_ in document_builder.requirements:
        # The document builder does not set the including document reference
        # that the parser sets for every node.
        requirement_.ng_including_document_reference = DocumentReference()
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    return TraceabilityIndexBuilder.create_from_document_tree(
        document_tree,
        project_config=document_builder.project_config,
    )


def _change(
    node: SDocNode, fields: List[Dict[str, Any]], base_hash: Optional[str]
) -> Dict[str, Any]:
    return {
        "op": "update_node",
        "document_path": "input.sdoc",
        "node": {"uid": node.reserved_uid, "mid": None},
        "node_type": node.node_type,
        "base_hash": base_hash
        if base_hash is not None
        else compute_node_content_hash(node),
        "fields": fields,
    }


def _field(
    name: str, index: Optional[int], old_value: Optional[str], new_value: str
) -> Dict[str, Any]:
    return {
        "name": name,
        "index": index,
        "old_value": old_value,
        "new_value": new_value,
    }


def _values(node: SDocNode, field_name: str) -> List[str]:
    # A multiline field value ends with a newline.
    return [
        field_.get_text_value().rstrip("\n")
        for field_ in node.ordered_fields_lookup.get(field_name, [])
    ]


def test_01_applies_a_changed_field_and_an_added_comment() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))

    result = applier.apply_change(
        _change(
            requirement,
            [
                _field("STATEMENT", 0, "System X shall do Y", "System X Z"),
                _field("COMMENT", None, None, "[bob] Clarify."),
            ],
            base_hash=None,
        )
    )

    assert result.status == ChangeStatus.APPLIED
    assert _values(requirement, "STATEMENT") == ["System X Z"]
    assert _values(requirement, "COMMENT") == ["[bob] Clarify."]
    assert len(applier.modified_documents) == 1


def test_02_a_conflict_leaves_the_whole_node_unchanged() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))

    result = applier.apply_change(
        _change(
            requirement,
            [
                _field("COMMENT", None, None, "[bob] Clarify."),
                _field("STATEMENT", 0, "An older statement", "System X Z"),
            ],
            base_hash="sha256:outdated",
        )
    )

    assert result.status == ChangeStatus.CONFLICT
    assert "The field STATEMENT has changed since the export." in (
        result.messages
    )
    assert _values(requirement, "STATEMENT") == ["System X shall do Y"]
    assert _values(requirement, "COMMENT") == []
    assert len(applier.modified_documents) == 0


def test_03_merges_changes_of_different_fields() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))
    base_hash = compute_node_content_hash(requirement)

    # Another reviewer has changed the title since the export.
    requirement.set_field_value(
        field_name="TITLE", form_field_index=0, value="Changed title"
    )
    result = applier.apply_change(
        _change(
            requirement,
            [_field("STATEMENT", 0, "System X shall do Y", "System X Z")],
            base_hash=base_hash,
        )
    )

    assert result.status == ChangeStatus.APPLIED
    assert result.messages[0].startswith("The node has changed since")
    assert _values(requirement, "TITLE") == ["Changed title"]
    assert _values(requirement, "STATEMENT") == ["System X Z"]


def test_04_skips_a_change_that_is_already_applied() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))
    change = _change(
        requirement,
        [
            _field("STATEMENT", 0, "System X shall do Y", "System X Z"),
            _field("COMMENT", None, None, "[bob] Clarify."),
        ],
        base_hash=None,
    )

    assert applier.apply_change(change).status == ChangeStatus.APPLIED
    assert applier.apply_change(change).status == ChangeStatus.ALREADY_APPLIED
    assert _values(requirement, "COMMENT") == ["[bob] Clarify."]


def test_05_finds_a_comment_by_its_old_value() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))
    applier.apply_change(
        _change(
            requirement,
            [
                _field("COMMENT", None, None, "First."),
                _field("COMMENT", None, None, "Second."),
            ],
            base_hash=None,
        )
    )

    # Reviewer A removes the first comment. Reviewer B edits the second
    # comment at its old index 1.
    result_a = applier.apply_change(
        _change(requirement, [_field("COMMENT", 0, "First.", "")], None)
    )
    result_b = applier.apply_change(
        _change(
            requirement, [_field("COMMENT", 1, "Second.", "Second, ok.")], None
        )
    )

    assert result_a.status == ChangeStatus.APPLIED
    assert result_b.status == ChangeStatus.APPLIED
    assert _values(requirement, "COMMENT") == ["Second, ok."]


def test_06_rejects_invalid_changes() -> None:
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))

    read_only = applier.apply_change(
        _change(requirement, [_field("UID", 0, "REQ-001", "REQ-002")], None)
    )
    assert read_only.status == ChangeStatus.ERROR
    assert read_only.messages == ["The field UID is read-only."]

    unknown_field = applier.apply_change(
        _change(requirement, [_field("UNKNOWN", 0, "A", "B")], None)
    )
    assert unknown_field.status == ChangeStatus.ERROR

    # The default grammar has no required field besides UID.
    document = document_builder.build()
    document.grammar.elements_by_type["REQUIREMENT"].fields_map[
        "TITLE"
    ].required = True
    required_field = applier.apply_change(
        _change(
            requirement,
            [_field("TITLE", 0, "Requirement title", "")],
            None,
        )
    )
    assert required_field.status == ChangeStatus.ERROR
    assert required_field.messages == [
        "The field TITLE is required and cannot be removed."
    ]

    unknown_node = _change(requirement, [], None)
    unknown_node["node"] = {"uid": "REQ-UNKNOWN", "mid": None}
    unknown_node_result = applier.apply_change(unknown_node)
    assert unknown_node_result.status == ChangeStatus.CONFLICT
    assert unknown_node_result.messages == ["The node does not exist anymore."]

    assert len(applier.modified_documents) == 0


def test_07_load_changes_file_checks_the_schema(tmp_path) -> None:
    valid_path = tmp_path / "valid.json"
    valid_path.write_text(
        json.dumps(
            {
                "schema": "strictdoc-static-editing-changes",
                "version": 1,
                "changes": [{"op": "update_node"}],
            }
        ),
        encoding="utf8",
    )
    assert load_changes_file(str(valid_path)) == [{"op": "update_node"}]

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(json.dumps({"schema": "other"}), encoding="utf8")
    with pytest.raises(ChangesFileError):
        load_changes_file(str(invalid_path))

    broken_path = tmp_path / "broken.json"
    broken_path.write_text("{", encoding="utf8")
    with pytest.raises(ChangesFileError):
        load_changes_file(str(broken_path))
