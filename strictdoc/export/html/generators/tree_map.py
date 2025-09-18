import sys

import pandas as pd
import plotly.express as px

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import DocumentCachingIterator

"""
TBD
"""

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex


class TreeMapGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
    ) -> None:
        data = [
        ]

        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            data.append(
                {
                    "WEIGHT": document_.get_total_size() if document_.get_total_size() > 10 else 10,
                    "MID": document_.reserved_mid,
                    "Title": document_.reserved_title + " (" + str(document_.get_total_size()) + ")",
                    "ParentMID": None
                },
            )

            document_iterator = DocumentCachingIterator(document_)
            for node, _ in document_iterator.all_content(print_fragments=False):
                if not isinstance(node, SDocNode):
                    continue

                parent_mid = node.parent.reserved_mid

                if node.reserved_title is not None:
                    title = "<br>".join(node.reserved_title.split(" ")) if node.section_contents is None or len(node.section_contents) == 0 else node.reserved_title
                    title += " (" + str(node.get_total_size()) + ")"

                    data.append(
                        {
                            "WEIGHT": node.get_total_size() if node.get_total_size() > 10 else 10,
                            "MID": node.reserved_mid,
                            "Title": title,
                            "Statement": node.reserved_statement if node.reserved_statement is not None else "",
                            "ParentMID": parent_mid
                        },
                    )

        df = pd.DataFrame(data)

        df["Label"] = df["Title"]

        fig = px.treemap(
            df,
            names="Label",
            ids="MID",
            parents="ParentMID",
            values="WEIGHT",
            hover_data=["Statement"]  # seems to have no effect.
        )

        fig.update_traces(root_color="lightgrey")
        fig.update_layout(
            margin=dict(t=25, l=25, r=25, b=25),
            # uniformtext=dict(minsize=10, mode="show")
        )

        fig.write_html("output/treemap.html", full_html=True, include_plotlyjs=True)

        sys.exit(1)
