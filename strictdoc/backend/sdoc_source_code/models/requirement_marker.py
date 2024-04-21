# mypy: disable-error-code="no-untyped-def"
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Req:
    def __init__(self, parent, uid: str):
        assert isinstance(uid, str)
        assert len(uid) > 0

        self.parent = parent
        self.uid: str = uid

        self.ng_source_line = None
        self.ng_source_column = None
