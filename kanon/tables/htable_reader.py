from typing import Dict, List, Optional, Protocol, Tuple, Union, cast

import astropy.units as u
import requests
from astropy.units.core import Unit

from kanon.models.meta import TableType, models
from kanon.tables.symmetries import Symmetry
from kanon.units import Historical, Sexagesimal
from kanon.units.definitions import IntegerAndSexagesimal, Temporal
from kanon.utils import Sign
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


def read_sexag_array(values: List[int], shift: int, sign: Sign = 1) -> Sexagesimal:
    return Sexagesimal(*values, sign=sign) >> shift


def read_intsexag_array(
    values: List[int], shift: int, sign: Sign = 1
) -> IntegerAndSexagesimal:
    return sign * (values[0] + IntegerAndSexagesimal((), values[1:]))


def read_historical(values: List[int], shift: int, sign: Sign = 1) -> Historical:
    integer = values[0]
    # Special case for non true Historical in DISHAS with 2 values
    if len(values) == 2 and shift == 0:
        return Historical(integer * 30 + Sexagesimal(values[1]))

    return Historical(
        values[: -shift or None], values[-shift or len(values) :], sign=sign
    )


def read_temporal(values: List[int], shift: int, sign: Sign = 1) -> Temporal:
    return sign * (values[0] + Temporal((), values[1:]))


class NumberReader(Protocol):
    def __call__(self, values: List[int], shift: int, sign: Sign = 1) -> Real:
        ...


number_reader: Dict[NumberType, NumberReader] = {
    "sexagesimal": read_sexag_array,
    "floating sexagesimal": read_sexag_array,
    "integer and sexagesimal": read_intsexag_array,
    "historical": read_historical,
    "temporal": read_temporal,
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

    entry_unit = tabc["entry_number_unit"]
    entry_shift = int(tabc["entry_significant_fractional_place"])

    argsvalues = values["args"]

    def reader(ntype: NumberType, shift: int):
        nreader = number_reader.get(ntype, lambda x, *_: x)

        def fn(val: List[str]):
            if "**" in val:
                return nreader([0], shift)
            sign: Sign = -1 if val[0][0] == "-" else 1
            return nreader([abs(int(v)) for v in val], shift, sign)

        return fn

    entry_reader = reader(tabc["entry_type_of_number"], entry_shift)
    arg_reader = reader(tabc["argument1_type_of_number"], arg_shift)

    args = [arg_reader(v["value"]) for v in argsvalues["argument1"]]

    table_type: Optional[TableType] = None
    any((table_type := v).value == int(tabc["table_type"]["id"]) for v in models)

    # Double argument

    if "argument2" in argsvalues:
        len1 = len(argsvalues["argument1"])
        len2 = len(argsvalues["argument2"])

        arg2_unit = tabc["argument2_number_unit"]
        arg2_shift = int(tabc["argument2_significant_fractional_place"])
        arg2_reader = reader(tabc["argument2_type_of_number"], arg2_shift)

        args2 = [arg2_reader(v["value"]) for v in argsvalues["argument2"]]

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
            source = tuple(arg_reader(v) for v in source_data)
            assert len(source) == 2
            symmetry.source = cast(Tuple[Real, Real], source)

        if target_data := data["target"]:
            symmetry.targets = [arg_reader(v) for v in target_data]

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
