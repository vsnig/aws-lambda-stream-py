# aws-lambda-stream-py

**_(non-official) python implementation of [aws-lambda-stream](https://github.com/jgilbert01/aws-lambda-stream)_**

## Details, differences and challenges
snake_case instead of camelCase in variables, function names etc. 

`RxPY` in place of `Highland.js` as underlying reactive framework.

With `RxPY` there's no (known to me) clean way to handle errors in source observables hence no error handling for `head` of pipelines. Any suggestions on this matter are appreciated.

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
Python 3.9+

## Install
`poetry add git+https://github.com/vsnig/aws-lambda-stream-py.git`
 
 or

`pip install git+https://github.com/vsnig/aws-lambda-stream-py.git`

## Example
```python
# pipeline.py
from rx import operators as ops
from awslambdastream import faulty, publish

def pipeline(**opt):
  @faulty
  def classify(uow):
    result = classify_text(uow['thing']['text'])
    return {
      **uow,
      classificationResult: result
    }
  
  def _pipeline(s):
    return s.pipe(
      ops.map(classify)
      opt["publish"](**opt)
    )
  return _pipeline
```

```python
# handler.py
from awslambdastream import initialize, from_kinesis, default_options

from pipeline1 import pipeline1
from pipeline2 import pipeline2

PIPELINES = {
  "pipeline1": pipeline1,
  "pipeline2": pipeline2,
}

OPTIONS = { **default_options, ... }

def handler(event):
  return initialize(PIPELINES, OPTIONS) \
    .assemble(from_kinesis(event)) \
    .run()
```
