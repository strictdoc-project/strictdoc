# mypy: disable-error-code="no-untyped-def"
class NodeCreationOrder:
    BEFORE = "before"
    CHILD = "child"
    AFTER = "after"

    @staticmethod
    def is_valid(order):
        return order in (
            NodeCreationOrder.BEFORE,
            NodeCreationOrder.CHILD,
            NodeCreationOrder.AFTER,
        )
