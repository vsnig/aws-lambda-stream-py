import rx
from rx import operators as ops
from rx.subject import ReplaySubject, Subject

from awslambdastream.utils.faults import HandledException, is_error
from awslambdastream.utils.misc import not_


# run with to_list() b/c its asynchronous
def run_pipelines(*pipelines, handled_error_handler=None):
    def fault_handler(e, _):
        return rx.of(e) if type(e) == HandledException else rx.throw(e)

    def _run_pipelines(source):
        def multicast_mapper(lines):
            def _multicast_mapper(shared):  # shared is multicast source Observable
                def pl_mapper(pipeline):
                    pipe_ops = [pipeline]
                    if handled_error_handler:
                        pipe_ops.append(ops.catch(fault_handler))
                    return shared.pipe(
                        ops.flat_map(lambda x: rx.of(x).pipe(*pipe_ops)),
                    )

                return rx.merge(*map(pl_mapper, lines))

            return _multicast_mapper

        merged = source.pipe(
            ops.multicast(
                subject_factory=lambda _: Subject(), mapper=multicast_mapper(pipelines)
            ),
        )
        # through ReplaySubject otherwise problems with concat on hot observable
        replay = ReplaySubject()

        merged.subscribe(replay)

        obvs_to_concat = [replay.pipe(ops.filter(not_(is_error)))]
        if handled_error_handler:
            obvs_to_concat.append(
                replay.pipe(
                    ops.filter(is_error), handled_error_handler
                )  # errors observable
            )

        return rx.concat(*obvs_to_concat)

    return _run_pipelines
