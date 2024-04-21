# mypy: disable-error-code="no-untyped-def"
import itertools
import typing as t

T = t.TypeVar("T")


class OrderedSet(t.MutableSet[T]):
    """A set that preserves insertion order by internally using a dict.

    >>> OrderedSet([1, 2, "foo"])

    Source: https://github.com/bustawin/ordered-set-37
    """

    __slots__ = ("_d",)

    def __init__(self, iterable: t.Optional[t.Iterable[T]] = None):
        self._d = dict.fromkeys(iterable) if iterable else {}

    def add(self, value: T) -> None:
        self._d[value] = None

    def clear(self) -> None:
        self._d.clear()

    def discard(self, value: T) -> None:
        self._d.pop(value, None)

    def __getitem__(self, index) -> T:
        try:
            return next(itertools.islice(self._d, index, index + 1))
        except StopIteration:
            raise IndexError(f"index {index} out of range") from None

    def __contains__(self, x: object) -> bool:
        return self._d.__contains__(x)

    def __len__(self) -> int:
        return self._d.__len__()

    def __iter__(self) -> t.Iterator[T]:
        return self._d.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"<OrderedSet {self}>"
