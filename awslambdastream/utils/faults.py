from awslambdastream.faults import handled


# use as @decorator
def faulty(fn):
    def _fn(uow, *args, **kwargs):
        try:
            fn(uow, *args, **kwargs)
        except Exception as e:
            raise handled.of(e, uow)

    return _fn


def throw_fault(e, uow, ignore=False):
    if not ignore:
        e = handled.of(e, uow)
    raise e


def is_error(e):
    bad = issubclass(type(e), Exception)
    # print("error?", bad)
    return bad
