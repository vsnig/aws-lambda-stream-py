import unittest.mock

import pytest

# import mock
import rx
from rx import operators as ops

from awslambdastream.utils.pipelines import run_pipelines


def test_run_all_pipelines_on_all_inputs():
    pl1 = rx.pipe(ops.map(lambda x: x + 1))
    # pl2 = rx.pipe(ops.map(lambda x: x + 1))
    pl2 = rx.pipe(ops.map(lambda x: x * 3))

    res = (
        rx.of(1, 2)
        .pipe(
            run_pipelines(pl1, pl2),
            ops.to_list(),
        )
        .run()
    )

    assert res == [2, 3, 3, 6]


def test_raises_on_unhandled_error():
    def simulate_handled_error(x):
        raise Exception("simulated error")

    pl = rx.pipe(ops.map(simulate_handled_error))

    with pytest.raises(Exception) as excinfo:
        rx.of(0).pipe(run_pipelines(pl), ops.to_list()).run()

    assert str(excinfo.value) == "simulated error"
