import math as m
import operator as op
import warnings
from decimal import Decimal, InvalidOperation
from fractions import Fraction

import hypothesis
import pytest
from hypothesis import strategies as st
from hypothesis.core import given

from kanon.units import BasedReal, Historical, Sexagesimal
from kanon.units.radices import (
    EmptyStringException,
    IllegalBaseValueError,
    IllegalFloatError,
    TooManySeparators,
)


def test_init():
    assert (
        Sexagesimal((1, 2, 31), (6,), sign=-1, remainder=Decimal("0.3")).__repr__()
        == "-01,02,31 ; 06 |r0.3"
    )

    # From float
    assert Sexagesimal.from_float(-0.016666666666666666, 2) == -Sexagesimal((0,), (1,))
    assert Sexagesimal.from_float(0.5, 4).equals(Sexagesimal("0; 30, 0, 0, 0"))
    with pytest.raises(TypeError):
        Sexagesimal.from_float("s", 1)

    # From int
    assert Sexagesimal.from_int(5, 2) == Sexagesimal(5)
    with pytest.raises(TypeError):
        Sexagesimal.from_int("s")

    # From Decimal
    assert Sexagesimal.from_decimal(Decimal(5), 2) == Sexagesimal(5)
    with pytest.raises(TypeError):
        Sexagesimal.from_decimal(5, 1)

    # From Fraction
    assert Sexagesimal.from_fraction(Fraction(5, 1)).equals(Sexagesimal(5))
    assert Sexagesimal.from_fraction(Fraction(5, 2)) == Sexagesimal("2;30")
    with pytest.raises(TypeError):
        Sexagesimal.from_fraction(5)

    # From str
    assert Sexagesimal("21,1,6,3;34") == Sexagesimal((21, 1, 6, 3), (34,))
    assert Sexagesimal("0,0,0,0;").equals(Sexagesimal(0))
    with pytest.raises(TypeError):
        Sexagesimal._from_string(5)
    with pytest.raises(EmptyStringException):
        Sexagesimal("")
    with pytest.raises(TooManySeparators):
        Sexagesimal("1;2;3")

    # From Sequence
    with pytest.raises(IllegalBaseValueError) as err:
        Sexagesimal((-6, 3), ())
    assert "should be in the range" in str(err.value)
    with pytest.raises(IllegalFloatError) as err:
        Sexagesimal((0.3, 5), (6, 8))
    assert "An illegal float" in str(err.value)

    # From BasedReal

    assert Sexagesimal(Historical("3;15"), 1).equals(Sexagesimal("3;15"))

    # From multiple ints
    with pytest.raises(ValueError):
        Sexagesimal(3, 5, remainder=Decimal(-5))
    with pytest.raises(ValueError):
        Sexagesimal(3, 5, remainder=0.6)

    # Incorrect parameters
    with pytest.raises(TypeError):
        BasedReal()
    with pytest.raises(ValueError):
        Sexagesimal(Decimal(5))
    with pytest.raises(ValueError):
        Sexagesimal("", "")
    with pytest.raises(ValueError):
        Sexagesimal("", "", "", "")
    with pytest.raises(TypeError):
        Sexagesimal(("a", 2), (1, 2))
    with pytest.raises(ValueError):
        Sexagesimal(1, sign=2)


def test_get():
    s = Sexagesimal("1, 2, 30; 18, 12, 23")
    assert s[-2] == 1
    assert s[0] == 30
    assert s[1] == 18
    assert s[:] == (1, 2, 30, 18, 12, 23)
    assert s[:0] == (1, 2)
    assert s[3::-1] == (23, 12, 18, 30, 2, 1)
    assert s[-1:] == (2, 30, 18, 12, 23)
    assert s[-1:2] == (2, 30, 18)

    with pytest.raises(IndexError):
        s[100]
    with pytest.raises(TypeError):
        s["5"]


def test_truncations():
    s = Sexagesimal("1, 2, 30; 18, 52, 23")
    assert round(s).equals(s)
    assert round(s, 1).equals(Sexagesimal("1,2,30;19"))
    assert s.truncate(1).equals(Sexagesimal("1,2,30;18"))
    assert s.truncate(100).equals(s)
    assert m.trunc(s) == 3750
    assert m.floor(s) == 3750
    assert m.ceil(s) == 3751
    assert m.floor(-s) == -3749
    assert m.ceil(-s) == -3750
    assert Sexagesimal(1, 2, 3).minimize_precision().equals(Sexagesimal(1, 2, 3))
    assert (
        Sexagesimal("1, 2, 3; 0, 0").minimize_precision().equals(Sexagesimal(1, 2, 3))
    )


def test_misc():
    s = Sexagesimal(5)
    assert (s or 1) == 5
    assert not s.equals("5")
    assert s.to_fraction() == Fraction(5)

    assert 5 / s == 1

    assert s ** -1 == 1 / 5
    assert s ** 1 == s
    assert 1 ** s == 1
    assert Sexagesimal(0) ** 1 == 0

    with pytest.raises(ValueError):
        (-Sexagesimal(5)) ** 2.5

    assert s > 4

    assert (s / 1).equals(s)
    assert (s / -1).equals(-s)
    with pytest.raises(ZeroDivisionError):
        s / 0

    assert Sexagesimal("1,0;2,30,1").subunit_quantity(1) == 3602

    assert 5 % Sexagesimal(2) == 1
    assert 5 // Sexagesimal(2) == 2

    assert divmod(Sexagesimal(5), 3) == divmod(5, 3)


def test_shift():
    s = Sexagesimal("20, 1, 2, 30; 0")
    assert (s >> 1).equals(Sexagesimal("20, 1, 2; 30, 0"))
    assert (s << 1).equals(Sexagesimal("20, 1, 2, 30, 0"))
    assert (s >> -1).equals(s << 1)
    assert (s >> 7).equals(Sexagesimal("0; 0, 0, 0, 20, 1, 2, 30, 0"))
    s = Sexagesimal((20,), (0, 2, 0), remainder=Decimal(0.5))
    assert (s << 2).equals(Sexagesimal((20, 0, 2), (0,), remainder=Decimal(0.5)))
    assert (s << 5).equals(Sexagesimal(20, 0, 2, 0, 30, 0))


@given(st.integers(min_value=0, max_value=15), st.integers(min_value=0, max_value=15))
def test_resize(x, y):
    s = Sexagesimal("1, 2, 3; 30, 25")
    assert s.resize(x) == s
    resized = s.resize(x).resize(y)
    assert m.isclose(resized, s)
    assert resized.significant == y


@given(st.floats(allow_infinity=False, allow_nan=False))
def test_comparisons(x):
    s = Sexagesimal("1, 2; 30")
    xs = Sexagesimal.from_float(x, 1)
    for comp in (op.lt, op.le, op.eq, op.ne, op.ge, op.gt):
        if comp(float(s), x):
            assert comp(s, xs)
        else:
            assert not comp(s, xs)


def biop_testing(x: BasedReal, y: BasedReal, operator):
    fx, fy = float(x), float(y)
    if (
        operator == op.pow
        and (fy < 0 or fy > 10 or x < 0 and int(fy) != fy)
        or operator == op.truediv
        and fy == 0
    ):
        return
    a = float(operator(x, y))
    b: float = operator(fx, fy)
    try:
        abstol = 1e-09 if a and b else 1e-11
        assert m.isclose(a, b.real, abs_tol=abstol)
        a = float(
            operator(x, type(x).from_float(fy, x.significant, remainder_threshold=1))
        )
        b = float(
            operator(type(x).from_float(fx, y.significant, remainder_threshold=1), y)
        )
        assert m.isclose(a, b.real, abs_tol=abstol)
    except Exception as e:
        hypothesis.note(f"{x.remainder} {y.remainder}")
        hypothesis.note(f"{operator.__name__}: {a} {b}")
        raise e


@given(st.from_type(Sexagesimal), st.from_type(Sexagesimal))
def test_operations_with_remainders(x, y):
    fx = float(x)

    assert float(-x) == -fx
    assert float(+x) == fx
    assert abs(x) == abs(fx)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for o in (op.mul, op.add, op.sub):
            biop_testing(x, y, o)

    if y != 0:
        try:
            biop_testing(x, y, op.truediv)
        except InvalidOperation:
            pass


@given(st.from_type(Sexagesimal), st.from_type(Sexagesimal))
def test_operations_without_remainders(x, y):
    x, y = x.truncate(), y.truncate()

    for o in (op.mul, op.add, op.sub, op.pow, op.truediv):
        biop_testing(x, y, o)


@given(
    st.integers(min_value=int(-1e15), max_value=int(1e15)).map(Sexagesimal.from_int),
    st.integers(min_value=int(-1e15), max_value=int(1e15))
    .filter(lambda x: x != 0)
    .map(Sexagesimal.from_int),
)
def test_mod_integers(x, y):
    hypothesis.assume(int(x) % int(y) == float(x) % float(y))
    biop_testing(x, y, op.mod)
    biop_testing(x, y, op.floordiv)


def test_sqrt():

    assert Sexagesimal(9).sqrt().equals(Sexagesimal(3))

    assert Sexagesimal(0).sqrt() == 0

    assert Sexagesimal("12;15").sqrt(5) == 3.5

    with pytest.raises(ValueError):
        Sexagesimal("-5").sqrt()


@given(st.from_type(Sexagesimal).filter(lambda x: x > 0))
def test_sqrt_hypo(n):
    assert m.isclose(float(n.sqrt(5)), m.sqrt(float(n)))


@given(
    st.integers(-20, 20),
    st.integers(-20, 20),
    st.integers(-2, 2).filter(lambda x: x != 0),
)
def test_range(start: int, stop: int, step: int):
    based_range = Sexagesimal.range(start, stop, step)
    normal_range = range(start, stop, step)

    assert list(normal_range) == [int(x) for x in based_range]

    based_range_stop = Sexagesimal.range(stop)
    normal_range_stop = range(stop)

    assert list(normal_range_stop) == [int(x) for x in based_range_stop]


def test_mixed_misc():
    assert Historical.from_int(60) == Historical("2s0")
    assert divmod(Historical(5), Historical("1s26;3")) == (0, 5)
    assert round(Historical(5, remainder=Decimal(0.6))) == 6


@given(st.from_type(Historical), st.from_type(Historical))
def test_operations_without_remainders_mixed(x, y):
    x, y = x.truncate(), y.truncate()

    for o in (op.mul, op.add, op.sub, op.pow, op.truediv):
        biop_testing(x, y, o)


def test_mod():
    assert (Sexagesimal("1,2;3,4") % Sexagesimal(4)).significant == 2
