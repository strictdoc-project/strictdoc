from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.plugin import StrictDocPlugin
from strictdoc.core.traceability_index import TraceabilityIndex


class UserPlugin(StrictDocPlugin):
    def traceability_index_build_finished(self, traceability: TraceabilityIndex):
        print("warning: traceability_index_build_finished() is called.")  # noqa: T201

        for document in traceability.document_tree.document_list:
            assert document.meta is not None

            document_iterator = DocumentCachingIterator(document)

            for node, _ in document_iterator.all_content(
                print_fragments=False,
            ):
                if not isinstance(node, SDocNode):
                    continue

                if node.reserved_title.endswith("."):
                    print(f'warning: Node title ends with a dot: "{node.reserved_title}".')  # noqa: T201
