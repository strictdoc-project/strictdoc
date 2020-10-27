from strictdoc.core.document_meta import DocumentMeta


class Document(object):
    def __init__(self, name, section_contents=[]):
        self.name = name
        self.section_contents = section_contents

        self.ng_sections = []
        self.ng_level = 0
        self.meta = None

    def __str__(self):
        return "Document: <name: {}, section_contents: {}>".format(
            self.name, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta


class ReqComment(object):
    def __init__(self, parent, comment_single, comment_multiline):
        self.parent = parent
        self.comment_single = comment_single
        self.comment_multiline = comment_multiline

    def __str__(self):
        return "Comment: <>".format()

    def __repr__(self):
        return self.__str__()

    def get_comment(self):
        comment = self.comment_single if self.comment_single else self.comment_multiline
        return comment


class Section(object):
    def __init__(self, parent, level, title, section_contents):
        self.parent = parent
        self.level = int(level)
        self.title = title
        self.section_contents = section_contents

        self.ng_level = self.level
        self.ng_sections = []
        self.export_title = None

    def __str__(self):
        return "Section: <level: {}, title: {}, section_contents: {}>".format(
            self.level, self.title, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return True


class Requirement(object):
    def __init__(self,
                 parent,
                 statement,
                 statement_multiline,
                 uid,
                 status,
                 tags,
                 references,
                 title,
                 body,
                 comments,
                 requirements=None):
        assert parent

        self.parent = parent
        self.uid = uid.strip()
        self.status = status
        self.tags = tags
        self.references: [Reference] = references
        self.title = title
        self.statement = statement
        self.statement_multiline = statement_multiline
        self.body = body
        self.comments = comments
        self.requirements = requirements

        # TODO: Is it worth to move this to dedicated Presenter* classes to
        # keep this class textx-only?
        self.ng_level = None
        self.export_title = None

    def __str__(self):
        return "{}: <ng_level: {}, uid: {}, title_or_none: {}, statement: {}>".format(
            self.__class__.__name__,
            self.ng_level,
            self.uid, self.title, self.statement
        )

    def __repr__(self):
        return self.__str__()

    @property
    def has_meta(self):
        return (
            self.uid is not None or
            (self.tags is not None and len(self.tags) > 0) or
            self.status is not None
        )

    @property
    def is_requirement(self):
        return True

    @property
    def is_section(self):
        return False

    @property
    def is_composite_requirement(self):
        return False

    def statement_or_multiline_statement(self):
        if self.statement:
            return self.statement
        elif self.statement_multiline:
            return self.statement_multiline
        raise NotImplementedError

    def statement_as_html_blocks(self):
        if self.statement:
            return [self.statement]
        elif self.statement_multiline:
            return self.statement_multiline.split('\n\n')


class CompositeRequirement(Requirement):
    def __init__(self, parent, **fields):
        super(CompositeRequirement, self).__init__(parent, **fields)
        self.ng_sections = []
        self.export_title = None

    @property
    def is_composite_requirement(self):
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


class FreeText:
    def __init__(self, parent, text):
        self.parent = parent
        self.text = text
        self.ng_level = None

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False

    @property
    def is_free_text(self):
        return True

    def text_as_paragraphs(self):
        return self.text.split('\n\n')
