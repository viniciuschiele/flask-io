class Error(object):
    def __init__(self, message, code=None, location=None, field=None, **kwargs):
        self.message = message
        self.code = code
        self.location = location
        self.field = field
        self.__dict__.update(kwargs)

    def as_dict(self):
        data = self.__dict__.copy()

        for key in set(data.keys()):
            if data[key] is None:
                data.pop(key)

        return data


class APIError(Exception):
    status_code = 500
    error = Error('A server error occurred.', 'server_error')

    def __init__(self, error=None):
        if isinstance(error, str):
            self.error = Error(error)
        elif error:
            self.error = error


class BadRequest(APIError):
    status_code = 400
    error = Error('Invalid request.')


class AuthenticationFailed(APIError):
    status_code = 401
    error = Error('Incorrect authentication credentials.')


class NotAuthenticated(APIError):
    status_code = 401
    error = Error('Authentication credentials were not provided.')


class PermissionDenied(APIError):
    status_code = 403
    error = Error('You do not have permission to perform this action.')


class NotFound(APIError):
    status_code = 404
    error = Error('Not found.')


class NotAcceptable(APIError):
    status_code = 406
    error = Error('Could not satisfy the request Accept header.')


class UnsupportedMediaType(APIError):
    status_code = 415
    error = Error('Unsupported media type in request.')

    def __init__(self, media_type, error=None):
        if error:
            self.error = error
        else:
            self.error = Error(self.error.message)

        self.error.media_type = media_type
