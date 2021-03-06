import abc
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import partial, wraps
from numbers import Number
from typing import Callable, List, Optional, SupportsFloat, Tuple

__all__ = ["PrecisionMode", "TruncatureMode", "set_precision", "PrecisionContext", "PreciseNumber"]


class FuncEnum(Enum):
    def __call__(self, *args, **kwds) -> "PreciseNumber":
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


ArithmeticIdentifier = Tuple[Optional[Callable[["PreciseNumber", "PreciseNumber"], "PreciseNumber"]], str]


@dataclass
class PrecisionContext:
    pmode: PrecisionMode
    tmode: TruncatureMode
    add: ArithmeticIdentifier
    sub: ArithmeticIdentifier
    mul: ArithmeticIdentifier
    div: ArithmeticIdentifier

    recording: bool = False
    stack: int = field(init=False, default=0)
    _records: List = field(init=False, default_factory=list)

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

    def mutate(self,
               pmode: Optional[PrecisionMode] = None,
               tmode: Optional[TruncatureMode] = None,
               recording: Optional[bool] = None,
               add: Optional[ArithmeticIdentifier] = None,
               sub: Optional[ArithmeticIdentifier] = None,
               mul: Optional[ArithmeticIdentifier] = None,
               div: Optional[ArithmeticIdentifier] = None
               ):
        self.pmode = pmode or self.pmode
        self.tmode = tmode or self.tmode
        self.recording = self.recording if recording is None else recording
        self.add = add or self.add
        self.sub = sub or self.sub
        self.mul = mul or self.mul
        self.div = div or self.div

        self.__post_init__()

    def freeze(self):
        return {
            "tmode": self.tmode.name,
            "pmode": self.pmode.name if isinstance(self.pmode, PrecisionMode) else self.pmode,
            "add": self.add[1],
            "sub": self.sub[1],
            "mul": self.mul[1],
            "div": self.div[1]
        }

    def record(self, *args):
        if self.recording:
            self._records.append({"args": args, **self.freeze()})


__CONTEXT = PrecisionContext(pmode=PrecisionMode.SCI, tmode=TruncatureMode.NONE,
                             add=(None, "DEFAULT"), sub=(None, "DEFAULT"),
                             mul=(None, "DEFAULT"), div=(None, "DEFAULT"))


def get_context() -> PrecisionContext:
    return __CONTEXT


def set_context(context: PrecisionContext):
    if get_context().stack > 0:
        raise ValueError("You can't change context while inside a precision_context")
    context.stack = 0
    global __CONTEXT
    __CONTEXT = context


def set_recording(flag: bool):
    ctx = get_context()
    if ctx.stack > 0:
        raise ValueError("You can't start recording while inside a precision_context,\
            you should use recording=True instead")
    ctx.recording = flag


def get_records():
    return get_context()._records


def clear_records():
    get_context()._records.clear()


@contextmanager
def set_precision(pmode: Optional[PrecisionMode] = None,
                  tmode: Optional[TruncatureMode] = None,
                  recording: Optional[bool] = None,
                  add: Optional[ArithmeticIdentifier] = None,
                  sub: Optional[ArithmeticIdentifier] = None,
                  mul: Optional[ArithmeticIdentifier] = None,
                  div: Optional[ArithmeticIdentifier] = None):
    ctx = get_context()
    current = asdict(ctx)
    del current["_records"]
    del current["stack"]
    try:
        ctx.stack += 1
        ctx.mutate(pmode, tmode, recording, add, sub, mul, div)
        yield asdict(ctx)
    finally:
        ctx.mutate(**current)
        ctx.stack -= 1


def _with_context_precision(func=None, symbol=None):
    if not func:
        return partial(_with_context_precision, symbol=symbol)

    @wraps(func)
    def wrapper(*args, **kwargs) -> "PreciseNumber":

        with set_precision(recording=False):
            value: "PreciseNumber" = func(*args, **kwargs)

        if len(args) != 2 or any(not isinstance(a, PreciseNumber) for a in args):
            return value

        if not isinstance(value, PreciseNumber):
            raise TypeError

        value = value.resize(args[0]._get_significant(args[1]))
        ctx = get_context()
        value = ctx.tmode(value)
        ctx.record(*args, symbol, value)
        return value

    return wrapper


class PreciseNumber(Number, SupportsFloat):

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

    @_with_context_precision(symbol="+")
    def __add__(self, other):
        if f := get_context().add[0]:
            return f(self, other)
        return self._add(other)

    @abc.abstractmethod
    def _add(self, other: "PreciseNumber") -> "PreciseNumber":
        raise NotImplementedError

    @_with_context_precision(symbol="-")
    def __sub__(self, other):
        if f := get_context().sub[0]:
            return f(self, other)
        return self._sub(other)

    @abc.abstractmethod
    def _sub(self, other: "PreciseNumber") -> "PreciseNumber":
        raise NotImplementedError

    @_with_context_precision(symbol="*")
    def __mul__(self, other):
        if f := get_context().mul[0]:
            return f(self, other)
        return self._mul(other)

    @abc.abstractmethod
    def _mul(self, other: "PreciseNumber") -> "PreciseNumber":
        raise NotImplementedError

    @_with_context_precision(symbol="/")
    def __truediv__(self, other):
        if f := get_context().div[0]:
            return f(self, other)
        return self._truediv(other)

    @abc.abstractmethod
    def _truediv(self, other: "PreciseNumber") -> "PreciseNumber":
        raise NotImplementedError


class PrecisionError(Exception):
    pass
