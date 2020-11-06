from jinja2 import Environment, PackageLoader


class DocumentDeepTraceHTMLGenerator:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export_deep(document, traceability_index, markup_renderer, link_renderer):
        output = ""

        template = DocumentDeepTraceHTMLGenerator.env.get_template(
            'single_document_traceability_deep/document.jinja.html'
        )

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  renderer=markup_renderer,
                                  link_renderer=link_renderer)

        return output
