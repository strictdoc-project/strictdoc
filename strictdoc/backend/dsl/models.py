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
    def __init__(self, parent, title, statement, comments):
        assert parent
        assert statement

        self.parent = parent
        self.title = title
        self.statement = statement
        self.comments = comments

    def __str__(self):
        return "Requirement: <title_or_none: {}, statement: {}, comments: {}>".format(
            self.title, self.statement, self.comments
        )

    def __repr__(self):
        return self.__str__()
