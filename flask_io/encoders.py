"""Encoders and decoders used to deserialize the request body and serialize the response body."""

try:
    import simplejson as json
except ImportError:
    import json


def json_decode(data):
    """
    Deserializes a byte array containing a JSON document to a Python object.
    :param data: A byte array containing a JSON document.
    :return: A Python object.
    """
    return json.loads(data.decode())


def json_encode(data):
    """
    Serializes a Python object into a byte array containing a JSON document.
    :param data: A Python object.
    :return: A byte array containing a JSON document.
    """
    return json.dumps(data).encode()
