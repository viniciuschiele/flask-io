"""
Provides various authentication policies.
"""

from abc import ABCMeta, abstractmethod


class Authentication(metaclass=ABCMeta):
    """
    A base class from which all authentication classes should inherit.
    """

    @abstractmethod
    def authenticate(self):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        pass
