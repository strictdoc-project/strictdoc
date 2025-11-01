from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.plugin import StrictDocPlugin
from strictdoc.core.traceability_index import TraceabilityIndex


class UserPlugin(StrictDocPlugin):
    def traceability_index_build_finished(self, traceability: TraceabilityIndex):
        print("warning: traceability_index_build_finished() is called.")  # noqa: T201

        for document in traceability.document_tree.document_list:
            assert document.meta is not None

            document_iterator = SDocDocumentIterator(document)

            for node, _ in document_iterator.all_content(
                print_fragments=False,
            ):
                if not isinstance(node, SDocNode):
                    continue

                traceability.validation_index.add_issue(
                    node,
                    issue="The whole node is really bad.",
                    field=None,
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="UID field is really bad.",
                    field="UID",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="CUSTOM_META_FIELD field is really bad.",
                    field="CUSTOM_META_FIELD",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="TITLE field is really bad.",
                    field="TITLE",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="STATEMENT field is really bad.",
                    field="STATEMENT",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="RATIONALE field is really bad.",
                    field="RATIONALE",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="COMMENT field is really bad.",
                    field="COMMENT",
                    subject=f"Node: {node.reserved_title}",
                )
                traceability.validation_index.add_issue(
                    node,
                    issue="CUSTOM_CONTENT_FIELD field is really bad.",
                    field="CUSTOM_CONTENT_FIELD",
                    subject=f"Node: {node.reserved_title}",
                )
