"""
@relation(SDOC-SRS-54, scope=file)
"""

import os

import orjson
from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.git_client import GitClient


class DocumentHTMLGenerator:
    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        markup_renderer: MarkupRenderer,
        link_renderer: LinkRenderer,
        git_client: GitClient,
        html_templates: HTMLTemplates,
    ) -> Markup:
        view_object = DocumentScreenViewObject(
            document_type=DocumentType.DOCUMENT,
            document=document,
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            jinja_environment=html_templates.jinja_environment(),
            git_client=git_client,
        )
        content = view_object.render_screen()

        # Static export has no FastAPI server to serve a chunk on demand, so
        # every non-first chunk is pre-rendered here and delivered to the
        # browser as a .js file (mirrors export_static_html_search_index's
        # window.StrictDoc.* delivery, since fetch()/XHR to a sibling file
        # is blocked under file://). Server mode instead serves chunks from
        # the /fragments/document/{mid}/chunk route on demand - see
        # main_router.py's get_document_chunk.
        if (
            not project_config.is_running_on_server
            and view_object.is_chunked_rendering()
        ):
            DocumentHTMLGenerator._export_static_chunks(view_object)

        return content

    @staticmethod
    def _export_static_chunks(view_object: DocumentScreenViewObject) -> None:
        assert view_object.document.meta is not None
        document_output_folder = (
            view_object.document.meta.output_document_dir_full_path
        )
        for chunk in view_object.document_content_chunks()[1:]:
            chunk_html = (
                view_object.jinja_environment.render_template_as_markup(
                    "screens/document/document/document_chunk.jinja.html",
                    view_object=view_object,
                    chunk_index=chunk.index,
                    from_node=chunk.first_node_mid,
                    count=chunk.size,
                )
            )
            chunk_js_bytes = (
                b"window.StrictDoc = window.StrictDoc || {};\n"
                b"window.StrictDoc.chunks = window.StrictDoc.chunks || {};\n"
                b"window.StrictDoc.chunks["
                + orjson.dumps(view_object.static_chunk_key(chunk))
                + b"] = "
                + orjson.dumps(str(chunk_html))
                + b";\n"
            )
            chunk_out_file = os.path.join(
                document_output_folder,
                view_object.static_chunk_relative_path(chunk),
            )
            with open(chunk_out_file, "wb") as file:
                file.write(chunk_js_bytes)
