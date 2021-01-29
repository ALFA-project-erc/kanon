class BaseNumberException(Exception):
    pass


class EmptyStringException(BaseNumberException):
    pass


class TooManySeparators(BaseNumberException):
    pass


class TypeMismatch(BaseNumberException):
    pass


class IllegalBaseValueError(ValueError):
    """
    Raised when a value is not in the range of the specified base.

    Parameters
    ----------
    :param radix: RadixBase
    :param base: int
    :param num: int
    :raises: IllegalBaseValueError

    ```python
    if not 0 <= val < radix[i]:
        raise IllegalBaseValueError(radix, radix[i], val)
    ```
    """

    def __init__(self, radix, base, num):
        self.radix = radix
        self.base = base
        self.num = num

    def __str__(self):
        return f"An invalid value for ({self.radix.name}) was found ('{self.num}'); should be in the range [0,{self.base}])."


class IllegalFloatError(TypeError):
    """
    Raised when an expected int value is a float.

    Parameters
    ----------
    :param num: float
    :raises: IllegalFloatError

    ```python
    if isinstance(val, float):
        raise IllegalFloatError(val)
    ```
    """

    def __init__(self, num):
        self.num = num

    def __str__(self):
        return f"An illegal float value was found ('{self.num}')"
