from typing import Any, Dict, List, Literal, Optional, TypedDict

# flake8: noqa


class OriginalValue(TypedDict):
    value: List[str]
    comment: str
    suggested: bool
    critical_apparatus: List[str]


NumberType = Literal[
    "sexagesimal", "floating sexagesimal", "integer and sexagesimal", "historical"
]
SymmetryType = Literal["mirror", "periodic"]
SymmetryOperation = Literal["opposite", "identity", "addition", "substraction"]
UnitType = Literal["degree", "day", "hour", "month", "year"]


class TemplateArgs(TypedDict):
    name: str
    type: NumberType
    unit: int
    nsteps: int
    ncells: int
    decpos: int
    subUnit: Optional[NumberType]
    firstMonth: Optional[Any]


class TemplateEntries(TypedDict):
    name: str
    type: NumberType
    ncells: int
    decpos: int
    unit: int


class Template(TypedDict):

    table_type: str
    readonly: bool
    args: List[TemplateArgs]
    entries: List[TemplateEntries]


class DSymmetry(TypedDict):
    symtype: SymmetryType
    offset: int
    sign: Literal[-1, 1]
    source: Optional[List[List[str]]]
    target: Optional[List[List[str]]]


class Args(TypedDict):
    argument1: List[str]
    argument2: Optional[List[str]]


class ValueFloat(TypedDict):
    args: Args
    entry: List[str]
    template: Template


class OriginalArgs(TypedDict):
    argument1: List[OriginalValue]
    argument2: Optional[List[OriginalValue]]


class SourceValueOriginal(TypedDict):
    args: OriginalArgs
    entry: List[OriginalValue]


class ValueOriginal(SourceValueOriginal):
    template: Template
    symmetries: List


class TableContent(TypedDict):
    argument1_number_of_steps: int
    argument2_number_of_steps: Optional[int]
    id: int
    source_value_original: SourceValueOriginal
    value_original: ValueOriginal
    value_float: ValueFloat
    corrected_value_float: ValueFloat
    edited_text: Dict
    entry_type_of_number: NumberType
    entry_number_unit: UnitType
    entry_significant_fractional_place: str
    entry_number_of_cell: str
    argument1_name: str
    argument1_type_of_number: NumberType
    argument1_number_unit: UnitType
    argument1_number_of_cell: str
    argument1_significant_fractional_place: str
    argument2_name: Optional[str]
    argument2_type_of_number: NumberType
    argument2_number_unit: Optional[UnitType]
    argument2_number_of_cell: Optional[str]
    argument2_significant_fractional_place: Optional[str]
    comment: str
    mathematical_parameter: str
    parameter_sets: Dict
    table_type: Dict
    created: str
    updated: str
    public: Literal[True]
    mean_motion: Optional[Any]
    kibana_name: str
    kibana_id: str
    symmetries: List[DSymmetry]
