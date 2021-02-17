from typing import Any, Dict

import pytest
from astropy.units import degree
from papermill.execute import execute_notebook

from kanon.units import Sexagesimal


class TestNotebooks:

    def assert_notebook_result(self, name: str, params: Dict[str, Any], result: str):
        nb = execute_notebook(f'./examples/{name}.ipynb', "-", parameters=params)
        assert nb.cells[-1].outputs[0].data["text/latex"] == result

    @pytest.mark.parametrize("params,result", [
        ({"year": 1327, "month": 7, "day": 3}, "1,47;18,49"),
        ({"year": 1691, "month": 9, "day": 9}, "2,55;31,33"),
    ])
    def test_sun_true_position(self, params, result):
        self.assert_notebook_result("sun_true_position", params,
                                    (Sexagesimal(result) * degree)._repr_latex_()
                                    )
