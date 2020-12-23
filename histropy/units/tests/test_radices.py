import math as m

import pytest

from histropy.units.errors import IllegalBaseValueError, IllegalFloatValueError
from histropy.units.radices import BasedReal, Historical, Sexagesimal

Sexagesimal: BasedReal
Historical: BasedReal


class TestRadix:

    def test_bases(self):
        assert Historical('2r 7s 29; 45, 2')

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
        assert s.left == (0,)
        s = Sexagesimal((0, 0), (3,), remainder=0.5)
        assert s == 3.5 * 1 / 60

        assert Sexagesimal((), (0, 0, 0, 0)).right == (0, 0, 0, 0)

        assert Sexagesimal(1, 2, 3, sign=-1) == -3723

        assert Sexagesimal("-1,2,3;30") == -3723.5

        assert Sexagesimal((1, 2, 3, 4, 5), (6, 7, 8))[
            :] == (1, 2, 3, 4, 5, 6, 7, 8)

        assert Sexagesimal((1, 2, 31), (6, 7, 8), sign=- 1).__repr__() == "-01,02,31 ; 06,07,08"

        with pytest.raises(IllegalBaseValueError):
            Sexagesimal((-6, 3), ())
        with pytest.raises(IllegalFloatValueError):
            Sexagesimal((0.3, 5), (6, 8))

        with pytest.raises(TypeError):
            BasedReal()

    def test_build(self):
        assert Sexagesimal.from_float(0.5, 4) == Sexagesimal((), (30,))
        assert Sexagesimal.from_float(0.5, 4).right == (30, 0, 0, 0)
        assert Sexagesimal.from_int(5, 2) == Sexagesimal(5)
        assert Sexagesimal.from_string(
            "21,1,6,3;34") == Sexagesimal((21, 1, 6, 3), (34,))

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
        assert s.shift(1) == Sexagesimal((20, 1, 2), (30,))
        assert s.shift(-1) == Sexagesimal((20, 1, 2, 30, 0), ())
        assert s.shift(7) == Sexagesimal((), (0, 0, 0, 20, 1, 2, 30))

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

        s = Sexagesimal((1,), (30,), remainder=0.5)
        assert s.resize(2).remainder == 0
        assert s.resize(2).resize(1).remainder == 0.5

        s = Sexagesimal((1,), (30, 36), remainder=0.5)
        assert s.resize(1).remainder == float(36.5 / 60)
        assert s.resize(1).right == (30,)
        s = Sexagesimal('02,02 ; 07,23,55,11,51,21,36')
        assert s.resize(4).right == (7, 23, 55, 11)
        assert s.resize(4).remainder == 51 / 60 + 21 / 60**2 + 36 / 60**3

        assert round(s, 4) == Sexagesimal((2, 2), (7, 23, 55, 12))

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
        assert s is not Sexagesimal(1, 2, remainder=0.5)
        assert s == Sexagesimal(1, 2, remainder=0.5)
        assert s is not Sexagesimal((1, 2), (30, 0, 0, 0))
        assert s == Sexagesimal((1, 2), (30, 0, 0, 0))

    def test_add_sub(self):
        s = Sexagesimal(20, 1, 2, 10)
        assert s + s == Sexagesimal(40, 2, 4, 20)

        a = Sexagesimal(3, 21, 0, 0)
        assert s + a == Sexagesimal(23, 22, 2, 10)

        s = Sexagesimal(31, 1, 2, 30)
        assert s + s == Sexagesimal(1, 2, 2, 5, 0)
        a = Sexagesimal(1, 31, 1, 2, 30)
        assert a + s == Sexagesimal(2, 2, 2, 5, 0)

        a = -Sexagesimal(3, 1, 4, 29)
        assert s + a == Sexagesimal(27, 59, 58, 1)

        a = Sexagesimal(3, 1, 0, 30)
        s = Sexagesimal(31, 1, 2, 30)
        assert a - s == -Sexagesimal(28, 0, 2, 0)
        assert -a + s == Sexagesimal(28, 0, 2, 0)
        assert s - a == Sexagesimal(28, 0, 2, 0)

        assert a + s.shift(1) == Sexagesimal((3, 32, 1, 32), (30,))
        assert a - s.shift(1) == Sexagesimal((2, 29, 59, 27), (30,))

        assert Sexagesimal(1, 2) + 0.5 == Sexagesimal((1, 2), (30,))

        s = Sexagesimal((1, 2), (30,)) + 0.5
        assert s.remainder == 0
        assert s.left == (1, 3)
        assert s.right == (0,)
        s = 0.5 + Sexagesimal((1, 2), (30,))
        assert s.remainder == 0
        assert s.left == (1, 3)
        assert s.right == (0,)

        s = Sexagesimal((1, 2), (30,), remainder=0.31) + \
            Sexagesimal((), (29,), remainder=0.70)
        assert m.isclose(s.remainder, 0.01, abs_tol=0.0001)
        assert s.left == (1, 3)
        assert s.right == (0,)

    def test_mul_div(self):
        def check_mul(a, b):
            assert m.isclose(float(a * b), float(a) * float(b))

        s = Sexagesimal(20, 1, 2, 10)

        assert s * Sexagesimal(2) == Sexagesimal(40, 2, 4, 20)
        assert s * Sexagesimal(3) == Sexagesimal(1, 0, 3, 6, 30)

        check_mul(s, Sexagesimal(38, 3))
        check_mul(s, Sexagesimal((3,), (30,)))
        check_mul(s, Sexagesimal((3,), (), remainder=0.5))
        check_mul(Sexagesimal((12, 3), (5, 38, 4), remainder=0.26),
                  Sexagesimal((2,), (53, 0, 1, 0, 0), remainder=0.84, sign=-1))
