"""
Provides a set of pluggable permission policies.
"""

from abc import ABCMeta, abstractmethod
from flask import request


class Permission(metaclass=ABCMeta):
    """
    A base class from which all permission classes should inherit.
    """

    @abstractmethod
    def has_permission(self):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        pass


class IsAuthenticated(Permission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self):
        if not hasattr(request, 'user'):
            return False
        return request.user is not None
