import math

import hypothesis.strategies as st
import pytest
from hypothesis import given

from kanon.calendars import Calendar, Date
from kanon.calendars.calendars import Era, Julian, float_to_hm, hm_to_float


class TestCalendars:
    def test_init(self):
        era = Era("test", 10)

        assert era.days_from_epoch(20) == 10

        new_cal = Julian(era)
        assert new_cal.era == era
        assert new_cal.name in Calendar.registry

        assert new_cal.__repr__() == "Calendar(Julian test)"

        with pytest.raises(ValueError):
            Julian(era)

        with pytest.raises(ValueError):
            new_cal.jdn_at_ymd(1, 50, 1)
        with pytest.raises(ValueError):
            new_cal.jdn_at_ymd(1, 1, 50)
        with pytest.raises(ValueError):
            new_cal.jdn_at_ymd(0, 1, 10)

    def test_first_day(self):
        for cal in Calendar.registry.values():
            assert cal.jdn_at_ymd(1, 1, 1) == cal.era.epoch
            assert Date(cal, (1, 1, 1)).days_from_epoch() == 0

    def test_from_julian(self):
        cal = Calendar.registry["Julian A.D."]
        days = cal.jdn_at_ymd(2, 1, 1)

        assert cal.from_julian_days(days).jdn == days
        assert cal.from_julian_days(640234).jdn == 640234
        assert cal.from_julian_days(cal.era.epoch - 1).jdn == cal.era.epoch - 1

    @given(st.integers(1, 10000), st.integers(1, 12), st.integers(1, 28))
    def test_dates_hypothesis(self, y: int, m: int, d: int):
        cal = Calendar.registry["Julian A.D."]

        date = Date(cal, (y, m, d))

        assert cal.from_julian_days(date.jdn) == date
        assert cal.get_time(y, m, d) == date.to_time()

    def test_conversion(self):
        arabic = Calendar.registry["Arabic Civil Hijra"]
        julian = Calendar.registry["Julian A.D."]

        date = Date(arabic, (1, 1, 1))
        conversion = date.to_calendar(julian)
        assert conversion.ymd == (622, 7, 16)

    def test_date(self):
        cal = Calendar.registry["Julian A.D."]
        date = Date(cal, (-4713, 1, 1))

        assert date.to_time().to_value("jd") == 0
        assert str(date) == "1 Ianuarius -4713 A.D. in Julian 12:00"

        date = Date(cal, (-1, 1, 1))

        assert date.to_time().to_value("jd") == 1721058
        assert str(date) == "1 Ianuarius -1 A.D. in Julian 12:00"

        date = Date(cal, (20, 3, 12))
        assert (date + 1).jdn == date.jdn + 1
        assert (date - 1).jdn == date.jdn - 1

        assert "13:30" in str(Date(cal, (1, 1, 1), hm_to_float(13, 30)))

        with pytest.raises(ValueError) as err:
            Date(cal, (1, 1, 1), -1)

        assert "Time must be" in str(err)

        assert Date(cal, (2021, 7, 1), 0.2) + 0 == Date(cal, (2021, 7, 1), 0.2)

    def test_jdn_at_ymd(self):
        cal = Calendar.registry["Julian A.D."]

        assert cal.jdn_at_ymd(-1, 12, 31) + 1 == cal.jdn_at_ymd(1, 1, 1)
        assert cal.jdn_at_ymd(-2, 12, 31) + 1 == cal.jdn_at_ymd(-1, 1, 1)

        assert cal.jdn_at_ymd(61, 1, 1) == 1743339

        assert cal.jdn_at_ymd(60, 12, 31) != cal.jdn_at_ymd(61, 1, 1)

    def test_persian(self):
        cal_normal = Calendar.registry["Persian Yazdigird Andarjah at the end"]
        cal_variant = Calendar.registry["Persian Yazdigird Andarjah after Ābān"]

        assert len(cal_normal.months) == len(cal_variant.months)
        assert cal_normal.months[-1].name == cal_variant.months[8].name

    def test_dates_fraction(self):
        cal = Calendar.registry["Julian A.D."]

        assert cal.from_julian_days(5000.6) != cal.from_julian_days(5000)

        date = Date(cal, (5, 2, 3), 0.4)

        assert math.isclose((date + 1).frac, 0.4)

        assert (date + 1).ymd == (5, 2, 4)

    def test_time_convert(self):
        assert float_to_hm(hm_to_float(12, 30)) == (12, 30)

        with pytest.raises(ValueError) as err:
            hm_to_float(-1, 5)

        assert "Incorrect" in str(err)

        with pytest.raises(ValueError) as err:
            float_to_hm(2)

        assert "Incorrect" in str(err)
