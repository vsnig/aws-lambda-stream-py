import unittest.mock

import pytest

# import mock
import rx
from rx import operators as ops

from awslambdastream.utils.faults import HandledException, handled_from
from awslambdastream.utils.pipelines import run_pipelines


def test_run_all_pipelines_on_all_inputs():
    pl1 = rx.pipe(ops.map(lambda x: x + 1))
    pl2 = rx.pipe(ops.map(lambda x: x * 3))

    res = rx.of(1, 2).pipe(run_pipelines(pl1, pl2), ops.to_list()).run()

    assert res == [2, 3, 3, 6]


def test_handle_errors_in_the_end():
    def simulate_handled_error(x):
        if x == 1:
            e = Exception("simulated error")
            raise handled_from(e, {})
        else:
            return x

    spy = unittest.mock.Mock(return_value="error processed")

    pl = rx.pipe(ops.map(simulate_handled_error))

    res = (
        rx.of(0, 1, 2)
        .pipe(run_pipelines(pl, handled_error_handler=ops.map(spy)), ops.to_list())
        .run()
    )

    spy.assert_called_once()
    assert res == [0, 2, "error processed"]


def test_raises_on_unhandled_error():
    def simulate_handled_error(x):
        raise Exception("simulated error")

    pl = rx.pipe(ops.map(simulate_handled_error))

    with pytest.raises(Exception) as excinfo:
        rx.of(0).pipe(run_pipelines(pl), ops.to_list()).run()

    assert str(excinfo.value) == "simulated error"
