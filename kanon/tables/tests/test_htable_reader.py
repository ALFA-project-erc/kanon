from kanon.tables.htable_reader import (
    read_historical,
    read_intsexag_array,
    read_temporal,
)
from kanon.units import Historical, IntegerAndSexagesimal
from kanon.units.definitions import Temporal


def test_read_historical():
    assert read_historical([12, 0], 0) == Historical(1, 0, 0)
    assert read_historical([11, 0], 0) == Historical(11, 0)
    assert read_historical([5], 0) == Historical(5)
    assert read_historical([9, 10, 5], 0) == Historical(9, 10, 5)
    assert read_historical([9, 10, 5], 1) == Historical((9, 10), (5,))
    assert read_historical([9, 10, 5], 1, -1) == -Historical((9, 10), (5,))


def test_read_intsexag():
    assert read_intsexag_array([1, 12, 0], 2, -1) == IntegerAndSexagesimal("-1; 12, 0")
    assert read_intsexag_array([0, 12, 0], 2, -1) == IntegerAndSexagesimal("-0; 12, 0")
    assert read_intsexag_array([121, 12, 0], 2) == IntegerAndSexagesimal("121; 12, 0")


def test_read_temporal():
    assert read_temporal([28, 18, 2, 6], 3, 1) == Temporal("28 ; 18,02,06")
    assert read_temporal([253, 18, 2, 6], 3, -1) == Temporal("-253 ; 18,02,06")
