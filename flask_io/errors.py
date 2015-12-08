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
        if error:
            self.error = error


class UnauthorizedError(APIError):
    status_code = 401
    error = Error('Access is denied due to invalid credentials.', 'invalid_credentials')
