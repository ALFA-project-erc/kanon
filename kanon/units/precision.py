import abc
from contextlib import contextmanager
from dataclasses import astuple, dataclass
from enum import Enum, unique
from functools import wraps
from numbers import Number
from typing import Optional

__all__ = ["PrecisionMode", "TruncatureMode", "set_precision", "PrecisionContext", "PreciseNumber"]


@unique
class PrecisionMode(Enum):
    SCI = 0  #: Following scientific notation
    MAX = 1  #: Using max significant
    FULL = 2  #: Full calculation (until 100 significant numbers)
    CUSTOM = 3  #: Use a specific significant number


@unique
class TruncatureMode(Enum):
    NONE = 0
    ROUND = 1
    TRUNC = 2
    CEIL = 3
    FLOOR = 4


@dataclass
class PrecisionContext:
    pmode: PrecisionMode
    tmode: TruncatureMode
    custom_precision: Optional[int]

    def __post_init__(self):
        if (self.pmode == PrecisionMode.CUSTOM) ^ (self.custom_precision is not None):
            raise CustomPrecisionError(self.pmode, self.custom_precision)

        if self.tmode == TruncatureMode.NONE:
            self._truncatefunc = lambda x: x
        elif self.tmode == TruncatureMode.ROUND:
            self._truncatefunc = round
        elif self.tmode == TruncatureMode.TRUNC:
            self._truncatefunc = lambda x: x.truncate()
        elif self.tmode == TruncatureMode.CEIL:
            self._truncatefunc = lambda x: x.ceil()
        elif self.tmode == TruncatureMode.FLOOR:
            self._truncatefunc = lambda x: x.floor()
        else:
            raise TypeError

        if self.pmode == PrecisionMode.CUSTOM:
            self._precisionfunc = lambda x, y: self.custom_precision
        elif self.pmode == PrecisionMode.SCI:
            self._precisionfunc = lambda x, y: min(x.significant, y.significant)
        elif self.pmode == PrecisionMode.MAX:
            self._precisionfunc = lambda x, y: max(x.significant, y.significant)
        # TODO: Implement PrecisionMode.FULL
        elif self.pmode == PrecisionMode.FULL:
            raise NotImplementedError
        else:
            raise TypeError

    def mutate(self, pmode: Optional[PrecisionMode] = None,
               tmode: Optional[TruncatureMode] = None,
               custom_precision: Optional[int] = None):
        self.custom_precision = custom_precision
        self.pmode = pmode or self.pmode
        self.tmode = tmode or self.tmode

        self.__post_init__()


CONTEXT: PrecisionContext = PrecisionContext(pmode=PrecisionMode.SCI, tmode=TruncatureMode.NONE, custom_precision=None)


@contextmanager
def set_precision(pmode: Optional[PrecisionMode] = None,
                  tmode: Optional[TruncatureMode] = None,
                  custom_precision: Optional[int] = None):
    current_ctx = astuple(CONTEXT)
    try:
        CONTEXT.mutate(pmode, tmode, custom_precision)
        yield CONTEXT
    finally:
        CONTEXT.mutate(*current_ctx)


def _with_context_precision(func):

    @wraps(func)
    def wrapper(*args, **kwargs) -> PreciseNumber:

        value: PreciseNumber = func(*args, **kwargs)

        if len(args) != 2 or any(not isinstance(a, PreciseNumber) for a in args):
            return value

        if not isinstance(value, PreciseNumber):
            raise TypeError

        value = value.resize(args[0]._get_significant(args[1]))

        return CONTEXT._truncatefunc(value)

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
        return CONTEXT._precisionfunc(self, other)


class PrecisionError(Exception):
    pass


class CustomPrecisionError(PrecisionError):
    def __init__(self, pmode: PrecisionMode, custom_precision: int) -> None:
        self.pmode = pmode
        self.custom_precision = custom_precision

    def __str__(self) -> str:
        if self.pmode == PrecisionMode.CUSTOM:
            return f"""
            Illegal value for custom_precision when in
             PrecisionMode.CUSTOM, must be an int : {self.custom_precision}"""
        else:
            return "Can't set a custom_precision without PrecisionMode.CUSTOM"
