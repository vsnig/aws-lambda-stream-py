from rx import operators as ops

from awslambdastream.pipelines import initialize
from awslambdastream.from_ import from_kinesis, to_kinesis_records
from awslambdastream.faults import handled, FAULT_EVENT_TYPE
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
  
  events = to_kinesis_records([{
      "type": 't1',
    }]);
  
  collected = initialize({
    "p1": pl,
    "p2": pl,
    "p3": pl,
  }, **default_options).assemble(from_kinesis(events)).pipe(
    ops.to_list()
  ).run()
  
  assert len(collected) == 3
  assert counter == 3
    

def test_propagate_pipeline_errors(mocker):
  mocker.patch(
    'awslambdastream.utils.eventbridge.EventBridgeConnector.put_events', 
    return_value={'FailedEntryCount': 0})
  
  def pl(**opt):
    def mapper(uow):
      e = ValueError("simulated error")
      h = handled.of(e, uow)
      raise h
    def _pl(s):
      return s.pipe(
        ops.map(mapper)  
      )
    return _pl
      
  events = to_kinesis_records([{
      "type": 't2',
    }])

  collected = initialize({"px1": pl}, **default_options) \
                .assemble(from_kinesis(events)) \
                .pipe(
                  ops.to_list()
                ).run()

  assert len(collected) == 1
  assert collected[0]["event"]["type"] == FAULT_EVENT_TYPE
  assert collected[0]["event"]["err"]["name"] == "ValueError"
  assert collected[0]["event"]["err"]["message"] == "simulated error"
  
  assert collected[0]["event"]["tags"]["functionname"] == "None"
  assert collected[0]["event"]["tags"]["pipeline"] == "px1"

  assert collected[0]["event"]["uow"] != None
  
  # propagate errors from head - not implemented