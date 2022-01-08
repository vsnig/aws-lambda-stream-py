# aws-lambda-stream-py

**_(non-official non-complete) python implementation of [aws-lambda-stream](https://github.com/jgilbert01/aws-lambda-stream)_**


## What's implemented
Most useful features for me at the moment. Basically, it's pipelines for processing Kinesis events and publishing to EventBridge.


### pipelines
 - [x]  pipeline initialization and execution

### connectors
- [x] EventBridgeConnector

### utils
- [x] eventbridge
- - [x]   publish_to_eventbridge

### from
- [x]  kinesis
- - [x] from_kinesis
- - [x] to_kinesis_records

## Details and differences
snake_case instead of camelCase in variables, function names etc. except UOW field names 

options are passed as named arguments

`RxPY` in place of `Highland.js` as underlying reactive framework

## Fault handling not implemented :(
..because of observable contract that requires observable to stop on error. The trick with lifting UOW and catching error in new observer, then flat_map'ing disables batch functionality that is unacceptable. Suggestions are welcome.
## Requirements
- Python 3.9+
- Poetry

## Install
`poetry add git+https://github.com/vsnig/aws-lambda-stream-py.git@master`

## Example

```python
# listener.py
from awslambdastream import default_options, from_kinesis, initialize

from .classify_pipeline import classify_pipeline

PIPELINES = {"classify_pipeline": classify_pipeline}

OPTIONS = {**default_options}


class Handler:
    def __init__(self, options=OPTIONS):
        self.options = options

    def handle(self, event, include_errors=True):
        return initialize(PIPELINES, **self.options).assemble(
            from_kinesis(event), include_errors
        )


def handle(event, context):
    print("event: ", event)
    print("context: ", context)

    Handler({**OPTIONS}).handle(event).run()
    return "Success"
```

```python
# classify_pipeline.py
import rx
from rx import operators as ops

from awslambdastream import faulty

from ..utils import classify_text


def classify_pipeline(**opt):
    return rx.pipe(
      ops.filter(on_event),
      ops.map(to_classification_result),
      ops.map(to_emit),
      opt["publish"](**opt, event_field="emit"),
    )


def on_event(uow):
    return uow["event"]["type"] == "document-created"


def to_classification_result(uow):
    result = classify_text(uow["event"]["document"]["text"])
    return {**uow, "classificationResult": result}


def to_emit(uow):
    return {
        **uow,
        "emit": {
            **uow["event"],
            "type": "document-classified",
            "cls": uow["classificationResult"],
        },
    }
```


