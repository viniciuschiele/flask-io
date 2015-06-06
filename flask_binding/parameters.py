from flask import request
from .binder import Binder

def bind(params):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs.update(Binder.bind(params))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ValueProvider(object):
    def __init__(self, type_, name=None, default=None, required=False, multiple=False):
        self.type = type_
        self.name = name
        self.default = default
        self.required = required
        self.multiple = multiple

    def get_values(self):
        pass


class FromQuery(ValueProvider):
    def get_values(self):
        return request.args
