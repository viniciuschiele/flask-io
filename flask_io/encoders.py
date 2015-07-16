import json

from abc import ABCMeta
from abc import abstractmethod


def get_default_encoders():
    return {
        'application/json': JsonEncoder()
    }


class Encoder(metaclass=ABCMeta):
    @abstractmethod
    def encode(self, data):
        pass

    @abstractmethod
    def decode(self, data):
        pass


class JsonEncoder(Encoder):
    def encode(self, data):
        return json.dumps(data).encode()

    def decode(self, data):
        return json.loads(data.decode())
