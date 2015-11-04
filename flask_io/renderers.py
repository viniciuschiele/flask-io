"""
Renderers used to serialize a Python object into response body.
"""

from abc import ABCMeta, abstractmethod
from . import json
from .mediatypes import MediaType


class Renderer(metaclass=ABCMeta):
    media_type = None

    @abstractmethod
    def render(self, data, accepted_media_type):
        pass


class JSONRenderer(Renderer):
    media_type = 'application/json'

    def render(self, data, accepted_media_type):
        """
        Serializes a Python object into a byte array containing a JSON document.
        :param data: A Python object.
        :param accepted_media_type:
        :return: A byte array containing a JSON document.
        """

        indent = self.get_indent(accepted_media_type)
        return json.dumps(data, indent=indent).encode('utf-8')

    def get_indent(self, accepted_media_type):
        media_type = MediaType(accepted_media_type)
        indent = media_type.params.get('indent', '0')
        indent = max(min(int(indent), 8), 0)

        if indent == 0:
            return None

        return indent
