"""
Build the nodes view of the specification graph in the background, for the
server.

The nodes view of a large project takes many seconds to build. The server
starts the build when it starts and when the screen is requested for a new
version of the traceability index. The screen opens at once and shows a
preloader in the nodes view. The build runs in another process, so that it
does not hold the interpreter lock of the server. When it is done, the view
is written into a JSON file next to the screen, with the version of the
index it was built for. The screen loads the file when the version matches.
"""

import json
import os
import threading
from concurrent.futures import Future, ProcessPoolExecutor
from typing import Optional

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.specification_graph.relations import (
    build_nodes_graph,
)
from strictdoc.features.specification_graph.svg_graph.model import Graph
from strictdoc.features.specification_graph.view_object import (
    SpecificationGraphView,
)

NODES_VIEW_ID = "nodes"
NODES_VIEW_LABEL = "Nodes"
NODES_DATA_FILENAME = "specification_graph_nodes.json"


def index_version(traceability_index: TraceabilityIndex) -> str:
    return traceability_index.index_last_updated.isoformat()


class _NodesViewBuilder:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._executor: Optional[ProcessPoolExecutor] = None
        self._future: Optional[Future[SpecificationGraphView]] = None
        self._version: Optional[str] = None

    def start(
        self,
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> str:
        """
        Start the build for the current version of the index, unless it is
        already started. Return the version.
        """

        version = index_version(traceability_index)
        with self._lock:
            if self._version == version:
                return version
            self._version = version
            # A build for an older version that has not started yet is not
            # needed anymore.
            if self._future is not None:
                self._future.cancel()
            if self._executor is None:
                self._executor = ProcessPoolExecutor(max_workers=1)
            # The graph model is plain data: it goes to the other process.
            # The traceability index stays in this one.
            graph = build_nodes_graph(
                traceability_index,
                LinkRenderer(
                    root_path="",
                    static_path=project_config.dir_for_sdoc_assets,
                ),
            )
            future = self._executor.submit(
                _render_nodes_view,
                graph,
                project_config.specification_graph_debug,
            )
            self._future = future
        future.add_done_callback(
            lambda done_: self._write(
                done_, version, project_config, html_templates
            )
        )
        return version

    def _write(
        self,
        future: "Future[SpecificationGraphView]",
        version: str,
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
    ) -> None:
        if future.cancelled():
            return
        with self._lock:
            if self._version != version:
                return
        exception = future.exception()
        if exception is not None:
            print(  # noqa: T201
                f"error: Specification graph, view {NODES_VIEW_LABEL}: "
                f"{exception}"
            )
            view = SpecificationGraphView(
                view_id=NODES_VIEW_ID,
                label=NODES_VIEW_LABEL,
                error=str(exception),
            )
        else:
            view = future.result()
        content = html_templates.jinja_environment().render_template_as_markup(
            "features/specification_graph/view.jinja", view=view
        )
        output_path = os.path.join(
            project_config.export_output_html_root, NODES_DATA_FILENAME
        )
        # The screen may read the file at any moment: it gets the old file
        # or the new one, never a part.
        temporary_path = output_path + ".tmp"
        with open(temporary_path, "w", encoding="utf8") as output_file:
            json.dump({"version": version, "html": str(content)}, output_file)
        os.replace(temporary_path, output_path)


def _render_nodes_view(graph: Graph, debug: bool) -> SpecificationGraphView:
    # Imported here: the screen module imports this module.
    from strictdoc.features.specification_graph.screen import (  # noqa: PLC0415
        render_view,
    )

    return render_view(
        view_id=NODES_VIEW_ID,
        label=NODES_VIEW_LABEL,
        debug=debug,
        build_graph=lambda: graph,
    )


NODES_VIEW_BUILDER = _NodesViewBuilder()
