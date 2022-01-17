def _hypothesis_sexagesimal_strategy():
    """We define hypothesis strategy to generate Sexagesimal values in tests"""
    from hypothesis import HealthCheck, settings
    from hypothesis.strategies import (
        builds,
        decimals,
        integers,
        lists,
        register_type_strategy,
        sampled_from,
        tuples,
    )

    from kanon.units import Historical, Sexagesimal

    settings.register_profile("def", suppress_health_check=(HealthCheck.too_slow,))
    settings.load_profile("def")

    strat = builds(
        Sexagesimal,
        lists(integers(0, 59), max_size=2),
        lists(integers(0, 59), max_size=2),
        remainder=decimals(0, 1).filter(lambda x: x != 1),
        sign=sampled_from((-1, 1)),
    )
    register_type_strategy(Sexagesimal, strat)

    strat = builds(
        Historical,
        tuples(integers(0, 9), integers(0, 11), integers(0, 29)),
        lists(integers(0, 59), max_size=2),
        remainder=decimals(0, 1).filter(lambda x: x != 1),
        sign=sampled_from((-1, 1)),
    )
    register_type_strategy(Historical, strat)


_hypothesis_sexagesimal_strategy()
