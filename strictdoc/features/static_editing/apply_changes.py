"""
Applies the changes that the static editor exports as JSON to the documents
of a project.

The changes of one node are applied together or not at all. For each field
instance, a change records its index and its value at the time of the export
(old_value). The current value of the instance must still equal old_value.
Otherwise, the node has changed in a conflicting way since the export, and
the change is reported as a conflict instead of overwriting the current
value.

@relation(SDOC-SRS-216, scope=file)
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
)
from strictdoc.backend.sdoc.models.model import RequirementFieldName
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.features.static_editing.edit_data import (
    compute_node_content_hash,
    get_node_not_editable_reason,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import ensure_newline

STATIC_EDITING_CHANGES_SCHEMA = "strictdoc-static-editing-changes"
STATIC_EDITING_CHANGES_VERSION = 1

OPERATION_UPDATE_NODE = "update_node"

READ_ONLY_FIELDS = (RequirementFieldName.UID, RequirementFieldName.MID)


class ChangesFileError(Exception):
    pass


class ChangeStatus(str, Enum):
    APPLIED = "applied"
    ALREADY_APPLIED = "already applied"
    CONFLICT = "conflict"
    ERROR = "error"


@dataclass
class ChangeResult:
    document_path: str
    node_label: str
    status: ChangeStatus
    messages: List[str] = field(default_factory=list)


class _ChangeRejected(Exception):
    def __init__(self, status: ChangeStatus, message: str) -> None:
        super().__init__(message)
        self.status: ChangeStatus = status
        self.message: str = message


@dataclass
class _FieldInstance:
    # The parsed field, or None for a new or changed value.
    source_field: Optional[SDocNodeField]
    value: str
    # For a changed value: whether the replaced field was a multiline field.
    # A changed field keeps its style unless the new value has more lines.
    was_multiline: Optional[bool] = None


def load_changes_file(path_to_changes_file: str) -> List[Dict[str, Any]]:
    try:
        with open(path_to_changes_file, encoding="utf8") as changes_file:
            changes_data = json.load(changes_file)
    except OSError as exception_:
        raise ChangesFileError(
            f"Cannot read the changes file: {path_to_changes_file}: "
            f"{exception_.strerror}."
        ) from exception_
    except json.JSONDecodeError as exception_:
        raise ChangesFileError(
            "The changes file is not valid JSON: "
            f"{path_to_changes_file}: {exception_}."
        ) from exception_

    if (
        not isinstance(changes_data, dict)
        or changes_data.get("schema") != STATIC_EDITING_CHANGES_SCHEMA
    ):
        raise ChangesFileError(
            "The file is not a changes file of the static editor: "
            f"{path_to_changes_file}."
        )
    if changes_data.get("version") != STATIC_EDITING_CHANGES_VERSION:
        raise ChangesFileError(
            "The changes file has an unsupported version: "
            f"{changes_data.get('version')}. Supported version: "
            f"{STATIC_EDITING_CHANGES_VERSION}."
        )
    changes = changes_data.get("changes")
    if not isinstance(changes, list):
        raise ChangesFileError(
            f"The changes file has no list of changes: {path_to_changes_file}."
        )
    return changes


def _normalize(value: str) -> str:
    return value.replace("\r\n", "\n").rstrip()


class ChangeApplier:
    """
    Applies the changes to the nodes in memory. The caller writes the
    modified documents.
    """

    def __init__(self, traceability_index: TraceabilityIndex) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.modified_documents: Dict[str, SDocDocument] = {}

    def apply_change(self, change: Any) -> ChangeResult:
        document_path, node_label = self._describe_change(change)
        result = ChangeResult(
            document_path=document_path,
            node_label=node_label,
            status=ChangeStatus.APPLIED,
        )
        try:
            node = self._find_node(change)
            if change.get("base_hash") != compute_node_content_hash(node):
                result.messages.append(
                    "The node has changed since the export. The changed "
                    "fields are merged."
                )
            changed_field_names = self._apply_fields(node, change, result)
        except _ChangeRejected as rejection_:
            result.status = rejection_.status
            result.messages.append(rejection_.message)
            return result

        if len(changed_field_names) == 0:
            result.status = ChangeStatus.ALREADY_APPLIED
            return result

        document: SDocDocument = assert_cast(node.get_document(), SDocDocument)
        document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
        self.modified_documents[document_meta.input_doc_full_path] = document
        # The export and this command can use different input paths, so the
        # document paths are compared by their common suffix.
        node_document_path = (
            document_meta.input_doc_rel_path.relative_path_posix
        )
        if not (
            node_document_path.endswith(document_path)
            or document_path.endswith(node_document_path)
        ):
            result.messages.append(
                f"The node has moved to the document {node_document_path}."
            )
        return result

    @staticmethod
    def _describe_change(change: Any) -> Tuple[str, str]:
        if not isinstance(change, dict):
            return "", "<invalid change>"
        document_path = str(change.get("document_path", ""))
        node_identity = change.get("node")
        if isinstance(node_identity, dict):
            if node_identity.get("uid"):
                return document_path, str(node_identity["uid"])
            if node_identity.get("mid"):
                return document_path, f"MID {node_identity['mid']}"
        return document_path, "<unknown node>"

    def _find_node(self, change: Any) -> SDocNode:
        if not isinstance(change, dict):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change is not a JSON object."
            )
        if change.get("op") != OPERATION_UPDATE_NODE:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"Unsupported operation: {change.get('op')}.",
            )
        node_identity = change.get("node")
        if not isinstance(node_identity, dict):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change does not identify a node."
            )

        node: Any = None
        uid = node_identity.get("uid")
        mid = node_identity.get("mid")
        if isinstance(uid, str) and len(uid) > 0:
            node = self.traceability_index.get_node_by_uid_weak2(uid)
        elif isinstance(mid, str) and len(mid) > 0:
            node = self.traceability_index.get_node_by_mid_weak(MID(mid))
        else:
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change does not identify a node."
            )

        if not isinstance(node, SDocNode):
            raise _ChangeRejected(
                ChangeStatus.CONFLICT,
                "The node does not exist anymore.",
            )
        not_editable_reason = get_node_not_editable_reason(
            node, self.traceability_index
        )
        if not_editable_reason is not None:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The node is not editable: {not_editable_reason}.",
            )
        if change.get("node_type") != node.node_type:
            raise _ChangeRejected(
                ChangeStatus.CONFLICT,
                f"The node type has changed from {change.get('node_type')} "
                f"to {node.node_type}.",
            )
        return node

    def _apply_fields(
        self, node: SDocNode, change: Dict[str, Any], result: ChangeResult
    ) -> List[str]:
        document: SDocDocument = assert_cast(node.get_document(), SDocDocument)
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[node.node_type]

        field_changes = change.get("fields")
        if not isinstance(field_changes, list):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change has no list of fields."
            )

        # The new instances of each field. The node is only modified after
        # all field changes of the node are accepted.
        instances_by_field: Dict[str, List[_FieldInstance]] = {}
        changed_field_names: List[str] = []
        for field_change_ in field_changes:
            field_name = self._validate_field_change(
                field_change_, element, node
            )
            if field_name not in instances_by_field:
                instances_by_field[field_name] = [
                    _FieldInstance(field_, field_.get_text_value())
                    for field_ in node.ordered_fields_lookup.get(field_name, [])
                ]
            if self._apply_field_change(
                field_change_,
                element.fields_map[field_name],
                instances_by_field[field_name],
            ):
                if field_name not in changed_field_names:
                    changed_field_names.append(field_name)

        for field_name_ in changed_field_names:
            self._write_field(
                node, element, field_name_, instances_by_field[field_name_]
            )
        if len(changed_field_names) > 0:
            result.messages.append(
                "Changed fields: " + ", ".join(changed_field_names) + "."
            )
        return changed_field_names

    @staticmethod
    def _validate_field_change(
        field_change: Any, element: GrammarElement, node: SDocNode
    ) -> str:
        if not isinstance(field_change, dict):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "A field change is not a JSON object."
            )
        field_name = field_change.get("name")
        if not isinstance(field_name, str) or field_name not in (
            element.fields_map
        ):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The grammar element {node.node_type} has no field "
                f"{field_name}.",
            )
        if field_name in READ_ONLY_FIELDS:
            raise _ChangeRejected(
                ChangeStatus.ERROR, f"The field {field_name} is read-only."
            )
        index = field_change.get("index")
        if index is not None and (not isinstance(index, int) or index < 0):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The field {field_name} has an invalid index: {index}.",
            )
        new_value = field_change.get("new_value")
        if not isinstance(new_value, str):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The field {field_name} has no new value.",
            )
        old_value = field_change.get("old_value")
        if index is not None and not isinstance(old_value, str):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The field {field_name} has no old value.",
            )
        return field_name

    @staticmethod
    def _apply_field_change(
        field_change: Dict[str, Any],
        grammar_field: GrammarElementField,
        instances: List[_FieldInstance],
    ) -> bool:
        """
        Apply one field change to the list of instances. Return False if the
        list already contains the change.
        """
        field_name: str = field_change["name"]
        index: Optional[int] = field_change["index"]
        new_value: str = field_change["new_value"]
        is_removal = len(new_value.strip()) == 0
        if not is_removal:
            _validate_value(grammar_field, new_value)

        # An added instance.
        if index is None:
            if is_removal:
                return False
            if any(
                _normalize(instance_.value) == _normalize(new_value)
                for instance_ in instances
            ):
                return False
            if (
                field_name != RequirementFieldName.COMMENT
                and len(instances) > 0
            ):
                raise _ChangeRejected(
                    ChangeStatus.CONFLICT,
                    f"The field {field_name} has been added since the export.",
                )
            instances.append(_FieldInstance(None, new_value))
            return True

        # A changed or removed instance. The instance is found by its old
        # value, preferably at its old index: other changes can have added
        # or removed instances before it.
        old_value: str = field_change["old_value"]
        matching_positions = [
            position_
            for position_, instance_ in enumerate(instances)
            if _normalize(instance_.value) == _normalize(old_value)
        ]
        if len(matching_positions) == 0:
            if is_removal or any(
                _normalize(instance_.value) == _normalize(new_value)
                for instance_ in instances
            ):
                return False
            raise _ChangeRejected(
                ChangeStatus.CONFLICT,
                f"The field {field_name} has changed since the export.",
            )
        position = min(
            matching_positions, key=lambda position_: abs(position_ - index)
        )
        if is_removal:
            if grammar_field.required and len(instances) == 1:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The field {field_name} is required and cannot be "
                    "removed.",
                )
            del instances[position]
        else:
            replaced_field = instances[position].source_field
            instances[position] = _FieldInstance(
                None,
                new_value,
                was_multiline=replaced_field.is_multiline()
                if replaced_field is not None
                else instances[position].was_multiline,
            )
        return True

    @staticmethod
    def _write_field(
        node: SDocNode,
        element: GrammarElement,
        field_name: str,
        instances: List[_FieldInstance],
    ) -> None:
        if len(instances) == 0:
            node.ordered_fields_lookup.pop(field_name, None)
            return

        multiline = element.is_field_multiline(field_name)
        new_fields: List[SDocNodeField] = []
        for instance_ in instances:
            if instance_.source_field is not None:
                new_fields.append(instance_.source_field)
                continue
            value = instance_.value.replace("\r\n", "\n").rstrip()
            is_multiline = (
                multiline
                if instance_.was_multiline is None
                else instance_.was_multiline
            ) or "\n" in value
            new_fields.append(
                SDocNodeField.create_from_string(
                    node,
                    field_name=field_name,
                    field_value=ensure_newline(value)
                    if is_multiline
                    else value,
                    multiline=is_multiline,
                )
            )

        # set_field_value() puts a new field at its position in the grammar.
        if field_name not in node.ordered_fields_lookup:
            node.set_field_value(
                field_name=field_name, form_field_index=0, value=new_fields[0]
            )
        node.ordered_fields_lookup[field_name] = new_fields


def _validate_value(grammar_field: GrammarElementField, value: str) -> None:
    field_name = grammar_field.title
    stripped_value = value.replace("\r\n", "\n").rstrip()
    if (
        field_name in RequirementFieldName.RESERVED_SINGLELINE_FIELDS
        and "\n" in stripped_value
    ):
        raise _ChangeRejected(
            ChangeStatus.ERROR,
            f"The field {field_name} must be a single line.",
        )
    if isinstance(grammar_field, GrammarElementFieldSingleChoice):
        if stripped_value not in grammar_field.options:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The field {field_name} has an invalid option: "
                f"{stripped_value}.",
            )
    elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
        for option_ in stripped_value.split(","):
            if option_.strip() not in grammar_field.options:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The field {field_name} has an invalid option: "
                    f"{option_.strip()}.",
                )
