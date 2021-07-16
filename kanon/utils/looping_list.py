from typing import Generic, TypeVar

T = TypeVar("T")


class LoopingList(list, Generic[T]):
    """
    A class for lists looping both sides.
    If an index is queried outside the boundaries of the list, the last element is returned.

    >>> test = LoopingList([0, 1, 2])
    >>> test
    [..., 0, 1, 2, ...]
    >>> test[45]
    2
    >>> test[-5]
    0

    """

    def __getitem__(self, key):
        if key >= len(self):
            return self[-1]
        if key < -len(self) + 1:
            return self[0]
        return super().__getitem__(key)

    def __repr__(self) -> str:
        return f"[..., {super().__repr__()[1:-1]}, ...]" if self else "[]"
