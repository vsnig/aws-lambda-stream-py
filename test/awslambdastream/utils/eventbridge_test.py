import json

import pytest
import rx
from rx import operators as ops

from awslambdastream.utils.eventbridge import publish_to_eventbridge as publish
from awslambdastream.utils.faults import HandledException


def test_batch_and_publish(mocker):
    mocker.patch(
        "awslambdastream.utils.eventbridge.EventBridgeConnector.put_events",
        return_value={"FailedEntryCount": 0},
    )

    uows = [
        {
            "event": {
                "id": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                "type": "p1",
                "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
            },
        }
    ]

    collected = rx.from_(uows).pipe(publish(), ops.to_list()).run()

    assert len(collected) == 1
    assert collected[0]["publishResponse"] == {"FailedEntryCount": 0}
    assert collected[0] == {
        "event": {
            "id": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
            "type": "p1",
            "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
        },
        "inputParams": {
            "Entries": [
                {
                    "EventBusName": "None",
                    "Source": "custom",
                    "DetailType": "p1",
                    "Detail": json.dumps(
                        {
                            "id": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                            "type": "p1",
                            "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                        }
                    ),
                }
            ]
        },
        "publishResponse": {"FailedEntryCount": 0},
    }
    # print(stub.call_args_list)
    # stub.assert_called_with(Entries=[{
    #   "EventBusName": 'None',
    #   "Source": 'custom',
    #   "DetailType": 'p1',
    #   "Detail": json.dumps({
    #       "id": '79a0d8f0-0eef-11ea-8d71-362b9e155667',
    #       "type": 'p1',
    #       "partitionKey": '79a0d8f0-0eef-11ea-8d71-362b9e155667',
    #     })
    # }])


def test_throw_handled_error(mocker):
    mocker.patch(
        "awslambdastream.utils.eventbridge.EventBridgeConnector.put_events",
        # return_value={'FailedEntryCount': 0},
        side_effect=ValueError("mocked error"),
    )

    uows = [
        {
            "event": {
                "id": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                "type": "p1",
                "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
            },
        }
    ]

    with pytest.raises(HandledException) as excinfo:
        rx.from_(uows).pipe(publish(), ops.to_list()).run()

    assert excinfo.value.name == "ValueError"
    assert excinfo.value.message == "mocked error"
    assert excinfo.value.uow == {
        "batch": [
            {
                "event": {
                    "id": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                    "type": "p1",
                    "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667",
                }
            }
        ],
        "inputParams": {
            "Entries": [
                {
                    "EventBusName": "None",
                    "Source": "custom",
                    "DetailType": "p1",
                    "Detail": '{"id": "79a0d8f0-0eef-11ea-8d71-362b9e155667", "type": "p1", "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667"}',
                }
            ]
        },
    }


def test_handle_failed_entry(mocker):
    mocker.patch(
        "awslambdastream.utils.eventbridge.EventBridgeConnector.put_events",
        return_value={
            "FailedEntryCount": 1,
            "Entries": [{"ErrorCode": "1", "ErrorMessage": "M1"}, {"EventId": "999"}],
        },
    )

    uows = [
        {
            "event": {
                "id": "14f46ef2-0ef0-11ea-8d71-362b9e155667",
                "type": "p2",
                "partitionKey": "f440c880-4c41-4965-8658-2cbd503a2c73",
            },
        }
    ]

    with pytest.raises(HandledException) as excinfo:
        rx.from_(uows).pipe(publish(), ops.to_list()).run()

    assert excinfo.value.name == "Exception"
    assert excinfo.value.message == "Event Bridge Failed Entry Count: 1"
    assert excinfo.value.uow == {
        "batch": [
            {
                "event": {
                    "id": "14f46ef2-0ef0-11ea-8d71-362b9e155667",
                    "type": "p2",
                    "partitionKey": "f440c880-4c41-4965-8658-2cbd503a2c73",
                },
                "inputParam": {
                    "EventBusName": "None",
                    "Source": "custom",
                    "DetailType": "p2",
                    "Detail": '{"id": "14f46ef2-0ef0-11ea-8d71-362b9e155667", "type": "p2", "partitionKey": "f440c880-4c41-4965-8658-2cbd503a2c73"}',
                },
                "err": {"code": "1", "msg": "M1"},
            }
        ]
    }
