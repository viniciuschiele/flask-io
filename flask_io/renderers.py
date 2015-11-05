"""
Renderers used to serialize a Python object into response body.
"""

from abc import ABCMeta, abstractmethod
from . import json
from .mimetypes import MimeType


class Renderer(metaclass=ABCMeta):
    mimetype = None

    @abstractmethod
    def render(self, data, mimetype):
        pass


class JSONRenderer(Renderer):
    mimetype = MimeType('application/json')

    def render(self, data, mimetype):
        """
        Serializes a Python object into a byte array containing a JSON document.
        :param data: A Python object.
        :return: A byte array containing a JSON document.
        """

        indent = self.get_indent(mimetype)
        encoding = mimetype.params.get('charset') or 'utf-8'
        return json.dumps(data, indent=indent).encode(encoding)

    def get_indent(self, mimetype):
        value = mimetype.params.get('indent', '0')
        indent = max(min(int(value), 8), 0)

        if indent == 0:
            return None

        return indent
