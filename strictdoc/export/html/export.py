import os

from jinja2 import Environment, PackageLoader

from strictdoc.helpers.hyperlinks import string_to_anchor_id


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


def get_traceability_link(document_name):
    return "{} - Traceability.html".format(document_name)


def get_traceability_deep_link(document_name):
    return "{} - Traceability Deep.html".format(document_name)


class SingleDocumentTableHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates')
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index, renderer):
        output = ""

        template = SingleDocumentTableHTMLExport.env.get_template('single_document_table/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id,
                                  renderer=renderer)

        return output


class SingleDocumentTraceabilityHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index, renderer):
        output = ""

        template = SingleDocumentTraceabilityHTMLExport.env.get_template('single_document_traceability/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id,
                                  renderer=renderer)

        return output

    @staticmethod
    def export_deep(document_tree, document, traceability_index, renderer):
        output = ""

        template = SingleDocumentTraceabilityHTMLExport.env.get_template('single_document_traceability_deep/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id,
                                  renderer=renderer)

        return output
