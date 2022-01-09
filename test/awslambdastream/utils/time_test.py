from awslambdastream.utils.time import now


def test_now(mocker):
    mocker.patch("awslambdastream.utils.time.time", return_value=1641682268.993365)
    assert now() == 1641682268993
