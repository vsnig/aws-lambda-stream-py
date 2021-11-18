import json

from awslambdastream.utils.json import MyEncoder


def test_bytes_encode():
    obj = {"byte_field": b"asdf"}
    res = json.dumps(obj, cls=MyEncoder)
    assert res == '{"byte_field": "asdf"}'
