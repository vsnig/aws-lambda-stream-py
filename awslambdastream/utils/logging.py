import os
import logging


def setup_logging():
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
    logging.getLogger().setLevel(LOG_LEVEL)
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s", force=True
    )
