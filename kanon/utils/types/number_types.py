from numbers import Real as _Real
from typing import Union

# Prefer this Real for type annotations because of mypy #3186
Real = Union[float, _Real]
