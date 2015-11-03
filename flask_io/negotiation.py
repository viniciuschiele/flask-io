from abc import ABCMeta, abstractmethod
from .mediatypes import MediaType


class ContentNegotiation(metaclass=ABCMeta):
    @abstractmethod
    def select_parser(self, request, parsers):
        pass


class DefaultContentNegotiation(ContentNegotiation):
    def select_parser(self, request, parsers):
        """
        Gets the parser which matches to the request's content type.
        """

        # If content_type is none or empty we just return
        # the first parser.
        if not request.content_type:
            return parsers[0]

        media_type = MediaType(request.content_type)

        for parser in parsers:
            if media_type.match(MediaType(parser.media_type)):
                return parser

        return None
