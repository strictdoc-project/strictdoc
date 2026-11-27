"""
Applies the changes that the static editor exports as JSON to the documents
of a project.

A change updates, creates, or deletes one node. The changes of one node are
applied together or not at all. For each field
instance, a change records its index and its value at the time of the export
(old_value). The current value of the instance must still equal old_value.
Otherwise, the node has changed in a conflicting way since the export, and
the change is reported as a conflict instead of overwriting the current
value.

A change can also add and remove Parent and Child relations of a node. The
command checks that the related node exists and that the relations form no
cycle.

A new node is placed after an existing node, or after a node that an earlier
change of the same run creates. A deleted node must not have changed since
the export.

@relation(SDOC-SRS-216, scope=file)
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementField,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    ReferenceType,
)
from strictdoc.backend.sdoc.models.model import RequirementFieldName
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
    Reference,
)
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.features.static_editing.edit_data import (
    EDITABLE_RELATION_TYPES,
    collect_incoming_relations,
    compute_node_content_hash,
    get_node_not_deletable_reason,
    get_node_not_editable_reason,
    get_relation_value,
    iterate_project_nodes,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import ensure_newline

STATIC_EDITING_CHANGES_SCHEMA = "strictdoc-static-editing-changes"
STATIC_EDITING_CHANGES_VERSION = 1

OPERATION_UPDATE_NODE = "update_node"
OPERATION_CREATE_NODE = "create_node"
OPERATION_DELETE_NODE = "delete_node"

READ_ONLY_FIELDS = (RequirementFieldName.UID, RequirementFieldName.MID)

_MESSAGE_NODE_DOES_NOT_EXIST = "The node does not exist anymore."


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
            if not isinstance(change, dict):
                raise _ChangeRejected(
                    ChangeStatus.ERROR, "The change is not a JSON object."
                )
            operation = change.get("op")
            if operation == OPERATION_UPDATE_NODE:
                node = self._update_node(change, result)
            elif operation == OPERATION_CREATE_NODE:
                node = self._create_node(change, result)
            elif operation == OPERATION_DELETE_NODE:
                node = self._delete_node(change, result)
            else:
                raise _ChangeRejected(
                    ChangeStatus.ERROR, f"Unsupported operation: {operation}."
                )
        except _ChangeRejected as rejection_:
            result.status = rejection_.status
            result.messages.append(rejection_.message)
            return result

        if result.status != ChangeStatus.APPLIED:
            return result

        assert node is not None
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

    def _update_node(
        self, change: Dict[str, Any], result: ChangeResult
    ) -> Optional[SDocNode]:
        node = self._find_node(change.get("node"), change.get("node_type"))
        if change.get("base_hash") != compute_node_content_hash(node):
            result.messages.append(
                "The node has changed since the export. The changed "
                "fields are merged."
            )
        # The relations are checked before any field changes, so that a
        # rejected relation leaves the whole node unchanged.
        new_relations = self._plan_relations(node, change.get("relations"))
        changed_field_names = self._apply_fields(node, change, result)
        if new_relations is not None:
            node.relations = new_relations
            result.messages.append("Changed relations.")
        if len(changed_field_names) == 0 and new_relations is None:
            result.status = ChangeStatus.ALREADY_APPLIED
        return node

    def _create_node(
        self, change: Dict[str, Any], result: ChangeResult
    ) -> Optional[SDocNode]:
        node_type = change.get("node_type")
        field_values = change.get("fields")
        if not isinstance(field_values, list):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change has no list of fields."
            )
        values_by_field: Dict[str, List[str]] = {}
        for field_value_ in field_values:
            if (
                not isinstance(field_value_, dict)
                or not isinstance(field_value_.get("name"), str)
                or not isinstance(field_value_.get("value"), str)
            ):
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    "A field of the new node has no name or no value.",
                )
            if len(field_value_["value"].strip()) == 0:
                continue
            values_by_field.setdefault(field_value_["name"], []).append(
                field_value_["value"]
            )

        uid_values = values_by_field.get(RequirementFieldName.UID, [])
        if len(uid_values) != 1:
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The new node must have one UID."
            )
        uid = uid_values[0].strip()

        existing_node = self.traceability_index.get_node_by_uid_weak2(uid)
        if existing_node is not None:
            if (
                isinstance(existing_node, SDocNode)
                and existing_node.node_type == node_type
                and self._node_has_values(existing_node, values_by_field)
            ):
                result.status = ChangeStatus.ALREADY_APPLIED
                return existing_node
            raise _ChangeRejected(
                ChangeStatus.ERROR, f"A node with the UID {uid} exists already."
            )

        position = change.get("position")
        if not isinstance(position, dict):
            raise _ChangeRejected(
                ChangeStatus.ERROR, "The change has no position of the node."
            )
        try:
            previous_node = self._find_node(position.get("after"), None)
        except _ChangeRejected as rejection_:
            if rejection_.status == ChangeStatus.CONFLICT:
                raise _ChangeRejected(
                    ChangeStatus.CONFLICT,
                    "The node after which the new node is placed does not "
                    "exist anymore.",
                ) from rejection_
            raise

        document: SDocDocument = assert_cast(
            previous_node.get_document(), SDocDocument
        )
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        if node_type not in grammar.elements_by_type:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The grammar of the document has no element {node_type}.",
            )
        element: GrammarElement = grammar.elements_by_type[node_type]
        for field_name_, values_ in values_by_field.items():
            if field_name_ not in element.fields_map:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The grammar element {node_type} has no field "
                    f"{field_name_}.",
                )
            if field_name_ == RequirementFieldName.MID:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The field {field_name_} is read-only.",
                )
            if len(values_) > 1 and field_name_ != RequirementFieldName.COMMENT:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The field {field_name_} can have only one value.",
                )
            for value_ in values_:
                _validate_value(element.fields_map[field_name_], value_)
        for grammar_field_ in element.fields:
            if (
                grammar_field_.required
                and grammar_field_.title != RequirementFieldName.MID
                and grammar_field_.title not in values_by_field
            ):
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The field {grammar_field_.title} is required.",
                )

        parent = previous_node.parent
        node = SDocNode(
            parent=parent, node_type=node_type, fields=[], relations=[]
        )
        node.ng_document_reference = DocumentReference()
        node.ng_document_reference.set_document(document)
        node.ng_including_document_reference = (
            previous_node.ng_including_document_reference
        )
        node.is_composite = element.property_is_composite is True
        if (
            document.config.enable_mid
            or RequirementFieldName.MID in element.fields_map
        ):
            node.mid_permanent = True
        for field_name_ in element.field_titles:
            if field_name_ in values_by_field:
                self._write_field(
                    node,
                    element,
                    field_name_,
                    [
                        _FieldInstance(None, value_)
                        for value_ in values_by_field[field_name_]
                    ],
                )
        relations = change.get("relations", [])
        if not isinstance(relations, list):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "The relations of the change are not a list.",
            )
        new_relations = self._plan_relations(
            node,
            [
                {**relation_, "action": "add"}
                if isinstance(relation_, dict)
                else relation_
                for relation_ in relations
            ],
        )
        if new_relations is not None:
            node.relations = new_relations
        parent.section_contents.insert(
            parent.section_contents.index(previous_node) + 1, node
        )
        self.traceability_index.create_requirement(node)
        result.messages.append(
            f"Created the node after {self._node_label(previous_node)}."
        )
        return node

    def _delete_node(
        self, change: Dict[str, Any], result: ChangeResult
    ) -> Optional[SDocNode]:
        try:
            node = self._find_node(change.get("node"), change.get("node_type"))
        except _ChangeRejected as rejection_:
            if rejection_.message == _MESSAGE_NODE_DOES_NOT_EXIST:
                result.status = ChangeStatus.ALREADY_APPLIED
                result.messages.append(rejection_.message)
                return None
            raise
        if change.get("base_hash") != compute_node_content_hash(node):
            raise _ChangeRejected(
                ChangeStatus.CONFLICT,
                "The node has changed since the export. Check the current "
                "version before you delete it.",
            )
        if len(node.section_contents) > 0:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "The node contains other nodes and cannot be deleted.",
            )
        if (
            get_node_not_deletable_reason(node, self.traceability_index)
            is not None
        ):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "Other nodes refer to the node with a LINK.",
            )
        relation_value = get_relation_value(node)
        incoming_relations = [
            source_node_
            for source_node_, _ in collect_incoming_relations(
                self.traceability_index
            ).get(relation_value if relation_value is not None else "", [])
            if source_node_ is not node
        ]
        if len(incoming_relations) > 0:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "Other nodes refer to the node with relations: "
                + ", ".join(
                    self._node_label(source_node_)
                    for source_node_ in incoming_relations
                )
                + ".",
            )
        # The node is removed from the tree, so its document is determined
        # first.
        document: SDocDocument = assert_cast(node.get_document(), SDocDocument)
        self.traceability_index.delete_requirement(node)
        node.parent.section_contents.remove(node)
        result.messages.append("Deleted the node.")
        document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
        self.modified_documents[document_meta.input_doc_full_path] = document
        return node

    def _plan_relations(
        self, node: SDocNode, relation_changes: Any
    ) -> Optional[List[Reference]]:
        """
        Return the new relations of the node after the relation changes, or
        None if the node already has them. A relation change is
        {"action": "add" or "remove", "type", "value", "role"}.
        """
        if relation_changes is None:
            return None
        if not isinstance(relation_changes, list):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "The relations of the change are not a list.",
            )
        document: SDocDocument = assert_cast(node.get_document(), SDocDocument)
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[node.node_type]

        relations: List[Reference] = list(node.relations)
        changed = False
        for relation_change_ in relation_changes:
            action, relation_type, value, role = _parse_relation_change(
                relation_change_
            )
            matching_relations = [
                relation_
                for relation_ in relations
                if isinstance(
                    relation_, (ParentReqReference, ChildReqReference)
                )
                and relation_.ref_type == relation_type
                and relation_.ref_uid == value
                and relation_.role == role
            ]
            if action == "remove":
                if len(matching_relations) > 0:
                    relations.remove(matching_relations[0])
                    changed = True
                continue
            if len(matching_relations) > 0:
                continue

            relation_label = _relation_label(relation_type, value, role)
            if not element.has_relation_type_role(relation_type, role):
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The grammar element {node.node_type} does not allow the "
                    f"relation {relation_label}.",
                )
            target_node = self._find_relation_target(document, value)
            if target_node is None:
                raise _ChangeRejected(
                    ChangeStatus.CONFLICT,
                    f"The node of the relation {relation_label} does not "
                    "exist.",
                )
            if target_node is node:
                raise _ChangeRejected(
                    ChangeStatus.ERROR,
                    f"The relation {relation_label} refers to the node itself.",
                )
            relations.append(
                ParentReqReference(node, value, role)
                if relation_type == ReferenceType.PARENT
                else ChildReqReference(node, value, role)  # type: ignore[arg-type]
            )
            changed = True

        if not changed:
            return None
        if self._has_relation_cycle(node, relations):
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                "The new relations of the node form a cycle.",
            )
        return relations

    def _find_relation_target(
        self, document: SDocDocument, value: str
    ) -> Optional[SDocNode]:
        target: Any
        if document.config.get_relation_field() == RequirementFieldName.MID:
            target = self.traceability_index.get_node_by_mid_weak(MID(value))
        else:
            target = self.traceability_index.get_node_by_uid_weak2(value)
        return target if isinstance(target, SDocNode) else None

    def _has_relation_cycle(
        self, node: SDocNode, node_relations: List[Reference]
    ) -> bool:
        """
        Check whether the node is its own ancestor when it has the given
        relations. A Parent relation of A to B makes B a parent of A. A Child
        relation of A to B makes A a parent of B.
        """
        nodes = list(iterate_project_nodes(self.traceability_index))
        if node not in nodes:
            nodes.append(node)
        nodes_by_value: Dict[str, SDocNode] = {}
        for node_ in nodes:
            if node_.reserved_uid is not None:
                nodes_by_value[node_.reserved_uid] = node_
            nodes_by_value[node_.reserved_mid.get_string_value()] = node_

        parents: Dict[int, List[SDocNode]] = {}
        for node_ in nodes:
            relations = node_relations if node_ is node else node_.relations
            for relation_ in relations:
                if not isinstance(
                    relation_, (ParentReqReference, ChildReqReference)
                ):
                    continue
                related_node = nodes_by_value.get(relation_.ref_uid)
                if related_node is None:
                    continue
                if isinstance(relation_, ParentReqReference):
                    parents.setdefault(id(node_), []).append(related_node)
                else:
                    parents.setdefault(id(related_node), []).append(node_)

        visited: set[int] = set()
        stack = list(parents.get(id(node), []))
        while len(stack) > 0:
            ancestor = stack.pop()
            if ancestor is node:
                return True
            if id(ancestor) in visited:
                continue
            visited.add(id(ancestor))
            stack.extend(parents.get(id(ancestor), []))
        return False

    @staticmethod
    def _node_has_values(
        node: SDocNode, values_by_field: Dict[str, List[str]]
    ) -> bool:
        for field_name_, values_ in values_by_field.items():
            node_values = [
                _normalize(field_.get_text_value())
                for field_ in node.ordered_fields_lookup.get(field_name_, [])
            ]
            if node_values != [_normalize(value_) for value_ in values_]:
                return False
        return True

    @staticmethod
    def _node_label(node: SDocNode) -> str:
        if node.reserved_uid is not None:
            return node.reserved_uid
        return f"MID {node.reserved_mid.get_string_value()}"

    @staticmethod
    def _describe_change(change: Any) -> Tuple[str, str]:
        if not isinstance(change, dict):
            return "", "<invalid change>"
        document_path = str(change.get("document_path", ""))
        if change.get("op") == OPERATION_CREATE_NODE:
            fields = change.get("fields")
            if isinstance(fields, list):
                for field_ in fields:
                    if (
                        isinstance(field_, dict)
                        and field_.get("name") == RequirementFieldName.UID
                        and isinstance(field_.get("value"), str)
                    ):
                        return document_path, f"new node {field_['value']}"
            return document_path, "<new node>"
        node_identity = change.get("node")
        if isinstance(node_identity, dict):
            if node_identity.get("uid"):
                return document_path, str(node_identity["uid"])
            if node_identity.get("mid"):
                return document_path, f"MID {node_identity['mid']}"
        return document_path, "<unknown node>"

    def _find_node(
        self, node_identity: Any, node_type: Optional[Any]
    ) -> SDocNode:
        """
        Find an editable node by its UID or MID. If node_type is given, the
        node must have this type.
        """
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
                ChangeStatus.CONFLICT, _MESSAGE_NODE_DOES_NOT_EXIST
            )
        not_editable_reason = get_node_not_editable_reason(
            node, self.traceability_index
        )
        if not_editable_reason is not None:
            raise _ChangeRejected(
                ChangeStatus.ERROR,
                f"The node is not editable: {not_editable_reason}.",
            )
        if node_type is not None and node_type != node.node_type:
            raise _ChangeRejected(
                ChangeStatus.CONFLICT,
                f"The node type has changed from {node_type} "
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


def _parse_relation_change(
    relation_change: Any,
) -> Tuple[str, str, str, Optional[str]]:
    if not isinstance(relation_change, dict):
        raise _ChangeRejected(
            ChangeStatus.ERROR, "A relation change is not a JSON object."
        )
    action = relation_change.get("action")
    relation_type = relation_change.get("type")
    value = relation_change.get("value")
    role = relation_change.get("role")
    if action not in ("add", "remove"):
        raise _ChangeRejected(
            ChangeStatus.ERROR, f"Unsupported relation action: {action}."
        )
    if relation_type not in EDITABLE_RELATION_TYPES:
        raise _ChangeRejected(
            ChangeStatus.ERROR,
            f"Unsupported relation type: {relation_type}.",
        )
    if not isinstance(value, str) or len(value.strip()) == 0:
        raise _ChangeRejected(
            ChangeStatus.ERROR, "A relation change has no value."
        )
    if role is not None and not isinstance(role, str):
        raise _ChangeRejected(
            ChangeStatus.ERROR, "A relation change has an invalid role."
        )
    return (
        action,
        relation_type,
        value.strip(),
        role if role is not None and len(role) > 0 else None,
    )


def _relation_label(relation_type: str, value: str, role: Optional[str]) -> str:
    if role is not None:
        return f"{relation_type} ({role}) {value}"
    return f"{relation_type} {value}"


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
