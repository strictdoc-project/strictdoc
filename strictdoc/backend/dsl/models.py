class Document(object):
    def __init__(self, name, sections=[]):
        self.name = name
        self.sections = sections

    def __str__(self):
        return "Document: <name: {}, contents: {}>".format(
            self.name, self.sections
        )

    def __repr__(self):
        return self.__str__()


class ReqComment(object):
    def __init__(self, parent, comment):
        self.parent = parent
        self.comment = comment

    def __str__(self):
        return "Comment: <{}>".format(
            self.comment
        )

    def __repr__(self):
        return self.__str__()


class Section(object):
    def __init__(self, parent, level, title, section_contents):
        self.parent = parent
        self.level = level
        self.title = title
        self.section_contents = section_contents

    def __str__(self):
        return "Section: <level: {}, title: {}, section_contents: {}>".format(
            self.level, self.title, self.section_contents
        )

    def __repr__(self):
        return self.__str__()


class Requirement(object):
    def __init__(self, parent, statement, uid, status, references, title, body=[], comments=[]):
        assert parent
        assert statement

        self.parent = parent
        self.references = references
        self.title = title
        self.uid = uid.strip()
        self.status = status
        self.statement = statement
        self.body = body
        self.comments = comments

    def __str__(self):
        return "Requirement: <uid: {}, title_or_none: {}, statement: {}, comments: {}>".format(
            self.uid, self.title, self.statement, self.comments
        )

    def __repr__(self):
        return self.__str__()


# class Body(object):
#     def __init__(self, parent, body_content=[]):
#         self.parent = parent
#         self.body_content = body_content
#
#     def __str__(self):
#         return "Body: <{}>".format(
#             self.body_content
#         )
#
#     def __repr__(self):
#         return self.__str__()


class Body(object):
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content.strip()

    def __str__(self):
        return "Body: <{}>".format(
            self.content
        )

    def __repr__(self):
        return self.__str__()


class Reference(object):
    def __init__(self, parent, file_type, path):
        self.parent = parent
        self.file_type = file_type
        self.path = path.strip()

    def __str__(self):
        return "File: <{}>".format(
            self.path
        )

    def __repr__(self):
        return self.__str__()
