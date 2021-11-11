import base64
import json

import rx
from rx import operators as ops


def from_kinesis(event):
    return rx.from_(event["Records"]).pipe(
        ops.map(
            lambda record: {
                "record": record,
                "event": base64.b64decode(record["kinesis"]["data"]),
            }
        ),
        ops.map(
            lambda uow: {
                **uow,
                "event": {"id": uow["record"]["eventID"], **json.loads(uow["event"])},
            }
        ),
    )


def to_kinesis_records(events):
    return {
        "Records": [
            {
                "eventSource": "aws:kinesis",
                "eventID": "shardId-000000000000:{}".format(i),
                "awsRegion": "us-east-1",
                "kinesis": {
                    "sequenceNumber": "{}".format(i),
                    "data": base64.b64encode(json.dumps(event).encode()),
                },
            }
            for i, event in enumerate(events)
        ]
    }


UNKNOWN_KINESIS_EVENT_TYPE = to_kinesis_records([{"type": "unknown-type"}])
