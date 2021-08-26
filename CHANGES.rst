0.4.0
_____

*Bug Fixes*

- `HTable.populate` correctly working with input array with number types different from index
- `BasedReal.__mod__` correctly working with negative values
- `BasedReal.__mod__` correctly keeping precision

*Features*

- `HTable.read` can be used with the ID as sole parameter and with options
- `HTable` support for double argument tables

0.3.2
_____

*Bug Fixes*

- Fixed `Date` not working with non default frac on month bounds
- Fixed `BasedReal.__round__` not working with mixed base
- Fixed `HTable.read` not correctly reading shifted `Historical` columns.
- Fixed `BasedReal.__mod__` returning a result with incorrect significant

0.3.1
_____

*Bug Fixes*

- Fixed `BasedReal.__pow__` with negative values raised to fractional power

*Features*

- `HTable.read` accepts DISHAS `Historical` columns

0.3.0
_____

*Bug Fixes*

- Fixed `Persian Andarjah after Aban` months
- Fixed incorrect behavior of `Calendar.jdn_at_ymd`
- Fixed mixed base `BasedReal` arithmetic

*Features*

- `FloatingSexagesimal` removed
- `Byzantine/Syrian` calendar renamed `Byzantine`
- `BasedQuantity` typing
- Fraction of day support for `Date`
- `HTable.get` now supports `key` of type `Quantity` with same unit as the table index


0.2.0
_____

- Update `HTable.read` with new DISHAS api source_value_original key.

0.1.2
_____

- Fixed calendars not able to process JDN below their era epoch.
- Fixed `HTable.read` with dishas format not correctly processing non existing id.
- Package typing enabled.

0.0.1
_____

- Units with radices and precision.
- Tables with HTable reading.
- Calendars with date conversions.
