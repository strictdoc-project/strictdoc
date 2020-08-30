import os

from jinja2 import Template, Environment, PackageLoader, select_autoescape

from strictdoc.backend.dsl.models import Requirement


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class DocumentTreeHTMLExport:
    OFFSET = 12

    @staticmethod
    def export(document_tree):
        output = ""

        output += "<h1>Document tree</h1>"

        output += "<div>"
        task_list = [document_tree.file_tree]
        while task_list:
            current_file_tree = task_list.pop(0)

            folder_name = os.path.basename(os.path.normpath(current_file_tree.root_path))

            output += "<div>"
            output += "&nbsp;" * current_file_tree.level * DocumentTreeHTMLExport.OFFSET
            output += "{}/".format(folder_name)
            output += "</div>"

            for doc_file in current_file_tree.files:
                doc_full_path = os.path.join(current_file_tree.root_path, doc_file)

                document = document_tree.document_map[doc_full_path]
                document_path = '{}.html'.format(document.name)
                output += "<div>"
                output += "&nbsp;" * (current_file_tree.level + 1) * DocumentTreeHTMLExport.OFFSET
                output += '<a href="{}">{}</a>'.format(document_path, document.name)
                output += "</div>"

            task_list.extend(current_file_tree.subfolder_trees)

        output += "</div>"

        # for document in document_tree.document_list:
        #     print("processing {}".format(document.name))
        #     output += "<div>"
        #     output += document.name
        #     output += "</div>"

        return output


class SingleDocumentHTMLExport:
    env = Environment(
        loader=PackageLoader('strictdoc', 'export/html/templates'),
        # autoescape=select_autoescape(['html', 'xml'])
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(document):
        print("doc: {}, number of sections: {}".format(document.name, len(document.sections)))
        output = ""

        template = SingleDocumentHTMLExport.env.get_template('single_document/document.jinja.html')

        output += template.render(document=document)

        return output
