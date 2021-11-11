import os
import traceback
import uuid

import rx
from rx import operators as ops

from awslambdastream.faults.handled import HandledException
from awslambdastream.utils import now
from awslambdastream.utils.eventbridge import publish_to_eventbridge as publish
from awslambdastream.utils.rx import from_subject

FAULT_EVENT_TYPE = "fault"


def fault_handler(e, _):
    if type(e) == HandledException:
        return rx.of(e)
    else:
        # rethrow unhandled to stop processing
        return rx.throw(e)


def to_fault_event(he):
    fault_event = {
        "id": str(uuid.uuid1()),
        "partitionKey": str(uuid.uuid4()),
        "type": FAULT_EVENT_TYPE,
        "timestamp": now(),
        "tags": {
            "functionname": os.getenv("AWS_LAMBDA_FUNCTION_NAME") or "None",
            "pipeline": he.uow["pipeline"] or "None",
        },
        "err": {
            "name": he.name,
            "message": he.message,
            "stack": "".join(
                traceback.format_exception(etype=he.name, value=he, tb=he.__traceback__)
            ),
        },
        "uow": he.uow,  # trimAndRedact(err.uow),
    }
    return fault_event


# def faults(e, source):
#   global the_faults
#   if type(e) == HandledException:
#     the_faults.append({
#       "id": uuid.uuid1(),
#       "partitionKey": uuid.uuid4(),
#       "type": FAULT_EVENT_TYPE,
#       "timestamp": now(),
#     })


def to_uow(fault):
    return {"event": fault}


def flush_faults(**opt):
    def _flush_faults(s):
        return rx.pipe(
            ops.map(to_fault_event),
            ops.map(to_uow),
            opt["publish"](
                **opt,
                handle_errors=False,  # don't publish faults for faults
                batch_size=int(os.getenv("FAULTS_BATCH_SIZE") or 0)
                or int(os.getenv("BATCH_SIZE") or 0)
                or 4,
                parallel=int(os.getenv("FAULTS_PARALLEL") or 0)
                or int(os.getenv("PARALLEL") or 0)
                or 4,
            ),
        )(s)

    return _flush_faults
