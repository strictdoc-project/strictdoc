from jinja2 import Environment, PackageLoader

from strictdoc.helpers.hyperlinks import string_to_anchor_id


class DocumentHTMLGenerator:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates')
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index, renderer):
        output = ""

        template = DocumentHTMLGenerator.env.get_template('single_document/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id,
                                  renderer=renderer)

        return output
