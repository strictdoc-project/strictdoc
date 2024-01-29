from typing import List, Optional

from strictdoc.backend.sdoc.models.type_system import (
    ViewElementHiddenTag,
    ViewElementTags,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described()
class ViewElement:
    def __init__(
        self,
        parent,
        view_id: str,
        tags: List[ViewElementTags],
        hidden_tags: Optional[List[ViewElementHiddenTag]],
        name: Optional[str],
    ):
        self.parent = parent
        self.view_id: str = view_id
        self.tags: List[ViewElementTags] = tags
        self.hidden_tags: Optional[List[ViewElementHiddenTag]] = hidden_tags
        self.name: Optional[str] = name


class DocumentView:
    def __init__(self, parent, views: List[ViewElement]):
        self.parent = parent
        self.views: List[ViewElement] = views
