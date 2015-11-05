"""
Parsers used to deserialize the request body into a Python's object.
"""

try:
    import simplejson as json
except ImportError:
    import json

from abc import ABCMeta, abstractmethod
from .mimetypes import MimeType


class Parser(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, data, mimetype):
        pass


class JSONParser(Parser):
    """
    Parses JSON-serialized data.
    """

    mimetype = MimeType('application/json')

    def parse(self, data, mimetype):
        """
        Deserializes a byte array containing a JSON document to a Python object.
        :param data: A byte array containing a JSON document.
        :return: A Python object.
        """
        encoding = mimetype.params.get('charset') or 'utf-8'

        return json.loads(data.decode(encoding))
