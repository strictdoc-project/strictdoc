"""
Generate the HTML "Project graph" screen.

Exports the project's document tree (documents, sections, requirement-like
nodes) as a JSON node/link graph, rendered client-side with 3d-force-graph.
"""

import os
from typing import Any, Dict, List, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.features.project_graph.view_object import (
    ProjectGraphViewObject,
)
from strictdoc.helpers.timing import timing_decorator


class ProjectGraphNodeType:
    DOCUMENT = "document"
    SECTION = "section"
    REQUIREMENT = "requirement"


class ProjectGraphLinkKind:
    CONTAINMENT = "containment"
    RELATION = "relation"


def _node_type(node_: Union[SDocDocument, SDocNode]) -> str:
    if isinstance(node_, SDocDocument):
        return ProjectGraphNodeType.DOCUMENT
    if node_.node_type == "SECTION":
        return ProjectGraphNodeType.SECTION
    return ProjectGraphNodeType.REQUIREMENT


def _node_label(node_: Union[SDocDocument, SDocNode]) -> str:
    title = node_.reserved_title if node_.reserved_title is not None else ""
    uid = getattr(node_, "reserved_uid", None)
    if uid:
        return f"{title} ({uid})"
    return title


class ProjectGraphGenerator:
    @staticmethod
    @timing_decorator("Export project graph screen")
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        nodes: List[Dict[str, Any]] = []
        links: List[Dict[str, str]] = []

        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            nodes.append(
                {
                    "id": document_.reserved_mid,
                    "name": _node_label(document_),
                    "type": ProjectGraphNodeType.DOCUMENT,
                }
            )

            document_iterator = SDocDocumentIterator(document_)
            for node_, _ in document_iterator.all_content(
                print_fragments=False
            ):
                if not isinstance(node_, SDocNode):
                    continue
                if node_.node_type == "TEXT":
                    continue

                nodes.append(
                    {
                        "id": node_.reserved_mid,
                        "name": _node_label(node_),
                        "type": _node_type(node_),
                    }
                )
                links.append(
                    {
                        "source": node_.parent.reserved_mid,
                        "target": node_.reserved_mid,
                        "kind": ProjectGraphLinkKind.CONTAINMENT,
                    }
                )

                if node_.reserved_uid is not None:
                    for parent_node_ in traceability_index.get_parent_requirements(
                        node_
                    ):
                        links.append(
                            {
                                "source": parent_node_.reserved_mid,
                                "target": node_.reserved_mid,
                                "kind": ProjectGraphLinkKind.RELATION,
                            }
                        )

        graph_data = {"nodes": nodes, "links": links}

        view_object = ProjectGraphViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            graph_data=graph_data,
        )
        html = view_object.render_screen(html_templates.jinja_environment())

        output_html = os.path.join(
            project_config.export_output_html_root,
            "project_graph.html",
        )

        with open(output_html, "w", encoding="utf-8") as file_:
            file_.write(html)
