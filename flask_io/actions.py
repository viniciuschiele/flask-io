"""

"""

from flask import request
from flask_io import errors


class Action(object):
    def __init__(self, func, default_authenticators, default_permissions, trace_enabled):
        self.func = func

        self.authenticators = default_authenticators
        if hasattr(func, 'authenticators'):
            self.authenticators = func.authenticators

        self.permissions = default_permissions
        if hasattr(func, 'permissions'):
            self.permissions = func.permissions

        self.trace_enabled = trace_enabled

    def __call__(self, *args, **kwargs):
        self.perform_authentication()
        self.perform_authorization()

        return self.func(*args, **kwargs)

    def perform_authentication(self):
        """
        Perform authentication on the incoming request.
        """

        if not self.authenticators:
            return

        request.user = None
        request.auth = None

        for authenticator in self.authenticators:
            auth_tuple = authenticator.authenticate()

            if auth_tuple:
                request.user = auth_tuple[0]
                request.auth = auth_tuple[1]
                break

    def perform_authorization(self):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """

        for permission in self.permissions:
            if not permission.has_permission():
                if request.user:
                    raise errors.PermissionDenied()
                else:
                    raise errors.NotAuthenticated()
