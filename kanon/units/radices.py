"""
In this module we define RadixBase and BasedReal.
RadixBase is the basis of the way we work with different radices.
BasedReal are a class of Real numbers with a 1-1 relation with a RadixBase.

.. testsetup::

    >>> import builtins
    >>> builtins.Sexagesimal = radix_registry["Sexagesimal"]
    >>> builtins.Historical = radix_registry["Historical"]

>>> from kanon.units import RadixBase, radix_registry
>>> example_base = RadixBase([20, 5, 18], [24, 60], "example_base", [" ","u ","sep "])
>>> number = radix_registry["ExampleBase"]((8, 12, 3, 1), (23, 31))
>>> number
08 12u 3sep 01 ; 23,31
>>> float(number)
15535.979861111111

"""

import math
from decimal import Decimal
from fractions import Fraction
from functools import cached_property, lru_cache
from numbers import Number
from numbers import Real as _Real
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Sequence,
    SupportsFloat,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

import numpy as np
from astropy.units.core import Unit, UnitBase, UnitTypeError
from astropy.units.quantity import Quantity
from astropy.units.quantity_helper.converters import UFUNC_HELPERS
from astropy.units.quantity_helper.helpers import _d

from kanon.utils.list_to_tuple import list_to_tuple
from kanon.utils.looping_list import LoopingList

from .precision import PreciseNumber, PrecisionMode, TruncatureMode, set_precision

__all__ = ["RadixBase", "BasedReal", "radix_registry"]


radix_registry: Dict[str, Type["BasedReal"]] = {}
"""Registry containing all instanciated BasedReal classes."""


class RadixBase:
    """
    A class representing a numeral system. A radix must be specified at each position,
    by specifying an integer list for the integer positions, and an integer list for the
    fractional positions.
    """

    def __init__(
        self,
        left: Sequence[int],
        right: Sequence[int],
        name: str,
        integer_separators: Optional[Sequence[str]] = None,
    ):
        """
        Definition of a numeral system. A radix must be specified for each integer position
        (left argument) and for each fractional position (right argument).
        Note that the integer position are counted from right to left (starting from the ';'
        symbol and going to the left).

        :param left: Radix list for the integer part
        :param right: Radix list for the fractional part
        :param name: Name of this numeral system
        :param integer_separators: List of string separators, used for displaying the integer part of the number
        """
        assert left and right
        assert all(isinstance(x, int) for x in left)
        assert all(isinstance(x, int) for x in right)

        self.left: LoopingList[int] = LoopingList(left)
        self.right: LoopingList[int] = LoopingList(right)
        self.name = name
        if integer_separators is not None:
            if len(integer_separators) != len(left):
                raise ValueError
            self.integer_separators = LoopingList[str](integer_separators)
        else:
            self.integer_separators = LoopingList[str](
                ["," if x != 10 else "" for x in left]
            )

        self.mixed = any(x != left[0] for x in tuple(left) + tuple(right))

        # Build a class inheriting from BasedReal, that will use this RadixBase as
        # its numeral system.
        type_name = "".join(map(str.capitalize, self.name.split("_")))
        if type_name in radix_registry:
            raise ValueError(f"Name {type_name} already exists in registry")

        new_type = type(type_name, (BasedReal,), {"base": self})
        radix_registry[type_name] = new_type

        # Store the newly created BasedReal class
        self.type: Type[BasedReal] = new_type

    @overload
    def __getitem__(self, key: int) -> int:
        ...

    @overload
    def __getitem__(self, key: slice) -> LoopingList[int]:
        ...

    def __getitem__(self, key):
        """
        Return the radix at the specified position. Position 0 represents the last integer
        position before the fractional part (i.e. the position just before the ';' in sexagesimal
        notation, or just before the '.' in decimal notation). Positive positions represent
        the fractional positions, negative positions represent the integer positions.

        :param key: Position. <= 0 for integer part (with 0 being the right-most integer position), > 0 for fractional part
        :return: Radix at the specified position
        """
        if isinstance(key, slice):
            if not key.start or not key.stop:
                raise ValueError("RadixBase slices must have a start and a stop value")
            array = [self[i] for i in range(key.start, key.stop)]
            return LoopingList[str](array[:: key.step])

        if key <= 0:
            return self.left[key - 1]
        else:
            return self.right[key - 1]

    @lru_cache
    def factor_at_pos(self, pos: int) -> int:
        """
        Returns an int factor corresponding to a digit at position pos.
        This factor is an integer, when dealing with fractional position you should invert
        the result to find relevant factor.

        >>> Sexagesimal.base.factor_at_pos(-2)
        3600
        >>> Sexagesimal.base.factor_at_pos(0)
        1

        :param pos: Position of the digit
        :type pos: int
        :return: Factor at pos
        :rtype: int
        """
        factor = 1
        for i in range(abs(pos)):
            factor *= self[i if pos > 0 else -i]
        return factor


def ndigit_for_radix(radix: int) -> int:
    """
    Compute how many digits are needed to represent a position of
    the specified radix.

    >>> ndigit_for_radix(10)
    1
    >>> ndigit_for_radix(60)
    2

    :param radix:
    :return:
    """
    return int(np.ceil(np.log10(radix)))


class BasedReal(PreciseNumber, _Real):
    """
    Abstract class allowing to represent a value in a specific `RadixBase`.
    Each time a new `RadixBase` object is recorded, a new class inheriting from BasedReal
    is created and recorded in `radix_registry`.
    The `RadixBase` to be used will be placed in the class attribute `base`

    Class attributes:
       - base :        A `RadixBase` object (will be attributed dynamically to the children inheriting this class)
    """

    base: RadixBase
    """`RadixBase` of this BasedReal"""
    __left: Tuple[int, ...]
    __right: Tuple[int, ...]
    __remainder: Decimal
    __sign: Literal[-1, 1]
    __slots__ = ("base", "__left", "__right", "__remainder", "__sign")

    def __check_range(self):
        """
        Checks that the given values are in the range of the base and are integers.
        """
        if self.sign not in (-1, 1):
            raise ValueError("Sign should be -1 or 1")
        if not (isinstance(self.remainder, Decimal) and 0 <= self.remainder < 1):
            if self.remainder == 1:  # pragma: no cover
                self += (self.one() * self.sign) >> self.significant
            else:
                raise ValueError(
                    f"Illegal remainder value ({self.remainder}), should be a Decimal between [0.,1.["
                )
        # if self.base.factor_at_pos(len(self.left) - 1) > 1e+15 and self.remainder:
        #     warnings.warn("""
        #                 Integer part of this number exceeds floating point precision.
        #                 Calculations made with this number as a float might return incorrect results.
        #                 """)
        for x in self[:]:
            if isinstance(x, float):
                raise IllegalFloatError(x)
            if not isinstance(x, int):
                raise TypeError(f"{x} not an int")
        for i, s in enumerate(self[:]):
            if s < 0.0 or s >= self.base[i - len(self.left) + 1]:
                raise IllegalBaseValueError(
                    self.base, self.base[i - len(self.left) + 1], s
                )

    def __simplify_integer_part(self) -> int:
        """
        Remove the useless trailing zeros in the integer part and return how many were removed
        """
        count = 0
        for i in self.left[:-1]:
            if i != 0:
                break
            count += 1
        if count > 0:
            self.__left = self.left[count:]

        return count != 0

    @list_to_tuple
    def __new__(cls, *args, remainder=Decimal(0.0), sign=1) -> "BasedReal":
        """Constructs a number with a given radix.

        Arguments:

        - `str`

        >>> Sexagesimal("-2,31;12,30")
        -02,31 ; 12,30

        - 2 `Sequence[int]` representing integral part and fractional part

        >>> Sexagesimal((2,31), (12,30), sign=-1)
        -02,31 ; 12,30
        >>> Sexagesimal([2,31], [12,30])
        02,31 ; 12,30

        - a `BasedReal` with a significant number of digits,

        >>> Sexagesimal(Sexagesimal("-2,31;12,30"), 1)
        -02,31 ; 12 |r0.5

        - multiple `int` representing an integral number in current `base`

        >>> Sexagesimal(21, 1, 3)
        21,01,03 ;

        :param remainder: When a computation requires more precision than the precision \
        of this number, we store a :class:`~decimal.Decimal` remainder to keep track of it, defaults to 0.0
        :type remainder: ~decimal.Decimal, optional
        :param sign: The sign of this number, defaults to 1
        :type sign: int, optional
        :raises ValueError: Unexpected or illegal arguments
        :rtype: BasedReal
        """
        if cls is BasedReal:
            raise TypeError("Can't instanciate abstract class BasedReal")
        self: BasedReal = super().__new__(cls)
        self.__left = ()
        self.__right = ()
        self.__remainder = remainder
        self.__sign = sign
        if np.all([isinstance(x, int) for x in args]):
            return cls.__new__(cls, args, (), remainder=remainder, sign=sign)
        if len(args) == 2:
            if isinstance(args[0], BasedReal):
                if isinstance(args[0], cls):
                    return args[0].resize(args[1])
                return cls.from_decimal(args[0].decimal, args[1])
            if isinstance(args[0], tuple) and isinstance(args[1], tuple):
                self.__left = args[0]
                self.__right = args[1]
            else:
                raise ValueError("Incorrect parameters at BasedReal creation")
        elif len(args) == 1:
            if isinstance(args[0], str):
                return cls._from_string(args[0])
            raise ValueError(
                "Please specify a number of significant positions"
                if isinstance(args[0], BasedReal)
                else "Incorrect parameters at BasedReal creation"
            )
        else:
            raise ValueError("Incorrect number of parameter at BasedReal creation")

        self.__check_range()

        if self.__simplify_integer_part() or not self.left:
            return cls.__new__(
                cls,
                self.left or (0,),
                self.right,
                remainder=self.remainder,
                sign=self.sign,
            )

        return self

    @property
    def left(self) -> Tuple[int, ...]:
        """
        Tuple of values at integer positions

        >>> Sexagesimal(1,2,3).left
        (1, 2, 3)

        :rtype: Tuple[int, ...]
        """
        return self.__left

    @property
    def right(self) -> Tuple[int, ...]:
        """
        Tuple of values at fractional positions

        >>> Sexagesimal((1,2,3), (4,5)).right
        (4, 5)

        :rtype: Tuple[int, ...]
        """
        return self.__right

    @property
    def remainder(self) -> Decimal:
        """
        When a computation requires more significant figures than the precision of this number,
        we store a :class:`~decimal.Decimal` remainder to keep track of it

        >>> Sexagesimal(1,2,3, remainder=Decimal("0.2")).remainder
        Decimal('0.2')

        :return: Remainder of this `BasedReal`
        :rtype: ~decimal.Decimal
        """
        return self.__remainder

    @property
    def sign(self) -> Literal[-1, 1]:
        """
        Sign of this `BasedReal`

        >>> Sexagesimal(1,2,3, sign=-1).sign
        -1

        :rtype: Literal[-1, 1]
        """
        return self.__sign

    @property
    def significant(self) -> int:
        """
        Precision of this `BasedReal` (equals to length of fractional part)

        >>> Sexagesimal((1,2,3), (4,5)).significant
        2

        :rtype: int
        """
        return len(self.right)

    @cached_property
    def decimal(self) -> Decimal:
        """
        This `BasedReal` converted as a `~decimal.Decimal`

        >>> Sexagesimal((1,2,3), (15,36)).decimal
        Decimal('3723.26')

        :rtype: Decimal
        """
        value = Decimal(abs(int(self)))
        factor = Decimal(1)
        for i in range(self.significant):
            factor *= self.base.right[i]
            value += self.right[i] / factor

        value += self.remainder / factor
        return value * self.sign

    def to_fraction(self) -> Fraction:
        """
        :return: this `BasedReal` as a :class:`~fractions.Fraction` object.
        """
        return Fraction(self.decimal)

    @classmethod
    def from_fraction(
        cls,
        fraction: Fraction,
        significant: Optional[int] = None,
    ) -> "BasedReal":
        """
        :param fraction: a `~fractions.Fraction` object
        :param significant: significant precision desired
        :return: a `BasedReal` object computed from a Fraction
        """

        if not isinstance(fraction, Fraction):
            raise TypeError(f"Argument {fraction} is not a Fraction")

        num, den = fraction.as_integer_ratio()
        res: BasedReal = cls.from_decimal(
            Decimal(num) / Decimal(den), significant or 100
        )

        return res if significant else res.minimize_precision()

    def __repr__(self) -> str:
        """
        Convert to string representation.
        Note that this representation is rounded (with respect to the remainder attribute) not truncated

        :return: String representation of this number
        """
        res = ""
        if self.sign < 0:
            res += "-"

        for i in range(len(self.left)):
            if i > 0:
                res += self.base.integer_separators[i - len(self.left)]
            num = str(self.left[i])
            digit = ndigit_for_radix(self.base.left[i - len(self.left)])
            res += "0" * (digit - len(num)) + num

        res += " ; "

        for i in range(len(self.right)):
            num = str(self.right[i])
            digit = ndigit_for_radix(self.base.right[i])
            res += "0" * (digit - len(num)) + num

            if i < len(self.right) - 1:
                res += ","

        if self.remainder:
            res += f" |r{self.remainder:3.1f}"

        return res

    __str__ = __repr__

    @classmethod
    def _from_string(cls, string: str) -> "BasedReal":
        """
        Parses and instantiate a `BasedReal` object from a string

        >>> Sexagesimal('1, 12; 4, 25')
        01,12 ; 04,25
        >>> Historical('2r 7s 29; 45, 2')
        2r 07s 29 ; 45,02
        >>> Sexagesimal('0 ; 4, 45')
        00 ; 04,45

        :param string: `str` representation of the number
        :return: a new instance of `BasedReal`
        """

        if not isinstance(string, str):
            raise TypeError(f"Argument {string} is not a str")

        string = string.strip().lower()
        if len(string) == 0:
            raise EmptyStringException("String is empty")
        if string[0] == "-":
            sign = -1
            string = string[1:]
        else:
            sign = 1
        left_right = string.split(";")
        if len(left_right) < 2:
            left = left_right[0]
            right = ""
        elif len(left_right) == 2:
            left, right = left_right
        else:
            raise TooManySeparators("Too many separators in string")

        left = left.strip()
        right = right.strip()

        left_numbers: List[int] = []
        right_numbers: List[int] = []

        if len(right) > 0:
            right_numbers = [int(i) for i in right.split(",")]

        if len(left) > 0:
            rleft = left[::-1]
            for i in range(len(left)):
                separator = cls.base.integer_separators[-i - 1].strip().lower()
                if separator != "":
                    split = rleft.split(separator, 1)
                    if len(split) == 1:
                        rem = split[0]
                        break
                    value, rem = split
                else:  # pragma: no cover
                    value = rleft[0]
                    rem = rleft[1:]
                left_numbers.insert(0, int(value[::-1]))
                rleft = rem.strip()
                if len(rleft) == 1:
                    break
            left_numbers.insert(0, int(rleft[::-1]))

        return cls(left_numbers, right_numbers, sign=sign)

    def resize(self, significant: int) -> "BasedReal":
        """
        Resizes and returns a new `BasedReal` object to the specified precision

        >>> n = Sexagesimal('02, 02; 07, 23, 55, 11, 51, 21, 36')
        >>> n
        02,02 ; 07,23,55,11,51,21,36
        >>> n.remainder
        Decimal('0')
        >>> n1 = n.resize(4)
        >>> n1.right
        (7, 23, 55, 11)
        >>> n1.remainder
        Decimal('0.8560000000000000000000000000')
        >>> n1.resize(7)
        02,02 ; 07,23,55,11,51,21,36

        :param significant: Number of desired significant positions
        :return: Resized `BasedReal`
        """
        if significant == self.significant:
            return self
        if significant > self.significant:
            rem = type(self).from_decimal(
                self.sign * self.remainder, significant - self.significant
            )
            return type(self)(
                self.left,
                self.right + rem.right,
                remainder=rem.remainder,
                sign=self.sign,
            )
        if significant >= 0:
            remainder = type(self)(
                (), self.right[significant:], remainder=self.remainder
            )

            return type(self)(
                self.left,
                self.right[:significant],
                remainder=remainder.decimal,
                sign=self.sign,
            )

        raise NotImplementedError

    def __trunc__(self):
        return int(float(self.truncate(0)))

    def truncate(self, significant: Optional[int] = None) -> "BasedReal":
        """
        Truncate this BasedReal object to the specified precision

        >>> n = Sexagesimal('02, 02; 07, 23, 55, 11, 51, 21, 36')
        >>> n
        02,02 ; 07,23,55,11,51,21,36
        >>> n = n.truncate(3); n
        02,02 ; 07,23,55
        >>> n = n.resize(7); n
        02,02 ; 07,23,55,00,00,00,00

        :param n: Desired significant positions
        :return: Truncated BasedReal
        """
        if significant is None:
            significant = self.significant
        if significant > self.significant:
            return self
        left = self.left if significant >= 0 else self.left[:-significant]
        right = self.right[:significant] if significant >= 0 else ()
        return type(self)(left, right, sign=self.sign)

    def floor(self, significant: Optional[int] = None) -> "BasedReal":
        resized = self.resize(significant) if significant else self
        if resized.remainder == 0 or self.sign == 1:
            return resized.truncate()

        return resized._set_remainder(Decimal(0.5)).__round__()

    def ceil(self, significant: Optional[int] = None) -> "BasedReal":
        resized = self.resize(significant) if significant else self
        if resized.remainder == 0 or self.sign == -1:
            return resized.truncate()

        return resized._set_remainder(Decimal(0.5)).__round__()

    def minimize_precision(self) -> "BasedReal":
        """
        Removes unnecessary zeros from fractional part of this BasedReal.

        :return: Minimized BasedReal
        """
        if self.remainder > 0 or self.significant == 0 or self.right[-1] > 0:
            return self

        count = 0
        for x in self.right[::-1]:
            if x != 0:
                break
            count += 1

        return self.truncate(self.significant - count)

    def __lshift__(self, other: int) -> "BasedReal":
        """self << other

        :param other: Amount to shift this BasedReal
        :type other: int
        :return: Shifted number
        :rtype: BasedReal
        """
        return self.shift(-other)

    def __rshift__(self, other: int) -> "BasedReal":
        """self >> other

        :param other: Amount to shift this BasedReal
        :type other: int
        :return: Shifted number
        :rtype: BasedReal
        """
        return self.shift(other)

    def shift(self, i: int) -> "BasedReal":
        """
        Shifts number to the left (-) or the right (+).
        Prefer using >> and << operators (right-shift and left-shift).

        >>> Sexagesimal(3).shift(-1)
        03,00 ;
        >>> Sexagesimal(3).shift(2)
        00 ; 00,03

        :param i: Amount to shift this BasedReal
        :return: Shifted number
        :rtype: BasedReal
        """

        if i == 0:
            return self

        if self.base.mixed:
            raise NotImplementedError

        offset = len(self.left) if i > 0 else len(self.left) - i
        br_rem = self.from_decimal(self.remainder, max(0, offset - len(self[:])))

        left_right = (0,) * i + self[:] + br_rem.right

        left = left_right[:offset]
        right = left_right[offset : -i if -i > offset else None]

        return type(self)(left, right, remainder=br_rem.remainder, sign=self.sign)

    @lru_cache
    def subunit_quantity(self, i: int) -> int:
        """Convert this sexagesimal to the integer value from the specified fractional point.

        >>> number = Sexagesimal("1,0;2,30")

        Amount of minutes in `number`

        >>> number.subunit_quantity(1)
        3602

        Amount of zodiacal signs in `number`

        >>> number.subunit_quantity(-1)
        1

        :param i: Rank of the subunit to compute from.
        :type i: int
        :return: Integer amount of the specified subunit.
        :rtype: int
        """

        res = 0
        factor = 1
        for idx, v in enumerate(self.resize(max(0, i + 1))[i::-1]):
            res += v * factor
            factor *= self.base[i - idx]
        return self.sign * res

    def __round__(self, significant: Optional[int] = None):
        """
        Round this BasedReal object to the specified precision.
        If no precision is specified, the rounding is performed with respect to the
        remainder attribute.

        >>> n = Sexagesimal('02, 02; 07, 23, 55, 11, 51, 21, 36')
        >>> n
        02,02 ; 07,23,55,11,51,21,36
        >>> round(n, 4)
        02,02 ; 07,23,55,12

        :param significant: Number of desired significant positions
        :return: self
        """
        if significant is None:
            significant = self.significant
        n = self.resize(significant)
        if n.remainder >= 0.5:
            with set_precision(
                pmode=PrecisionMode.MAX, tmode=TruncatureMode.NONE, recording=False
            ):
                values = [0] * significant + [1]
                n += type(self)(values[:1], values[1:], sign=self.sign)
        return n.truncate(significant)

    def __getitem__(self, key):
        """
        Allow to get a specific position value of this BasedReal object
        by specifying an index. The position 0 corresponds to the right-most integer position.
        Negative positions correspond to the other integer positions, positive
        positions correspond to the fractional positions.

        :param key: desired index
        :return: value at the specified position
        """
        if isinstance(key, slice):
            array = self.left + self.right
            start = key.start + len(self.left) - 1 if key.start is not None else None
            stop = key.stop + len(self.left) - 1 if key.stop is not None else None
            return array[start : stop : key.step]

        if isinstance(key, int):
            if -len(self.left) < key <= 0:
                return self.left[key - 1]
            if self.significant >= key > 0:
                return self.right[key - 1]
            raise IndexError

        raise TypeError

    @classmethod
    def from_float(
        cls, floa: float, significant: int, remainder_threshold: float = 0.999999
    ) -> "BasedReal":
        """
        Class method to produce a new BasedReal object from a floating number

        >>> Sexagesimal.from_float(1/3, 4)
        00 ; 20,00,00,00

        :param floa: floating value of the number
        :param significant: precision of the number
        :return: a new BasedReal object
        """

        if not isinstance(floa, (int, float)):
            raise TypeError(f"Argument {floa} is not a float")

        integer_part = cls.from_int(int(floa), significant=significant)
        value = abs(floa - int(integer_part))

        right = [0] * significant

        factor = 1.0
        if value != 0:
            for i in range(significant):
                factor = cls.base.right[i]
                value *= factor
                if value - int(value) > remainder_threshold and value + 1 < factor:
                    value = int(value) + 1
                elif value - int(value) < 1 - remainder_threshold and any(
                    x != 0 for x in right
                ):
                    value = int(value)
                position_value = int(value)
                value -= position_value
                right[i] = position_value

        return cls(
            integer_part.left,
            tuple(right),
            remainder=Decimal(value),
            sign=-1 if floa < 0 else 1,
        )

    @classmethod
    def from_decimal(cls, dec: Decimal, significant: int) -> "BasedReal":
        """
        Class method to produce a new BasedReal object from a Decimal number

        >>> Sexagesimal.from_decimal(Decimal('0.1'), 4)
        00 ; 06,00,00,00

        :param dec: floating value of the number
        :param significant: precision of the number
        :return: a new BasedReal object
        """

        if not isinstance(dec, Decimal):
            raise TypeError(f"Argument {dec} is not a Decimal")

        integer_part = cls.from_int(int(dec), significant=significant)
        value = abs(dec - int(integer_part))

        right = [0] * significant

        factor = Decimal(1)
        for i in range(significant):
            factor = cls.base.right[i]
            value *= factor
            position_value = int(value)
            value -= position_value
            right[i] = position_value

        return cls(
            integer_part.left, tuple(right), remainder=value, sign=-1 if dec < 0 else 1
        )

    @classmethod
    def zero(cls, significant=0) -> "BasedReal":
        """
        Class method to produce a zero number of the specified precision

        >>> Sexagesimal.zero(7)
        00 ; 00,00,00,00,00,00,00

        :param significant: desired precision
        :return: a zero number
        """
        return cls((0,), (0,) * significant)

    @classmethod
    def one(cls, significant=0) -> "BasedReal":
        """
        Class method to produce a unit number of the specified precision

        >>> Sexagesimal.one(5)
        01 ; 00,00,00,00,00

        :param significant: desired precision
        :return: a unit number
        """
        return cls((1,), (0,) * significant)

    @classmethod
    @overload
    def range(cls, stop: int) -> Generator["BasedReal", None, None]:
        ...

    @classmethod
    @overload
    def range(cls, start: int, stop: int, step=1) -> Generator["BasedReal", None, None]:
        ...

    @classmethod
    def range(cls, *args, **kwargs) -> Generator["BasedReal", None, None]:
        """
        Range generator, equivalent to `range` builtin but yields `BasedReal` numbers.

        :yield: `BasedReal` integers.
        """
        for i in range(*args, **kwargs):
            yield cls.from_int(i)

    @classmethod
    def from_int(cls, value: int, significant=0) -> "BasedReal":
        """
        Class method to produce a new BasedReal object from an integer number

        >>> Sexagesimal.from_int(12, 4)
        12 ; 00,00,00,00

        :param value: integer value of the number
        :param significant: precision of the number
        :return: a new BasedReal object
        """

        if not np.issubdtype(type(value), np.integer):
            raise TypeError(f"Argument {value} is not an int")

        base = cls.base
        sign = -1 if value < 0 else 1
        value *= sign

        pos = 0
        int_factor = 1

        while value >= int_factor:
            int_factor *= base.left[-1 - pos]
            pos += 1

        left = [0] * pos

        for i in range(pos):
            int_factor //= base.left[-pos + i]
            position_value = value // int_factor
            value -= position_value * int_factor
            left[i] = position_value

        return cls(left, (0,) * significant, sign=sign)

    def __float__(self) -> float:
        """
        Compute the float value of this BasedReal object

        >>> float(Sexagesimal('01;20,00'))
        1.3333333333333333
        >>> float(Sexagesimal('14;30,00'))
        14.5

        :return: float representation of this BasedReal object
        """
        value = float(abs(int(self)))
        factor = 1.0
        for i in range(self.significant):
            factor /= self.base.right[i]
            value += factor * self.right[i]

        value += factor * float(self.remainder)
        return float(value * self.sign)

    def __int__(self) -> int:
        """
        Compute the int value of this BasedReal object
        """
        value = 0
        factor = 1
        for i in range(len(self.left)):
            value += factor * self.left[-i - 1]
            factor *= self.base.left[-i - 1]

        return value * self.sign

    def _truediv(self, _other: PreciseNumber) -> "BasedReal":

        other = cast(BasedReal, _other)

        if self.base.mixed:
            return self.from_float(float(self) / float(other), self.significant)

        max_significant = max(self.significant, other.significant)

        if self == 0:
            return self.zero(significant=max_significant)
        elif other == 1:
            return self
        elif other == -1:
            return -self
        elif other == 0:
            raise ZeroDivisionError

        sign = self.sign * other.sign

        q_res = self.zero(max_significant)
        right = list(q_res.right)

        numerator = abs(self)
        denominator = abs(other)

        q, r = divmod(numerator, denominator)

        q_res += q

        for i in range(0, max_significant):
            numerator = r * self.base.right[i]
            q, r = divmod(numerator, denominator)
            if q == self.base.right[i]:  # pragma: no cover
                q_res += 1
                r = self.zero()
                break
            right[i] = int(q)

        return type(self)(
            q_res.left, right, remainder=r.decimal / denominator.decimal, sign=sign
        )

    def _add(self, _other: PreciseNumber) -> "BasedReal":

        other = cast(BasedReal, _other)

        if self.decimal == -other.decimal:
            return self.zero()

        maxright = max(self.significant, other.significant)
        maxleft = max(len(self.left), len(other.left))
        va = self.resize(maxright)
        vb = other.resize(maxright)

        sign = va.sign if abs(va) > abs(vb) else vb.sign
        if sign < 0:
            va = -va
            vb = -vb

        maxlen = max(len(va[:]), len(vb[:]))
        values = (
            [v.sign * x for x in v[::-1]] + [0] * (maxlen - len(v[:])) for v in (va, vb)
        )
        numbers: List[int] = [a + b for a, b in zip(*values)] + [0]

        remainder = va.remainder * va.sign + vb.remainder * vb.sign
        fn = remainder if remainder >= 0 else remainder - 1
        remainder -= int(fn)
        numbers[0] += int(fn)

        for i, r in enumerate(numbers):
            factor = self.base[maxright - i]
            if r < 0 or r >= factor:
                numbers[i] = r % factor
                numbers[i + 1] += 1 if r > 0 else -1

        numbers = [abs(x) for x in numbers[::-1]]
        left = numbers[: maxleft + 1]
        right = numbers[maxleft + 1 :]

        return type(self)(left, right, remainder=abs(remainder), sign=sign)

    def __add__(self, other) -> "BasedReal":
        """
        self + other

        >>> Sexagesimal('01, 21; 47, 25') + Sexagesimal('45; 32, 14, 22')
        02,07 ; 19,39,22
        """
        if not np.isreal(other):
            raise NotImplementedError

        if type(self) is not type(other):
            return self + self.from_float(float(other), significant=self.significant)

        return super().__add__(other)

    def __radd__(self, other) -> "BasedReal":
        """other + self"""
        return self + other

    def _sub(self, _other: PreciseNumber) -> "BasedReal":

        other = cast(BasedReal, _other)
        return self + -other

    def __rtruediv__(self, other):
        """other / self"""
        return other / float(self)

    def __pow__(self, exponent):
        """self**exponent
        Negative numbers cannot be raised to a non-integer power
        """
        res = self.one(self.significant)

        if exponent == 0:
            return res
        if self == 0:
            return self

        if self < 0 and int(exponent) != exponent:
            raise ValueError(
                "Negative BasedReal cannot be raised to a non-integer power"
            )

        int_exp = int(exponent)
        f_exp = float(exponent - int_exp)

        if int_exp > 0:
            for _ in range(0, int_exp):
                res *= self
        else:
            for _ in range(0, -int_exp):
                res /= self
        res *= float(self) ** f_exp

        return res

    def __rpow__(self, base):
        """base ** self"""
        return self.from_float(float(base), self.significant) ** self

    def __neg__(self) -> "BasedReal":
        """-self"""
        return type(self)(
            self.left, self.right, remainder=self.remainder, sign=-self.sign
        )

    def __pos__(self) -> "BasedReal":
        """+self"""
        return self

    def __abs__(self) -> "BasedReal":
        """
        abs(self)

        >>> abs(Sexagesimal('-12; 14, 15'))
        12 ; 14,15

        :return: the absolute value of self
        """
        if self.sign >= 0:
            return self
        return -self

    def _mul(self, _other: PreciseNumber) -> "BasedReal":

        other = cast(BasedReal, _other)

        if self in (1, -1):
            return other if self == 1 else -other
        if other in (1, -1):
            return self if other == 1 else -self
        if self == 0 or other == 0:
            return self.zero()

        if self.base.mixed:
            return self.from_float(float(self) * float(other), self.significant)

        max_right = max(self.significant, other.significant)

        va = self.resize(max_right)
        vb = other.resize(max_right)

        res_int = int(va << max_right) * int(vb << max_right)

        res = self.from_int(res_int) >> 2 * max_right

        factor = self.base.factor_at_pos(max_right)
        vb_rem = vb.sign * vb.remainder / factor
        va_rem = va.sign * va.remainder / factor

        rem = (
            va.truncate().decimal * vb_rem
            + vb.truncate().decimal * va_rem
            + va_rem * vb_rem
        )

        if rem:
            res += float(rem)

        return res

    @overload
    def __mul__(self, other: Union[float, "BasedReal"]) -> "BasedReal":  # type: ignore
        ...

    @overload
    def __mul__(self, other: Unit) -> "BasedQuantity":
        ...

    def __mul__(self, other):
        """
        self * other

        >>> Sexagesimal('01, 12; 04, 17') * Sexagesimal('7; 45, 55')
        09,19 ; 39,15 |r0.7
        """

        if isinstance(other, UnitBase):
            return BasedQuantity(self, unit=other)

        if not np.isreal(other) or not isinstance(other, SupportsFloat):
            raise NotImplementedError

        if type(self) is not type(other):
            return self * self.from_float(float(other), self.significant)

        return super().__mul__(other)

    def __rmul__(self, other):
        """other * self"""
        return self * other

    def __divmod__(self, other: Any) -> Tuple["BasedReal", "BasedReal"]:
        """divmod(self, other)"""

        if type(self) is type(other):

            if self.base.mixed:
                res = divmod(float(self), float(other))
                return (
                    self.from_float(res[0], self.significant),
                    self.from_float(res[1], self.significant),
                )

            max_sig = max(self.significant, other.significant)
            if self == 0:
                zero = self.zero(max_sig)
                return (zero, zero)

            max_significant = max(self.significant, other.significant)
            s_self = self.resize(max_significant)
            s_other = other.resize(max_significant)
            if s_self.remainder == s_other.remainder == 0:
                qself = s_self.subunit_quantity(max_significant)
                qother = s_other.subunit_quantity(max_significant)
                fdiv, mod = divmod(qself, qother)
                return (
                    self.from_int(fdiv, max_sig),
                    self.from_int(mod) >> max_significant,
                )

            fdiv = math.floor(self.decimal / other.decimal)
            if fdiv == self.decimal / other.decimal:
                mod = Decimal(0)
            else:
                mod = (
                    self.decimal % other.decimal + 0
                    if self.sign == other.sign
                    else other.decimal
                )
            return self.from_int(fdiv, max_sig), self.from_decimal(mod, max_sig)

        if np.isreal(other):
            return divmod(self, self.from_float(float(other), self.significant))

        raise NotImplementedError

    def __floordiv__(self, other) -> "BasedReal":  # type: ignore
        """self // other"""
        return divmod(self, other)[0]

    def __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
        return other // float(self)

    def __mod__(self, other) -> "BasedReal":
        """self % other"""
        return divmod(self, other)[1]

    def __rmod__(self, other):
        """other % self"""
        return other % float(self)

    @overload
    def __truediv__(self, other: Number) -> "BasedReal":  # type: ignore
        ...

    @overload
    def __truediv__(self, other: Unit) -> "BasedQuantity":
        ...

    def __truediv__(self, other) -> "BasedReal":
        """self / other"""
        if isinstance(other, UnitBase):
            return self * (other ** -1)

        if type(self) is type(other):
            return super().__truediv__(other)

        return self / self.from_float(float(other), significant=self.significant)

    def __gt__(self, other) -> bool:
        """self > other"""
        if not isinstance(other, Number):
            return other <= self
        if isinstance(other, BasedReal):
            return self.decimal > other.decimal
        other = cast(SupportsFloat, other)
        return float(self) > float(other)

    def __eq__(self, other) -> bool:
        """self == other"""
        if not isinstance(other, SupportsFloat):
            return False
        if isinstance(other, BasedReal):
            return self.decimal == other.decimal
        return float(self) == float(other)

    def equals(self, other: "BasedReal") -> bool:
        """Tests strict equivalence between this BasedReal and another

        >>> Sexagesimal("1,2;3").equals(Sexagesimal("1,2;3"))
        True
        >>> Sexagesimal("1,2;3").equals(Sexagesimal("1,2;3,0"))
        False

        :param other: The other BasedReal to be compared with the first
        :type other: BasedReal
        :return: True if both objects are the same, False otherwise
        :rtype: bool

        """
        if type(self) is not type(other):
            return False

        return (
            self.left == other.left
            and self.right == other.right
            and self.sign == other.sign
            and self.remainder == other.remainder
        )

    def __ne__(self, other) -> bool:
        """self != other"""
        return not self == other

    def __ge__(self, other) -> bool:
        """self >= other"""
        return self > other or self == other

    def __lt__(self, other) -> bool:
        """self < other"""
        return not self >= other

    def __le__(self, other) -> bool:
        """self <= other"""
        return not self > other

    def __floor__(self):
        """Finds the greatest Integral <= self."""
        return self.__trunc__() + (1 if self.sign < 0 else 0)

    def __ceil__(self):
        """Finds the least Integral >= self."""
        return self.__trunc__() + (1 if self.sign > 0 else 0)

    def __hash__(self) -> int:
        if self.remainder == 0 and all([x == 0 for x in self.right]):
            return int(self)
        return hash((self.left, self.right, self.sign, self.remainder))

    def sqrt(self, iteration: Optional[int] = None) -> "BasedReal":
        """Returns the square root, using Babylonian method

        :param iteration: Number of iterations, defaults to the significant number
        :type iteration: Optional[int], optional
        """
        if self.sign < 0:
            raise ValueError("Square root domain error")

        if self == 0:
            return self

        if iteration is None:
            iteration = self._get_significant(self)

        if self >= 1:
            res = self.from_int(int(math.sqrt(float(self))))
        else:
            res = self.from_float(math.sqrt(float(self)), self.significant)
            iteration = 0

        for _ in range(iteration):
            res += self / res
            res /= 2

        return res

    def _set_remainder(self, remainder: Decimal) -> "BasedReal":
        return type(self)(self.left, self.right, sign=self.sign, remainder=remainder)


class BasedQuantity(Quantity):

    value: BasedReal

    def __new__(cls, value, unit, **kwargs):
        if (
            not isinstance(value, BasedReal)
            or isinstance(value, (Sequence, np.ndarray))
            and not all(isinstance(v, BasedReal) for v in value)
        ):
            return Quantity(value, unit, **kwargs)

        def _len(_):
            del type(value).__len__
            return 0

        type(value).__len__ = _len
        self = super().__new__(cls, value, unit=unit, dtype=object, **kwargs)
        return self

    def __mul__(self, other) -> "BasedQuantity":  # pragma: no cover
        return super().__mul__(other)

    def __add__(self, other) -> "BasedQuantity":  # pragma: no cover
        return super().__add__(other)

    def __sub__(self, other) -> "BasedQuantity":  # pragma: no cover
        return super().__sub__(other)

    def __truediv__(self, other) -> "BasedQuantity":  # pragma: no cover
        return super().__truediv__(other)

    def __lshift__(self, other) -> "BasedQuantity":
        if isinstance(other, Number):
            return super(Quantity, self).__lshift__(other)
        return super().__lshift__(other)

    def __rshift__(self, other) -> "BasedQuantity":
        if isinstance(other, Number):
            return super(Quantity, self).__rshift__(other)
        return super().__rshift__(other)

    def __getattr__(self, attr: str):
        if attr.startswith(("_", "__")) and not attr.endswith("__"):
            raise AttributeError
        vect = np.frompyfunc(lambda x: getattr(x, attr), 1, 1)
        properties = ("left", "right", "significant", "sign", "remainder", "base")
        unit = _d(self.unit) if attr not in properties else None
        UFUNC_HELPERS[vect] = lambda *_: ([None, None], unit)
        if callable(getattr(BasedReal, attr)):

            def _new_func(*args):
                vfunc = np.frompyfunc(lambda x: x(*args), 1, 1)
                UFUNC_HELPERS[vfunc] = lambda *_: ([None, None], unit)
                return vfunc(vect(self))

            return _new_func
        return vect(self)

    def __round__(self, significant: Optional[int] = None) -> "BasedQuantity":
        return self.__getattr__("__round__")(significant)

    def __abs__(self) -> "BasedQuantity":  # pragma: no cover
        return self.__getattr__("__abs__")()

    def __quantity_subclass__(self, _):
        return type(self), True


# here we define standard bases and automatically generate the corresponding BasedReal classes
RadixBase([60], [60], "sexagesimal")
RadixBase([10, 12, 30], [60], "historical", ["", "r ", "s "])
RadixBase([10], [100], "historical_decimal")
RadixBase([10], [60], "integer_and_sexagesimal")
RadixBase([10], [24, 60], "temporal")
# add new definitions here, corresponding BasedReal inherited classes will be automatically generated


def _shift_helper(f, unit1, unit2):
    if unit2:  # pragma: no cover
        raise UnitTypeError(
            "Can only apply '{}' function to "
            "dimensionless quantities".format(f.__name__)
        )
    return [None, None], _d(unit1)


UFUNC_HELPERS[np.left_shift] = _shift_helper
UFUNC_HELPERS[np.right_shift] = _shift_helper


class BasedRealException(Exception):
    pass


class EmptyStringException(BasedRealException, ValueError):
    pass


class TooManySeparators(BasedRealException, ValueError):
    pass


class IllegalBaseValueError(BasedRealException, ValueError):
    """
    Raised when a value is not in the range of the specified base.

    ```python
    if not 0 <= val < radix[i]:
        raise IllegalBaseValueError(radix, radix[i], val)
    ```
    """

    def __init__(self, radix, base, num):
        super().__init__()
        self.radix = radix
        self.base = base
        self.num = num

    def __str__(self):
        return f"An invalid value for ({self.radix.name}) was found \
        ('{self.num}'); should be in the range [0,{self.base}[)."


class IllegalFloatError(BasedRealException, TypeError):
    """
    Raised when an expected int value is a float.

    ```python
    if isinstance(val, float):
        raise IllegalFloatError(val)
    ```
    """

    def __init__(self, num):
        super().__init__()
        self.num = num

    def __str__(self):
        return f"An illegal float value was found ('{self.num}')"
