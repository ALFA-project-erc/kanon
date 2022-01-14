"""The `precision` module is used when wanting to
adjust `~kanon.units.radices.BasedReal` arithmetical operations behavior.
All operations are made within a `PrecisionContext` rules, which indicate :

- A `TruncatureMode`
- A `PrecisionMode`
- 4 `CustomArithmeticAlgorithm`, (add, sub, mul, div)

Default precision context is set to `TruncatureMode.NONE`, `PrecisionMode.MAX`, and all
`CustomArithmeticAlgorithm` as default.

To set new precision rules you should use the `set_precision` context manager. In
the example below, I set the precision so that the result significant number is 0
and that it should be truncated.

>>> from kanon.units import Sexagesimal
>>> a = Sexagesimal("1;50")
>>> b = Sexagesimal("2;0")
>>> a + b
03 ; 50
>>> with set_precision(tmode=TruncatureMode.TRUNC, pmode=0):
...     a + b
...
03 ;

If you want to use a specific algorithm for one of the arithmetical operations,
you first need to define the algorithm with this signature with the `identify_func`
decorator specifying a unique ID :

.. code:: python

    Callable[[PreciseNumber, PreciseNumber], PreciseNumber]

For example, a multiplication algorithm which is essentialy
equivalent to ``a * round(b,0)`` with `TEST_MUL` as its ID:

>>> @identify_func("TEST_MUL")
... def test_mul(a: PreciseNumber, b: PreciseNumber) -> PreciseNumber:
...     res = 0
...     for i in range(int(round(b,0))):
...         res += a
...     return res

You can now use this function to make multiplications use this algorithm

>>> b * a
03 ; 40
>>> with set_precision(mul=test_mul):
...     b * a
04 ; 00

All operations and their associated context are stored inside the `ContextPrecision`
when the recording flag is set to ``True``. You can either set it to ``True`` inside
of a `set_precision` context manager, or globally turn it on with `set_recording(True)`.
Records are displayed with `get_records`, and can be cleared with `clear_records`.

Let's try to record our operations.

>>> set_recording(True)
>>> get_records()
[]
>>> a + b
03 ; 50
>>> with set_precision(tmode=TruncatureMode.ROUND, pmode=1):
...     a + Sexagesimal("2;5,30")
03 ; 56
>>> with set_precision(mul=test_mul):
...     b * a
04 ; 00
>>> get_records()
[{'args': (01 ; 50, 02 ; 00, '+', 03 ; 50), 'tmode': 'NONE', 'pmode': 'MAX', 'add': \
'DEFAULT', 'sub': 'DEFAULT', 'mul': 'DEFAULT', 'div': 'DEFAULT'}, {'args': (01 ; 50, \
02 ; 05,30, '+', 03 ; 56), 'tmode': 'ROUND', 'pmode': 1, 'add': 'DEFAULT', 'sub': \
'DEFAULT', 'mul': 'DEFAULT', 'div': 'DEFAULT'}, {'args': (02 ; 00, 01 ; 50, '*', 04 ; \
00), 'tmode': 'NONE', 'pmode': 'MAX', 'add': 'DEFAULT', 'sub': 'DEFAULT', 'mul': \
'TEST_MUL', 'div': 'DEFAULT'}]
>>> clear_records()
>>> set_recording(False)
>>> a + b
03 ; 50
>>> get_records()
[]

Types
-----

.. py:attribute:: CustomArithmeticAlgorithm

    :type: Optional[Callable[[PreciseNumber, PreciseNumber], PreciseNumber]
"""
from __future__ import annotations

import abc
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import partial, wraps
from numbers import Number
from typing import Callable, Dict, List, Literal, Optional, TypeVar, Union

__all__ = [
    "PrecisionMode",
    "TruncatureMode",
    "set_precision",
    "PrecisionContext",
    "PreciseNumber",
    "get_context",
    "set_context",
    "set_recording",
    "get_records",
    "clear_records",
    "CustomArithmeticAlgorithm",
    "Truncable",
]


def _with_context_precision(func=None, symbol=None):
    if not func:
        return partial(_with_context_precision, symbol=symbol)

    @wraps(func)
    def wrapper(*args, **kwargs) -> "Truncable":

        with set_precision(recording=False):
            value: "Truncable" = func(*args, **kwargs)

        if len(args) != 2 or any(not isinstance(a, Truncable) for a in args):
            return value

        if not isinstance(value, Truncable):
            raise TypeError

        value = value.resize(args[0]._get_significant(args[1]))
        ctx = get_context()
        value = ctx.tmode(value)
        ctx.record(*args, symbol, value)
        return value

    return wrapper


TTruncable = TypeVar("TTruncable", bound="Truncable")
TPreciseNumber = TypeVar("TPreciseNumber", bound="PreciseNumber")


class Truncable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def resize(self: TTruncable, significant: int) -> TTruncable:
        raise NotImplementedError

    @abc.abstractmethod
    def truncate(self: TTruncable, significant: Optional[int] = None) -> TTruncable:
        raise NotImplementedError

    @abc.abstractmethod
    def ceil(self: TTruncable, significant: Optional[int] = None) -> TTruncable:
        raise NotImplementedError

    @abc.abstractmethod
    def floor(self: TTruncable, significant: Optional[int] = None) -> TTruncable:
        raise NotImplementedError

    @abc.abstractmethod
    def __round__(self: TTruncable, significant: Optional[int] = None) -> TTruncable:
        raise NotImplementedError


class PreciseNumber(Number, Truncable):
    """Abstract class of numbers with `PrecisionContext` compatibility"""

    @property
    @abc.abstractmethod
    def significant(self) -> int:
        raise NotImplementedError

    def _get_significant(self: TPreciseNumber, other: "PreciseNumber") -> int:
        return get_context()._precisionfunc(self, other)

    @_with_context_precision(symbol="+")
    def __add__(self: TPreciseNumber, other):
        if f := get_context().add:
            return f(self, other)
        return self._add(other)

    @abc.abstractmethod
    def _add(self: TPreciseNumber, other: "PreciseNumber") -> TPreciseNumber:
        raise NotImplementedError

    @_with_context_precision(symbol="-")
    def __sub__(self: TPreciseNumber, other):
        if f := get_context().sub:
            return f(self, other)
        return self._sub(other)

    @abc.abstractmethod
    def _sub(self: TPreciseNumber, other: "PreciseNumber") -> TPreciseNumber:
        raise NotImplementedError

    @_with_context_precision(symbol="*")
    def __mul__(self: TPreciseNumber, other):
        if f := get_context().mul:
            return f(self, other)
        return self._mul(other)

    @abc.abstractmethod
    def _mul(self: TPreciseNumber, other: "PreciseNumber") -> TPreciseNumber:
        raise NotImplementedError

    @_with_context_precision(symbol="/")
    def __truediv__(self: TPreciseNumber, other):
        if f := get_context().div:
            return f(self, other)
        return self._truediv(other)

    @abc.abstractmethod
    def _truediv(self: TPreciseNumber, other: "PreciseNumber") -> TPreciseNumber:
        raise NotImplementedError

    @abc.abstractmethod
    def __float__(self) -> float:
        raise NotImplementedError


class FuncEnum(Enum):
    def __call__(self, *args, **kwds) -> PreciseNumber:
        return self.value[0](*args, **kwds)


class PrecisionMode(FuncEnum):
    """Enumeration of standard precision modes available.
    You can also use a positive integer to indicate a precision at a
    constant significant number.
    """

    SCI = (
        lambda x, y: min(x.significant, y.significant),
        0,
    )  #: Following scientific notation
    MAX = (lambda x, y: max(x.significant, y.significant), 1)  #: Using max significant
    FULL = (
        lambda *_: (_ for _ in ()).throw(NotImplementedError),
        2,
    )  #: TODO Full calculation


class TruncatureMode(FuncEnum):
    """Enumeration of standard truncature modes available."""

    NONE = (lambda x: x, 0)  #: No truncature
    ROUND = (round, 1)  #: round()
    TRUNC = (lambda x: x.truncate(), 2)  #: truncate()
    CEIL = (lambda x: x.ceil(), 3)  #: ceil()
    FLOOR = (lambda x: x.floor(), 4)  #: floor()


CustomArithmeticAlgorithm = Optional[
    Callable[[PreciseNumber, PreciseNumber], PreciseNumber]
]

_AI_REGISTRY: Dict[CustomArithmeticAlgorithm, str] = {None: "DEFAULT"}


def identify_func(identifier: str):
    """Identify a custom arithmetic algorithm with a unique name"""

    def wrapper(fn: Callable) -> CustomArithmeticAlgorithm:
        if identifier in _AI_REGISTRY.values():
            raise ValueError("Identifier already in use")
        if fn in _AI_REGISTRY:
            raise ValueError(
                f"Function already registered with identifier {_AI_REGISTRY[fn]}"
            )
        _AI_REGISTRY[fn] = identifier
        return fn

    return wrapper


def remove_func(func: CustomArithmeticAlgorithm):
    """Remove a custom arithmetic algorithm from the registry"""
    if func in _AI_REGISTRY:
        del _AI_REGISTRY[func]
        return True
    return False


def find_func(identifier: str):
    """Find the function of an identifier that has been registered"""
    return [k for k, v in _AI_REGISTRY.items() if v == identifier][0]


@dataclass
class PrecisionContext:
    """Context containing `PreciseNumber` arithmetic rules."""

    #: Precision mode
    pmode: PrecisionMode = PrecisionMode.MAX
    #: Truncature mode
    tmode: TruncatureMode = TruncatureMode.NONE
    #: Addition `CustomArithmeticAlgorithm`
    add: CustomArithmeticAlgorithm = None
    #: Substraction `CustomArithmeticAlgorithm`
    sub: CustomArithmeticAlgorithm = None
    #: Multiplication `CustomArithmeticAlgorithm`
    mul: CustomArithmeticAlgorithm = None
    #: Division `CustomArithmeticAlgorithm`
    div: CustomArithmeticAlgorithm = None
    #: Recording mode
    recording: bool = False

    #: `set_precision` context stack
    stack: int = field(init=False, default=0)
    _records: List = field(init=False, default_factory=list)

    def __post_init__(self):
        if not isinstance(self.tmode, TruncatureMode):
            raise TypeError

        if isinstance(self.pmode, int):
            if self.pmode < 0:
                raise ValueError("Precision cannot be negative")
            self._precisionfunc = lambda *_: self.pmode
        elif isinstance(self.pmode, PrecisionMode):
            self._precisionfunc = self.pmode
        else:
            raise TypeError

    def mutate(
        self,
        pmode: Optional[PrecisionMode] = None,
        tmode: Optional[TruncatureMode] = None,
        recording: Optional[bool] = None,
        add: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
        sub: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
        mul: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
        div: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
    ):
        """Mutates this `PrecisionContext` with new rules."""

        for f in [add, sub, mul, div]:
            if f is not False and f not in _AI_REGISTRY:
                raise ValueError("CustomArithmeticFunction not registered")

        self.pmode = self.pmode if pmode is None else pmode
        self.tmode = tmode or self.tmode
        self.recording = self.recording if recording is None else recording
        self.add = add if add is not False else self.add
        self.sub = sub if sub is not False else self.sub
        self.mul = mul if mul is not False else self.mul
        self.div = div if div is not False else self.div

        self.__post_init__()

    def freeze(self):
        """Returns a `Dict` containing this context rules"""
        return {
            "tmode": self.tmode.name,
            "pmode": self.pmode.name
            if isinstance(self.pmode, PrecisionMode)
            else self.pmode,
            "add": _AI_REGISTRY[self.add],
            "sub": _AI_REGISTRY[self.sub],
            "mul": _AI_REGISTRY[self.mul],
            "div": _AI_REGISTRY[self.div],
        }

    def record(self, *args):
        """Record an operation"""
        if self.recording:
            self._records.append({"args": args, **self.freeze()})


__CONTEXT = PrecisionContext()


def get_context() -> PrecisionContext:
    """Returns current context"""
    return __CONTEXT


def set_context(context: PrecisionContext):
    """Replace current `PrecisionContext`.

    :raises ValueError: Raise if you set a new context while inside a `set_precision` \
    context manager.
    """
    if get_context().stack > 0:
        raise ValueError("You can't change context while inside a precision_context")
    context.stack = 0
    global __CONTEXT
    __CONTEXT = context


def set_recording(flag: bool):
    """Set current `PrecisionContext` recording mode to `flag`.

    :raises ValueError: Raise if you set recording while inside a `set_precision` \
    context manager
    """
    ctx = get_context()
    if ctx.stack > 0:
        raise ValueError(
            "You can't start recording while inside a precision_context,\
            you should use recording=True instead"
        )
    ctx.recording = flag


def get_records():
    """Get current `PrecisionContext` records."""
    return get_context()._records


def clear_records():
    """Clear current `PrecisionContext` records."""
    get_context()._records.clear()


@contextmanager
def set_precision(
    pmode: Optional[PrecisionMode] = None,
    tmode: Optional[TruncatureMode] = None,
    recording: Optional[bool] = None,
    add: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
    sub: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
    mul: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
    div: Union[CustomArithmeticAlgorithm, Literal[False]] = False,
):
    """Mutates the current `PrecisionContext` with the specified rules."""
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


class PrecisionError(Exception):
    pass
