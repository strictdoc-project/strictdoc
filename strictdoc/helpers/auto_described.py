# This function could be a separate package but keeping it within the project
# for simplicity.
__version__ = "0.0.1"

from typing import Any, Callable, Optional, Type, TypeVar, Union, overload

T = TypeVar("T", bound=Type[Any])


@overload
def auto_described(cls: T) -> T: ...
@overload
def auto_described(
    cls: None = ..., *, str_and_repr: bool = ...
) -> Callable[[T], T]: ...


# Maybe there is a better way to generate __str__ and __repr__.
# But for now, this solution works good enough:
# https://stackoverflow.com/a/33800620/598057
# https://stackoverflow.com/a/24617244/598057
def auto_described(
    cls: Optional[Any] = None, str_and_repr: bool = True
) -> Union[T, Callable[[T], T]]:
    def configure_class(clz: T) -> T:
        def __str__(self: object) -> str:
            return auto_str(self)

        def __repr__(self: object) -> str:
            return auto_str(self)

        clz.__str__ = __str__  # type: ignore[assignment]
        if str_and_repr:
            clz.__repr__ = __repr__  # type: ignore[assignment]
        return clz

    if cls is not None:
        return configure_class(cls)

    def factory(clz: T) -> T:
        return configure_class(clz)

    return factory


def auto_str(obj: object) -> str:
    items = []

    # This is a rather defensive implementation that prevents auto_str from
    # breaking on the objects with recursive references:
    # Example: A -> B -> A.
    for prop, value in obj.__dict__.items():
        if isinstance(value, list):
            if len(value) == 0:
                item = f"{prop} = []"
            else:
                item = f"{prop} = [{len(value)} elements]"
        elif isinstance(value, dict):
            if len(value) == 0:
                item = f"{prop} = {{}}"
            else:
                item = f"{prop} = {{{len(value)} elements}}"
        elif isinstance(value, set):
            item = f"{prop} = {value.__class__.__name__}({len(value)} elements)"
        elif isinstance(value, str):
            item = f'{prop} = "{value}"'
        elif isinstance(value, bytes):
            item = f"{prop} = {value!r}"
        elif isinstance(value, (int, float, bool)):
            item = f"{prop} = {value}"
        elif isinstance(value, object):
            item = f"{prop} = {value.__class__.__name__}(...)"
        else:
            item = f"{prop} = {value}"

        items.append(item)
    return f"{obj.__class__.__name__}({', '.join(items)})"
