import boto3
from botocore.config import Config


class EventBridgeConnector:
    def __init__(
        self,
        *,
        timeout=1000,
        endpoint_url,
        logger,
    ):
        config = Config(read_timeout=timeout)
        self.bus = boto3.client("events", config=config, endpoint_url=endpoint_url)
        self.logger = logger

    def put_events(self, **params):
        try:
            response = self.bus.put_events(**params)
            self.logger.info(response)
            return response
        except Exception as e:  # pragma: no cover
            self.logger.error(e)
            raise e
