import math as m
import operator as op
from decimal import Decimal, InvalidOperation
from typing import Type

import hypothesis
import pytest
from hypothesis import strategies as st
from hypothesis.core import given
from hypothesis.strategies._internal.core import integers

from histropy.units import BasedReal, Historical, Sexagesimal
from histropy.units.errors import IllegalBaseValueError, IllegalFloatValueError

Sexagesimal: Type[BasedReal]
Historical: Type[BasedReal]


class TestRadix:

    def test_bases(self):
        assert Historical('2r 7s 29; 45') == 339.75
        with pytest.raises(IllegalBaseValueError):
            Historical((-6, 3), ())
        with pytest.raises(IllegalBaseValueError):
            Historical((11, 10, 10), ())

    def test_init(self):
        s = Sexagesimal((1, 2), (30,))
        assert float(s) == 62.5
        assert s == 62.5
        s = -Sexagesimal((1, 2), (30,))
        assert s == -62.5
        s = Sexagesimal((0, 0, 1, 2), (30, 0))
        assert s == Sexagesimal((1, 2), (30,))
        s = Sexagesimal((0, 0), (36,))
        assert s == 0.6
        assert s.decimal == Decimal('0.6')
        assert s.left == (0,)
        s = Sexagesimal((0, 0), (3,), remainder=Decimal('0.5'))
        assert s == 3.5 * 1 / 60

        assert Sexagesimal((), (0, 0, 0, 0)).right == (0, 0, 0, 0)

        assert Sexagesimal(1, 2, 3, sign=-1) == -3723

        assert Sexagesimal("-1,2,3;30") == -3723.5

        assert Sexagesimal((1, 2, 3, 4, 5), (6, 7, 8))[:] == (1, 2, 3, 4, 5, 6, 7, 8)

        assert Sexagesimal((1, 2, 31), (6, 7, 8), sign=-1).__repr__() == "-01,02,31 ; 06,07,08"
        assert Sexagesimal((1, 2, 31), (6,), sign=-1, remainder=Decimal('0.3')).__repr__() == "-01,02,31 ; 06 |r0.3"

        with pytest.raises(IllegalBaseValueError):
            Sexagesimal((-6, 3), ())
        with pytest.raises(IllegalFloatValueError):
            Sexagesimal((0.3, 5), (6, 8))
        with pytest.raises(ValueError):
            Sexagesimal(3, 5, remainder=Decimal(-5))
        with pytest.raises(ValueError):
            Sexagesimal(3, 5, remainder=0.6)

        with pytest.raises(TypeError):
            BasedReal()

    def test_build(self):
        assert Sexagesimal.from_float(0.5, 4) == Sexagesimal((), (30,))
        assert Sexagesimal.from_float(-0.016666666666666666, 2) == -Sexagesimal((0,), (1,))
        assert Sexagesimal.from_float(0.5, 4).right == (30, 0, 0, 0)
        assert Sexagesimal.from_int(5, 2) == Sexagesimal(5)
        assert Sexagesimal("21,1,6,3;34") == Sexagesimal((21, 1, 6, 3), (34,))

    def test_get(self):
        s = Sexagesimal((1, 2, 30), (18,))
        assert s[-2] == 1
        assert s[-1] == 2
        assert s[0] == 30
        assert s[1] == 18
        assert s[:] == (1, 2, 30, 18)
        assert s[:0] == (1, 2)
        assert s[3::-1] == (18, 30, 2, 1)
        assert s[-1:] == (2, 30, 18)
        s = Sexagesimal((1, 2, 3, 4, 5, 6), (7, 8, 9, 10))
        assert s[-4:1] == (2, 3, 4, 5, 6)

    def test_shift(self):
        s = Sexagesimal((20, 1, 2, 30), (0,))
        assert s >> 1 == Sexagesimal((20, 1, 2), (30,))
        assert s << 1 == Sexagesimal((20, 1, 2, 30, 0), ())
        assert s >> -1 == Sexagesimal((20, 1, 2, 30, 0), ())
        assert s >> 7 == Sexagesimal((), (0, 0, 0, 20, 1, 2, 30))
        s = Sexagesimal((20,), (0, 2, 0), remainder=Decimal(0.5))
        assert s << 2 == Sexagesimal((20, 0, 2), (0, 30))
        assert s << 5 == Sexagesimal((20, 0, 2, 0, 30, 0), ())

    def test_resize(self):
        s = Sexagesimal(1, 2, 3)
        assert s.resize(4) == s
        assert s.resize(4).resize(2) == s
        s = Sexagesimal((1, 2, 3), (30, 30))
        assert s.resize(4) == s
        assert s.resize(4).resize(2) == s
        assert len(s.right) == 2
        assert len(s.resize(4).right) == 4
        assert len(s.resize(4).resize(0).right) == 0

        s = Sexagesimal((1,), (30,), remainder=Decimal('0.5'))
        assert s.resize(2).remainder == 0
        assert s.resize(2).resize(1).remainder == 0.5

        s = Sexagesimal((1,), (30, 36), remainder=Decimal('0.5'))
        assert s.resize(1).remainder == Decimal('36.5') / 60
        assert s.resize(1).right == (30,)
        s = Sexagesimal('02,02 ; 07,23,55,11,51,21,36')
        assert s.resize(4).right == (7, 23, 55, 11)
        assert s.resize(4).remainder == Decimal(51) / 60 + Decimal(21) / 60**2 + Decimal(36) / 60**3

        assert round(s, 4) == Sexagesimal((2, 2), (7, 23, 55, 12))

        a = Sexagesimal(1, 0, remainder=Decimal("0.0000714235"))
        assert a / (a >> 2) == 3600

    def test_comparisons(self):
        s = Sexagesimal((1, 2), (30,))
        assert s <= Sexagesimal((1, 2), (30,))
        assert s >= Sexagesimal((1, 2), (30,))
        with pytest.raises(AssertionError):
            assert s > Sexagesimal((1, 2), (30,))

        assert s > Sexagesimal(1, 2)
        assert s >= Sexagesimal(1, 2)
        with pytest.raises(AssertionError):
            assert s == Sexagesimal(1, 2)

        assert s < Sexagesimal(1, 2, 3)
        assert s <= Sexagesimal(1, 2, 3)
        with pytest.raises(AssertionError):
            assert s == Sexagesimal(1, 2, 3)

        assert s != Sexagesimal(1, 2, 3)
        assert s is not Sexagesimal(1, 2, 3)

        assert s is Sexagesimal((1, 2), (30,))
        assert s == Sexagesimal((1, 2), (30,))
        assert s is not Sexagesimal(1, 2, remainder=Decimal('0.5'))
        assert s == Sexagesimal(1, 2, remainder=Decimal('0.5'))
        assert s is not Sexagesimal((1, 2), (30, 0, 0, 0))
        assert s == Sexagesimal((1, 2), (30, 0, 0, 0))

    def biop_testing(self, x, y, operator):
        fx, fy = float(x), float(y)
        a = float(operator(x, y))
        b: float = operator(fx, fy)
        try:
            abstol = 1e-11 if a and b else 1e-09
            assert m.isclose(a, b.real, abs_tol=abstol)
            a = float(operator(x, fy))
            b = float(operator(fx, y))
            assert m.isclose(a, b.real, abs_tol=abstol)
        except Exception as e:
            hypothesis.note(f"{operator.__name__}: {a} {b}")
            raise e

    @given(st.from_type(Sexagesimal),
           st.from_type(Sexagesimal))
    def test_operations_with_remainders(self, x, y):
        hypothesis.note(x.remainder)
        hypothesis.note(y.remainder)
        fx = float(x)

        assert float(-x) == -fx
        assert float(+x) == fx
        assert abs(x) == abs(fx)

        for o in (op.mul, op.add, op.sub):
            self.biop_testing(x, y, o)

        if y != 0:
            try:
                self.biop_testing(x, y, op.truediv)
            except InvalidOperation:
                pass

    @given(st.from_type(Sexagesimal),
           st.from_type(Sexagesimal))
    def test_operations_without_remainders(self, x, y):
        x, y = x.truncate(), y.truncate()
        fy = float(y)

        for o in (op.mul, op.add, op.sub, op.pow):
            if o == op.pow and (fy < 0 or fy > 10):
                continue
            self.biop_testing(x, y, o)

        if y != 0:
            self.biop_testing(x, y, op.truediv)

    @given(integers(min_value=-1e15, max_value=1e15).map(Sexagesimal.from_int),
           integers(min_value=-1e15, max_value=1e15).filter(lambda x: x != 0).map(Sexagesimal.from_int))
    def test_mod_integers(self, x, y):
        hypothesis.assume(int(x) % int(y) == float(x) % float(y))
        self.biop_testing(x, y, op.mod)
        self.biop_testing(x, y, op.floordiv)
