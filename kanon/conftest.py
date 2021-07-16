"""Configure Test Suite.

This file is used to configure the behavior of pytest when using the Astropy
test infrastructure. It needs to live inside the package in order for it to
get picked up when running the tests inside an interpreter using
packagename.test

"""

import os

from hypothesis.strategies._internal.core import tuples

# For Astropy 3.0 and later, we can use the standalone pytest plugin
try:
    from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS

    ASTROPY_HEADER = True
except ImportError:
    ASTROPY_HEADER = False


def pytest_configure(config):
    """Configure Pytest with Astropy.

    Parameters
    ----------
    config : pytest configuration

    """
    if ASTROPY_HEADER:

        config.option.astropy_header = True

        # Customize the following lines to add/remove entries from the list of
        # packages for which version numbers are displayed when running the tests.
        PYTEST_HEADER_MODULES.pop("Pandas", None)
        PYTEST_HEADER_MODULES["scikit-image"] = "skimage"

        from . import __version__

        packagename = os.path.basename(os.path.dirname(__file__))
        TESTED_VERSIONS[packagename] = __version__


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


# Uncomment the last two lines in this block to treat all DeprecationWarnings as
# exceptions. For Astropy v2.0 or later, there are 2 additional keywords,
# as follow (although default should work for most cases).
# To ignore some packages that produce deprecation warnings on import
# (in addition to 'compiler', 'scipy', 'pygments', 'ipykernel', and
# 'setuptools'), add:
#     modules_to_ignore_on_import=['module_1', 'module_2']
# To ignore some specific deprecation warning messages for Python version
# MAJOR.MINOR or later, add:
#     warnings_to_ignore_by_pyver={(MAJOR, MINOR): ['Message to ignore']}
# from astropy.tests.helper import enable_deprecations_as_exceptions  # noqa
# enable_deprecations_as_exceptions()
