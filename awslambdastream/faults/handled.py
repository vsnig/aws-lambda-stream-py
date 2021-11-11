class HandledException(Exception):
    def __init__(self, *, uow, name, message):
        super().__init__(message)
        self.uow = uow
        self.name = name
        self.message = message

    def __str__(self):
        return f"{self.name} - {self.message}"


# create HandledException from exception and uow
def of(e, uow):
    return HandledException(
        uow=uow,
        name=type(e).__name__,
        message=str(e),
    ).with_traceback(e.__traceback__)
