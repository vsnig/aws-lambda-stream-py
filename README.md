# aws-lambda-stream-py

**_(non-official) python implementation of [aws-lambda-stream](https://github.com/jgilbert01/aws-lambda-stream)_**

## Details and differences
snake_case instead of camelCase in variables, function names etc. 

`RxPY` in place of `Highland.js` as underlying reactive framework.

## What's implemented
Most useful features for me at the moment. Basically, it's pipelines for processing Kinesis events and publishing to EventBridge (with parallel processing and error handling).
### pipelines
 - [x]  pipeline initialization and execution
 - [x]  pipeline error propagation/publishing
 - [ ]  head error propagation/publishing

### connectors
- [x] EventBridgeConnector

### utils
- [x] eventbridge
- - [x]   publish_to_eventbridge

### from
- [x]  kinesis
- - [x] from_kinesis
- - [x] to_kinesis_records

## Requirements
- Python 3.9+
- Poetry

## Install
`poetry add git+https://github.com/vsnig/aws-lambda-stream-py.git`

## Example
```python
# classify_pipeline.py
from rx import operators as ops

from awslambdastream import faulty

def classify_pipeline(**opt):
    def _classify_pipeline(s):
        return s.pipe(
            ops.filter(on_event),
            ops.map(to_classification_result),
            ops.map(to_publish_request),
            opt["publish"](**opt),
        )

    return _classify_pipeline


@faulty
def on_event(uow):
    return uow["event"]["type"] == "document-created"


@faulty
def to_classification_result(uow):
    result = classify_text(uow["event"]["document"]["text"])
    return {**uow, "classificationResult": result}

...
```

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
