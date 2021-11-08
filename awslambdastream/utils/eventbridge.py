import json
import logging
import rx
from functools import reduce
from rx import operators as ops
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler

from awslambdastream.utils.faults import throw_fault
from awslambdastream.utils.batch import to_batch_uow, unbatch_uow
from awslambdastream.utils.json import MyEncoder
from awslambdastream.connectors.eventbridge import EventBridgeConnector


def publish_to_eventbridge(
  logger=logging.getLogger("eventbridge"),
  bus_name="None",
  source="custom",
  event_field="event",
  batch_size=10,
  parallel=8,
  handle_errors=True,
  **_
):
  connector = EventBridgeConnector(logger=logger)
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
      "inputParams": {
        "Entries": [makeEntry(uow) for uow in batch_uow['batch']]
      }
    }

  def put_events(batch_uow):
    try:
      publish_response = connector.put_events(**batch_uow['inputParams'])
    except Exception as e:
      throw_fault(e, batch_uow, ignore=not handle_errors)
    
    handle_failed_entries(batch_uow, publish_response)
    return {**batch_uow, "publishResponse": publish_response } 

  def _publish(source):
    return source.pipe(
      ops.buffer_with_count(batch_size),
      ops.map(to_batch_uow),

      ops.map(to_input_params),
      ops.flat_map(lambda batch_uow: rx.just(batch_uow).pipe(
        ops.subscribe_on(pool_scheduler),
        ops.map(put_events),
      )),

      ops.flat_map(unbatch_uow)
    )

  return _publish

def handle_failed_entries(batch_uow, publish_response):
  if publish_response["FailedEntryCount"] > 0:
    def reducer(a, ic):
      i, c = ic
      if "ErrorCode" in c:
        return [
          *a, {
            **batch_uow["batch"][i],
            "inputParam": batch_uow["inputParams"]["Entries"][i],
            "err": {
              "code": c["ErrorCode"],
              "msg": c["ErrorMessage"],
            }
          }
        ]
      else:
        return a
    
    failed = reduce(reducer, enumerate(publish_response["Entries"]) , [])

    return throw_fault(
      Exception(f"Event Bridge Failed Entry Count: {publish_response['FailedEntryCount']}"), 
      { "batch": failed })
