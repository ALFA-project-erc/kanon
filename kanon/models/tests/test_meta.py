import pytest

from kanon.models.meta import (
    TableType,
    _registered_ids,
    dmodel,
    get_model_by_id,
    models,
)


@pytest.fixture
def mock_models():

    _models = models.copy()
    __reg = _registered_ids.copy()

    models.clear()
    _registered_ids.clear()

    yield

    models.clear()
    _registered_ids.clear()
    models.update(_models)
    _registered_ids.update(__reg)


def test_table_type(mock_models):
    class A(TableType):
        C = "v"

    assert A.C in models


def test_dmodel(mock_models):
    class A(TableType):
        C = "c"
        R = "r"

    @dmodel(A.C, 5, 1)
    def func(x, a):
        ...

    assert get_model_by_id(5) == func
    assert models[A.C]["func"] == func

    assert func.formula_id == 5
    assert func.table_type == A.C
    assert func.params == (1,)
    assert func.args == 1

    with pytest.raises(ValueError) as err:

        @dmodel(A.C, 6, 1)
        def func1(x):
            ...

    assert "Incorrect number of parameters" in str(err)

    with pytest.raises(ValueError) as err:

        @dmodel(A.R, 5, 1)
        def func2(x, a):
            ...

    assert "Formula ID" in str(err)

    with pytest.raises(ValueError) as err:

        @dmodel(A.C, 8, 11, 5)
        def func(x, a, b):
            ...

    assert "func already" in str(err)


def test_astro_id():
    for tt in models:
        assert tt.astro_id() > 0
