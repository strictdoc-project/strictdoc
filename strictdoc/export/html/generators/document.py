from jinja2 import Environment, PackageLoader


class DocumentHTMLGenerator:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates')
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index,
               markup_renderer,
               link_renderer):
        output = ""

        template = DocumentHTMLGenerator.env.get_template('single_document/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  link_renderer=link_renderer,
                                  renderer=markup_renderer)

        return output
