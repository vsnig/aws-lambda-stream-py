from collections import namedtuple
from functools import reduce

import rx
from rx import operators as ops

from awslambdastream.utils.pipelines import run_pipelines

the_pipelines = {}


def initialize(pipelines, **opt):
    Assembleable = namedtuple("Assembleable", "assemble")
    global the_pipelines

    keys = pipelines.keys()

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
            lines[i] = rx.pipe(
                ops.map(
                    lambda uow: {
                        "pipeline": getattr(l, "id", None),
                        **uow,
                    }
                ),
                l,
            )

        return run_pipelines(*lines)(head).pipe(ops.to_list())

    return _assemble
