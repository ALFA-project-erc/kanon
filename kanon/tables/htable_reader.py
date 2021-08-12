from typing import Callable, Dict, List, Tuple, cast

import astropy.units as u
import requests
from astropy.units.core import Unit

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
        "entry_significant_fractional_place",
        "entry_number_unit",
        "entry_type_of_number",
        "symmetries",
        "edited_text",
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
        return integer * 30 + Historical(array[1])

    values = tuple(int(x) for x in array)
    return Historical(values[: -shift or None], values[-shift or len(values) :])


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


def read_table_dishas(requested_id: str) -> HTable:

    res: TableContent = requests.get(
        DISHAS_REQUEST_URL.format(int(requested_id)),
    ).json()
    if not res or "error" in res:
        raise FileNotFoundError(f"{requested_id} ID not found in DISHAS database")

    values = res["source_value_original"]

    arg_unit = res["argument1_number_unit"]
    arg_shift = int(res["argument1_significant_fractional_place"])
    arg_reader = number_reader.get(res["argument1_type_of_number"], lambda x, _: x)

    entry_unit = res["entry_number_unit"]
    entry_shift = int(res["entry_significant_fractional_place"])
    entry_reader = number_reader.get(res["entry_type_of_number"], lambda x, _: x)

    args = [arg_reader(v["value"], arg_shift) for v in values["args"]["argument1"]]
    entries = [entry_reader(v["value"], entry_shift) for v in values["entry"]]

    symmetry_raw = res["symmetries"]

    def build_sym(data: DSymmetry) -> Symmetry:
        symmetry = Symmetry(data["symtype"], data["offset"], sign=data["sign"])

        if source_data := data["source"]:
            source = tuple(arg_reader(v, arg_shift) for v in source_data)
            assert len(source) == 2
            symmetry.source = cast(Tuple[Real, Real], source)

        if target_data := data["target"]:
            symmetry.targets = [arg_reader(v, arg_shift) for v in target_data]

        return symmetry

    symmetries = [build_sym(sym) for sym in symmetry_raw]

    table = HTable(
        [args, entries],
        names=(res["argument1_name"], "Entries"),
        index=(res["argument1_name"]),
        units=[unit_reader.get(arg_unit), unit_reader.get(entry_unit)],
        dtype=[object, object],
        symmetry=symmetries,
        meta=res["edited_text"],
    )

    return table
