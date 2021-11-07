0.5.2
_____

*Features*

- tables : New `HTable.freeze` method to cache `get` and `to_pandas` results

*Bug Fixes*

- tables : `with_units` replaces `units` in `HTable.read` parameter to make it work

0.5.1
_____

*Features*

- tables : `HTable.read` now uses `Sexagesimal` for `Historical` input

0.5.0
_____

*Features*

- calendars : `Date.frac` no longer exists, replaced with `Date.hours` which is `Sexagesimal`
- models : Introducing `models`
- precision : Custom arithmetic algorithms now declared with `identify_func` decorator

0.4.0
_____

*Bug Fixes*

- tables : `HTable.populate` correctly working with input array with number types different from index
- radices : `BasedReal.__mod__` correctly working with negative values
- radices : `BasedReal.__mod__` correctly keeping precision

*Features*

- tables : `HTable.read` can be used with the ID as sole parameter and with options
- tables : `HTable` support for double argument tables

0.3.2
_____

*Bug Fixes*

- calendars : Fixed `Date` not working with non default frac on month bounds
- tables : Fixed `HTable.read` not correctly reading shifted `Historical` columns.
- radices : Fixed `BasedReal.__round__` not working with mixed base
- radices : Fixed `BasedReal.__mod__` returning a result with incorrect significant

0.3.1
_____

*Bug Fixes*

- radices : Fixed `BasedReal.__pow__` with negative values raised to fractional power

*Features*

- tables : `HTable.read` accepts DISHAS `Historical` columns

0.3.0
_____

*Bug Fixes*

- calendars : Fixed `Persian Andarjah after Aban` months
- calendars : Fixed incorrect behavior of `Calendar.jdn_at_ymd`
- calendars : Fixed mixed base `BasedReal` arithmetic

*Features*

- radices : `FloatingSexagesimal` removed
- other : `BasedQuantity` typing
- calendars : `Byzantine/Syrian` calendar renamed `Byzantine`
- calendars : Fraction of day support for `Date`
- tables : `HTable.get` now supports `key` of type `Quantity` with same unit as the table index


0.2.0
_____

- tables : Update `HTable.read` with new DISHAS api source_value_original key.

0.1.2
_____

- calendars : Fixed calendars not able to process JDN below their era epoch.
- tables : Fixed `HTable.read` with dishas format not correctly processing non existing id.
- other : Package typing enabled.

0.0.1
_____

- radices : Units with radices and precision.
- tables : Tables with HTable reading.
- calendars : Calendars with date conversions.
