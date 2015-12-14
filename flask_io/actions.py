"""

"""

from flask import request
from flask_io import errors


class Action(object):
    def __init__(self, func, default_authentications, default_permissions, trace_enabled):
        self.func = func

        self.authentications = default_authentications
        if hasattr(func, 'authentications'):
            self.authentications = func.authentications

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

        if not self.authentications:
            return

        request.user = None
        request.auth = None

        for authentications in self.authentications:
            auth_tuple = authentications.authenticate()

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
