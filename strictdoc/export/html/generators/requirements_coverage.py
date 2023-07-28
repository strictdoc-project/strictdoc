from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class RequirementsCoverageHTMLGenerator:
    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ):
        assert isinstance(html_templates, HTMLTemplates)

        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        output = ""

        template = html_templates.jinja_environment().get_template(
            "screens/requirements_coverage/index.jinja"
        )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            html_templates,
            project_config,
            None,
        )
        output += template.render(
            project_config=project_config,
            traceability_index=traceability_index,
            documents_iterator=document_tree_iterator.iterator(),
            link_renderer=link_renderer,
            renderer=markup_renderer,
            document_type=DocumentType.deeptrace(),
            strictdoc_version=__version__,
            standalone=False,
        )

        return output
