from abc import ABCMeta, abstractmethod


class Authentication(metaclass=ABCMeta):
    """
    All authentication classes should extend Authentication.
    """

    @abstractmethod
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        pass
