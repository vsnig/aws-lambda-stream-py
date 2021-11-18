import json


# custom encoder to properly encode b'bytes'
#   https://programmerah.com/solved-typeerror-object-of-type-bytes-is-not-json-serializable-32328/
#   https://stackoverflow.com/questions/40000495/how-to-encode-bytes-in-json-json-dumps-throwing-a-typeerror
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding="ascii")
        else:  # pragma: no cover
            return json.JSONEncoder.default(self, obj)
