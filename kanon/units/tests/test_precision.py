from decimal import Decimal
from typing import Type

import pytest

from kanon.units import BasedReal, Sexagesimal
from kanon.units.precision import (PrecisionMode, TruncatureMode,
                                   _with_context_precision, set_precision)

Sexagesimal: Type[BasedReal]


class TestPrecision:

    def equality(self, a: Sexagesimal, b: Sexagesimal):
        assert a.equals(b), f"{a},r:{a.remainder} != {b},r:{b.remainder}"

    def test_precision_modes(self):
        s1 = Sexagesimal("0;30,0,0,6")
        s2 = Sexagesimal(2)
        with set_precision(pmode=PrecisionMode.MAX):
            self.equality(s1 + s2, Sexagesimal("2;30,0,0,6"))
            self.equality(s1 * s2, Sexagesimal("1;0,0,0,12"))
            self.equality(s1 / s2, Sexagesimal("0;15,0,0,3"))

        with set_precision(pmode=PrecisionMode.SCI):
            s1_ = s1.truncate(3)
            self.equality(s1_ + s2, Sexagesimal(2, remainder=Decimal("0.5")))
            self.equality(s1_ * s2, Sexagesimal(1))
            self.equality(s1_ / s2, Sexagesimal(0, remainder=Decimal("0.25")))

        with set_precision(pmode=3):
            self.equality(s1 + s2, Sexagesimal((2,), (30, 0, 0), remainder=Decimal("0.1")))
            self.equality(s1 * s2, Sexagesimal((1,), (0, 0, 0), remainder=Decimal("0.2")))
            self.equality(s1 / s2, Sexagesimal((0,), (15, 0, 0), remainder=Decimal("0.05")))

            assert round(Sexagesimal(2, remainder=Decimal("0.5"))) == 3

        with pytest.raises(NotImplementedError):
            with set_precision(pmode=PrecisionMode.FULL):
                s1 + s2

        with pytest.raises(ValueError):
            with set_precision(pmode=-1):
                pass

    def test_truncature_modes(self):
        s1 = Sexagesimal("0;30,0,0,6")
        s2 = Sexagesimal(2)
        with set_precision(tmode=TruncatureMode.ROUND):
            self.equality(s1 + s2, Sexagesimal(3))
            self.equality(s1 * s2, Sexagesimal(1))
            self.equality(s1 / s2, Sexagesimal(0))
            self.equality(s1 / Sexagesimal(1), Sexagesimal(1))
        with set_precision(tmode=TruncatureMode.TRUNC):
            self.equality(s1 + s2, Sexagesimal(2))
            self.equality(s1 * s2, Sexagesimal(1))
            self.equality(s1 / s2, Sexagesimal(0))
            self.equality(s1 / Sexagesimal(1), Sexagesimal(0))
        with set_precision(tmode=TruncatureMode.FLOOR):
            self.equality(s1 + s2, Sexagesimal(2))
            self.equality(s1 * s2, Sexagesimal(1))
            self.equality(s1 / s2, Sexagesimal(0))
            self.equality(s1 / Sexagesimal(1), Sexagesimal(0))
            self.equality(-s1 + -s2, -Sexagesimal(3))
            self.equality(s1 * -s2, -Sexagesimal(2))
            self.equality(s1 / -s2, -Sexagesimal(1))
            self.equality(-s1 / Sexagesimal(1), -Sexagesimal(1))
        with set_precision(tmode=TruncatureMode.CEIL):
            self.equality(s1 + s2, Sexagesimal(3))
            self.equality(s1 * s2, Sexagesimal(2))
            self.equality(s1 / s2, Sexagesimal(1))
            self.equality(s1 / Sexagesimal(1), Sexagesimal(1))
            self.equality(-s1 + -s2, -Sexagesimal(2))
            self.equality(s1 * -s2, -Sexagesimal(1))
            self.equality(s1 / -s2, -Sexagesimal(0))
            self.equality(-s1 / Sexagesimal(1), -Sexagesimal(0))

        with pytest.raises(TypeError):
            with set_precision(tmode=1):
                pass

    def test_wrapper(self):
        @_with_context_precision
        def func(a, b):
            return 1

        with pytest.raises(TypeError):
            func(Sexagesimal(1), Sexagesimal(2))
        assert func(1, 2) == 1
