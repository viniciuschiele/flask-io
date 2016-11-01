"""
Renderers used to render a Python object into byte array.
"""

from abc import ABCMeta, abstractmethod
from flask import json
from .mimetypes import MimeType


class Renderer(metaclass=ABCMeta):
    """
    Base class for all renderers.
    """

    mimetype = None

    @abstractmethod
    def render(self, data, mimetype):
        """
        Render the given data into JSON and returns a byte array.
        :param data: The data to be rendered.
        :param mimetype: The mimetype to render the data.
        :return: A byte array.
        """
        pass


class JSONRenderer(Renderer):
    """
    Renderer which render into JSON.
    """

    mimetype = MimeType.parse('application/json')

    def render(self, data, mimetype):
        """
        Serializes a Python object into a byte array containing a JSON document.
        :param data: A Python object.
        :param mimetype: The mimetype to render the data.
        :return: A byte array containing a JSON document.
        """

        indent = self.__get_indent(mimetype)
        encoding = mimetype.params.get('charset') or 'utf-8'
        return json.dumps(data, indent=indent).encode(encoding)

    def __get_indent(self, mimetype):
        """
        Gets the indent parameter from the mimetype.
        :param MimeType mimetype: The mimetype with parameters.
        :return int: The indent if found, otherwise none.
        """
        indent = max(int(mimetype.params.get('indent', '0')), 0)

        if indent == 0:
            return None

        return indent
