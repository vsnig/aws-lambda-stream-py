import pytest

from awslambdastream.utils.faults import HandledException, faulty, is_error, throw_fault


def test_HandledException_constructor():
    def fn():
        raise HandledException(message="error!", uow={"a": "b"}, name="ErrorName")

    with pytest.raises(HandledException) as excinfo:
        fn()
    assert isinstance(excinfo.value, Exception)
    assert excinfo.value.message == "error!"
    assert excinfo.value.name == "ErrorName"
    assert excinfo.value.uow == {"a": "b"}


def test_faulty_handles_ok():
    @faulty
    def fn(uow):
        return "ok"

    uow = {"hey": "you"}
    res = fn(uow)
    assert res == "ok"


def test_faulty_handles_fault():
    @faulty
    def fn(uow):
        raise Exception("Some error")

    uow = {"hey": "you"}
    with pytest.raises(HandledException) as excinfo:
        fn(uow)
    assert excinfo.value.message == "Some error"
    assert excinfo.value.uow == {"hey": "you"}
    assert excinfo.value.name == "Exception"


def test_throw_fault():
    e = Exception("error")
    uow = {"id": "000"}

    with pytest.raises(HandledException) as excinfo:
        throw_fault(e, uow)

    assert excinfo.value.name == "Exception"
    assert excinfo.value.message == "error"
    assert excinfo.value.uow == {"id": "000"}


def test_throw_fault_ignore():
    e = Exception("error")
    uow = {"id": "000"}

    with pytest.raises(Exception) as excinfo:
        throw_fault(e, uow, ignore=True)
    assert str(excinfo.value) == "error"


def test_is_error_pos():
    assert is_error(Exception("error")) == True


def test_is_error_neg():
    assert is_error("str") == False
