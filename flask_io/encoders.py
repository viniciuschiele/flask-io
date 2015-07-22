import json


def register_default_decoders(io):
    io.register_encoder('application/json', json_decode)


def register_default_encoders(io):
    io.register_encoder('application/json', json_encode)


def json_decode(data):
    return json.loads(data.decode())


def json_encode(data):
    return json.dumps(data).encode()
