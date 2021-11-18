from rx import operators as ops

from awslambdastream import default_options
from awslambdastream.faults import FAULT_EVENT_TYPE, flush_faults
from awslambdastream.from_ import from_kinesis, to_kinesis_records
from awslambdastream.utils.faults import handled_from


def test_flush_faults(mocker):
    stub = mocker.patch(
        "awslambdastream.utils.eventbridge.EventBridgeConnector.put_events",
        return_value={"FailedEntryCount": 0},
    )

    def simulate_handled_exception(uow):
        e = Exception("simulated exception")
        return handled_from(e, uow)

    events = to_kinesis_records([{"type": "thing-created"}])

    collected = (
        from_kinesis(events)
        .pipe(
            ops.map(simulate_handled_exception),
            flush_faults(**{**default_options}),
            ops.to_list(),
        )
        .run()
    )

    # print("collected::::", collected[0]["event"]["uow"])
    stub.assert_called_once()

    assert len(collected) == 1
    assert collected[0]["event"]["type"] == FAULT_EVENT_TYPE
    assert collected[0]["event"]["err"]["name"] == "Exception"
    assert collected[0]["event"]["err"]["message"] == "simulated exception"

    assert collected[0]["event"]["tags"]["functionname"] == "None"
    assert collected[0]["event"]["tags"]["pipeline"] == "None"

    assert collected[0]["event"]["uow"] == {
        "record": {
            "eventSource": "aws:kinesis",
            "eventID": "shardId-000000000000:0",
            "awsRegion": "us-east-1",
            "kinesis": {
                "sequenceNumber": "0",
                "data": b"eyJ0eXBlIjogInRoaW5nLWNyZWF0ZWQifQ==",
            },
        },
        "event": {"id": "shardId-000000000000:0", "type": "thing-created"},
    }
