from jinja2 import Environment, PackageLoader

from strictdoc.helpers.hyperlinks import string_to_anchor_id


class SingleDocumentTraceabilityHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document, traceability_index, renderer):
        output = ""

        template = SingleDocumentTraceabilityHTMLExport.env.get_template('single_document_traceability/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id,
                                  renderer=renderer)

        return output
