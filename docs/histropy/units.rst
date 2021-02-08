:mod:`radices` --- Arithmetic for any positional notation systems
==================================================================

    >>> from kanon.units.radices import RadixBase, radix_registry
    >>> RadixBase([20, 5, 18], [24, 60], "example_radix", ["","u ","sep "])
    >>> number = radix_registry.ExampleRadix((8, 12, 3, 1), (23, 31))
    >>> number
    08 12u 3sep 01 ; 23,31
    >>> float(number)
    1261.979861111111

.. automodapi:: kanon.units.radices
    :inherited-members:
    :include-all-objects:
