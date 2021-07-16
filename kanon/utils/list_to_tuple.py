from functools import wraps
from typing import Sequence


def _no_list(v):
    return tuple(v) if isinstance(v, Sequence) and not isinstance(v, str) else v


def list_to_tuple(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = (_no_list(arg) for arg in args)
        kwargs = {k: _no_list(v) for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapper
