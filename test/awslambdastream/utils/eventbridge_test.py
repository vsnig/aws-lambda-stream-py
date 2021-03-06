import json

import pytest
import rx
from rx import operators as ops

from awslambdastream.utils.eventbridge import publish_to_eventbridge as publish


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
            "tags": {
                "account": "None",
                "region": "us-east-1",
                "stage": "None",
                "source": "None",
                "functionname": "None",
                "pipeline": "None",
            },
        },
        "inputParams": {
            "Entries": [
                {
                    "EventBusName": "None",
                    "Source": "custom",
                    "DetailType": "p1",
                    "Detail": '{"id": "79a0d8f0-0eef-11ea-8d71-362b9e155667", "type": "p1", "partitionKey": "79a0d8f0-0eef-11ea-8d71-362b9e155667", "tags": {"account": "None", "region": "us-east-1", "stage": "None", "source": "None", "functionname": "None", "pipeline": "None"}}',
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
