from strictdoc.backend.dsl.models import Document, Requirement, ReqComment, Section


class SDWriter:
    def __init__(self):
        pass

    def write(self, document):
        output = ""

        output += "[DOCUMENT]"
        output += "\n"

        output += "NAME: "
        output += document.name
        output += "\n"

        if len(document.section_contents) > 0:
            output += "\n"
        for section in document.section_contents:
            output += "[SECTION]"
            output += "\n"
            output += "LEVEL: "
            output += str(section.level)
            output += "\n"
            output += "TITLE: "
            output += str(section.title)

            output += "\n"

            for section_content in section.section_contents:
                output += "\n"
                if isinstance(section_content, Requirement):
                    output += "[REQUIREMENT]"
                    output += "\n"

                    if section_content.uid:
                        output += "UID: "
                        output += section_content.uid
                        output += "\n"

                    if section_content.status:
                        output += "STATUS: "
                        output += section_content.status
                        output += "\n"

                    if section_content.references:
                        output += "REFS:"
                        output += "\n"

                        for reference in section_content.references:
                            output += "- TYPE: "
                            output += reference.ref_type
                            output += "\n"
                            output += "  VALUE: "
                            output += reference.path
                            output += "\n"

                    if section_content.title:
                        output += "TITLE: "
                        output += section_content.title
                        output += "\n"

                    output += "STATEMENT: "
                    output += section_content.statement
                    output += "\n"

                    if section_content.body:
                        output += "BODY: >>>"
                        output += "\n"
                        output += section_content.body.content
                        output += "\n"
                        output += "<<<"
                        output += "\n"

                    for comment in section_content.comments:
                        output += "COMMENT: "
                        output += comment.comment
                        output += "\n"

            output += "\n"
            output += "[/SECTION]"
            output += "\n"

        return output
