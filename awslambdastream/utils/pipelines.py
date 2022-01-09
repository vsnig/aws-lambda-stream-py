import rx
from rx import operators as ops
from rx.subject import Subject


def run_pipelines(*pipelines):
    def _run_pipelines(source):
        def multicast_mapper(lines):
            return lambda shared_source: rx.merge(
                *[line(shared_source) for line in lines]
            )

        merged = source.pipe(
            ops.multicast(
                subject_factory=lambda _: Subject(), mapper=multicast_mapper(pipelines)
            ),
        )
        return merged

    return _run_pipelines
