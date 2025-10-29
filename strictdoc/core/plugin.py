from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strictdoc.core.traceability_index import TraceabilityIndex


class StrictDocPlugin:
    def traceability_index_build_finished(
        self, traceability_index: "TraceabilityIndex"
    ) -> None:
        pass
