def print_start_pipeline(uow):
    print_start(uow["logger"])(uow)


def print_end_pipeline(uow):
    print_end(uow["logger"])(uow)


def print_start(logger):
    return lambda uow: logger.info(
        f'start type: {uow["event"]["type"]}, eid: {uow["event"]["id"]}'
    )


def print_end(logger):
    return lambda uow: logger.info(
        f'end type: {uow["event"]["type"]}, eid: {uow["event"]["id"]}, uow: {uow}'
    )
