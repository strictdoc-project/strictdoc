import os

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

                output += "<div>"
                output += "&nbsp;" * (current_file_tree.level + 1) * DocumentTreeHTMLExport.OFFSET
                output += document.name
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
    @staticmethod
    def export(document):
        output = ""

        output += "<h1>"
        output += document.name
        output += "</h1>"

        output += "\n"

        if len(document.sections) > 0:
            output += "\n"
        for section in document.sections:
            output += "<div>"
            output += "\n"

            output += "<h2>"
            output += str(section.title)
            output += "</h2>"
            output += "\n"

            for section_content in section.section_contents:
                output += "\n"
                if isinstance(section_content, Requirement):
                    output += "<div>"
                    output += "\n"

                    if section_content.uid:
                        output += "<h3>"
                        output += section_content.uid

                        if section_content.title:
                            output += " "
                            output += section_content.title
                            output += "\n"

                        output += "</h3>"
                        output += "\n"

                    if section_content.status:
                        output += "<div>"
                        output += section_content.status
                        output += "</div>"
                        output += "\n"

                    if section_content.references:
                        output += "<h5>Links:</h5>"
                        output += "\n"

                        for reference in section_content.references:
                            output += "<div>"
                            output += "\n"
                            output += "- "
                            output += reference.path
                            output += " ("
                            output += reference.ref_type
                            output += ")"
                            output += "</div>"
                            output += "\n"

                        output += "<br/>"

                    output += "<div>"
                    output += section_content.statement
                    output += "</div>"
                    output += "\n"

                    if section_content.body:
                        output += "<div>"
                        output += "\n"
                        output += section_content.body.content
                        output += "\n"
                        output += "</div>"
                        output += "\n"

                    if len(section_content.comments):
                        output += "<br/>"

                    for comment in section_content.comments:
                        output += "<div>"
                        output += "<b>Comment: </b>"
                        output += comment.comment
                        output += "</div>"
                        output += "\n"

                    output += "</div>"

        return output
