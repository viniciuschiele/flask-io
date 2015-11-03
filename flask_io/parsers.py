"""Parsers used to deserialize the request body."""

try:
    import simplejson as json
except ImportError:
    import json

from abc import ABCMeta, abstractmethod


class Parser(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, stream):
        pass


class JSONParser(Parser):
    """
    Parses JSON-serialized data.
    """

    media_type = 'application/json'

    def parse(self, data):
        """
        Deserializes a byte array containing a JSON document to a Python object.
        :param data: A byte array containing a JSON document.
        :return: A Python object.
        """
        return json.loads(data.decode())
