import json
import logging
import botocore.session
from botocore.stub import Stubber

from awslambdastream.connectors.eventbridge import EventBridgeConnector

logger = logging.getLogger('test')

def test_putEvents():
  entries = [{
    'Source': 'custom',
    'DetailType': 'test-type',
    'Detail': json.dumps({'hey': 'you'}),
  }]

  bus = botocore.session.get_session().create_client('events')

  stubber = Stubber(bus)
  stubber.add_response('put_events', service_response={'FailedEntryCount': 0}, expected_params={'Entries': entries} )
  stubber.activate()

  connector = EventBridgeConnector(logger=logger)
  connector.bus = bus #*important

  res = connector.put_events(Entries=entries)

  stubber.assert_no_pending_responses()
  assert res == {'FailedEntryCount': 0}
