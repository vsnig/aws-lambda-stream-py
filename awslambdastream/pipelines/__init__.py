import sys
from collections import namedtuple
from functools import reduce

import rx
from rx import operators as ops
from rx.core import Observable
from rx.subject import ReplaySubject, Subject

from awslambdastream.faults import fault_handler, flush_faults
from awslambdastream.utils.faults import is_error
from awslambdastream.utils.misc import not_

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
    def assemble_(head, include_fault_handler=True) -> Observable:
        print("assemble")
        keys = the_pipelines.keys()

        def reducer(a, key):
            p = the_pipelines[key]
            p.id = key
            return [*a, p]

        lines = reduce(reducer, keys, [])

        if len(lines) > 0:

            def multicast_mapper(lines):
                def multicast_mapper_(shared):  # shared is multicast source Observable
                    def pl_mapper(pipeline):
                        pipe_ops = [pipeline]
                        if include_fault_handler:
                            pipe_ops.append(ops.catch(fault_handler))

                        return shared.pipe(
                            ops.map(
                                lambda uow: {
                                    "pipeline": pipeline.id,  # todo: change to pipeline id
                                    **uow,
                                }
                            ),
                            ops.flat_map(lambda x: rx.of(x).pipe(*pipe_ops)),
                        )

                    return rx.merge(*map(pl_mapper, lines))

                return multicast_mapper_

            # todo: see original, what's with last pipeline?
            merged = head.pipe(
                ops.multicast(
                    subject_factory=lambda _: Subject(), mapper=multicast_mapper(lines)
                ),
                ops.do_action(lambda x: print("AFTER MULTICAST!!")),
            )
            replay = (
                ReplaySubject()
            )  # through ReplaySubject otherwise problems with concat on hot observable
            merged.subscribe(replay)

            main = replay.pipe(ops.filter(not_(is_error)))
            errors = replay.pipe(ops.filter(is_error), flush_faults(**opt))

            return rx.concat(main, errors)
        # todo: else? (len(lines) == 0) what to return?

    return assemble_
