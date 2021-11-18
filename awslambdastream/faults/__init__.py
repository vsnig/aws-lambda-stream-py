import os
import traceback
import uuid

import rx
from rx import operators as ops

from awslambdastream.utils.faults import HandledException
from awslambdastream.utils.time import now

FAULT_EVENT_TYPE = "fault"


def flush_faults(**opt):
    def to_uow(fault):
        return {"event": fault}

    def to_fault_event(handled_error):
        return {
            "id": str(uuid.uuid1()),
            "partitionKey": str(uuid.uuid4()),
            "type": FAULT_EVENT_TYPE,
            "timestamp": now(),
            "tags": {
                "functionname": os.getenv("AWS_LAMBDA_FUNCTION_NAME") or "None",
                "pipeline": handled_error.uow.get("pipeline", "None"),
            },
            "err": {
                "name": handled_error.name,
                "message": handled_error.message,
                "stack": "".join(
                    traceback.format_exception(
                        etype=handled_error.name,
                        value=handled_error,
                        tb=handled_error.__traceback__,
                    )
                ),
            },
            "uow": handled_error.uow,  # trimAndRedact(err.uow),
        }

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
