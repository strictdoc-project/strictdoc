class NodeCreationOrder:
    BEFORE = "before"
    CHILD = "child"
    AFTER = "after"

    @staticmethod
    def is_valid(order: str) -> bool:
        return order in (
            NodeCreationOrder.BEFORE,
            NodeCreationOrder.CHILD,
            NodeCreationOrder.AFTER,
        )
