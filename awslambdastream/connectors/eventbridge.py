import boto3
from botocore.config import Config


class EventBridgeConnector:
    def __init__(self, *, logger, timeout=1000, **client_opts):
        config = Config(read_timeout=timeout)
        self.bus = boto3.client("events", config=config, **client_opts)
        self.logger = logger

    def put_events(self, **params):
        try:
            response = self.bus.put_events(**params)
            self.logger.info(response)
            return response
        except Exception as e:  # pragma: no cover
            self.logger.error(e)
            raise e
