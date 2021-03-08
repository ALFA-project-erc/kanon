.. image:: https://gitlab.obspm.fr/lgauffier/kanon/badges/master/pipeline.svg
    :target: https://gitlab.obspm.fr/lgauffier/kanon/-/commits/master
    :alt: Gitlab Pipeline Status
.. image:: https://gitlab.obspm.fr/lgauffier/kanon/badges/master/coverage.svg
    :target: https://gitlab.obspm.fr/lgauffier/kanon/-/commits/master
    :alt: Coverage
.. image:: https://readthedocs.org/projects/kanon/badge/?version=latest
    :target: https://kanon.readthedocs.io/en/latest/?badge=latest
    :alt: Docs status
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

`~kanon.units`

- Define standard positional numeral systems (through `~kanon.units.radices.BasedReal`)
- Working arithmetics on those numbers
- Specify custom precision and algorithms on arithmetical operations and keep a history of it

`~kanon.tables`

- Build or import ancient astronomical tables
- Perform basic operations on those tables

`~kanon.calendars`

- Define new calendar types
- Convert dates between calendars

How to use
__________

Clone the repository then install the package

.. code:: bash

    git clone git@gitlab.obspm.fr:lgauffier/kanon.git
    pip install .

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
    pip install -e .

The changes you make in the code are reflected on your Python environment

Tests
_____

Run tests with tox

.. code:: bash

    tox -e test
