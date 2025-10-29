"""
Generate HTML graphs with documentation tree information.

Uses Plotly.js for generating tree map graphs.

@relation(SDOC-SRS-157, scope=file)
"""

import os
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.io as pio

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.tree_map.helpers import (
    get_color,
    split_into_max_n_lines,
)
from strictdoc.features.tree_map.view_object import TreeMapViewObject
from strictdoc.helpers.timing import timing_decorator


@dataclass
class GraphSection:
    title: str
    description: str
    graph_content: str

    def get_html(self) -> str:
        return f"""
<h2 class="section">{self.title}</h2>

<p class="section_description">{self.description}</p>

{self.graph_content}
"""


@dataclass
class NodeStats:
    child_nodes: int = 0
    child_nodes_with_links_to_source_files: int = 0
    child_nodes_with_links_to_test_files: int = 0

    @staticmethod
    def create_child_node_without_stats() -> "NodeStats":
        return NodeStats(
            child_nodes=0,
            child_nodes_with_links_to_source_files=0,
            child_nodes_with_links_to_test_files=0,
        )

    def add_child_stats(self, child_node_stats: "NodeStats") -> None:
        self.child_nodes += child_node_stats.child_nodes
        self.child_nodes_with_links_to_source_files += (
            child_node_stats.child_nodes_with_links_to_source_files
        )
        self.child_nodes_with_links_to_test_files += (
            child_node_stats.child_nodes_with_links_to_test_files
        )

    def get_code_coverage_ratio(self) -> float:
        covered = self.child_nodes_with_links_to_source_files
        total = self.child_nodes
        ratio = max(0.0, min(1.0, covered / total))
        return ratio

    def get_test_coverage_ratio(self) -> float:
        covered = self.child_nodes_with_links_to_test_files
        total = self.child_nodes
        ratio = max(0.0, min(1.0, covered / total))
        return ratio


class PlotlyDataFrameColumn:
    COLOR_SOURCE = "_COLOR_SOURCE"
    COLOR_TEST = "_COLOR_TEST"
    LEVEL = "_LEVEL"
    PARENT_MID = "_PARENT_MID"
    WEIGHT = "_WEIGHT"
    IS_NORMATIVE = "_IS_NORMATIVE"


class TreeMapGenerator:
    @staticmethod
    @timing_decorator("Export tree map visualizations")
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        data = []

        for document_ in traceability_index.document_tree.document_list:
            assert document_.meta is not None
            if traceability_index.file_dependency_manager.must_generate(
                document_.meta.output_document_full_path
            ):
                break
        else:
            print(  # noqa: T201
                "All documents are up-to-date. "
                "Skipping the generation of the tree map screen."
            )
            return

        documents_with_requirements = set()

        map_node_to_coverage: Dict[
            Union[SDocNode, SDocDocument], NodeStats
        ] = {}

        def get_node_stats(
            node_: Union[SDocNode, SDocDocument],
        ) -> NodeStats:
            if node_ in map_node_to_coverage:
                return map_node_to_coverage[node_]

            if not node_.section_contents:
                if (
                    not isinstance(node_, SDocNode)
                    or node_.node_type in ("TEXT", "SECTION")
                    or node_.reserved_uid is None
                ):
                    return NodeStats.create_child_node_without_stats()

                node_stats = NodeStats(child_nodes=1)

                children = traceability_index.get_children_requirements(node_)

                has_children_all_covered_with_code = len(children) > 0
                has_children_all_covered_with_test = len(children) > 0

                for child_node_ in children:
                    child_node_stats = get_node_stats(child_node_)
                    if (
                        child_node_stats.child_nodes_with_links_to_source_files
                        == 0
                    ):
                        has_children_all_covered_with_code = False

                    if (
                        child_node_stats.child_nodes_with_links_to_test_files
                        == 0
                    ):
                        has_children_all_covered_with_test = False

                node_stats.child_nodes_with_links_to_source_files = int(
                    has_children_all_covered_with_code
                )
                node_stats.child_nodes_with_links_to_test_files = int(
                    has_children_all_covered_with_test
                )

                source_files = traceability_index.get_file_traceability_index().get_requirement_file_links(
                    node_
                )
                for source_file_tuple_ in source_files:
                    if "tests/" in source_file_tuple_[0]:
                        node_stats.child_nodes_with_links_to_test_files = 1
                    else:
                        node_stats.child_nodes_with_links_to_source_files = 1

                return node_stats

            this_node_counters = NodeStats()

            for sub_node_ in node_.section_contents:
                if not isinstance(sub_node_, SDocNode):
                    continue
                if sub_node_.node_type == "TEXT":
                    continue
                sub_node_stats = get_node_stats(sub_node_)
                map_node_to_coverage[sub_node_] = sub_node_stats

                this_node_counters.add_child_stats(sub_node_stats)

            return this_node_counters

        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            map_node_to_coverage[document_] = get_node_stats(document_)

            document_iterator = SDocDocumentIterator(document_)
            for node_, _ in document_iterator.all_content(
                print_fragments=False
            ):
                if not isinstance(node_, SDocNode):
                    continue

                if node_.node_type not in ("TEXT", "SECTION"):
                    documents_with_requirements.add(document_)
                map_node_to_coverage[node_] = get_node_stats(node_)

        root_node_title = project_config.project_title

        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            color_code = "white"
            color_test = "white"

            if document_ in documents_with_requirements:
                node_stats = get_node_stats(document_)
                if node_stats.child_nodes > 0:
                    color_code = get_color(node_stats.get_code_coverage_ratio())
                    color_test = get_color(node_stats.get_test_coverage_ratio())

            title = document_.reserved_title
            title += " (" + str(document_.get_total_size()) + ")"

            data.append(
                {
                    PlotlyDataFrameColumn.WEIGHT: document_.get_total_size()
                    if document_.get_total_size() > 10
                    else 10,
                    "MID": document_.reserved_mid,
                    "UID": document_.reserved_uid
                    if document_.reserved_uid is not None
                    else "",
                    "TITLE": title,
                    "STATEMENT": " (" + str(document_.get_total_size()) + ")",
                    PlotlyDataFrameColumn.PARENT_MID: root_node_title,
                    PlotlyDataFrameColumn.COLOR_SOURCE: color_code,
                    PlotlyDataFrameColumn.COLOR_TEST: color_test,
                    PlotlyDataFrameColumn.IS_NORMATIVE: document_
                    in documents_with_requirements,
                },
            )

            document_iterator = SDocDocumentIterator(document_)
            for node, context_ in document_iterator.all_content(
                print_fragments=False
            ):
                if not isinstance(node, SDocNode):
                    continue

                is_normative = node.node_type == "REQUIREMENT" or (
                    node.node_type == "SECTION" and node.ng_has_requirements
                )

                parent_mid = node.parent.reserved_mid

                if parent_mid == "c2d4542d5f1741c88dfcb4f68ad7dcbd":
                    assert not is_normative, node

                if node.reserved_title is not None:
                    title = node.reserved_title
                else:
                    title = "[TEXT] node"

                if (
                    node.section_contents is not None
                    and len(node.section_contents) > 0
                ):
                    title += " (" + str(node.get_total_size()) + ")"

                statement = (
                    node.reserved_statement
                    if node.reserved_statement is not None
                    else ""
                )
                if len(statement) > 120:
                    statement = statement[:120] + "..."

                color_code = "white"
                color_test = "white"

                if (
                    node.node_type != "TEXT"
                    and document_ in documents_with_requirements
                ):
                    if document_ in documents_with_requirements:
                        node_stats = get_node_stats(node)
                        if node_stats.child_nodes > 0:
                            color_code = get_color(
                                node_stats.get_code_coverage_ratio()
                            )
                            color_test = get_color(
                                node_stats.get_test_coverage_ratio()
                            )

                data.append(
                    {
                        PlotlyDataFrameColumn.WEIGHT: node.get_total_size()
                        if node.get_total_size() > 10
                        else 10,
                        "MID": node.reserved_mid,
                        "UID": node.reserved_uid
                        if node.reserved_uid is not None
                        else "",
                        "TITLE": title,
                        "STATEMENT": statement,
                        PlotlyDataFrameColumn.PARENT_MID: parent_mid,
                        PlotlyDataFrameColumn.LEVEL: context_.get_level(),
                        PlotlyDataFrameColumn.COLOR_SOURCE: color_code,
                        PlotlyDataFrameColumn.COLOR_TEST: color_test,
                        PlotlyDataFrameColumn.IS_NORMATIVE: is_normative,
                    },
                )

        root_row = {
            "MID": root_node_title,
            "UID": "",
            "TITLE": root_node_title,
            "STATEMENT": "",
            PlotlyDataFrameColumn.WEIGHT: 0,
            "_SHORT_LABEL": "",
            "_LONG_LABEL": "",
            "_IS_LEAF": False,
            PlotlyDataFrameColumn.PARENT_MID: "",
            PlotlyDataFrameColumn.LEVEL: 0,
            PlotlyDataFrameColumn.COLOR_SOURCE: "white",
            PlotlyDataFrameColumn.COLOR_TEST: "white",
            PlotlyDataFrameColumn.IS_NORMATIVE: True,
        }
        data.append(root_row)

        df = pd.DataFrame(data)

        df["_IS_LEAF"] = ~df["MID"].isin(df[PlotlyDataFrameColumn.PARENT_MID])

        def short_label(row_: Any) -> Any:
            title = row_["TITLE"]
            # FIXME: Move this reasoning to JS based on zoom depth.
            if len(title) > 20:
                title = split_into_max_n_lines(title, max_lines=2)
            return title

        df["_SHORT_LABEL"] = df.apply(short_label, axis=1)

        def wrap_text(text: Optional[str], width: int = 80) -> str:
            if not text:
                return ""
            return "<br>".join(textwrap.wrap(text, width=width))

        def long_or_short_label(row_: Any) -> Any:
            if row_["_IS_LEAF"] and row_["STATEMENT"]:
                statement = row_["STATEMENT"]
                statement = statement.replace("\n", "<br>")
                statement = wrap_text(statement, 80)

                return f"<b>{row_['TITLE']}</b><br><br>{statement}"
            title = row_["TITLE"]
            if len(title) > 30:
                title = "<br>".join(title.split(" "))
            return title

        df["_LONG_LABEL"] = df.apply(long_or_short_label, axis=1)

        def hover_(row_: Any) -> Any:
            mid = row_["MID"]
            uid = row_["UID"]
            title = row_["TITLE"]
            statement = row_["STATEMENT"]

            return f"""\
<b>MID</b>: {mid}<br>
<b>UID</b>: {uid}<br>
<b>TITLE</b>: {title}<br>
<b>STATEMENT</b>: {statement}<br>
            """

        df["_HOVER"] = df.apply(hover_, axis=1)

        parts: List[GraphSection] = []

        # FIGURE: Document tree map.
        fig = px.treemap(
            df,
            names="_SHORT_LABEL",
            ids="MID",
            parents=PlotlyDataFrameColumn.PARENT_MID,
            values=PlotlyDataFrameColumn.WEIGHT,
            custom_data=[
                "_HOVER",
                "_SHORT_LABEL",
                "_LONG_LABEL",
                "_IS_LEAF",
                PlotlyDataFrameColumn.LEVEL,
            ],
        )
        fig.update_layout(
            margin={"t": 25, "l": 25, "r": 25, "b": 25},
            height=800,
        )
        fig.update_traces(
            root_color="lightgray",
            marker={
                "colors": ["white"] * len(df),
            },
            marker_line_color="#ddd",
            marker_line_width=1,
            textposition="middle center",
            texttemplate="%{customdata[0]}",
            hoverinfo="skip",
            hovertemplate=None,
        )
        parts.append(
            GraphSection(
                title="Document tree map",
                description="""\
This is a general representation of a document tree. All nodes are included,
both normative (e.g., REQUIREMENT) and non-normative (e.g., TEXT). The numbers
indicate how many nodes each section or node contains.
""",
                graph_content=pio.to_html(
                    fig,
                    full_html=False,
                    include_plotlyjs=True,
                ),
            )
        )

        # FIGURE: Document tree: Requirements coverage with source.
        df = df[df[PlotlyDataFrameColumn.IS_NORMATIVE]]
        fig = px.treemap(
            df,
            names="_SHORT_LABEL",
            ids="MID",
            parents=PlotlyDataFrameColumn.PARENT_MID,
            values=PlotlyDataFrameColumn.WEIGHT,
            custom_data=[
                "_HOVER",
                "_SHORT_LABEL",
                "_LONG_LABEL",
                "_IS_LEAF",
                PlotlyDataFrameColumn.LEVEL,
            ],
        )
        fig.update_layout(
            margin={"t": 25, "l": 25, "r": 25, "b": 25},
            height=800,
        )
        fig.update_traces(
            root_color="lightgray",
            marker={
                "colors": df[PlotlyDataFrameColumn.COLOR_SOURCE],
            },
            marker_line_color="#ddd",
            marker_line_width=1,
            textposition="middle center",
            texttemplate="%{customdata[0]}",
            hoverinfo="skip",
            hovertemplate=None,
        )
        parts.append(
            GraphSection(
                title="Requirements coverage with source",
                description="""\
This graph shows which requirements are covered by at least one source file.
A requirement is also considered covered if it has child requirements that are
themselves covered by source files.

<ul>
  <li>
    <span style="background-color: #AAFFAA;">Green</span> –
    Requirement/section is fully covered with one or more source file.
  </li>
  <li>
    <span style="background-color: #FFFFAA;">Yellow</span> –
    Section is partially covered with one or more source file.
  </li>
  <li>
    <span style="background-color: #FFAAAA;">Red</span> –
        Requirement/section is not covered by any source files.
  </li>
</ul>
""",
                graph_content=pio.to_html(
                    fig,
                    full_html=False,
                    include_plotlyjs=False,
                ),
            )
        )

        # FIGURE: Document tree: Requirements coverage with test.
        fig = deepcopy(fig)
        fig.update_traces(
            root_color="lightgray",
            marker={
                "colors": df[PlotlyDataFrameColumn.COLOR_TEST],
            },
            marker_line_color="#ddd",
            marker_line_width=1,
            textposition="middle center",
            texttemplate="%{customdata[0]}",
            hoverinfo="skip",
            hovertemplate=None,
        )
        parts.append(
            GraphSection(
                title="Requirements coverage with test",
                description="""\
This graph shows which requirements are covered by at least one test.
A requirement is also considered covered if it has child requirements that are
themselves covered by tests. A source file is considered a test file if its path
contains "tests/".

<ul>
  <li>
    <span style="background-color: #AAFFAA;">Green</span> –
    Requirement/section is fully covered with one or more tests.
  </li>
  <li>
    <span style="background-color: #FFFFAA;">Yellow</span> –
    Section is partially covered with one or more test.
  </li>
  <li>
    <span style="background-color: #FFAAAA;">Red</span> –
        Requirement/section is not covered with by any tests.
  </li>
</ul>
""",
                graph_content=pio.to_html(
                    fig,
                    full_html=False,
                    include_plotlyjs=False,
                ),
            )
        )

        body = "".join(part_.get_html() for part_ in parts)

        view_object = TreeMapViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            body=body,
        )
        html = view_object.render_screen(html_templates.jinja_environment())

        output_html = os.path.join(
            project_config.export_output_html_root,
            "tree_map.html",
        )

        with open(output_html, "w", encoding="utf-8") as file_:
            file_.write(html)
