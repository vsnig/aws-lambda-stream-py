import rx
from rx import operators as ops
from awslambdastream.from_ import from_kinesis, to_kinesis_records
from awslambdastream.pipelines import initialize
from awslambdastream.utils import default_options


def test_invoke_all_pipelines():
    counter = 0

    def count(uow):
        nonlocal counter
        counter += 1
        uow["counter"] = counter
        return uow

    def pl(**opt):
        return lambda s: s.pipe(ops.map(count))

    events = to_kinesis_records(
        [
            {
                "type": "t1",
            }
        ]
    )

    collected = (
        initialize(
            {
                "p1": pl,
                "p2": pl,
                "p3": pl,
            },
            **default_options
        )
        .assemble(from_kinesis(events))
        .run()
    )
    # pprint(collected)

    assert len(collected) == 3
    assert counter == 3


def test_invoke_pipeline_with_buffer():
    def pl(**opt):
        return rx.pipe(ops.buffer_with_count(2))

    events = to_kinesis_records(
        [
            {
                "type": "t1",
            },
            {
                "type": "t1",
            },
        ]
    )
    collected = (
        initialize(
            {
                "p1": pl,
            },
            **default_options
        )
        .assemble(from_kinesis(events))
        .run()
    )
    # collected = rx.from_(events["Records"]).pipe(pl(), ops.to_list()).run()
    # pprint(collected)

    assert collected == [
        [
            {
                "event": {"id": "shardId-000000000000:0", "type": "t1"},
                "pipeline": "p1",
                "record": {
                    "awsRegion": "us-east-1",
                    "eventID": "shardId-000000000000:0",
                    "eventSource": "aws:kinesis",
                    "kinesis": {"data": b"eyJ0eXBlIjogInQxIn0=", "sequenceNumber": "0"},
                },
            },
            {
                "event": {"id": "shardId-000000000000:1", "type": "t1"},
                "pipeline": "p1",
                "record": {
                    "awsRegion": "us-east-1",
                    "eventID": "shardId-000000000000:1",
                    "eventSource": "aws:kinesis",
                    "kinesis": {"data": b"eyJ0eXBlIjogInQxIn0=", "sequenceNumber": "1"},
                },
            },
        ]
    ]

    [
        [
            {
                "event": {"id": "shardId-000000000000:0", "type": "t1"},
                "pipeline": "p1",
                "record": {
                    "awsRegion": "us-east-1",
                    "eventID": "shardId-000000000000:0",
                    "eventSource": "aws:kinesis",
                    "kinesis": {"data": b"eyJ0eXBlIjogInQxIn0=", "sequenceNumber": "0"},
                },
            }
        ],
        [
            {
                "event": {"id": "shardId-000000000000:1", "type": "t1"},
                "pipeline": "p1",
                "record": {
                    "awsRegion": "us-east-1",
                    "eventID": "shardId-000000000000:1",
                    "eventSource": "aws:kinesis",
                    "kinesis": {"data": b"eyJ0eXBlIjogInQxIn0=", "sequenceNumber": "1"},
                },
            }
        ],
    ]
