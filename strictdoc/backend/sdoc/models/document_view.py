# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import List, Optional

from strictdoc.helpers.auto_described import auto_described


@auto_described
class ViewElementField:
    def __init__(self, parent, name: str, placement: Optional[str]):
        self.parent = parent
        self.name: str = name
        self.placement: Optional[str] = placement


@auto_described
class ViewElementTags:
    def __init__(
        self, parent, object_type: str, visible_fields: List[ViewElementField]
    ):
        self.parent = parent
        self.object_type: str = object_type
        self.visible_fields: List[ViewElementField] = visible_fields


@auto_described
class ViewElementHiddenTag:
    def __init__(self, parent, hidden_tag: str):
        self.parent = parent
        self.hidden_tag: str = hidden_tag


class NullViewElement:
    def includes_field(
        self,
        node_type: str,  # noqa: ARG002
        field_name: str,  # noqa: ARG002
    ) -> bool:
        return True


@auto_described()
class ViewElement(NullViewElement):
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

    def includes_field(self, node_type: str, field_name: str) -> bool:
        for tag_ in self.tags:
            if tag_.object_type == node_type:
                field_: ViewElementField
                for field_ in tag_.visible_fields:
                    if field_.name == field_name:
                        return True
                break
        return False


@auto_described()
class DefaultViewElement(ViewElement):
    """
    FIXME: It is not great to provide a default implementation this way but it
           works fine for now.
    """

    def includes_field(self, node_type: str, field_name: str) -> bool:  # noqa: ARG002
        return True


@auto_described()
class DocumentView:
    def __init__(self, parent, views: List[ViewElement]):
        self.parent = parent
        self.views: List[ViewElement] = views
        self.ng_line_start: int = 0
        self.ng_col_start: int = 0

    @staticmethod
    def create_default(parent) -> "DocumentView":
        return DocumentView(
            parent,
            [
                DefaultViewElement(
                    parent=parent,
                    view_id="NOT_RELEVANT",
                    tags=[],
                    hidden_tags=[],
                    name=None,
                )
            ],
        )

    def get_default_view(self) -> ViewElement:
        return self.views[0]

    def get_current_view(self, view_id: Optional[str]) -> ViewElement:
        if view_id is None:
            return self.get_default_view()
        for view_element_ in self.views:
            if view_element_.view_id == view_id:
                return view_element_
        raise NotImplementedError
