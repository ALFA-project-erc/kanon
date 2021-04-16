.. image:: https://gitlab.obspm.fr/lgauffier/kanon/badges/master/pipeline.svg
    :target: https://gitlab.obspm.fr/lgauffier/kanon/-/pipelines
    :alt: Gitlab Pipeline Status
.. image:: https://gitlab.obspm.fr/lgauffier/kanon/badges/master/coverage.svg
    :target: https://gitlab.obspm.fr/lgauffier/kanon/-/commits/master
    :alt: Coverage
.. image:: https://readthedocs.org/projects/kanon/badge/?version=latest
    :target: https://kanon.readthedocs.io/en/latest/?badge=latest
    :alt: Docs status
.. image:: https://img.shields.io/pypi/v/kanonpy
    :target: https://pypi.org/project/kanonpy/
    :alt: Kanon Pypi
.. image:: https://shields.io/badge/python-v3.8-blue
    :target: https://www.python.org/downloads/release/python-380/
    :alt: Python 3.8
.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge


--------

**Kanon** is the History of Astronomy Python package and tools. Still in early development.

Current Features
________________

`units`

- Define standard positional numeral systems (`BasedReal`)
- Working arithmetics on those numbers
- Set your own precision contexts and algorithms on arithmetical operations
- Keep track of all operations

`tables`

- Build or import ancient astronomical tables
- Perform arithmetical and statistical operations
- Support for `BasedReal` values

`calendars`

- Define new calendar types
- Date conversions

How to use
__________

Install the package with `pip`

.. code:: bash

    pip install kanonpy

For now ``kanon`` features are only available through its Python library

.. code:: python

    import kanon.units as u

    a = u.Sexagesimal(1,2,3)
    b = u.Sexagesimal(2,1,59)

    a + b
    # 3,4,2 ;


Development
___________

To start developing on this project you need to install the package in editable mode

.. code:: bash

    git clone git@gitlab.obspm.fr:lgauffier/kanon.git
    cd kanon
    pip install -e .

The changes you make in the code are reflected on your Python environment

Tests
_____

Run tests with tox

.. code:: bash

    # source code tests
    tox -e test

    # example notebooks tests
    tox -e test_notebooks

    # mypy
    tox -e mypy
