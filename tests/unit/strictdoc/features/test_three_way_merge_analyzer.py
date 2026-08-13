import os

from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.git_workspace.three_way_merge_analyzer import (
    PLACEMENT_START,
    NodeClassification,
    classify_documents,
    splice_document,
)

# find_requirement (reused from the Diff feature) matches nodes by MID, then
# UID, then title/content similarity -- never by STATEMENT alone. Every
# fixture below gives the node a stable UID so independently-parsed
# base/target/incoming trees can be matched to "the same" logical node while
# only its STATEMENT varies.
REQ = "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement}\n"


def _write_doc(path_to_dir: str, filename: str, content: str) -> None:
    os.makedirs(path_to_dir, exist_ok=True)
    with open(
        os.path.join(path_to_dir, filename), "w", encoding="utf8"
    ) as file_:
        file_.write(content)


def _project_config(path_to_dir: str) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.input_paths = [path_to_dir]
    return project_config


DOC_HEADER = "[DOCUMENT]\nTITLE: Test\n\n"


def _classify_raw(
    tmp_path, base_body: str, target_body: str, incoming_body: str
):
    path_base = str(tmp_path / "base")
    path_target = str(tmp_path / "target")
    path_incoming = str(tmp_path / "incoming")
    _write_doc(path_base, "requirement.sdoc", DOC_HEADER + base_body)
    _write_doc(path_target, "requirement.sdoc", DOC_HEADER + target_body)
    _write_doc(path_incoming, "requirement.sdoc", DOC_HEADER + incoming_body)

    return classify_documents(
        base_project_config=_project_config(path_base),
        target_project_config=_project_config(path_target),
        incoming_project_config=_project_config(path_incoming),
        base_revision="base_sha",
        target_revision="target_sha",
        incoming_revision="incoming_sha",
    )


def _classify(tmp_path, base_body: str, target_body: str, incoming_body: str):
    result = _classify_raw(tmp_path, base_body, target_body, incoming_body)
    assert len(result.documents) == 1
    document_result = result.documents[0]
    assert len(document_result.node_results) == 1
    return document_result.node_results[0]


class TestNodeClassificationTruthTable:
    def test_unchanged(self, tmp_path):
        body = REQ.format(statement="Same.")
        result = _classify(tmp_path, body, body, body)
        assert result.classification == NodeClassification.UNCHANGED
        assert result.resolved_node is result.target_node

    def test_only_incoming_changed(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = REQ.format(statement="Base.")
        incoming = REQ.format(statement="Incoming.")
        result = _classify(tmp_path, base, target, incoming)
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is result.incoming_node

    def test_only_target_changed(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = REQ.format(statement="Target.")
        incoming = REQ.format(statement="Base.")
        result = _classify(tmp_path, base, target, incoming)
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is result.target_node

    def test_both_changed_to_same_result(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = REQ.format(statement="Converged.")
        incoming = REQ.format(statement="Converged.")
        result = _classify(tmp_path, base, target, incoming)
        assert result.classification == NodeClassification.AUTO_MERGED

    def test_true_conflict(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = REQ.format(statement="Target.")
        incoming = REQ.format(statement="Incoming.")
        result = _classify(tmp_path, base, target, incoming)
        assert result.classification == NodeClassification.TRUE_CONFLICT
        assert result.resolved_node is None
        assert result.resolve("target") is result.target_node
        assert result.resolve("incoming") is result.incoming_node

    def test_removed_in_target_incoming_unchanged(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = ""
        incoming = REQ.format(statement="Base.")
        result = _classify(tmp_path, base, target, incoming)
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is None

    def test_removed_in_target_incoming_modified(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = ""
        incoming = REQ.format(statement="Incoming.")
        result = _classify(tmp_path, base, target, incoming)
        assert (
            result.classification == NodeClassification.DELETE_MODIFY_CONFLICT
        )
        assert result.deleted_side == "target"
        assert result.resolve("target") is None
        assert result.resolve("incoming") is result.incoming_node

    def test_removed_in_incoming_target_modified(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = REQ.format(statement="Target.")
        incoming = ""
        result = _classify(tmp_path, base, target, incoming)
        assert (
            result.classification == NodeClassification.DELETE_MODIFY_CONFLICT
        )
        assert result.deleted_side == "incoming"
        assert result.resolve("incoming") is None
        assert result.resolve("target") is result.target_node

    def test_removed_in_both(self, tmp_path):
        base = REQ.format(statement="Base.")
        result = _classify(tmp_path, base, "", "")
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is None

    def test_target_only_addition(self, tmp_path):
        target = REQ.format(statement="New in target.")
        result = _classify(tmp_path, "", target, "")
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is result.target_node

    def test_incoming_only_addition(self, tmp_path):
        incoming = REQ.format(statement="New in incoming.")
        result = _classify(tmp_path, "", "", incoming)
        assert result.classification == NodeClassification.AUTO_MERGED
        assert result.resolved_node is result.incoming_node

    def test_both_added_unrelated_uids_are_two_separate_additions(
        self, tmp_path
    ):
        target = "[REQUIREMENT]\nUID: REQ_ALPHA\nSTATEMENT: Target only.\n"
        incoming = "[REQUIREMENT]\nUID: REQ_BETA\nSTATEMENT: Incoming only.\n"
        result = _classify_raw(tmp_path, "", target, incoming)
        node_results = result.documents[0].node_results
        assert len(node_results) == 2
        assert all(
            r.classification == NodeClassification.AUTO_MERGED
            for r in node_results
        )


class TestSpliceDocumentRoundTrip:
    def test_splice_resolves_conflict_and_reparsed_content_matches(
        self, tmp_path
    ):
        base = (
            "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Base one.\n\n"
            "[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: Base two.\n"
        )
        target = (
            "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Target one.\n\n"
            "[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: Base two.\n"
        )
        incoming = (
            "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Incoming one.\n\n"
            "[REQUIREMENT]\nUID: REQ_2\nSTATEMENT: Base two.\n\n"
            "[REQUIREMENT]\nUID: REQ_3\nSTATEMENT: New from incoming.\n"
        )
        result = _classify_raw(tmp_path, base, target, incoming)
        document_result = result.documents[0]
        node_results = document_result.node_results
        assert len(node_results) == 3

        conflict = next(
            r
            for r in node_results
            if r.classification == NodeClassification.TRUE_CONFLICT
        )
        allocations = {conflict.key: "incoming"}

        composite_document = splice_document(document_result, allocations)
        assert composite_document is not None

        project_config = _project_config(str(tmp_path / "target"))
        written = SDWriter(project_config).write(composite_document)

        assert "STATEMENT: Incoming one." in written
        assert "STATEMENT: Base two." in written
        assert "STATEMENT: New from incoming." in written
        assert "STATEMENT: Target one." not in written

        # Round-trips cleanly back through the parser.
        reparsed = SDReader.read(written)
        statements = [
            node.reserved_statement for node in reparsed.section_contents
        ]
        assert statements == [
            "Incoming one.",
            "Base two.",
            "New from incoming.",
        ]

    def test_splice_restores_section_when_conflict_under_it_resolved_as_incoming(
        self, tmp_path
    ):
        # A section deleted entirely on target while a node inside it was
        # independently modified on incoming: the section's own fields are
        # unchanged from base, so it auto-resolves to "removed" -- but the
        # child node is a real DELETE_MODIFY_CONFLICT. Resolving that
        # conflict as "incoming" must restore both the node and its now-
        # necessary container section, even though the section itself was
        # never a conflict and was never explicitly allocated.
        section = (
            "[[SECTION]]\nUID: SEC_1\nTITLE: Section\n\n"
            "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement}\n\n"
            "[[/SECTION]]\n"
        )
        base = section.format(statement="Base.")
        target = ""
        incoming = section.format(statement="Incoming.")
        result = _classify_raw(tmp_path, base, target, incoming)
        document_result = result.documents[0]

        conflict = next(
            r
            for r in document_result.iter_all()
            if r.classification == NodeClassification.DELETE_MODIFY_CONFLICT
        )
        assert conflict.deleted_side == "target"

        composite_document = splice_document(
            document_result, {conflict.key: "incoming"}
        )
        assert composite_document is not None

        project_config = _project_config(str(tmp_path / "target"))
        written = SDWriter(project_config).write(composite_document)

        assert "[[SECTION]]" in written
        assert "STATEMENT: Incoming." in written

        reparsed = SDReader.read(written)
        assert len(reparsed.section_contents) == 1
        restored_section = reparsed.section_contents[0]
        assert restored_section.reserved_title == "Section"
        assert len(restored_section.section_contents) == 1
        assert (
            restored_section.section_contents[0].reserved_statement
            == "Incoming."
        )

    def test_splice_keeps_section_deleted_when_conflict_under_it_resolved_as_target(
        self, tmp_path
    ):
        section = (
            "[[SECTION]]\nUID: SEC_1\nTITLE: Section\n\n"
            "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: {statement}\n\n"
            "[[/SECTION]]\n"
        )
        base = section.format(statement="Base.")
        target = ""
        incoming = section.format(statement="Incoming.")
        result = _classify_raw(tmp_path, base, target, incoming)
        document_result = result.documents[0]

        conflict = next(
            r
            for r in document_result.iter_all()
            if r.classification == NodeClassification.DELETE_MODIFY_CONFLICT
        )

        composite_document = splice_document(
            document_result, {conflict.key: "target"}
        )
        # Resolving "target" reproduces target's already-empty document
        # exactly -- nothing to materialize, target's blob stays as-is.
        assert composite_document is None

    def test_splice_returns_none_when_document_unchanged_from_target(
        self, tmp_path
    ):
        body = REQ.format(statement="Same.")
        result = _classify_raw(tmp_path, body, body, body)
        document_result = result.documents[0]
        assert splice_document(document_result, {}) is None


class TestSpliceDocumentPlacements:
    """
    SDOC-SRS-215 sub-scenario 2: two independent, non-conflicting
    additions (one target-only, one incoming-only) land in a fixed default
    order (target-only first, incoming-only last) -- `placements` lets a
    genuinely-new node be repositioned among its siblings.
    """

    def _two_independent_additions(self, tmp_path):
        target = "[REQUIREMENT]\nUID: REQ_TARGET\nSTATEMENT: From target.\n"
        incoming = (
            "[REQUIREMENT]\nUID: REQ_INCOMING\nSTATEMENT: From incoming.\n"
        )
        result = _classify_raw(tmp_path, "", target, incoming)
        document_result = result.documents[0]
        assert len(document_result.node_results) == 2
        assert all(
            r.classification == NodeClassification.AUTO_MERGED
            for r in document_result.node_results
        )
        target_result = next(
            r for r in document_result.node_results if r.target_node is not None
        )
        incoming_result = next(
            r
            for r in document_result.node_results
            if r.incoming_node is not None
        )
        return document_result, target_result, incoming_result

    def test_default_order_is_target_only_then_incoming_only(self, tmp_path):
        document_result, target_result, incoming_result = (
            self._two_independent_additions(tmp_path)
        )
        composite_document = splice_document(document_result, {})
        assert composite_document is not None
        statements = [
            node.reserved_statement
            for node in composite_document.section_contents
        ]
        assert statements == ["From target.", "From incoming."]

    def test_placement_moves_incoming_addition_before_target_addition(
        self, tmp_path
    ):
        document_result, target_result, incoming_result = (
            self._two_independent_additions(tmp_path)
        )
        composite_document = splice_document(
            document_result,
            {},
            placements={incoming_result.key: PLACEMENT_START},
        )
        assert composite_document is not None
        statements = [
            node.reserved_statement
            for node in composite_document.section_contents
        ]
        assert statements == ["From incoming.", "From target."]

    def test_placement_after_a_specific_sibling(self, tmp_path):
        base = REQ.format(statement="Base.")
        target = "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Base.\n\n[REQUIREMENT]\nUID: REQ_TARGET\nSTATEMENT: From target.\n"
        incoming = "[REQUIREMENT]\nUID: REQ_1\nSTATEMENT: Base.\n\n[REQUIREMENT]\nUID: REQ_INCOMING\nSTATEMENT: From incoming.\n"
        result = _classify_raw(tmp_path, base, target, incoming)
        document_result = result.documents[0]
        unchanged_result = next(
            r
            for r in document_result.node_results
            if r.classification == NodeClassification.UNCHANGED
        )
        incoming_result = next(
            r
            for r in document_result.node_results
            if r.incoming_node is not None
            and r.classification == NodeClassification.AUTO_MERGED
        )

        composite_document = splice_document(
            document_result,
            {},
            placements={incoming_result.key: unchanged_result.key},
        )
        assert composite_document is not None
        statements = [
            node.reserved_statement
            for node in composite_document.section_contents
        ]
        assert statements == ["Base.", "From incoming.", "From target."]

    def test_unknown_placement_key_is_ignored(self, tmp_path):
        document_result, target_result, incoming_result = (
            self._two_independent_additions(tmp_path)
        )
        composite_document = splice_document(
            document_result,
            {},
            placements={incoming_result.key: "no-such-key#0"},
        )
        assert composite_document is not None
        # Falls back to appending at the end of the sibling list -- still a
        # valid, deterministic result rather than dropping the node.
        statements = [
            node.reserved_statement
            for node in composite_document.section_contents
        ]
        assert statements == ["From target.", "From incoming."]
