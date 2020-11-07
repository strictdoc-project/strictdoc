from strictdoc.backend.dsl.models.reference import Reference


class RequirementContext(object):
    def __init__(self):
        self.title_number_string = None


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

        # TODO: Why textX creates empty uid when the sdoc doesn't declare the
        # UID field?
        self.uid = uid.strip() if (isinstance(uid, str) and len(uid) > 0) else None
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
        self.context = RequirementContext()

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

    def get_statement_single_or_multiline(self):
        if self.statement:
            return self.statement
        elif self.statement_multiline:
            return self.statement_multiline
        raise NotImplementedError


class CompositeRequirement(Requirement):
    def __init__(self, parent, **fields):
        super(CompositeRequirement, self).__init__(parent, **fields)
        self.ng_sections = []

    @property
    def is_composite_requirement(self):
        return True


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


class RequirementComment(object):
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
