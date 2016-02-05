"""
Parsers used to parse a byte array into Python object.
"""

from abc import ABCMeta, abstractmethod
from flask import json
from .mimetypes import MimeType


class Parser(metaclass=ABCMeta):
    """
    Base class for all parsers.
    """

    mimetype = None

    @abstractmethod
    def parse(self, data, mimetype):
        """
        Parses the given data and returns a Python object.
        :param data: The data to be parsed.
        :param mimetype: The mimetype to parse the data.
        :return: A Python object
        """
        pass


class JSONParser(Parser):
    """
    Parses JSON data into Python object.
    """

    mimetype = MimeType('application/json')

    def parse(self, data, mimetype):
        """
        Parses a byte array containing a JSON document and returns a Python object.
        :param data: The byte array containing a JSON document.
        :param MimeType mimetype: The mimetype chose to parse the data.
        :return: A Python object.
        """
        encoding = mimetype.params.get('charset') or 'utf-8'

        return json.loads(data.decode(encoding))
