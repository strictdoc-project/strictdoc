import os
from pathlib import Path

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DoxygenGenerator:
    def __init__(self, project_config: ProjectConfig):
        self.project_config: ProjectConfig = project_config

    def export(
        self,
        *,
        traceability_index: TraceabilityIndex,
        path_to_output_dir: str,
    ) -> None:
        Path(path_to_output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(path_to_output_dir, "strictdoc.tag")

        link_renderer = LinkRenderer(
            root_path="NOT_RELEVANT", static_path="NOT_RELEVANT"
        )

        def template_node(node_uid: str, path_to_html: str) -> str:
            return f"""\
  <compound kind="file">
    <name>{node_uid}</name>
    <filename>html/{path_to_html}</filename>
  </compound>
"""

        template_all_nodes = ""

        assert traceability_index.document_tree is not None
        assert traceability_index.document_tree.document_list is not None

        document_: SDocDocument
        for document_ in traceability_index.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document_)

            for node in document_iterator.all_content(
                print_fragments=False,
                print_fragments_from_files=False,
            ):
                if isinstance(node, SDocNode) and node.reserved_uid is not None:
                    path_to_html = link_renderer.render_node_doxygen_link(node)
                    template_all_nodes += template_node(
                        node.reserved_uid, path_to_html
                    )

        template_xml = f"""\
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<tagfile doxygen_version="1.9.8">
{template_all_nodes.rstrip()}
</tagfile>
"""
        with open(output_path, "w", encoding="utf8") as file:
            file.write(template_xml)
