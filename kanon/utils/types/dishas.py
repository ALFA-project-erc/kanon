from typing import Any, Dict, List, Literal, Optional, TypedDict


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
    argument2: List[str]


class ValueFloat(TypedDict):
    args: Args
    entry: List[str]
    template: Template


class OriginalArgs(TypedDict):
    argument1: List[OriginalValue]
    argument2: List[OriginalValue]


class SourceValueOriginal(TypedDict):
    args: OriginalArgs
    entry: Any


class ValueOriginal(SourceValueOriginal):
    template: Template
    symmetries: List


class WithID(TypedDict):
    id: str


class TableType(WithID):
    astronomical_object: WithID


class TableContent(TypedDict):
    argument1_number_of_steps: int
    argument2_number_of_steps: int
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
    argument2_name: str
    argument2_type_of_number: NumberType
    argument2_number_unit: UnitType
    argument2_number_of_cell: str
    argument2_significant_fractional_place: str
    comment: str
    mathematical_parameter: str
    parameter_sets: Dict
    table_type: TableType
    created: str
    updated: str
    public: Literal[True]
    mean_motion: Optional[Any]
    kibana_name: str
    kibana_id: str
    symmetries: List[DSymmetry]
