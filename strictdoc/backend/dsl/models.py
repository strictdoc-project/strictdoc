import collections


class Document(object):
    def __init__(self, name, section_contents=[]):
        self.name = name
        self.section_contents = section_contents
        self.path = "<No document path>"

        self.ng_sections = []

    def __str__(self):
        return "Document: <name: {}, section_contents: {}>".format(
            self.name, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    def assign_path(self, path):
        assert isinstance(path, str)
        self.path = path

    def ng_toc_section_iterator(self):
        task_list = collections.deque([self])

        while True:
            current = task_list.popleft()

            task_list.extendleft(reversed(current.ng_sections))

            if not task_list:
                break

            yield task_list[0]

    def ng_section_iterator(self):
        task_list = collections.deque([self])

        while True:
            current = task_list.popleft()

            if isinstance(current, Section) or isinstance(current, Document):
                task_list.extendleft(reversed(current.section_contents))

            if not task_list:
                break

            yield task_list[0]


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

        self.ng_sections = []

    def __str__(self):
        return "Section: <level: {}, title: {}, section_contents: {}>".format(
            self.level, self.title, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False


class Requirement(object):
    def __init__(self,
                 parent,
                 statement,
                 uid,
                 status,
                 tags,
                 references,
                 title,
                 body,
                 comments):
        assert parent

        self.parent = parent
        self.uid = uid.strip()
        self.status = status
        self.tags = tags
        self.references: [Reference] = references
        self.title = title
        self.statement = statement
        self.body = body
        self.comments = comments

    def __str__(self):
        return "Requirement: <uid: {}, title_or_none: {}, statement: {}, comments: {}>".format(
            self.uid, self.title, self.statement, self.comments
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return True


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
    def __init__(self, parent, ref_type, path):
        self.parent = parent
        self.ref_type = ref_type
        self.path = path.strip()

    def __str__(self):
        return "Reference: <ref_type = {}, path = {}>".format(
            self.ref_type, self.path
        )

    def __repr__(self):
        return self.__str__()
