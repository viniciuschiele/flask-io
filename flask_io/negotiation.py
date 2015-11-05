from abc import ABCMeta, abstractmethod
from .mimetypes import MimeType


class ContentNegotiation(metaclass=ABCMeta):
    @abstractmethod
    def select_parser(self, request, parsers):
        pass

    @abstractmethod
    def select_renderer(self, request, renderers):
        pass


class DefaultContentNegotiation(ContentNegotiation):
    def select_parser(self, request, parsers):
        """
        Gets the parser which matches to the request's content type.
        """

        # If content_type is none or empty we just return the first parser.
        if not request.content_type:
            return parsers[0], parsers[0].mimetype

        mimetype = MimeType(request.content_type)

        for parser in parsers:
            if mimetype.match(parser.mimetype):
                return parser, mimetype

        return None, None

    def select_renderer(self, request, renderers):
        """
        Gets the renderer which matches to the request's accept.
        """

        if not len(request.accept_mimetypes):
            return renderers[0], renderers[0].mimetype

        for mimetype, quality in request.accept_mimetypes:
            accept_mimetype = MimeType(mimetype)
            for renderer in renderers:
                if accept_mimetype.match(renderer.mimetype):
                    return renderer, accept_mimetype

        return None, None
