from kanon.tables.htable_reader import read_historical
from kanon.units import Historical


def test_read_historical():

    assert read_historical(["12", "0"], 0) == Historical(1, 0, 0)
    assert read_historical(["11", "0"], 0) == Historical(11, 0)
    assert read_historical(["5"], 0) == Historical(5)
    assert read_historical(["9", "10", "5"], 0) == Historical(9, 10, 5)
    assert read_historical(["9", "10", "5"], 1) == Historical((9, 10), (5,))
