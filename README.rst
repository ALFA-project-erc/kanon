.. image:: https://github.com/legau/kanon/workflows/CI/badge.svg
    :target: https://github.com/legau/kanon/actions
    :alt: GitHub Pipeline Status
.. image:: https://codecov.io/gh/legau/kanon/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/legau/kanon/branch/master
    :alt: Coverage
.. image:: https://readthedocs.org/projects/kanon/badge/?version=latest
    :target: https://kanon.readthedocs.io/en/latest/?badge=latest
    :alt: Docs status
.. image:: https://img.shields.io/pypi/v/kanon
    :target: https://pypi.org/project/kanon/
    :alt: Kanon Pypi
.. image:: https://shields.io/badge/python-v3.8-blue
    :target: https://www.python.org/downloads/release/python-380/
    :alt: Python 3.8
.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge


--------

**Kanon** is the History of Astronomy Python package and tools.

Current Features
________________

`units`

- Define standard positional numeral systems with standard arithmetics (`BasedReal`)
- Set your own precision contexts and algorithms on arithmetical operations (`PrecisionContext`)
- Keep track of all operations

`tables`

- Build or import ancient astronomical tables
- Perform arithmetical and statistical operations
- Support for `BasedReal` values

`calendars`

- Define new calendar types
- Date conversions

`models`

- Collection of mathematical models used for all kinds of geocentric astronomical tables

How to use
__________

Install the package with `pip`

.. code:: bash

    pip install kanon

Import Kanon and begin trying all its features

.. code:: python

    import kanon.units as u

    a = u.Sexagesimal(1,2,3)
    b = u.Sexagesimal(2,1,59)

    a + b
    # 3,4,2 ;


Development
___________

To start developing on this project you need to install
the package with `poetry` (`Installing Poetry <https://python-poetry.org/docs/>`)

.. code:: bash

    git clone https://github.com/legau/kanon.git
    cd kanon
    poetry install

The changes you make in the code are reflected on your Python environment.

Activate pre-commit checks :

.. code:: bash

    pre-commit install

Tests
_____

Run tests with tox

.. code:: bash

    # source code tests
    tox -e test

    # example notebooks tests
    tox -e test_notebooks

    # linting
    pre-commit run --all-files
