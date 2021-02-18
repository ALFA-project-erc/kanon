import abc
from contextlib import contextmanager
from dataclasses import astuple, dataclass
from enum import Enum
from functools import wraps
from numbers import Number
from typing import Optional

__all__ = ["PrecisionMode", "TruncatureMode", "set_precision", "PrecisionContext", "PreciseNumber"]


class FuncEnum(Enum):
    def __call__(self, *args, **kwds) -> Number:
        return self.value[0](*args, **kwds)


class PrecisionMode(FuncEnum):
    SCI = (lambda x, y: min(x.significant, y.significant), 0)  #: Following scientific notation
    MAX = (lambda x, y: max(x.significant, y.significant), 1)  #: Using max significant
    FULL = (lambda *_: (_ for _ in ()).throw(NotImplementedError), 2)  #: TODO Full calculation


class TruncatureMode(FuncEnum):
    NONE = (lambda x: x, 0)  #: No truncature
    ROUND = (round, 1)  #: round()
    TRUNC = (lambda x: x.truncate(), 2)  #: truncate()
    CEIL = (lambda x: x.ceil(), 3)  #: ceil()
    FLOOR = (lambda x: x.floor(), 4)  #: floor()


@dataclass
class PrecisionContext:
    pmode: PrecisionMode
    tmode: TruncatureMode

    def __post_init__(self):
        if type(self.tmode) is not TruncatureMode:
            raise TypeError

        if isinstance(self.pmode, int):
            if self.pmode < 0:
                raise ValueError("Precision cannot be negative")
            self._precisionfunc = lambda *_: self.pmode
        elif type(self.pmode) is PrecisionMode:
            self._precisionfunc = self.pmode
        else:
            raise TypeError

    def mutate(self, pmode: Optional[PrecisionMode] = None, tmode: Optional[TruncatureMode] = None):
        self.pmode = pmode or self.pmode
        self.tmode = tmode or self.tmode

        self.__post_init__()


__CONTEXT: PrecisionContext = PrecisionContext(pmode=PrecisionMode.SCI, tmode=TruncatureMode.NONE)


def get_context() -> PrecisionContext:
    return __CONTEXT


@contextmanager
def set_precision(pmode: Optional[PrecisionMode] = None, tmode: Optional[TruncatureMode] = None):
    ctx = get_context()
    current_ctx = astuple(ctx)
    try:
        ctx.mutate(pmode, tmode)
        yield ctx
    finally:
        ctx.mutate(*current_ctx)


def _with_context_precision(func):

    @wraps(func)
    def wrapper(*args, **kwargs) -> PreciseNumber:

        value: PreciseNumber = func(*args, **kwargs)

        if len(args) != 2 or any(not isinstance(a, PreciseNumber) for a in args):
            return value

        if not isinstance(value, PreciseNumber):
            raise TypeError

        value = value.resize(args[0]._get_significant(args[1]))

        return get_context().tmode(value)

    return wrapper


class PreciseNumber(Number):

    @property
    @abc.abstractmethod
    def significant(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def resize(self, significant: int) -> "PreciseNumber":
        raise NotImplementedError

    @abc.abstractmethod
    def truncate(self, significant: Optional[int] = None) -> "PreciseNumber":
        raise NotImplementedError

    @abc.abstractmethod
    def ceil(self, significant: Optional[int] = None) -> "PreciseNumber":
        raise NotImplementedError

    @abc.abstractmethod
    def floor(self, significant: Optional[int] = None) -> "PreciseNumber":
        raise NotImplementedError

    def _get_significant(self, other: "PreciseNumber") -> int:
        return get_context()._precisionfunc(self, other)

    def __init_subclass__(cls):
        cls.__add__ = _with_context_precision(cls.__add__)
        cls.__mul__ = _with_context_precision(cls.__mul__)
        cls.__truediv__ = _with_context_precision(cls.__truediv__)


class PrecisionError(Exception):
    pass
