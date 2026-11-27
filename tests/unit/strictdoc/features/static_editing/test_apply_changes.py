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


def _create_change(
    after_uid: str, fields: List[Dict[str, str]], node_type: str = "REQUIREMENT"
) -> Dict[str, Any]:
    return {
        "op": "create_node",
        "document_path": "input.sdoc",
        "node_type": node_type,
        "position": {"after": {"uid": after_uid, "mid": None}},
        "fields": fields,
    }


def _delete_change(
    node: SDocNode, base_hash: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "op": "delete_node",
        "document_path": "input.sdoc",
        "node": {"uid": node.reserved_uid, "mid": None},
        "node_type": node.node_type,
        "base_hash": base_hash
        if base_hash is not None
        else compute_node_content_hash(node),
    }


def test_08_creates_a_node_after_an_existing_node() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    traceability_index = _build_traceability_index(document_builder)
    applier = ChangeApplier(traceability_index)
    first_change = _create_change(
        "REQ-001",
        [
            {"name": "UID", "value": "REQ-003"},
            {"name": "TITLE", "value": "New requirement"},
            {"name": "STATEMENT", "value": "System X shall do W."},
        ],
    )
    # A new node can be placed after a new node of an earlier change.
    second_change = _create_change(
        "REQ-003",
        [
            {"name": "UID", "value": "REQ-004"},
            {"name": "COMMENT", "value": "[bob] First."},
            {"name": "COMMENT", "value": "[bob] Second."},
        ],
    )

    assert applier.apply_change(first_change).status == ChangeStatus.APPLIED
    assert applier.apply_change(second_change).status == ChangeStatus.APPLIED

    document = document_builder.build()
    assert [node_.reserved_uid for node_ in document.section_contents] == [
        "REQ-001",
        "REQ-003",
        "REQ-004",
        "REQ-002",
    ]
    new_node = traceability_index.get_node_by_uid("REQ-003")
    assert _values(new_node, "TITLE") == ["New requirement"]
    assert _values(new_node, "STATEMENT") == ["System X shall do W."]
    assert _values(
        traceability_index.get_node_by_uid("REQ-004"), "COMMENT"
    ) == ["[bob] First.", "[bob] Second."]
    assert len(applier.modified_documents) == 1

    # Applying the change again finds the node with the same values.
    again = applier.apply_change(first_change)
    assert again.status == ChangeStatus.ALREADY_APPLIED


def test_09_rejects_invalid_new_nodes() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    applier = ChangeApplier(_build_traceability_index(document_builder))

    existing_uid = applier.apply_change(
        _create_change(
            "REQ-001",
            [
                {"name": "UID", "value": "REQ-001"},
                {"name": "TITLE", "value": "Other title"},
            ],
        )
    )
    assert existing_uid.status == ChangeStatus.ERROR
    assert existing_uid.messages == [
        "A node with the UID REQ-001 exists already."
    ]

    no_uid = applier.apply_change(
        _create_change("REQ-001", [{"name": "TITLE", "value": "Title"}])
    )
    assert no_uid.status == ChangeStatus.ERROR
    assert no_uid.messages == ["The new node must have one UID."]

    unknown_field = applier.apply_change(
        _create_change(
            "REQ-001",
            [
                {"name": "UID", "value": "REQ-002"},
                {"name": "UNKNOWN", "value": "Value"},
            ],
        )
    )
    assert unknown_field.status == ChangeStatus.ERROR

    unknown_type = applier.apply_change(
        _create_change(
            "REQ-001", [{"name": "UID", "value": "REQ-002"}], "UNKNOWN"
        )
    )
    assert unknown_type.status == ChangeStatus.ERROR

    unknown_position = applier.apply_change(
        _create_change("REQ-UNKNOWN", [{"name": "UID", "value": "REQ-002"}])
    )
    assert unknown_position.status == ChangeStatus.CONFLICT
    assert unknown_position.messages == [
        "The node after which the new node is placed does not exist anymore."
    ]

    document = document_builder.build()
    document.grammar.elements_by_type["REQUIREMENT"].fields_map[
        "TITLE"
    ].required = True
    missing_required = applier.apply_change(
        _create_change("REQ-001", [{"name": "UID", "value": "REQ-002"}])
    )
    assert missing_required.status == ChangeStatus.ERROR
    assert missing_required.messages == ["The field TITLE is required."]

    assert len(document.section_contents) == 1
    assert len(applier.modified_documents) == 0


def test_10_deletes_a_node() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    requirement = document_builder.add_requirement("REQ-002")
    traceability_index = _build_traceability_index(document_builder)
    applier = ChangeApplier(traceability_index)
    change = _delete_change(requirement)

    result = applier.apply_change(change)

    assert result.status == ChangeStatus.APPLIED
    document = document_builder.build()
    assert [node_.reserved_uid for node_ in document.section_contents] == [
        "REQ-001"
    ]
    assert traceability_index.get_node_by_uid_weak2("REQ-002") is None
    assert len(applier.modified_documents) == 1

    again = applier.apply_change(change)
    assert again.status == ChangeStatus.ALREADY_APPLIED


def test_11_does_not_delete_a_changed_or_referenced_node() -> None:
    document_builder = DocumentBuilder()
    parent_requirement = document_builder.add_requirement("REQ-001")
    child_requirement = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    applier = ChangeApplier(_build_traceability_index(document_builder))

    changed = applier.apply_change(
        _delete_change(child_requirement, base_hash="sha256:outdated")
    )
    assert changed.status == ChangeStatus.CONFLICT

    referenced = applier.apply_change(_delete_change(parent_requirement))
    assert referenced.status == ChangeStatus.ERROR
    assert referenced.messages == [
        "Other nodes refer to the node with relations: REQ-002."
    ]

    document = document_builder.build()
    assert len(document.section_contents) == 2
    assert len(applier.modified_documents) == 0


def _relation(
    action: str, relation_type: str, value: str, role: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "action": action,
        "type": relation_type,
        "value": value,
        "role": role,
    }


def test_12_removes_a_relation_and_then_deletes_the_parent() -> None:
    document_builder = DocumentBuilder()
    parent_requirement = document_builder.add_requirement("REQ-001")
    child_requirement = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    applier = ChangeApplier(_build_traceability_index(document_builder))
    update = _change(child_requirement, [], None)
    update["relations"] = [_relation("remove", "Parent", "REQ-001")]

    assert applier.apply_change(update).status == ChangeStatus.APPLIED
    assert child_requirement.relations == []
    assert (
        applier.apply_change(_delete_change(parent_requirement)).status
        == ChangeStatus.APPLIED
    )
    assert applier.apply_change(update).status == ChangeStatus.ALREADY_APPLIED


def test_13_adds_relations() -> None:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    requirement = document_builder.add_requirement("REQ-002")
    applier = ChangeApplier(_build_traceability_index(document_builder))
    update = _change(requirement, [], None)
    update["relations"] = [_relation("add", "Parent", "REQ-001")]

    assert applier.apply_change(update).status == ChangeStatus.APPLIED
    assert [
        (relation_.ref_type, relation_.ref_uid)
        for relation_ in requirement.relations
    ] == [("Parent", "REQ-001")]
    assert applier.apply_change(update).status == ChangeStatus.ALREADY_APPLIED

    # A new node can have relations.
    create = _create_change("REQ-002", [{"name": "UID", "value": "REQ-003"}])
    create["relations"] = [{"type": "Parent", "value": "REQ-002", "role": None}]
    assert applier.apply_change(create).status == ChangeStatus.APPLIED
    document = document_builder.build()
    assert [
        (relation_.ref_type, relation_.ref_uid)
        for relation_ in document.section_contents[2].relations
    ] == [("Parent", "REQ-002")]


def test_14_rejects_invalid_relations() -> None:
    document_builder = DocumentBuilder()
    parent_requirement = document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    applier = ChangeApplier(_build_traceability_index(document_builder))

    def apply_relation(relation: Dict[str, Any]) -> Any:
        update = _change(
            parent_requirement,
            [_field("TITLE", 0, "Requirement title", "Changed title")],
            None,
        )
        update["relations"] = [relation]
        return applier.apply_change(update)

    missing_node = apply_relation(_relation("add", "Parent", "REQ-404"))
    assert missing_node.status == ChangeStatus.CONFLICT
    assert missing_node.messages[-1] == (
        "The node of the relation Parent REQ-404 does not exist."
    )

    cycle = apply_relation(_relation("add", "Parent", "REQ-002"))
    assert cycle.status == ChangeStatus.ERROR
    assert cycle.messages[-1] == "The new relations of the node form a cycle."

    unknown_role = apply_relation(_relation("add", "Parent", "REQ-002", "R"))
    assert unknown_role.status == ChangeStatus.ERROR

    file_relation = apply_relation(_relation("add", "File", "file.py"))
    assert file_relation.status == ChangeStatus.ERROR

    # A rejected relation leaves the fields unchanged as well.
    assert _values(parent_requirement, "TITLE") == ["Requirement title"]
    assert parent_requirement.relations == []
