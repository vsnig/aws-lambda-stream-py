import json

from awslambdastream.utils.json import MyEncoder, json_dumps


def test_bytes_encode():
    obj = {"byte_field": b"asdf"}
    res = json.dumps(obj, cls=MyEncoder)
    assert res == '{"byte_field": "asdf"}'


def test_json_dumps():
    obj = {"byte_field": b"asdf"}
    res = json_dumps(obj)
    assert res == '{"byte_field": "asdf"}'
