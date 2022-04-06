from typing import Generic, SupportsIndex, Tuple, TypeVar, overload

T = TypeVar("T")


class LoopingList(tuple, Generic[T]):
    """
    A class for lists looping both sides.
    If an index is queried outside the boundaries of the list,
    the last element is returned.

    >>> test = LoopingList([0, 1, 2])
    >>> test
    (..., 0, 1, 2, ...)
    >>> test[45]
    2
    >>> test[-5]
    0

    """

    @overload
    def __getitem__(self, __i: SupportsIndex) -> T:
        ...

    @overload
    def __getitem__(self, __s: slice) -> Tuple[T]:
        ...

    def __getitem__(self, key):
        if len(self) > 0:
            if key >= len(self):
                return self[-1]
            elif key < -len(self) + 1:
                return self[0]
        return super().__getitem__(key)

    def __repr__(self) -> str:
        return f"(..., {list(self).__repr__()[1:-1]}, ...)" if self else "()"


class LoopingSList(LoopingList, Generic[T]):
    """

    >>> test = LoopingSList([0, 0, 1, 2, 2, 2])
    >>> test == (0, 0, 1, 2, 2, 2)
    False
    >>> test == (0, 1, 2)
    True
    >>> test = LoopingSList([1, 2, 1, 2, 2])
    >>> test == (1, 2, 1, 2)
    True

    """

    def __new__(cls, __iterable):
        new_iterable = list(__iterable)
        for idx, x in enumerate(new_iterable):
            if x != new_iterable[0]:
                new_iterable = new_iterable[idx - 1 :]
                break
        else:
            new_iterable = new_iterable[:1]

        for idx, x in enumerate(new_iterable[-2::-1]):
            if x != new_iterable[-1]:
                if idx > 0:
                    new_iterable = new_iterable[:-idx]
                break

        return super().__new__(LoopingSList, new_iterable)
