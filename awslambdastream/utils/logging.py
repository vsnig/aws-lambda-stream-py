import logging


def start_logging():
    logging.basicConfig(format="%(name)s %(message)s", level=logging.INFO)
