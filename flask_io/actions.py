"""

"""

from flask import request
from flask_io import errors


class Action(object):
    def __init__(self, func, default_authentication, default_permissions, trace_enabled):
        self.func = func

        self.authentication = default_authentication
        if hasattr(func, 'authentication'):
            self.authentication = func.authentication

        self.permissions = default_permissions
        if hasattr(func, 'permissions'):
            self.permissions = func.permissions

        self.trace_enabled = trace_enabled

    def __call__(self, *args, **kwargs):
        self.perform_authentication()
        self.perform_authorization()

        return self.func(*args, **kwargs)

    def get_authenticator(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        if self.authentication:
            return self.authentication()

        return None

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if not self.permissions:
            return []

        return [permission() for permission in self.permissions]

    def perform_authentication(self):
        """
        Perform authentication on the incoming request.
        """

        request.user = None
        request.auth = None

        authenticator = self.get_authenticator()

        if not authenticator:
            return

        auth_tuple = authenticator.authenticate()

        if auth_tuple:
            request.user = auth_tuple[0]
            request.auth = auth_tuple[1]

    def perform_authorization(self):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """

        permissions = self.get_permissions()

        if not permissions:
            return

        for permission in permissions:
            if permission().has_permission():
                break
        else:
            if request.user:
                raise errors.PermissionDenied()
            else:
                raise errors.NotAuthenticated()
