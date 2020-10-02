import collections
import os

from jinja2 import Environment, PackageLoader

from strictdoc.core.document_tree import FileTree
from strictdoc.helpers.hyperlinks import string_to_anchor_id


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


def get_traceability_link(document_name):
    return "{} - Traceability.html".format(document_name)


def get_traceability_deep_link(document_name):
    return "{} - Traceability Deep.html".format(document_name)


class DocumentTreeHTMLExport:
    OFFSET = 8

    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree):
        task_list = collections.deque([document_tree.file_tree])
        artefact_list = []

        while task_list:
            file_tree_or_file = task_list.popleft()
            artefact_list.append(file_tree_or_file)
            if isinstance(file_tree_or_file, FileTree):
                task_list.extendleft(reversed(file_tree_or_file.files))
                task_list.extendleft(reversed(file_tree_or_file.subfolder_trees))


        template = SingleDocumentHTMLExport.env.get_template('document_tree/document_tree.jinja.html')
        output = template.render(document_tree=document_tree,
                                 artefact_list=artefact_list,
                                 get_traceability_link=get_traceability_link,
                                 get_traceability_deep_link=get_traceability_deep_link)

        return output


class SingleDocumentHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index):
        print("doc: {}, number of sections: {}".format(document.name, len(document.section_contents)))
        output = ""

        template = SingleDocumentHTMLExport.env.get_template('single_document/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id)

        return output


class SingleDocumentTableHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index):
        print("doc: {}, number of sections: {}".format(document.name, len(document.section_contents)))
        output = ""

        template = SingleDocumentHTMLExport.env.get_template('single_document_table/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id)

        return output


class SingleDocumentTraceabilityHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document_tree, document, traceability_index):
        print("doc: {}, number of sections: {}".format(document.name, len(document.section_contents)))
        output = ""

        template = SingleDocumentHTMLExport.env.get_template('single_document_traceability/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id)

        return output

    @staticmethod
    def export_deep(document_tree, document, traceability_index):
        print("doc: {}, number of sections: {}".format(document.name, len(document.section_contents)))
        output = ""

        template = SingleDocumentHTMLExport.env.get_template('single_document_traceability_deep/document.jinja.html')

        output += template.render(document=document,
                                  traceability_index=traceability_index,
                                  string_to_anchor_id=string_to_anchor_id)

        return output
