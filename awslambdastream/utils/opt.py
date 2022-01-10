import os
import logging

from awslambdastream.utils.eventbridge import publish_to_eventbridge

default_options = {
    "logger": logging.getLogger("handler"),
    "bus_name": os.getenv("BUS_NAME"),
    "publish": publish_to_eventbridge,
}
