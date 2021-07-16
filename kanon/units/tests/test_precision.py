from dataclasses import asdict
from decimal import Decimal

import pytest

from kanon.units import Sexagesimal
from kanon.units.precision import (
    PreciseNumber,
    PrecisionContext,
    PrecisionMode,
    TruncatureMode,
    _with_context_precision,
    clear_records,
    get_context,
    get_records,
    set_context,
    set_precision,
    set_recording,
)
from kanon.units.radices import BasedReal


class TestPrecision:
    @classmethod
    def setup_class(cls):
        cls.context = asdict(get_context())
        del cls.context["_records"]
        del cls.context["stack"]

    def test_context(self):

        current_ctx = get_context()
        ctx = PrecisionContext(
            1, TruncatureMode.CEIL, (None, ""), (None, ""), (None, ""), (None, "")
        )
        set_context(ctx)
        with set_precision() as ctx_dict:
            assert ctx_dict["pmode"] == 1
            with pytest.raises(ValueError):
                set_context(ctx)
        set_context(current_ctx)

    def equality(self, a: BasedReal, b: BasedReal):
        assert a.equals(
            b
        ), f"{a.truncate()},r:{a.remainder} != {b.truncate()},r:{b.remainder}"

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
            self.equality(
                s1 + s2, Sexagesimal((2,), (30, 0, 0), remainder=Decimal("0.1"))
            )
            self.equality(
                s1 * s2, Sexagesimal((1,), (0, 0, 0), remainder=Decimal("0.2"))
            )
            self.equality(
                s1 / s2, Sexagesimal((0,), (15, 0, 0), remainder=Decimal("0.05"))
            )

            assert round(Sexagesimal(2, remainder=Decimal("0.5"))) == 3

        with pytest.raises(NotImplementedError):
            with set_precision(pmode=PrecisionMode.FULL):
                s1 + s2

        with pytest.raises(ValueError):
            with set_precision(pmode=-1):
                pass

        with pytest.raises(TypeError):
            with set_precision(pmode="a"):
                pass

    def test_truncature_modes(self):
        get_context().mutate(pmode=PrecisionMode.SCI)
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
        get_context().mutate(pmode=PrecisionMode.MAX)

        with pytest.raises(TypeError):
            with set_precision(tmode=1):
                pass

    def test_custom_arithmetic(self):
        def add(a: PreciseNumber, b: PreciseNumber):
            return a._add(Sexagesimal.from_float(float(b) + 1, 0))

        def sub(a: PreciseNumber, b: PreciseNumber):
            return a._sub(Sexagesimal.from_float(float(b) + 1, 0))

        def mul(a: PreciseNumber, b: PreciseNumber):
            return a._mul(Sexagesimal.from_float(float(b) + 1, 0))

        def div(a: PreciseNumber, b: PreciseNumber):
            return Sexagesimal(5)

        with set_precision(
            add=(add, "ADD"),
            sub=(sub, "SUB"),
            div=(div, "DIV"),
            mul=(mul, "MUL"),
        ):
            assert Sexagesimal(1) + Sexagesimal(1) == 3
            assert Sexagesimal(1) - Sexagesimal(1) == 0
            assert Sexagesimal(1) * Sexagesimal(1) == 2
            assert Sexagesimal(1) / Sexagesimal(1) == 5

    def test_history(self):
        set_recording(True)
        with set_precision(pmode=5):
            Sexagesimal(1) + Sexagesimal(2)

        records = get_records()
        assert len(records) == 1
        rec = records[0]
        assert rec["args"] == (Sexagesimal(1), Sexagesimal(2), "+", Sexagesimal(3))
        assert rec["add"] == "DEFAULT"

        set_recording(False)
        with set_precision(pmode=5):
            Sexagesimal(1) + Sexagesimal(2)
        assert len(records) == 1

        set_recording(True)
        Sexagesimal(1) + Sexagesimal(1)
        assert len(records) == 2

        def add(a, b):
            return Sexagesimal(0)

        with set_precision(add=(add, "ADD")):
            Sexagesimal(1) + Sexagesimal(1)
        assert len(records) == 3
        assert records[-1]["add"] == "ADD"

        with set_precision():
            with pytest.raises(ValueError):
                set_recording(False)

        set_recording(False)

        clear_records()

        assert len(records) == 0

    def test_wrapper(self):
        @_with_context_precision
        def func(a, b):
            return 1

        with pytest.raises(TypeError):
            func(Sexagesimal(1), Sexagesimal(2))
        assert func(1, 2) == 1

    @classmethod
    def teardown_class(cls):
        get_context().mutate(**cls.context)
