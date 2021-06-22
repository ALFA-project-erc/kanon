"""
The `~kanon.calendars` package provides everything you need to manipulate historical dates
with ancient calendars. All calculations on dates are based on Julian Day Numbers, starting
the 1st January 4713 B.C. at 12:00. This module already has a few of the major historical
calendars subclassed (see `calendars`). Once subclassed, a `Calendar` is created with an
`~kanon.calendars.calendars.Era` to define its beginning.

You can find all the calendars already instantiated in the `Calendar.registry` :

+---------------------+-----------------------+------------------------+------------------------+-------------------------------+
| `~calendars.Arabic` | `~calendars.Egyptian` | `~calendars.Julian`    | `~calendars.Byzantine` | `~calendars.Persian`          |
+---------------------+-----------------------+------------------------+------------------------+-------------------------------+
| Civil Hijra         | Nabonassar            | A.D.                   | A.D.                   | Yazdigird Andarjah at the end |
+---------------------+-----------------------+------------------------+------------------------+-------------------------------+
| Astronomical Hijra  | Philippus             | A.D. Leap December     |                        | Yazdigird Andarjah after Ābān |
+---------------------+-----------------------+------------------------+------------------------+-------------------------------+
|                     |                       | A.D. First month March |                        |                               |
+---------------------+-----------------------+------------------------+------------------------+-------------------------------+
|                     |                       | Julian Era             |                        |                               |
+---------------------+-----------------------+------------------------+------------------------+-------------------------------+

You can easily convert dates between all kinds of calendars. For this we use `Date` objects.
To start, let's try to build a `Date` of the 10th March 1324 from the Julian A.D. calendar :

>>> julian_ad = Calendar.registry["Julian A.D."]
>>> date = Date(julian_ad, (1324, 3, 10))
>>> str(date)
'10 Martius 1324 A.D. in Julian 12:00'
>>> date.jdn
2204718.0

Then we can convert this date in the Arabic Civil Hijra calendar :

>>> arabic_civil_hijra = Calendar.registry["Arabic Civil Hijra"]
>>> arabic_date = date.to_calendar(arabic_civil_hijra)
>>> str(arabic_date)
'13 Rabīʿ al-awwal 724 Civil Hijra in Arabic 12:00'
>>> arabic_date.jdn
2204718.0

We have succesfully converted a date expressed in one calendar into another. And we see that its
absolute date value (expressed in Julian Day Numbers) stays the same.
"""
from .calendars import Calendar, Date

__all__ = ("Calendar", "Date")
