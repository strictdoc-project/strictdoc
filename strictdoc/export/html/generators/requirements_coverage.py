from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html.html_templates import HTMLTemplates


class RequirementsCoverageHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        config: ExportCommandConfig,
        traceability_index: TraceabilityIndex,
        link_renderer,
    ):
        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        output = ""

        template = RequirementsCoverageHTMLGenerator.env.get_template(
            "requirements_coverage/requirements_coverage.jinja.html"
        )

        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            None,
        )
        output += template.render(
            config=config,
            traceability_index=traceability_index,
            documents_iterator=document_tree_iterator.iterator(),
            link_renderer=link_renderer,
            renderer=markup_renderer,
            static_path="_static",
            document_type=DocumentType.deeptrace(),
        )

        return output
