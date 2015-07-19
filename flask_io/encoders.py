import json

from abc import ABCMeta
from abc import abstractmethod


def register_default_encoders(io):
    io.register_encoder(JsonEncoder())


class Encoder(metaclass=ABCMeta):
    @property
    @abstractmethod
    def mime_type(self):
        pass

    @abstractmethod
    def encode(self, data):
        pass

    @abstractmethod
    def decode(self, data):
        pass


class JsonEncoder(Encoder):
    @property
    def mime_type(self):
        return 'application/json'

    def encode(self, data):
        return json.dumps(data).encode()

    def decode(self, data):
        return json.loads(data.decode())
