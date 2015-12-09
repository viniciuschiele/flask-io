"""
Provides a set of pluggable permission policies.
"""

from abc import ABCMeta, abstractmethod


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
