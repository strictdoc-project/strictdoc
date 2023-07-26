from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DocumentTreeHTMLGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ):
        assert isinstance(html_templates, HTMLTemplates)

        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        template = html_templates.jinja_environment().get_template(
            "screens/project_index/index.jinja"
        )
        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )

        output = template.render(
            project_config=project_config,
            document_tree=traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            strictdoc_version=__version__,
            standalone=False,
        )

        return output
