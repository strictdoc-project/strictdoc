from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class DocumentTableHTMLGenerator:
    @staticmethod
    def export(  # pylint: disable=too-many-arguments
        project_config: ProjectConfig,
        document,
        traceability_index,
        markup_renderer,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
    ):
        output = ""

        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        template = html_templates.jinja_environment().get_template(
            "screens/document/table/index.jinja"
        )

        document_iterator = traceability_index.get_document_iterator(document)

        output += template.render(
            project_config=project_config,
            document=document,
            traceability_index=traceability_index,
            renderer=markup_renderer,
            link_renderer=link_renderer,
            document_type=DocumentType.table(),
            standalone=False,
            document_iterator=document_iterator,
            strictdoc_version=__version__,
            document_tree=traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
        )

        return output
