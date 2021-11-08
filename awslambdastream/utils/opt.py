import os

from awslambdastream.utils.eventbridge import publish_to_eventbridge

default_options = {
  "bus_name": os.getenv("BUS_NAME"),
  "publish": publish_to_eventbridge
}