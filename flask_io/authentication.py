"""
Provides various authentication policies.
"""

from abc import ABCMeta, abstractmethod


class Authenticator(metaclass=ABCMeta):
    """
    A base class from which all authenticator classes should inherit.
    """

    @abstractmethod
    def authenticate(self):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        pass
