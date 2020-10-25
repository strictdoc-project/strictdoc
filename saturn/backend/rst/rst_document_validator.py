import docutils.nodes

from saturn.backend.rst.rst_constants import SATURN_ATTR_LEVEL


class RSTDocumentValidator:
    @staticmethod
    def validate_rst_document(rst_document):
        assert rst_document

        print("Validation: Checking invariants:")
        print("- All nodes must be unique (no cycles in the tree)")
        print("- Each child has to be at least one level down compared to its parent")

        print(rst_document.pformat())
        unique_nodes = set()
        unique_nodes.add(rst_document)

        queue = [rst_document]
        cursor = queue.pop()

        while True:
            print("Checking node against its children: {}".format(cursor))

            for child in cursor:
                if not isinstance(child, docutils.nodes.section):
                    continue

                if child in unique_nodes:
                    raise RuntimeError(
                        'tree seems to contain cycles. the node is not unique: {}'.format(
                            child
                        )
                    )

                unique_nodes.add(child)

                if child[SATURN_ATTR_LEVEL] <= cursor[SATURN_ATTR_LEVEL]:
                    raise RuntimeError(
                        'level is broken between node and its child: {} {}'.format(
                            cursor, child
                        )
                    )

                queue.append(child)
            try:
                cursor = queue.pop(0)
            except IndexError:
                break
