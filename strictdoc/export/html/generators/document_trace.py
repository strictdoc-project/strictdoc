from jinja2 import Environment, PackageLoader


class DocumentTraceHTMLGenerator:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document, traceability_index, markup_renderer, link_renderer):
        output = ""

        template = DocumentTraceHTMLGenerator.env.get_template(
            'single_document_traceability/document.jinja.html'
        )

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  renderer=markup_renderer,
                                  link_renderer=link_renderer)

        return output
