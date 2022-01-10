import logging
from awslambdastream.utils.print import print_start_pipeline, print_end_pipeline


def test_print_start_pipeline(caplog):
    uow = {"logger": logging.getLogger(), "event": {"id": "0", "type": "type1"}}

    with caplog.at_level(logging.INFO):
        print_start_pipeline(uow)
    # print(caplog.records[-1].message)
    assert caplog.records[-1].message == "start type: type1, eid: 0"
    assert caplog.records[-1].levelname == "INFO"


def test_print_end_pipeline(caplog):
    uow = {"logger": logging.getLogger(), "event": {"id": "0", "type": "type1"}}

    with caplog.at_level(logging.INFO):
        print_end_pipeline(uow)
    # print(caplog.records[-1].message)
    assert (
        caplog.records[-1].message
        == "end type: type1, eid: 0, uow: {'logger': <RootLogger root (INFO)>, 'event': {'id': '0', 'type': 'type1'}}"
    )
    assert caplog.records[-1].levelname == "INFO"
