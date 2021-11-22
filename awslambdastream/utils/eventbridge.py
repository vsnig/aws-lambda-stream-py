import os
import json
import logging
from functools import reduce

import rx
from rx import operators as ops
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

from awslambdastream.connectors.eventbridge import EventBridgeConnector
from awslambdastream.utils.batch import to_batch_uow, unbatch_uow
from awslambdastream.utils.faults import throw_fault
from awslambdastream.utils.json import MyEncoder


def publish_to_eventbridge(
    logger=logging.getLogger("eventbridge"),
    bus_name=os.getenv("BUS_NAME") or "None",
    source="custom",
    event_field="event",
    batch_size=os.getenv("PUBLISH_BATCH_SIZE") or os.getenv("BATCH_SIZE") or 10,
    parallel=os.getenv("PUBLISH_PARALLEL") or os.getenv("PARALLEL") or 8,
    endpoint_url=os.getenv("EVENTBRIDGE_ENDPOINT") or None,  # for localstack testing
    handle_errors=True,
    **_,
):
    connector = EventBridgeConnector(logger=logger, endpoint_url=endpoint_url)
    pool_scheduler = ThreadPoolScheduler(parallel)

    print("bus_name:::::::::", bus_name)

    def to_input_params(batch_uow):
        def makeEntry(uow):
            return {
                # "EventBusName": bus_name,
                # "Source": source,
                "DetailType": uow[event_field]["type"],
                "Detail": json.dumps(uow[event_field], cls=MyEncoder),
            }

        return {
            **batch_uow,
            "inputParams": {"Entries": [makeEntry(uow) for uow in batch_uow["batch"]]},
        }

    def put_events(batch_uow):
        try:
            publish_response = connector.put_events(**batch_uow["inputParams"])
        except Exception as e:
            throw_fault(e, batch_uow, ignore=not handle_errors)

        handle_failed_entries(batch_uow, publish_response)
        return {**batch_uow, "publishResponse": publish_response}

    def _publish(source):
        return source.pipe(
            ops.buffer_with_count(batch_size),
            ops.map(to_batch_uow),
            ops.map(to_input_params),
            ops.flat_map(
                lambda batch_uow: rx.just(batch_uow).pipe(
                    ops.subscribe_on(pool_scheduler),
                    ops.map(put_events),
                )
            ),
            ops.flat_map(unbatch_uow),
        )

    return _publish


def handle_failed_entries(batch_uow, publish_response):
    if publish_response["FailedEntryCount"] > 0:

        def reducer(a, ic):
            i, c = ic
            if "ErrorCode" in c:
                return [
                    *a,
                    {
                        **batch_uow["batch"][i],
                        "inputParam": batch_uow["inputParams"]["Entries"][i],
                        "err": {
                            "code": c["ErrorCode"],
                            "msg": c["ErrorMessage"],
                        },
                    },
                ]
            else:
                return a

        failed = reduce(reducer, enumerate(publish_response["Entries"]), [])

        return throw_fault(
            Exception(
                f"Event Bridge Failed Entry Count: {publish_response['FailedEntryCount']}"
            ),
            {"batch": failed},
        )
