import hypothesis.strategies as st
import pytest
from hypothesis import given

from kanon.calendars import Calendar, Date
from kanon.calendars.calendars import Era, Julian


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

    def test_first_day(self):
        for cal in Calendar.registry.values():
            assert cal.jdn_at_ymd(1, 1, 1) == cal.era.epoch
            assert Date(cal, (1, 1, 1)).days_from_epoch() == 0

    def test_from_julian(self):
        cal = Calendar.registry["Julian A.D."]
        days = cal.jdn_at_ymd(2, 1, 1)

        assert cal.from_julian_days(days).jdn == days

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
        assert str(date) == "1 Ianuarius -4713 A.D. in Julian"

        date = Date(cal, (-1, 1, 1))

        assert date.to_time().to_value("jd") == 1721058
        assert str(date) == "1 Ianuarius -1 A.D. in Julian"

        date = Date(cal, (20, 3, 12))
        assert (date + 1).jdn == date.jdn + 1
        assert (date - 1).jdn == date.jdn - 1
