from typing import Any, Optional, Tuple, Type, TypeVar, Union, cast, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")


@overload
def assert_cast(node: Any, node_type: Type[A]) -> A: ...


@overload
def assert_cast(
    node: Any, node_type: Tuple[Type[B], Type[C]]
) -> Union[B, C]: ...


@overload
def assert_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D]]
) -> Union[B, C, D]: ...


@overload
def assert_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D], Type[E]]
) -> Union[B, C, D, E]: ...


@overload
def assert_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D], Type[E], Type[F]]
) -> Union[B, C, D, E, F]: ...


def assert_cast(
    node: Any, node_type: Union[Type[Any], Tuple[Type[Any], ...]]
) -> Any:
    assert isinstance(node, node_type), (node, node_type)
    return cast(Any, node)


@overload
def assert_optional_cast(node: None, node_type: Type[A]) -> None: ...


@overload
def assert_optional_cast(node: Any, node_type: Type[A]) -> A: ...


@overload
def assert_optional_cast(
    node: None, node_type: Tuple[Type[B], Type[C]]
) -> None: ...


@overload
def assert_optional_cast(
    node: Any, node_type: Tuple[Type[B], Type[C]]
) -> Union[B, C]: ...


@overload
def assert_optional_cast(
    node: None, node_type: Tuple[Type[B], Type[C], Type[D]]
) -> None: ...


@overload
def assert_optional_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D]]
) -> Union[B, C, D]: ...


@overload
def assert_optional_cast(
    node: None, node_type: Tuple[Type[B], Type[C], Type[D], Type[E]]
) -> None: ...


@overload
def assert_optional_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D], Type[E]]
) -> Union[B, C, D, E]: ...


@overload
def assert_optional_cast(
    node: None, node_type: Tuple[Type[B], Type[C], Type[D], Type[E], Type[F]]
) -> None: ...


@overload
def assert_optional_cast(
    node: Any, node_type: Tuple[Type[B], Type[C], Type[D], Type[E], Type[F]]
) -> Union[B, C, D, E, F]: ...


def assert_optional_cast(
    node: Any, node_type: Union[Type[Any], Tuple[Type[Any], ...]]
) -> Optional[Any]:
    if node is not None:
        assert isinstance(node, node_type), (node, node_type)
        return cast(Any, node)
    return None
