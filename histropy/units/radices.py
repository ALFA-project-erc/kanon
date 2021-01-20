import math
import warnings
from decimal import Decimal
from fractions import Fraction
from functools import cached_property, lru_cache
from numbers import Number, Real
from typing import (Any, ClassVar, Dict, Iterable, List, Literal, Optional,
                    Tuple, Type)

import numpy as np

from histropy.utils.list_to_tuple import list_to_tuple
from histropy.utils.looping_list import LoopingList

from .errors import (EmptyStringException, IllegalBaseValueError,
                     IllegalFloatValueError, TooManySeparators)

"""
In this module we define RadixBase and BasedReal.
RadixBase is the basis of the way we work with different radices.
BasedReal are a class of Real numbers with a 1-1 relation with a RadixBase.
"""

__all__ = ["RadixBase", "BasedReal", "radix_registry"]


radix_registry: ClassVar[Dict[str, Type["BasedReal"]]] = {}
"""
Registry containing all instanciated BasedReal classes.
"""


class RadixBase:
    """
    A class representing a numeral system. A radix must be specified at each position,
    by specifying an integer list for the integer positions, and an integer list for the
    fractional positions.
    """

    def __init__(
        self,
        left: Iterable[int],
        right: Iterable[int],
        name: str,
        integer_separators: Optional[Iterable[str]] = None,
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
        assert len(left) > 0 < len(right)
        assert all(isinstance(x, int) for x in left)
        assert all(isinstance(x, int) for x in right)

        self.left: LoopingList[int] = LoopingList(left)
        self.right: LoopingList[int] = LoopingList(right)
        self.name = name
        if integer_separators is not None:
            self.integer_separators: LoopingList[str] = LoopingList(
                integer_separators)
        else:
            self.integer_separators: LoopingList[str] = LoopingList([
                "," if x != 10 else "" for x in left
            ])

        self.mixed = any(x != left[0] for x in left)
        self.mixed = any(x != right[0] for x in right)

        # Build a class inheriting from BasedReal, that will use this RadixBase as
        # its numeral system.
        type_name = "".join(map(str.capitalize, self.name.split("_")))
        if type_name in radix_registry:
            raise ValueError(f"Name {type_name} already exists in registry")

        new_type = type(type_name, (BasedReal,), {"base": self})
        radix_registry[type_name] = new_type

        # Store the newly created BasedReal class
        self.type: Type[BasedReal] = new_type

    def __getitem__(self, pos: int) -> int:
        """
        Return the radix at the specified position. Position 0 represents the last integer
        position before the fractional part (i.e. the position just before the ';' in sexagesimal
        notation, or just before the '.' in decimal notation). Positive positions represent
        the fractional positions, negative positions represent the integer positions.

        :param pos: Position. <= 0 for integer part (with 0 being the right-most integer position), > 0 for fractional part
        :return: Radix at the specified position
        """
        if pos <= 0:
            return self.left[pos - 1]
        else:
            return self.right[pos - 1]

    @lru_cache(maxsize=None)
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

    @lru_cache(maxsize=None)
    def mul_factor(self, i, j):
        numerator = 1
        for k in range(1, i + j + 1):
            numerator *= self[k]
        denom_i = 1
        for k in range(1, i + 1):
            denom_i *= self[k]
        denom_j = 1
        for k in range(1, j + 1):
            denom_j *= self[k]
        if numerator % (denom_i * denom_j) == 0:
            return numerator // (denom_i * denom_j)
        return numerator / (denom_i * denom_j)


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


class BasedReal(Real):
    """
    Abstract class allowing to represent a value in a specific RadixBase.
    Each time a new RadixBase object is recorded, a new class inheriting from BasedReal
    is created and recorded in radix_registry.
    The RadixBase to be used will be placed in the class attribute 'base'

    Class attributes:
       - base :        A RadixBase object (will be attributed dynamically to the children inheriting this class)
    """

    base: RadixBase
    """
    RadixBase of this BasedReal
    """
    __left: Tuple[int]
    __right: Tuple[int]
    __remainder: Decimal
    __sign: Literal[-1, 1]
    __slots__ = ('base', '__left', '__right', '__remainder', '__sign')

    def __check_range(self):
        """
        Checks that the given values are in the range of the base and are integers.
        """
        if self.sign not in (-1, 1):
            raise ValueError("Sign should be -1 or 1")
        if not (isinstance(self.remainder, Decimal) and 0 <= self.remainder < 1):
            if self.remainder == 1:
                self += (self.one() * self.sign) >> self.significant
            else:
                raise ValueError(f"Illegal remainder value ({self.remainder}), should be a Decimal between [0.,1.[")
        if self.base.factor_at_pos(len(self.left) - 1) > 1e+15:
            warnings.warn("""
                        Integer part of this number exceeds floating point precision.
                        Calculations made with this number might return incorrect results
                        """)
        for x in self[:]:
            if isinstance(x, float):
                raise IllegalFloatValueError(x)
            elif not isinstance(x, int):
                raise ValueError(f"{x} not an int")
        for i, s in enumerate(self[:]):
            if s < 0. or s >= self.base[i - len(self.left) + 1]:
                raise IllegalBaseValueError(self.base, self.base[i - len(self.left) + 1], s)

    def __simplify_integer_part(self) -> int:
        """
        Remove the useless trailing zeros in the integer part and return how many were removed
        """
        count = 0
        for i in self.left:
            if i != 0:
                break
            count += 1
        if count > 0:
            self.__left = self.left[count:]

        return count != 0

    @list_to_tuple
    @lru_cache(maxsize=None)
    def __new__(cls, *args, remainder=Decimal(0.0), sign=1) -> "BasedReal":
        """Constructs a number with a given radix.

        Arguments:

        - a String

        >>> Sexagesimal("-2,31;12,30")
        -02,31 ; 12,30

        - 2 Sequences representing integral part and fractional part

        >>> Sexagesimal((2,31), (12,30), sign=-1)
        -02,31 ; 12,30
        >>> Sexagesimal([2,31], [12,30])
        02,31 ; 12,30

        - a BasedReal with a significant number of digits,

        >>> Sexagesimal(Sexagesimal("-2,31;12,30"), 1)
        -02,31 ; 12 |r0.5

        - multiple integers representing an integral number in current base

        >>> Sexagesimal(21, 1, 3)
        21,01,03 ;

        :param remainder: When a computation requires more precision than the precision \
        of this number, we store a Decimal remainder to keep track of it, defaults to 0.0
        :type remainder: Decimal, optional
        :param sign: The sign of this number, defaults to 1
        :type sign: int, optional
        :raises ValueError: Unexpected or illegal arguments
        :rtype: BasedReal
        """
        if cls is BasedReal:
            raise TypeError("Can't instanciate abstract class BasedReal")
        self = super().__new__(cls)
        self.__left = ()
        self.__right = ()
        self.__remainder = remainder
        self.__sign = sign
        if np.all([isinstance(x, int) for x in args]):
            return cls.__new__(cls, args, (), remainder=remainder, sign=sign)
        elif len(args) == 2:
            if isinstance(args[0], BasedReal):
                return cls.base.type.from_decimal(args[0].decimal, args[1])
            elif isinstance(args[0], tuple) and isinstance(args[1], tuple):
                self.__left = args[0]
                self.__right = args[1]
            elif all([isinstance(a, Iterable) and not isinstance(a, str) for a in args]):
                return cls.__new__(cls, tuple(args[0]), tuple(args[1]), remainder=remainder, sign=sign)
            else:
                raise ValueError("Incorrect parameters at BasedReal creation")
        elif len(args) == 1:
            if isinstance(args[0], str):
                return cls._from_string(args[0])
            raise ValueError(
                "Please specify a number of significant positions" if isinstance(args[0], Number)
                else "Incorrect parameters at BasedReal creation"
            )
        else:
            raise ValueError(
                "Incorrect number of parameter at BasedReal creation")

        self.__check_range()

        if self.__simplify_integer_part():
            return cls.__new__(cls, self.left, self.right, remainder=self.remainder, sign=self.sign)

        if len(self.__left) == 0:
            self.__left = (0,)

        return self

    @property
    def left(self) -> Tuple[int]:
        """
        Tuple of values at integer positions

        >>> Sexagesimal(1,2,3).left
        (1, 2, 3)

        :rtype: Tuple[int]
        """
        return self.__left

    @property
    def right(self) -> Tuple[int]:
        """
        Tuple of values at fractional positions

        >>> Sexagesimal((1,2,3), (4,5)).right
        (4, 5)

        :rtype: Tuple[int]
        """
        return self.__right

    @property
    def remainder(self) -> Decimal:
        """
        When a computation requires more significant figures than the precision of this number,
        we store a Decimal remainder to keep track of it

        >>> Sexagesimal(1,2,3, remainder=Decimal("0.2")).remainder
        Decimal('0.2')

        :return: Remainder of this BasedReal
        :rtype: Decimal
        """
        return self.__remainder

    @property
    def sign(self) -> Literal[-1, 1]:
        """
        Sign of this BasedReal

        >>> Sexagesimal(1,2,3, sign=-1).sign
        -1

        :rtype: Literal[-1, 1]
        """
        return self.__sign

    @property
    def significant(self) -> int:
        """
        Precision of this BasedReal (equals to length of fractional part)

        >>> Sexagesimal((1,2,3), (4,5)).significant
        2

        :rtype: int
        """
        return len(self.right)

    @cached_property
    def decimal(self) -> Decimal:
        """
        This BasedNumber converted as a Decimal

        >>> Sexagesimal((1,2,3), (15,36)).decimal
        Decimal('3723.26')

        :rtype: Decimal
        """
        value = Decimal()
        factor = Decimal(1)
        for i in range(len(self.left)):
            value += factor * self.left[-i - 1]
            factor *= self.base.left[i]
        factor = Decimal(1)
        for i in range(self.significant):
            factor *= self.base.right[i]
            value += self.right[i] / factor

        value += self.remainder / factor
        return value * self.sign

    def to_fraction(self) -> Fraction:
        """
        :return: this BasedReal as a Fraction object.
        """
        return Fraction(self.decimal.as_integer_ratio())

    @classmethod
    def from_fraction(
        cls,
        fraction: Fraction,
        significant: Optional[int] = None,
    ) -> "BasedReal":
        """
        :param fraction: a Fraction object
        :param significant: signifcant precision desired
        :return: a BasedReal object computed from a Fraction
        """

        if not isinstance(fraction, Fraction):
            raise ValueError(f"Argument {fraction} is not a Fraction")

        num, den = fraction.as_integer_ratio()
        res: BasedReal = cls.from_decimal(Decimal(num) / Decimal(den), significant or 100)

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
                res += self.base.integer_separators[i]
            num = str(self.left[i])
            digit = ndigit_for_radix(self.base.left[i])
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
        Instantiate a BasedReal object from a string

        >>> Sexagesimal('1, 12; 4, 25')
        01,12 ; 04,25
        >>> Historical('2r 7s 29; 45, 2')
        2r 07s 29 ; 45,02
        >>> Sexagesimal('0 ; 4, 45')
        00 ; 04,45

        :param string: String representation of the number
        :return: a new instance of BasedReal
        """

        if not isinstance(string, str):
            raise ValueError(f"Argument {string} is not a str")

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

        left_numbers = []
        right_numbers = []

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
                else:
                    value = rleft[0]
                    rem = rleft[1:]
                left_numbers.insert(0, int(value[::-1]))
                rleft = rem.strip()
                if len(rleft) == 1:
                    break
            left_numbers.insert(0, int(rleft[::-1]))

        return cls(left_numbers, right_numbers, sign=sign)

    def resize(self, significant: int):
        """
        Resizes and returns a new BasedReal object to the specified precision

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
        :return: Resized BasedReal
        """
        if significant == self.significant:
            return self
        if significant > self.significant:
            rem = type(self).from_decimal(self.sign * self.remainder, significant - self.significant)
            return type(self)(self.left, self.right + rem.right, remainder=rem.remainder, sign=self.sign)
        elif significant >= 0:
            remainder = type(self)(
                (), self.right[significant:], remainder=self.remainder)

            return type(self)(self.left, self.right[:significant], remainder=remainder.decimal, sign=self.sign)
        else:
            raise NotImplementedError

    def __trunc__(self):
        return int(float(self.truncate(0)))

    def truncate(self, n: Optional[int] = None) -> "BasedReal":
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
        if n is None:
            n = self.significant
        if n > self.significant:
            return self
        left = self.left if n >= 0 else self.left[:-n]
        right = self.right[:n] if n >= 0 else ()
        return type(self)(left, right, sign=self.sign)

    def minimize_precision(self) -> "BasedReal":
        """
        Removes unnecessary zeros from fractional part if this BasedReal.

        :return: Minimized BasedReal
        """
        if self.remainder > 0 or self.right[-1] > 0:
            return self

        right = self.right
        for x in self.right[::-1]:
            if x != 0:
                return right
            right = right[:-1]

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

        else:

            offset = len(self.left) if i > 0 else len(self.left) - i
            remainder = self.from_decimal(self.remainder, max(0, offset - len(self[:])))

            left_right = (0,) * i + self[:] + remainder.right

            left = left_right[:offset]
            right = left_right[offset:-i if -i > offset else None]

        return type(self)(left, right, remainder=remainder.remainder, sign=self.sign)

    def subunit_quantity(self, i: int) -> int:
        return round(self >> i)

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
            n += type(self)(1, sign=self.sign) >> significant
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
            return array[start:stop:key.step]
        elif isinstance(key, int):
            if -len(self.left) < key <= 0:
                return self.left[key - 1]
            elif self.significant >= key > 0:
                return self.right[key - 1]
            else:
                raise IndexError
        else:
            raise TypeError

    @classmethod
    def from_float(cls, floa: float, significant: int) -> "BasedReal":
        """
        Class method to produce a new BasedReal object from a floating number

        >>> Sexagesimal.from_float(1/3, 4)
        00 ; 20,00,00,00

        :param floa: floating value of the number
        :param significant: precision of the number
        :return: a new BasedReal object
        """

        if not isinstance(floa, (int, float)):
            raise ValueError(f"Argument {floa} is not a float")

        integer_part = cls.from_int(int(floa), significant=significant)
        value = abs(floa - int(integer_part))

        right = [0] * significant

        factor = 1.0
        for i in range(significant):
            factor = cls.base.right[i]
            value *= factor
            position_value = int(value)
            value -= position_value
            right[i] = position_value

        return cls(integer_part.left, tuple(right), remainder=Decimal(value), sign=-1 if floa < 0 else 1)

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
            raise ValueError(f"Argument {dec} is not a Decimal")

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

        return cls(integer_part.left, tuple(right), remainder=value, sign=-1 if dec < 0 else 1)

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
    def from_int(cls, value: int, significant=0) -> "BasedReal":
        """
        Class method to produce a new BasedReal object from an integer number

        >>> Sexagesimal.from_int(12, 4)
        12 ; 00,00,00,00

        :param value: integer value of the number
        :param significant: precision of the number
        :return: a new BasedReal object
        """

        if not isinstance(value, int):
            raise ValueError(f"Argument {value} is not an int")

        base = cls.base
        sign = -1 if value < 0 else 1
        value *= sign

        pos = 0
        max_integer = 1

        while value >= max_integer:
            max_integer *= base.left[pos]
            pos += 1

        left = [0] * pos

        int_factor = max_integer

        for i in range(pos):
            int_factor //= base.left[i]
            position_value = int(value / int_factor)
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
        value = abs(int(self))
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
            factor *= self.base.left[i]

        return value * self.sign

    def division(self, other: "BasedReal", significant: int) -> "BasedReal":
        """
        Divide this BasedReal object with another

        :param other: the other BasedReal object
        :param significant: the number of desired significant positions
        :return: the division of the two BasedReal objects
        """

        if self == 0:
            return self.zero(significant=significant)
        if other == 1:
            return self
        if other == -1:
            return -self

        sign = self.sign * other.sign

        q_res = self.zero(significant)
        right = list(q_res.right)

        numerator = abs(self)
        denominator = abs(other)

        q, r = divmod(numerator, denominator)

        q_res += q

        for i in range(0, significant):
            numerator = r * self.base.right[i]
            q, r = divmod(numerator, denominator)
            if q == self.base.right[i]:
                q_res += 1
                r = self.zero()
                break
            right[i] = int(q)

        return type(self)(q_res.left, right, remainder=r.decimal / denominator.decimal, sign=sign)

    def __add__(self, other: "BasedReal") -> "BasedReal":
        """
        self + other

        >>> Sexagesimal('01, 21; 47, 25') + Sexagesimal('45; 32, 14, 22')
        02,07 ; 19,39 |r0.4

        :param other:
        :return: the sum of the two BasedReal objects
        """
        if type(self) is not type(other):
            return self + self.from_float(float(other), significant=self.significant)

        if self.decimal == -other.decimal:
            return self.zero(min(self.significant, other.significant))

        maxright = max(self.significant, other.significant)
        maxleft = max(len(self.left), len(other.left))
        va = self.resize(maxright)
        vb = other.resize(maxright)

        sign = va.sign if abs(va) > abs(vb) else vb.sign
        if sign < 0:
            va = -va
            vb = -vb

        maxlen = max(len(va[:]), len(vb[:]))
        values = ([v.sign * x for x in v[::-1]] + [0] * (maxlen - len(v[:])) for v in (va, vb))
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

        numbers = tuple(abs(x) for x in numbers[::-1])
        left = numbers[:maxleft + 1]
        right = numbers[maxleft + 1:]

        return type(self)(left, right, remainder=abs(remainder), sign=sign).resize(min(self.significant, other.significant))

    def __radd__(self, other) -> "BasedReal":
        """other + self"""
        return self + other

    def __sub__(self, other: "BasedReal") -> "BasedReal":
        """self - other"""
        return self + -other

    def __rsub__(self, other) -> "BasedReal":
        """other - self"""
        return other + -self

    def __rtruediv__(self, other):
        """other / self"""
        return other / float(self)

    def __pow__(self, exponent):
        """self**exponent; should promote to float or complex when necessary."""
        res = self.one(self.significant)

        if exponent == 0:
            return res
        if self == 0:
            return self

        int_exp = int(exponent)
        f_exp = float(exponent - int_exp)

        if int_exp > 0:
            for _ in range(0, int_exp):
                res *= self
        else:
            for _ in range(0, -int_exp):
                res /= self
        res *= (float(self) ** f_exp).real

        return res

    def __rpow__(self, base):
        """base ** self"""
        return self.from_float(float(base), self.significant) ** self

    def conjugate(self):
        """(x+y*i).conjugate() returns (x-y*i)."""
        return self

    def __neg__(self) -> "BasedReal":
        """-self"""
        return type(self)(self.left, self.right, remainder=self.remainder, sign=-self.sign)

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

    def __mul__(self, other: "BasedReal") -> "BasedReal":
        """
        self * other

        >>> Sexagesimal('01, 12; 04, 17') * Sexagesimal('7; 45, 55')
        09,19 ; 39,15 |r0.7

        :param other: The other BasedReal to multiply
        :return: The product of the 2 BasedReal object
        """
        if type(self) is not type(other):
            return self * self.from_float(other, self.significant)

        if self == 1:
            return other
        if self == -1:
            return -other
        if other == 1:
            return self
        if other == -1:
            return -self
        if self == 0 or other == 0:
            return self.zero(max(self.significant, other.significant))

        sign = self.sign * other.sign

        max_right = max(self.significant, other.significant)

        va = self.resize(max_right)
        vb = other.resize(max_right)

        numbers = [[0] * i + [fv * s for s in vb[:]][::-1]
                   for i, fv in enumerate(va[::-1])]

        count = [0] * max(len(x) for x in numbers) + [0]

        for n in numbers:
            for i, r in enumerate(n):
                count[i] += r
                factor = self.base[max_right - i]
                n = count[i]
                if n < 0 or n >= factor:
                    count[i] = n % factor
                    count[i + 1] += n // factor

        while count[-1] != 0:
            factor = self.base[max_right - len(count)]
            n = count[-1]
            count[-1] = n % factor
            count.append(n // factor)

        res = type(self)(*tuple(count[::-1]), sign=sign)
        res = res >> 2 * max_right

        factor = self.base.factor_at_pos(max_right)
        vb_rem = vb.sign * vb.remainder / factor
        va_rem = va.sign * va.remainder / factor
        res += float(va.truncate().decimal * vb_rem
                     + vb.truncate().decimal * va_rem
                     + va_rem * vb_rem
                     )

        return res.resize(min(self.significant, other.significant))

    def __rmul__(self, other):
        """other * self"""
        return self * other

    def __divmod__(self, other: Any) -> Tuple["BasedReal", "BasedReal"]:
        """divmod(self, other)"""

        if type(self) is type(other):

            min_significant = min(self.significant, other.significant)
            if self == 0:
                return (self.zero(min_significant),) * 2

            max_significant = max(self.significant, other.significant)
            s_self = self << max_significant
            s_other = other << max_significant
            if s_self.remainder == s_other.remainder == 0:
                fdiv, mod = divmod(int(s_self), int(s_other))
                return self.from_int(fdiv, min_significant), self.from_int(mod, min_significant) >> max_significant
            else:
                fdiv = math.floor(self.decimal / other.decimal)
                if fdiv == self.decimal / other.decimal:
                    mod = Decimal(0)
                else:
                    mod = self.decimal % other.decimal + 0 if self.sign == other.sign else other.decimal
                return self.from_int(
                    fdiv, min_significant
                ), self.from_decimal(mod, min_significant)
        elif isinstance(other, Number):
            return divmod(self, self.from_float(float(other), self.significant))
        else:
            raise TypeError

    def __floordiv__(self, other: Number) -> "BasedReal":
        """self // other"""
        return divmod(self, other)[0]

    def __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
        return other // float(self)

    def __mod__(self, other: "BasedReal") -> "BasedReal":
        """self % other"""
        return divmod(self, other)[1]

    def __rmod__(self, other):
        """other % self"""
        return other % float(self)

    def __truediv__(self, other: "BasedReal") -> "BasedReal":
        """
        self / other
        NB: To specify the precision of the result (i.e. its number of significant positions) you should use the
        division method. By default it will take the maximum of significant places + 1

        :param other: the other BasedReal object
        :return: the division of self with other
        """
        if type(self) is type(other):
            return self.division(other, min(self.significant, other.significant) + 1)
        elif isinstance(other, Number):
            return self / self.from_float(float(other), significant=self.significant)
        else:
            raise TypeError

    def __gt__(self, other: Number) -> bool:
        """self > other"""
        if type(self) is type(other):
            return self.decimal > other.decimal
        return float(self) > float(other)

    def __eq__(self, other: Number) -> bool:
        """self == other"""
        if type(self) is type(other):
            return self.decimal == other.decimal
        return float(self) == float(other)

    def __ne__(self, other: object) -> bool:
        """self != other"""
        return not self == other

    def __ge__(self, other: "BasedReal") -> bool:
        """self >= other"""
        return self == other or self > other

    def __lt__(self, other: "BasedReal") -> bool:
        """self < other"""
        return not self >= other

    def __le__(self, other: "BasedReal") -> bool:
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

    def sqrt(self, precision=None):
        raise NotImplementedError
        return type(self).from_float(math.sqrt(float(self)), self.significant)


# here we define standard bases and automatically generate the corresponding BasedReal classes
RadixBase([60], [60], "sexagesimal")
RadixBase([60], [60], "floating_sexagesimal")
RadixBase([10, 12, 30], [60], "historical", ["", "r ", "s "])
RadixBase([10], [100], "historical_decimal")
RadixBase([10], [60], "integer_and_sexagesimal")
RadixBase([10], [24, 60], "temporal")
# add new definitions here, corresponding BasedReal inherited classes will be automatically generated

Sexagesimal = radix_registry["Sexagesimal"]
Historical = radix_registry["Historical"]
