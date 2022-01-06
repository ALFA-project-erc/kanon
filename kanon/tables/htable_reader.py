from typing import Callable, Dict, List, Optional, Tuple, Union, cast

import astropy.units as u
import requests
from astropy.units.core import Unit

from kanon.models.meta import TableType, models
from kanon.tables.symmetries import Symmetry
from kanon.units import Historical, Sexagesimal
from kanon.units.radices import BasedReal
from kanon.utils.types.dishas import DSymmetry, NumberType, TableContent, UnitType
from kanon.utils.types.number_types import Real

from .htable import HTable

_dishas_fields = '","'.join(
    [
        "source_value_original",
        "argument1_name",
        "argument1_number_unit",
        "argument1_significant_fractional_place",
        "argument1_type_of_number",
        "argument2_name",
        "argument2_number_unit",
        "argument2_significant_fractional_place",
        "argument2_type_of_number",
        "entry_significant_fractional_place",
        "entry_number_unit",
        "entry_type_of_number",
        "symmetries",
        "edited_text",
        "table_type",
    ]
)
DISHAS_REQUEST_URL = f'https://dishas.obspm.fr/elastic-query\
?index=table_content&hits=true&id={{}}&source=["{_dishas_fields}"]'


def read_sexag_array(array: List[str], shift: int) -> BasedReal:
    sign = -1 if array[0][0] == "-" else 1
    return Sexagesimal(*(abs(int(v)) for v in array), sign=sign) >> shift


def read_intsexag_array(array: List[str], _: int) -> BasedReal:
    integer = int(array[0])
    if len(array) == 1:
        return Sexagesimal.from_int(integer)
    return integer + (read_sexag_array(array[1:], 0) >> len(array) - 1)


def read_historical(array: List[str], shift: int) -> BasedReal:
    integer = int(array[0])
    # Special case for non true Historical in DISHAS with 2 values
    if len(array) == 2 and shift == 0:
        return integer * 30 + Sexagesimal(array[1])

    sign = -1 if array[0][0] == "-" else 1
    values = tuple(abs(int(x)) for x in array)
    intpart = Historical(*values[: -shift or None])
    floatpart = Sexagesimal((), values[-shift or len(values) :])

    return sign * (floatpart + int(intpart))


number_reader: Dict[NumberType, Callable[[List[str], int], Real]] = {
    "sexagesimal": read_sexag_array,
    "floating sexagesimal": read_sexag_array,
    "integer and sexagesimal": read_intsexag_array,
    "historical": read_historical,
}

unit_reader: Dict[UnitType, Unit] = {
    "degree": u.degree,
    "day": u.day,
    "year": u.year,
    "month": u.year / 12,
    "hour": u.hour,
}


def read_table_dishas(
    requested_id: Union[int, str],
    symmetry=True,
    with_units=True,
    entries_name="Entries",
    freeze=False,
) -> HTable:

    qid = int(requested_id)

    res: TableContent = requests.get(
        DISHAS_REQUEST_URL.format(qid),
    ).json()
    if not res or "error" in res:
        raise FileNotFoundError(f"{qid} ID not found in DISHAS database")

    return read_table_content(res, symmetry, with_units, entries_name, freeze)


def read_table_content(
    tabc: TableContent, symmetry=True, units=True, entries_name="Entries", freeze=False
):

    values = tabc["source_value_original"]

    arg_unit = tabc["argument1_number_unit"]
    arg_shift = int(tabc["argument1_significant_fractional_place"])
    arg_reader = number_reader.get(tabc["argument1_type_of_number"], lambda x, _: x)

    entry_unit = tabc["entry_number_unit"]
    entry_shift = int(tabc["entry_significant_fractional_place"])

    def entry_reader(val):
        reader = number_reader.get(tabc["entry_type_of_number"], lambda x, _: x)
        if "**" in val:
            return reader(["0"], entry_shift)
        return reader(val, entry_shift)

    args = [arg_reader(v["value"], arg_shift) for v in values["args"]["argument1"]]

    table_type: Optional[TableType] = None
    any((table_type := v).value == int(tabc["table_type"]["id"]) for v in models)

    # Double argument

    if "argument2" in values["args"]:
        len1 = len(values["args"]["argument1"])
        len2 = len(values["args"]["argument2"])

        arg2_unit = tabc["argument2_number_unit"]
        arg2_shift = int(tabc["argument2_significant_fractional_place"])
        arg2_reader = number_reader.get(
            tabc["argument2_type_of_number"], lambda x, _: x
        )

        args2 = [
            arg2_reader(v["value"], arg2_shift) for v in values["args"]["argument2"]
        ]

        tables = [
            HTable(
                [
                    args,
                    [
                        entry_reader(v["value"])
                        for v in [values["entry"][j][i] for j in range(len1)]
                    ],
                ],
                names=(tabc["argument1_name"], entries_name),
                index=(tabc["argument1_name"]),
                dtype=[object, object],
            )
            for i in range(len2)
        ]

        units_info = (
            {
                "unit_arg": unit_reader.get(arg_unit),
                "unit_entry": unit_reader.get(entry_unit),
            }
            if units
            else {}
        )

        return HTable(
            [args2, tables],
            names=(tabc["argument2_name"], "Tables"),
            index=(tabc["argument2_name"]),
            units=[unit_reader.get(arg2_unit), u.dimensionless_unscaled]
            if units
            else None,
            dtype=None,
            table_type=table_type,
            meta={
                **tabc["edited_text"],
                **units_info,
                "index": tabc["argument1_name"],
                "double": True,
            },
        )

    entries = [entry_reader(v["value"]) for v in values["entry"]]

    symmetry_raw = tabc["symmetries"]

    def build_sym(data: DSymmetry) -> Symmetry:
        symmetry = Symmetry(data["symtype"], data["offset"], sign=data["sign"])

        if source_data := data["source"]:
            source = tuple(arg_reader(v, arg_shift) for v in source_data)
            assert len(source) == 2
            symmetry.source = cast(Tuple[Real, Real], source)

        if target_data := data["target"]:
            symmetry.targets = [arg_reader(v, arg_shift) for v in target_data]

        return symmetry

    symmetries = [build_sym(sym) for sym in symmetry_raw] if symmetry else []

    table = HTable(
        [args, entries],
        names=(tabc["argument1_name"], entries_name),
        index=(tabc["argument1_name"]),
        units=[unit_reader.get(arg_unit), unit_reader.get(entry_unit)]
        if units
        else None,
        dtype=[object, object],
        symmetry=symmetries,
        meta=tabc["edited_text"],
        table_type=table_type,
    )

    if freeze:
        table.freeze()

    return table
