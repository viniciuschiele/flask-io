try:
    import simplejson as json
except ImportError:
    import json


def json_decode(data):
    return json.loads(data.decode())


def json_encode(data):
    return json.dumps(data).encode()
