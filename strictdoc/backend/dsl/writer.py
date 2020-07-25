from strictdoc.backend.dsl.models import Document, Requirement, ReqComment, Section


class SDWriter:
    def __init__(self):
        pass

    def write(self, document):
        output = ""

        output += "<DOCUMENT>"
        output += "\n"

        if len(document.sections) > 0:
            output += "\n"
        for section in document.sections:
            output += "<SECTION>"
            output += "\n"
            output += "LEVEL: "
            output += str(section.level)

            output += "\n"

            for section_content in section.section_contents:
                output += "\n"
                if isinstance(section_content, Requirement):
                    output += "<REQUIREMENT>"
                    output += "\n"

                    if section_content.title:
                        output += "TITLE: "
                        output += section_content.title
                        output += "\n"

                    output += "STATEMENT: "
                    output += section_content.statement
                    output += "\n"

                    for comment in section_content.comments:
                        output += "COMMENT: "
                        output += comment.comment
                        output += "\n"

        return output
