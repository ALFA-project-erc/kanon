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
