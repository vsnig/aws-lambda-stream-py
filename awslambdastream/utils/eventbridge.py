import os
import json
import logging
from functools import reduce

import rx
from rx import operators as ops
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

from awslambdastream.connectors.eventbridge import EventBridgeConnector
from awslambdastream.utils.tags import adorn_standard_tags
from awslambdastream.utils.batch import to_batch_uow, unbatch_uow
from awslambdastream.utils.json import MyEncoder


def publish_to_eventbridge(
    logger=logging.getLogger("eventbridge"),
    bus_name=os.getenv("BUS_NAME") or "None",
    source="custom",
    event_field="event",
    batch_size=os.getenv("PUBLISH_BATCH_SIZE") or os.getenv("BATCH_SIZE") or 10,
    parallel=os.getenv("PUBLISH_PARALLEL") or os.getenv("PARALLEL") or 8,
    endpoint_url=os.getenv("EVENTBRIDGE_ENDPOINT") or None,  # for localstack testing
    **_,
):
    connector = EventBridgeConnector(logger=logger, endpoint_url=endpoint_url)
    pool_scheduler = ThreadPoolScheduler(parallel)

    def to_input_params(batch_uow):
        def makeEntry(uow):
            return {
                "EventBusName": bus_name,
                "Source": source,
                "DetailType": uow[event_field]["type"],
                "Detail": json.dumps(uow[event_field], cls=MyEncoder),
            }

        return {
            **batch_uow,
            "inputParams": {"Entries": [makeEntry(uow) for uow in batch_uow["batch"]]},
        }

    def put_events(batch_uow):
        publish_response = connector.put_events(**batch_uow["inputParams"])
        return {**batch_uow, "publishResponse": publish_response}

    def _publish(source):
        return source.pipe(
            ops.map(adorn_standard_tags(event_field)),
            # ops.do_action(lambda uow: print(uow)),
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
