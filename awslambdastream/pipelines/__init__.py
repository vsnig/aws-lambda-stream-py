import json
import logging
from collections import namedtuple
from functools import reduce

import rx
from rx import operators as ops

from awslambdastream.utils.pipelines import run_pipelines
from awslambdastream.utils.logging import setup_logging

the_pipelines = {}

logger = logging.getLogger("pl:init")


def initialize(pipelines, **opt):
    Assembleable = namedtuple("Assembleable", "assemble")
    global the_pipelines

    setup_logging()

    keys = list(pipelines.keys())

    logger.info(f"initialize: {json.dumps(keys)}")

    the_pipelines = reduce(
        lambda acc, id: {
            **acc,
            id: pipelines[id](id=id, **opt),
        },
        keys,
        {},
    )

    # ? memoryCache.clear();

    return Assembleable(assemble=assemble(**opt))


def assemble(**opt):
    def _assemble(head):
        keys = the_pipelines.keys()

        def reducer(a, key):
            p = the_pipelines[key]
            p.id = key
            return [*a, p]

        lines = reduce(reducer, keys, [])

        for i, l in enumerate(lines):
            p_id = getattr(l, "id", None)
            logger.info(f"FORK: {p_id}")

            lines[i] = rx.pipe(
                ops.map(
                    lambda uow: {
                        "pipeline": p_id,
                        **uow,
                        **add_logger(p_id),
                    }
                ),
                l,
            )

        return run_pipelines(*lines)(head).pipe(ops.to_list())

    return _assemble


def add_logger(id):
    return {"logger": logging.getLogger(f"pl:{id}")}
