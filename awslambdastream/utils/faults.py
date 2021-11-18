class HandledException(Exception):
    def __init__(self, *, uow, name, message):
        super().__init__(message)
        self.uow = uow
        self.name = name
        self.message = message

    def __str__(self):
        return f"{self.name} - {self.message}"


# create HandledException from exception and uow
def handled_from(e, uow):
    return HandledException(
        uow=uow,
        name=type(e).__name__,
        message=str(e),
    ).with_traceback(e.__traceback__)


# use as @decorator
def faulty(fn):
    def _fn(uow, *args, **kwargs):
        try:
            return fn(uow, *args, **kwargs)
        except Exception as e:
            raise handled_from(e, uow)

    return _fn


def throw_fault(e, uow, ignore=False):
    if not ignore:
        e = handled_from(e, uow)
    raise e


def is_error(e):
    bad = issubclass(type(e), Exception)
    # print("error?", bad)
    return bad
