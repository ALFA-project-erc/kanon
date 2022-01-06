from enum import EnumMeta, IntEnum, unique
from inspect import signature
from typing import Dict, Protocol, Tuple

from kanon.utils.types.number_types import Real


class ModelCallable(Protocol):
    def __call__(self, *args: Real) -> Real:
        ...

    __name__: str
    table_type: "TableType"
    args: int
    params: Tuple[int, ...]
    formula_id: int


models: Dict["TableType", Dict[str, ModelCallable]] = {}


class EnumRegisterMeta(EnumMeta):
    def __new__(*args, **kwargs):
        cls = EnumMeta.__new__(*args, **kwargs)
        models.update({v: {} for v in cls.__members__.values()})
        return cls


@unique
class TableType(IntEnum, metaclass=EnumRegisterMeta):
    @classmethod
    def astro_id(cls) -> int:
        """Returns its DISHAS Astronomical Object ID

        :rtype: int
        """
        raise NotImplementedError


_registered_ids: Dict[int, ModelCallable] = {}


def dmodel(table_type: TableType, formula_id: int, *params: int):
    """Decorator for models existing in DISHAS as a Formula Definition

    :param table_type: TableType of the formula
    :type table_type: TableType
    :param formula_id: ID of the formula from DISHAS
    :type formula_id: int
    :param *params: Parameters IDs
    :type formula_id: *int
    """

    def decorator(fn: ModelCallable):
        fn_params_len = len(signature(fn).parameters)

        if fn_params_len - len(params) not in (1, 2):
            raise ValueError("Incorrect number of parameters")

        if formula_id in _registered_ids:
            raise ValueError(f"Formula ID {formula_id} already registered")

        if fn.__name__ in models[table_type]:
            raise ValueError(
                f"{fn.__name__} already defined for table_type {table_type}"
            )

        models[table_type][fn.__name__] = fn
        _registered_ids[formula_id] = fn

        fn.table_type = table_type
        fn.args = fn_params_len - len(params)
        fn.params = params
        fn.formula_id = formula_id

        return fn

    return decorator


def get_model_by_id(formula_id: int) -> ModelCallable:
    """Returns a model function from its DISHAS Formula ID

    :type formula_id: int
    :rtype: ModelCallable
    """
    return _registered_ids[formula_id]
